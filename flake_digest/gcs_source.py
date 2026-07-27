"""Fetch midstream Prow results from the public test-platform-results bucket.

Anonymous GCS JSON API via requests; no credentials or gsutil needed. A few
things I confirmed against live builds (PRs 1505/1606/1613, 2026-07):

- started.json's repos value is comma-separated "<ref>:<sha>" pairs: the
  target branch first (any name, not just master), then one entry per PR
  (batch runs list several). finished.json independently carries the head
  SHA in its top-level `revision`. Both get read and must agree before
  the SHA counts as verified; if they disagree the build is
  unclassifiable, because a wrong grouping key fabricates or hides pairs.
- The `pull` key is the PR number and repo-commit is the merged test
  commit, which moves as master moves; neither can group same-commit
  reruns.
- ci-operator writes a finished.json per step deep in the tree (must-gather
  steps included). The job-level result must come only from the build-root
  <build_id>/finished.json, which I fetch by exact name.
- A full build tree is thousands of objects (must-gather dumps), so this
  module only ever does names-only listings and downloads basename matches.
  An infra-failed build can have no e2e_results.json at all; that stays a
  job-level data point with no test rows.
"""
import json
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BUCKET_API = "https://storage.googleapis.com/storage/v1/b/test-platform-results/o"
PROW_VIEW = "https://prow.ci.openshift.org/view/gs/test-platform-results/"

RESULT_BASENAME = "e2e_results.json"

# a full git SHA; anything else in a sha slot means the format changed
_FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")

# a backfill makes thousands of small requests over an hour, so a single
# transient reset will happen (the first bootstrap run died to exactly
# that); retry connect/read errors and the usual 429/5xx with backoff
_session = requests.Session()
_session.mount("https://", HTTPAdapter(max_retries=Retry(
    total=5, connect=5, read=5, backoff_factor=1.0,
    status_forcelist=(429, 500, 502, 503, 504),
    allowed_methods=("GET",))))


def pr_logs_prefix(repo: str) -> str:
    """GCS prefix for a repo's PR builds, e.g. "opendatahub-io/kserve" ->
    "pr-logs/pull/opendatahub-io_kserve/"."""
    return f"pr-logs/pull/{repo.replace('/', '_')}/"


@dataclass
class ProwBuild:
    """One Prow build of one job: job-level signal plus any test results."""
    repo: str
    job: str                           # full Prow job name, kept for evidence
    build_id: str
    prefix: str
    url: str
    target: str | None = None          # normalized job key, e.g. "e2e-predictor"
    branch: str | None = None
    sha: str | None = None
    sha_verified: bool = False         # started.json and finished.json agree
    sha_conflict: bool = False         # they disagree: build unclassifiable
    base_sha: str | None = None
    result: str | None = None          # finished.json: SUCCESS/FAILURE/ABORTED
    timestamp: str | None = None       # ISO 8601 from finished.json
    has_results_file: bool = False
    no_results_reason: str | None = None   # timeout / setup_failure / unknown
    results_raw: bytes | None = None
    result_paths: list[str] = field(default_factory=list)


def normalize_job(job: str, repo: str) -> tuple[str, str] | None:
    """(target, branch) from a full Prow job name, or None if unrecognized.

    Presubmit names look like pull-ci-<org>-<repo>-<branch>-<target>, and
    hyphens appear inside org, repo, AND branch (stable-2.x, release-v0.17),
    so position alone can't split them. What holds instead: the repo slug is
    a known prefix, and every target this tool ingests starts with "e2e-",
    so the branch is whatever sits between the slug and the first "-e2e-".
    Keying on the target keeps a row's history through branch renames
    (master -> stable), which would otherwise silently reset every count.

    A name that doesn't fit gets None, not a guess; a guessed key orphans
    history the same way a guessed SHA fabricates pairs.
    """
    prefix = f"pull-ci-{repo.replace('/', '-')}-"
    if not job.startswith(prefix):
        return None
    rest = job[len(prefix):]
    marker = rest.find("-e2e-")
    if marker < 1:
        return None
    return rest[marker + 1:], rest[:marker]


# no_results_reason markers, checked in this order: Prow's entrypoint
# writes "Process did not finish" on its ~2h SIGTERM; the e2e script
# prints "Starting E2E" once pytest is actually reached, so its absence
# points at setup/provisioning death.
TIMEOUT_MARKER = "Process did not finish"
PYTEST_REACHED_MARKER = "Starting E2E"

# don't pull huge logs just to classify; over this size the reason stays
# unknown
MAX_BUILD_LOG_BYTES = 8_000_000


def classify_no_results(build_log: str | None) -> str:
    if build_log is None:
        return "unknown"
    if TIMEOUT_MARKER in build_log:
        return "timeout"
    if PYTEST_REACHED_MARKER not in build_log:
        return "setup_failure"
    return "unknown"


