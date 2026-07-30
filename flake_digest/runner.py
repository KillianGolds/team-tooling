"""Shared fetch-and-fold pipeline, used by dump (preview) and issue (cron).

fold_window is incremental: the directory listing gives build ids before
any build is fetched, so anything already in processed_builds is skipped
without a single request. A build with no finished.json yet is still
running; it's left unmarked so the next run picks it up once Prow writes
the result.
"""
import sys
import time

from flake_digest import store
from flake_digest.config import bare_untrusted, is_job_level_only
from flake_digest.flakes import record_build
from flake_digest.gcs_source import (
    _BARE_RESULTS,
    ProwBuild,
    fetch_build,
    list_job_directories,
    list_recent_builds,
    min_build_id_for,
    normalize_job,
)
from flake_digest.model import RunMeta
from flake_digest.parser import parse_e2e_results

# the snowflake window floor is decoded from an inferred id scheme, so
# over-include on the old side; a build listed twice is skipped as
# processed, a build silently missed is invisible
WINDOW_PAD_DAYS = 2


def file_disposition(entry: dict, build: ProwBuild) -> str:
    """What to do with a build's results files:
    parse / bare_untrusted / job_level_only / no_files.

    bare_untrusted is per-build on purpose: a raw build with suffixed
    per-invocation files parses normally, while a historical build whose
    only file is the clobbered bare one stays job-level. Driving this off
    what files the build actually has means no exclusion flip is ever
    needed as the migration rolls through.
    """
    if not build.results_files:
        return "no_files"
    if build.target is None or is_job_level_only(build.target, entry):
        return "job_level_only"
    only_bare = all(path.rsplit("/", 1)[-1] == _BARE_RESULTS
                    for path, _ in build.results_files)
    if only_bare and bare_untrusted(build.target, entry):
        return "bare_untrusted"
    return "parse"


def parse_build_results(entry: dict, build: ProwBuild):
    """Parse and merge every trusted results file of one build.

    Multiple files mean multiple pytest invocations; detection has to see
    the union, because picking one file would reintroduce exactly the
    blindness the per-invocation split fixed. Invocations select disjoint
    markers so a nodeid should appear in one file only; if it shows up in
    two, the non-pass observation wins (that's the side flake pairing
    cares about) and it gets logged, since it means markers overlap.
    """
    if file_disposition(entry, build) != "parse" or not build.sha:
        return []
    run = RunMeta(origin="midstream", repo=entry["repo"],
                  job=build.target, sha=build.sha,
                  build_id=build.build_id, url=build.url,
                  timestamp=build.timestamp or "")
    merged = {}
    for path, raw in build.results_files:
        for r in parse_e2e_results(raw, run):
            prev = merged.get(r.nodeid)
            if prev is None:
                merged[r.nodeid] = r
            else:
                print(f"WARNING: {r.nodeid} appears in more than one "
                      f"results file of {build.prefix} (marker overlap?); "
                      f"keeping the non-pass observation", file=sys.stderr)
                if not prev.is_non_pass and r.is_non_pass:
                    merged[r.nodeid] = r
    return list(merged.values())


def build_key(repo: str, target: str, build_id: str) -> str:
    return f"midstream:{repo}:{target}:{build_id}"


def build_timing(build: ProwBuild, results) -> dict | None:
    """Per-build timing aggregate for results-bearing builds; None
    otherwise. Aggregate on purpose: the headroom feature needs per-job
    trailing averages, and per-test durations for every build would blow
    up the state file for nothing it uses. Reader-side concerns stay
    reader-side: outcome and truncation ride along untouched, and
    files_parsed vs files_expected exposes a listed-but-unfetchable
    invocation file, so a partial total can't silently read as the build
    getting faster."""
    if not results:
        return None
    durations = [r.duration for r in results if r.duration is not None]
    wall = None
    if build.started_unix and build.finished_unix:
        wall = build.finished_unix - build.started_unix
    return {
        "tests_total_s": round(sum(durations), 3),
        "test_count": len(results),
        "wall_clock_s": wall,
        "result": build.result,
        "truncated": any(r.truncated for r in results),
        "files_parsed": len(build.results_files),
        "files_expected": len(build.result_paths),
    }


def fold_build(state: dict, build: ProwBuild, results) -> dict:
    # unrecognizable job name or SHA conflict: source already logged it
    job = build.target or build.job
    return record_build(
        state, origin="midstream", repo=build.repo, job=job,
        build_key=build_key(build.repo, job, build.build_id),
        timing=build_timing(build, results),
        sha=build.sha, base_sha=build.base_sha,
        sha_verified=build.sha_verified,
        discard=build.sha_conflict or build.target is None,
        has_results=build.has_results_file,
        no_results_reason=build.no_results_reason,
        branch=build.branch, job_name=build.job,
        timestamp=build.timestamp, url=build.url,
        job_result=build.result, test_results=results)


def fold_window(state: dict, cfg: dict, progress=lambda msg: None) -> dict:
    """Fold every unseen completed build in the window into state."""
    summary = {"listed": 0, "fetched": 0, "known": 0, "pending": 0,
               "bare_untrusted_skips": 0, "new_occurrences": []}
    floor = min_build_id_for(
        int(time.time() * 1000)
        - (cfg["window_days"] + WINDOW_PAD_DAYS) * 86_400_000)
    transition_list_exists = False
    for entry in cfg["midstream"]:
        if entry["bare_untrusted_until_migrated"]:
            transition_list_exists = True
        for job in list_job_directories(entry["repo"], entry["job_pattern"]):
            normalized = normalize_job(job, entry["repo"])
            target = normalized[0] if normalized else job
            recent = list_recent_builds(entry["repo"], job, floor)
            summary["listed"] += len(recent)
            progress(f"{job}: {len(recent)} builds in window")
            for done, (pr, bid) in enumerate(recent, 1):
                if store.is_processed(state, build_key(entry["repo"], target, bid)):
                    summary["known"] += 1
                    continue
                build = fetch_build(entry["repo"], pr, job, bid)
                if build.result is None and not build.has_results_file:
                    summary["pending"] += 1
                    continue
                if file_disposition(entry, build) == "bare_untrusted":
                    summary["bare_untrusted_skips"] += 1
                out = fold_build(state, build, parse_build_results(entry, build))
                summary["fetched"] += 1
                summary["new_occurrences"] += out["new_occurrences"]
                if done % 25 == 0:
                    progress(f"  {job}: {done}/{len(recent)}")
    # the transition list only exists to guard pre-migration bare files;
    # once runs stop seeing any, it's guarding nothing and can go
    if (transition_list_exists and summary["fetched"]
            and not summary["bare_untrusted_skips"]):
        progress("bare_untrusted_until_migrated matched nothing this run; "
                 "once pre-migration builds have aged out of the window "
                 "the list can be deleted from config.yml")
    return summary
