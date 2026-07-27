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
from flake_digest.config import is_test_level
from flake_digest.flakes import record_build
from flake_digest.gcs_source import (
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


def parse_build_results(entry: dict, build: ProwBuild):
    if (build.target and is_test_level(build.target, entry)
            and build.results_raw and build.sha):
        run = RunMeta(origin="midstream", repo=entry["repo"],
                      job=build.target, sha=build.sha,
                      build_id=build.build_id, url=build.url,
                      timestamp=build.timestamp or "")
        return parse_e2e_results(build.results_raw, run)
    return []


def build_key(repo: str, target: str, build_id: str) -> str:
    return f"midstream:{repo}:{target}:{build_id}"


def fold_build(state: dict, build: ProwBuild, results) -> dict:
    # unrecognizable job name or SHA conflict: source already logged it
    job = build.target or build.job
    return record_build(
        state, origin="midstream", repo=build.repo, job=job,
        build_key=build_key(build.repo, job, build.build_id),
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
               "new_occurrences": []}
    floor = min_build_id_for(
        int(time.time() * 1000)
        - (cfg["window_days"] + WINDOW_PAD_DAYS) * 86_400_000)
    for entry in cfg["midstream"]:
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
                out = fold_build(state, build, parse_build_results(entry, build))
                summary["fetched"] += 1
                summary["new_occurrences"] += out["new_occurrences"]
                if done % 25 == 0:
                    progress(f"  {job}: {done}/{len(recent)}")
    return summary