# Prow build ids look like bwmarrin/snowflake output: id >> 22 is ms
# since Twitter's epoch. Checked one against its started.json and it
# landed within 7 seconds, and time-sorted ids are what make the
# pr-logs/directory/<job>/ listing windowable with startOffset, so the
# whole pipeline runs without a GitHub API call or any credentials.
# It's still an inferred scheme, not a documented contract: use it only
# to pick where a listing starts, pad windows generously on the old side
# (over-including is cheap, silently missing builds is not), and keep
# started/finished.json as the timestamps that actually get stored.
SNOWFLAKE_EPOCH_MS = 1288834974657


def min_build_id_for(unix_ms: int) -> int:
    return max(0, unix_ms - SNOWFLAKE_EPOCH_MS) << 22


def build_id_unix_ms(build_id: int) -> int:
    return (build_id >> 22) + SNOWFLAKE_EPOCH_MS


def list_job_directories(repo: str, job_re: str) -> list[str]:
    """All of a repo's job names (any branch) from pr-logs/directory/,
    filtered by job_re. New branches appear here automatically."""
    prefix = f"pr-logs/directory/pull-ci-{repo.replace('/', '-')}-"
    pattern = re.compile(job_re)
    return [
        name for p in _list_prefixes(prefix)
        if pattern.match(name := p.rstrip("/").rsplit("/", 1)[-1])
    ]


def list_recent_builds(repo: str, job: str,
                       min_build_id: int) -> list[tuple[int, str]]:
    """(pr_number, build_id) for every build of `job` at or after
    min_build_id, across ALL PRs including closed ones. Each directory
    entry is a tiny text file whose content is the gs:// path of the real
    build, which carries the PR number."""
    prefix = f"pr-logs/directory/{job}/"
    out = []
    for name in _list_names(prefix, start_offset=f"{prefix}{min_build_id}"):
        if not name.endswith(".txt") or name.endswith("latest-build.txt"):
            continue
        content = _fetch(name)
        entry = _parse_directory_entry(content.decode() if content else "", repo, job)
        if entry:
            out.append(entry)
        else:
            print(f"WARNING: unrecognized directory entry {name}; skipped",
                  file=sys.stderr)
    return out


def _parse_directory_entry(content: str, repo: str,
                           job: str) -> tuple[int, str] | None:
    """gs://<bucket>/pr-logs/pull/<repo_slug>/<pr>/<job>/<build_id> ->
    (pr, build_id), or None if the shape is off."""
    parts = content.strip().split("/")
    try:
        pr = int(parts[-3])
    except (IndexError, ValueError):
        return None
    if parts[-2] != job or not parts[-1].isdigit():
        return None
    return pr, parts[-1]


def list_job_dirs(repo: str, pr_number: int, job_re: str) -> list[str]:
    """Job directory names under a PR's pr-logs, filtered by job_re."""
    prefix = f"{pr_logs_prefix(repo)}{pr_number}/"
    pattern = re.compile(job_re)
    return [
        p.rstrip("/").rsplit("/", 1)[-1]
        for p in _list_prefixes(prefix)
        if pattern.match(p.rstrip("/").rsplit("/", 1)[-1])
    ]


def list_build_ids(repo: str, pr_number: int, job: str) -> list[str]:
    """Build IDs for one job; every rerun is a distinct build."""
    prefix = f"{pr_logs_prefix(repo)}{pr_number}/{job}/"
    return [p.rstrip("/").rsplit("/", 1)[-1] for p in _list_prefixes(prefix)]


def fetch_build(repo: str, pr_number: int, job: str, build_id: str) -> ProwBuild:
    """Fetch one build's job-level result and its e2e_results.json if any."""
    prefix = f"{pr_logs_prefix(repo)}{pr_number}/{job}/{build_id}/"
    build = ProwBuild(repo=repo, job=job, build_id=build_id, prefix=prefix,
                      url=PROW_VIEW + prefix.rstrip("/"))

    normalized = normalize_job(job, repo)
    if normalized:
        build.target, build.branch = normalized
    else:
        print(f"WARNING: job name {job!r} doesn't fit "
              f"pull-ci-<repo>-<branch>-e2e-<target>; build discarded as "
              f"unclassifiable", file=sys.stderr)

    finished = _fetch_json(prefix + "finished.json")
    if finished:
        build.result = finished.get("result")
        ts = finished.get("timestamp")
        if ts:
            build.timestamp = datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()

    started = _fetch_json(prefix + "started.json")
    started_sha = head_sha_from_started(started, pr_number) if started else None
    finished_sha = None
    if finished:
        rev = finished.get("revision")
        if isinstance(rev, str) and _FULL_SHA_RE.match(rev):
            finished_sha = rev
    build.sha, build.sha_verified, build.sha_conflict = _resolve_head(
        started_sha, finished_sha)
    if build.sha_conflict:
        print(f"WARNING: head SHA conflict in {prefix}: started={started_sha} "
              f"finished.revision={finished_sha}; build discarded as "
              f"unclassifiable", file=sys.stderr)
    elif build.sha is None and (started or finished):
        print(f"WARNING: no head SHA for PR {pr_number} in {prefix}; "
              f"build left unclassifiable", file=sys.stderr)
    if started:
        build.base_sha = base_sha_from_started(started, pr_number)

    build.result_paths = [
        n for n in _list_names(prefix)
        if n.rsplit("/", 1)[-1] == RESULT_BASENAME
    ]
    if build.result_paths:
        build.has_results_file = True
        build.results_raw = _fetch(build.result_paths[0])
    elif build.result == "FAILURE":
        # only the minority of builds lack results; the build log tells
        # timeout apart from setup death, which have different owners
        build.no_results_reason = classify_no_results(
            _fetch_build_log(prefix))
    return build


