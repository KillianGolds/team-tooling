"""Flake detection: fold builds into state, counting same-SHA fail/pass pairs.

An occurrence is one (origin, repo, job, nodeid, sha) where both a pass
and a non-pass have been seen. job here is the normalized target
(e2e-predictor), never the branch-embedding Prow name; see
gcs_source.normalize_job. A nodeid shows up at most once per results
file and idempotency keys stop a build from being folded twice, which is
why the two sides of a pair always come from different builds without
any explicit check.

A few things hold no matter the origin. Confirmed and suspected counts
never blend. A build the source couldn't classify (SHA conflict,
unrecognizable job name) gets discarded and counted, not guessed into a
pair. And absence never pairs: only results present in tests[] reach
this module, so a truncated run's missing tests stay unknown, while the
results it did write are real observations and count like any other.
skipped/xfailed/xpassed sit on neither side.

What separates confirmed from suspected is the origin's own call (see
CLASSIFIERS): the substrates fail differently in kind, not degree.
"""
from flake_digest.model import JOB_LEVEL_NODEID, FlakeRecord, TestResult
from flake_digest import store


def record_build(
    state: dict,
    *,
    origin: str,
    repo: str,
    job: str,
    build_key: str,
    sha: str | None,
    base_sha: str | None = None,
    sha_verified: bool = False,
    discard: bool = False,
    has_results: bool = False,
    no_results_reason: str | None = None,
    branch: str | None = None,
    job_name: str | None = None,
    timestamp: str | None,
    url: str,
    job_result: str | None = None,
    test_results: list[TestResult] = (),
) -> dict:
    """Fold one build into state. Returns
    {"skipped": bool, "run_counted": bool, "discarded": bool,
     "new_occurrences": [record keys]}.

    job_result feeds the job-level row; only SUCCESS and FAILURE are
    signals. ABORTED and missing results mean the build never really ran,
    so it doesn't count toward the run denominator either. sha=None still
    counts as a run but can't participate in pairing. discard=True means
    the source flagged the build unclassifiable; it only bumps counters.
    """
    if store.is_processed(state, build_key):
        return {"skipped": True, "run_counted": False, "discarded": False,
                "new_occurrences": []}
    store.mark_processed(state, build_key)

    job_key = f"{origin}|{repo}|{job}"
    completed = job_result in ("SUCCESS", "FAILURE") or bool(test_results)
    if completed:
        state["job_runs"][job_key] = state["job_runs"].get(job_key, 0) + 1

    if discard:
        state["discarded"][job_key] = state["discarded"].get(job_key, 0) + 1
        return {"skipped": False, "run_counted": completed, "discarded": True,
                "new_occurrences": []}

    new: list[str] = []
    common = dict(base_sha=base_sha, sha_verified=sha_verified,
                  ts=timestamp, url=url, build_key=build_key,
                  branch=branch, job_name=job_name,
                  no_results_reason=no_results_reason)
    if sha:
        if job_result in ("SUCCESS", "FAILURE"):
            occ = _record_outcome(
                state, origin, repo, job, JOB_LEVEL_NODEID, sha,
                passed=(job_result == "SUCCESS"), has_results=has_results,
                failure_message=None, **common)
            if occ:
                new.append(occ)
        for r in test_results:
            if r.is_neutral:
                continue
            occ = _record_outcome(
                state, origin, repo, job, r.nodeid, sha,
                passed=r.is_pass, has_results=True,
                failure_message=r.failure_message, **common)
            if occ:
                new.append(occ)

    return {"skipped": False, "run_counted": completed, "discarded": False,
            "new_occurrences": new}


