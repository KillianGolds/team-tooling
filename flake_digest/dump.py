"""Local preview of midstream fetching, parsing, detection, and rendering.
Writes nothing unless --out is given.

Usage:
    python -m flake_digest.dump 1613 1606              # per-build preview
    python -m flake_digest.dump 1613 --evidence        # pairs as bundles
    python -m flake_digest.dump --window-days 30 --render --out DIR
        # backfill everything in the window, render the issue body and
        # report pages, run the cross-ref assertions, write under DIR
"""
import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from flake_digest import store
from flake_digest.config import load_config
from flake_digest.gcs_source import fetch_build, list_build_ids, list_job_dirs
from flake_digest.markdown_formatter import ensure_render_safe, render_issue_body
from flake_digest.reports import build_pages, write_reports
from flake_digest.runner import fold_build, fold_window, parse_build_results


def fetch_pr_builds(entry: dict, pr: int, max_builds: int | None = None):
    """(build, test_results) for every e2e build of one PR."""
    for job in list_job_dirs(entry["repo"], pr, entry["job_pattern"]):
        build_ids = list_build_ids(entry["repo"], pr, job)
        if max_builds:
            build_ids = build_ids[-max_builds:]
        for build_id in build_ids:
            build = fetch_build(entry["repo"], pr, job, build_id)
            yield build, parse_build_results(entry, build)


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
                base = s.get("base_sha")
                print(f"    {side.upper():4} {s['timestamp']}  build {s['build_id']}"
                      f"  (branch {s['branch']}"
                      + (f", base {base[:12]}" if base else "") + ")")
                print(f"         {s['url']}")
            reason = occ["fail"].get("no_results_reason")
            if reason:
                print(f"    no results file on failing side: {reason}")
            msg = occ["fail"].get("failure_message")
            if msg:
                print(f"    failure: {msg.splitlines()[0][:110]}")
    if state["discarded"]:
        print(f"\ndiscarded (unclassifiable) builds: {state['discarded']}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("prs", type=int, nargs="*")
    ap.add_argument("--window-days", type=int, default=None,
                    help="ignore the PR list; fetch everything in the window")
    ap.add_argument("--evidence", action="store_true",
                    help="print detected pairs as auditable bundles")
    ap.add_argument("--render", action="store_true",
                    help="render issue body + report pages, run the "
                         "cross-ref and size assertions")
    ap.add_argument("--out", type=Path, default=None,
                    help="with --render: write body.md and reports/ here")
    ap.add_argument("--max-builds", type=int, default=None,
                    help="newest N builds per job (PR mode only)")
    args = ap.parse_args()
    if not args.prs and args.window_days is None:
        ap.error("give PR numbers or --window-days")

    cfg = load_config()
    state = store.empty_state()
    if args.window_days is not None:
        cfg["window_days"] = args.window_days
        fold_window(state, cfg, progress=lambda m: print(m, file=sys.stderr))
    else:
        for entry in cfg["midstream"]:
            for pr in args.prs:
                for build, results in fetch_pr_builds(entry, pr, args.max_builds):
                    out = fold_build(state, build, results)
                    if not (args.evidence or args.render):
                        sha = (build.sha or "?")[:12]
                        counts = dict(Counter(r.outcome for r in results))
                        print(f"{build.job} {build.build_id} result={build.result} "
                              f"sha={sha} verified={build.sha_verified} "
                              f"tests={counts or '-'} "
                              f"new_pairs={len(out['new_occurrences'])}")

    if args.evidence:
        print_evidence(state)
    if args.render:
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        body = render_issue_body(state, cfg, now)
        ensure_render_safe(body, "issue body")
        pages = build_pages(state)
        print(f"render checks passed: issue body {len(body)} chars, "
              f"{len(pages)} report page(s)", file=sys.stderr)
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            (args.out / "body.md").write_text(body)
            write_reports(state, args.out / "reports")
            store.save_state(state, args.out / "flakes_state.json")
            print(f"wrote {args.out}/body.md, reports/, flakes_state.json",
                  file=sys.stderr)
        else:
            print(body)
    return 0


if __name__ == "__main__":
    sys.exit(main())
