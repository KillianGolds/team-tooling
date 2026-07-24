"""Local preview of midstream fetching, parsing, and flake detection.
Writes nothing.

Usage:
    python -m flake_digest.dump PR [PR ...]             # per-build preview
    python -m flake_digest.dump PR [PR ...] --evidence  # detected pairs as
                                                        # auditable bundles
"""
import argparse
import sys
from collections import Counter

from flake_digest import store
from flake_digest.config import is_test_level, load_config
from flake_digest.flakes import record_build
from flake_digest.gcs_source import ProwBuild, fetch_build, list_build_ids, list_job_dirs
from flake_digest.model import RunMeta
from flake_digest.parser import parse_e2e_results


def fetch_pr_builds(entry: dict, pr: int, max_builds: int | None = None):
    """Yield (build, test_results) for every e2e build of one PR."""
    for job in list_job_dirs(entry["repo"], pr, entry["job_pattern"]):
        build_ids = list_build_ids(entry["repo"], pr, job)
        if max_builds:
            build_ids = build_ids[-max_builds:]
        for build_id in build_ids:
            build = fetch_build(entry["repo"], pr, job, build_id)
            results = []
            if (build.target and is_test_level(build.target, entry)
                    and build.results_raw and build.sha):
                run = RunMeta(origin="midstream", repo=entry["repo"],
                              job=build.target, sha=build.sha,
                              build_id=build_id, url=build.url,
                              timestamp=build.timestamp or "")
                results = parse_e2e_results(build.results_raw, run)
            yield build, results


def fold_build(state: dict, build: ProwBuild, results) -> dict:
    # unrecognizable job name or SHA conflict: source already logged it
    job = build.target or build.job
    return record_build(
        state, origin="midstream", repo=build.repo, job=job,
        build_key=f"midstream:{build.repo}:{job}:{build.build_id}",
        sha=build.sha, base_sha=build.base_sha,
        sha_verified=build.sha_verified,
        discard=build.sha_conflict or build.target is None,
        has_results=build.has_results_file,
        no_results_reason=build.no_results_reason,
        branch=build.branch, job_name=build.job,
        timestamp=build.timestamp, url=build.url,
        job_result=build.result, test_results=results)


def print_evidence(state: dict) -> None:
    """Render every detected pair as a human-auditable bundle."""
    flakes = sorted(
        state["flakes"].values(),
        key=lambda r: (-r["confirmed_count"], -r["suspected_count"]))
    for rec in flakes:
        print(f"\n{rec['origin']} {rec['repo']} {rec['job']}")
        print(f"  {rec['nodeid']}")
        print(f"  confirmed={rec['confirmed_count']} "
              f"suspected={rec['suspected_count']}")
        for occ in rec["occurrences"]:
            print(f"  [{occ['classification']}, {occ['tag']}] "
                  f"sha {occ['sha'][:12]}")
            for side in ("fail", "pass"):
                s = occ[side]
                print(f"    {side.upper():4} {s['timestamp']}  build {s['build_id']}"
                      f"  (branch {s['branch']})")
                print(f"         {s['url']}")
            reason = occ["fail"].get("no_results_reason")
            if reason:
                print(f"    no results file on failing side: {reason}")
            msg = occ["fail"].get("failure_message")
            if msg:
                print(f"    failure: {msg.splitlines()[0][:110]}")
    if state["discarded"]:
        print(f"\ndiscarded (SHA-conflict) builds: {state['discarded']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prs", type=int, nargs="+")
    ap.add_argument("--evidence", action="store_true",
                    help="fold all builds and print detected pairs as bundles")
    ap.add_argument("--max-builds", type=int, default=None,
                    help="newest N builds per job (default: all)")
    args = ap.parse_args()

    cfg = load_config()
    state = store.empty_state()
    for entry in cfg["midstream"]:
        for pr in args.prs:
            for build, results in fetch_pr_builds(entry, pr, args.max_builds):
                out = fold_build(state, build, results)
                if not args.evidence:
                    sha = (build.sha or "?")[:12]
                    counts = dict(Counter(r.outcome for r in results))
                    print(f"{build.job} {build.build_id} result={build.result} "
                          f"sha={sha} verified={build.sha_verified} "
                          f"tests={counts or '-'} "
                          f"new_pairs={len(out['new_occurrences'])}")

    if args.evidence:
        print_evidence(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