def _record_outcome(state, origin, repo, job, nodeid, sha, *, passed,
                    base_sha, sha_verified, has_results, ts, url,
                    build_key, branch, job_name, no_results_reason,
                    failure_message):
    """Update the sha_index for one observation; if this completes a
    fail/pass pair not yet counted, record the occurrence and return the
    FlakeRecord key. At most one occurrence per sha; the stored side is
    the latest observation of each kind."""
    entry = state["sha_index"].setdefault(
        f"{origin}|{repo}|{job}|{nodeid}|{sha}",
        {"pass": None, "fail": None, "counted": False},
    )
    obs = {
        "build_id": build_key.rsplit(":", 1)[-1],
        "url": url,
        "timestamp": ts,
        "outcome": "pass" if passed else "fail",
        "branch": branch,
        "job_name": job_name,
        "base_sha": base_sha,
        "head_verified": sha_verified,
        "has_results": has_results,
        "no_results_reason": no_results_reason,
    }
    if passed:
        entry["pass"] = obs
    else:
        obs["failure_message"] = failure_message
        entry["fail"] = obs

    if not (entry["pass"] and entry["fail"] and not entry["counted"]):
        return None
    entry["counted"] = True

    classification, tag = classify_pair(origin, entry["pass"], entry["fail"])
    key = f"{origin}|{repo}|{job}|{nodeid}"
    rec = state["flakes"].get(key)
    if rec is None:
        rec = FlakeRecord(origin=origin, repo=repo, job=job,
                          nodeid=nodeid).to_dict()
        state["flakes"][key] = rec

    if classification == "confirmed":
        rec["confirmed_count"] += 1
    else:
        rec["suspected_count"] += 1
    rec["shas_flaked"].append(sha)
    rec["occurrences"].append({
        "sha": sha,
        "classification": classification,
        "tag": tag,
        "fail": {k: entry["fail"][k] for k in
                 ("build_id", "url", "timestamp", "outcome", "branch",
                  "job_name", "base_sha", "no_results_reason",
                  "failure_message")},
        "pass": {k: entry["pass"][k] for k in
                 ("build_id", "url", "timestamp", "outcome", "branch",
                  "job_name", "base_sha")},
    })
    occurred = ts or entry["fail"]["timestamp"]
    if occurred:
        # ISO 8601 UTC strings, so lexicographic comparison is fine
        if rec["first_seen"] is None or occurred < rec["first_seen"]:
            rec["first_seen"] = occurred
        if rec["last_seen"] is None or occurred > rec["last_seen"]:
            rec["last_seen"] = occurred
    rec["last_failure_url"] = entry["fail"]["url"]
    return key


# --- per-origin classification ---
#
# One predicate can't serve every substrate; they fail differently in
# kind. Prow tests the PR merged onto its base branch, so the base can
# move between reruns, and that movement is what the predicate below
# guards. Konflux (deferred) never merges: it tests the PR branch tip
# against images from a built snapshot, so its hazard is a rerun testing
# newer source against older images, and having no base is normal there,
# not weak evidence. Upstream GHA (deferred) tests the branch head
# directly and dodges both. Each grows its own predicate when its
# fetcher lands; an origin without one can only ever say suspected.

def _classify_prow(pass_obs: dict, fail_obs: dict) -> tuple[str, str]:
    base_p, base_f = pass_obs["base_sha"], fail_obs["base_sha"]
    if base_p and base_f:
        tag = "same_base" if base_p == base_f else "base_moved"
    else:
        tag = "base_unknown"
    confirmed = (
        tag == "same_base"
        and pass_obs["head_verified"] and fail_obs["head_verified"]
        and pass_obs["has_results"] and fail_obs["has_results"]
    )
    return ("confirmed" if confirmed else "suspected"), tag


CLASSIFIERS = {
    "midstream": _classify_prow,
}


def classify_pair(origin: str, pass_obs: dict, fail_obs: dict) -> tuple[str, str]:
    """(classification, tag) for a completed pair. Confirmed only ever
    comes from an origin-specific predicate; anything else is suspected."""
    fn = CLASSIFIERS.get(origin)
    if fn is None:
        return "suspected", "no_classifier_for_origin"
    return fn(pass_obs, fail_obs)