def _fetch_build_log(prefix: str) -> str | None:
    size = _object_size(prefix + "build-log.txt")
    if size is None or size > MAX_BUILD_LOG_BYTES:
        return None
    raw = _fetch(prefix + "build-log.txt")
    return None if raw is None else raw.decode("utf-8", errors="replace")


def _object_size(name: str) -> int | None:
    r = _get(f"{BUCKET_API}/{quote(name, safe='')}", {"fields": "size"},
             timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return int(r.json().get("size", 0))


def head_sha_from_started(started: dict, pr_number: int) -> str | None:
    """Pull this PR's head SHA out of started.json's repos value.

    Only the entry whose ref equals our PR number counts, and the sha must
    look like a full git SHA. Anything else returns None rather than a
    guess.
    """
    want = str(pr_number)
    for spec in started.get("repos", {}).values():
        if not isinstance(spec, str):
            continue
        for segment in spec.split(","):
            ref, _, sha = segment.partition(":")
            if ref == want:
                return sha if _FULL_SHA_RE.match(sha) else None
    return None


def base_sha_from_started(started: dict, pr_number: int) -> str | None:
    """The target branch's SHA from the same repos value: the first segment
    whose ref is neither our PR number nor numeric (a numeric ref is
    another PR from a batch run; branch names aren't purely numeric)."""
    want = str(pr_number)
    for spec in started.get("repos", {}).values():
        if not isinstance(spec, str):
            continue
        for segment in spec.split(","):
            ref, _, sha = segment.partition(":")
            if ref == want or ref.isdigit():
                continue
            return sha if _FULL_SHA_RE.match(sha) else None
    return None


def _resolve_head(started_sha: str | None,
                  finished_sha: str | None) -> tuple[str | None, bool, bool]:
    """(sha, verified, conflict). Verified means both sources agree; one
    source alone is usable but weaker evidence; disagreement means neither
    can be trusted."""
    if started_sha and finished_sha:
        if started_sha == finished_sha:
            return started_sha, True, False
        return None, False, True
    if started_sha or finished_sha:
        return started_sha or finished_sha, False, False
    return None, False, False


# --- GCS JSON API plumbing ---

def _get(url: str, params: dict, timeout: int) -> requests.Response:
    # the adapter's Retry covers connect/read failures, but a reset that
    # lands mid response body still escapes it; one more try is enough
    try:
        return _session.get(url, params=params, timeout=timeout)
    except requests.ConnectionError:
        time.sleep(2)
        return _session.get(url, params=params, timeout=timeout)


def _api(params: dict) -> dict:
    r = _get(BUCKET_API, params, timeout=30)
    r.raise_for_status()
    return r.json()


def _fetch(name: str) -> bytes | None:
    r = _get(f"{BUCKET_API}/{quote(name, safe='')}", {"alt": "media"},
             timeout=60)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.content


def _fetch_json(name: str) -> dict | None:
    raw = _fetch(name)
    return None if raw is None else json.loads(raw)


def _list_prefixes(prefix: str) -> list[str]:
    prefixes, token = [], None
    while True:
        params = {"prefix": prefix, "delimiter": "/",
                  "fields": "prefixes,nextPageToken"}
        if token:
            params["pageToken"] = token
        d = _api(params)
        prefixes += d.get("prefixes", [])
        token = d.get("nextPageToken")
        if not token:
            return prefixes


def _list_names(prefix: str, start_offset: str | None = None) -> list[str]:
    names, token = [], None
    while True:
        params = {"prefix": prefix, "fields": "items/name,nextPageToken"}
        if start_offset:
            params["startOffset"] = start_offset
        if token:
            params["pageToken"] = token
        d = _api(params)
        names += [i["name"] for i in d.get("items", [])]
        token = d.get("nextPageToken")
        if not token:
            return names
