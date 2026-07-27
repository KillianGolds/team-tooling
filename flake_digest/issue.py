"""Fold new midstream builds, refresh state and reports/, and rewrite the
pinned flake issue. The cron entrypoint.

Usage:
    python -m flake_digest.issue               # fold, write, update the issue
    python -m flake_digest.issue --no-publish  # fold and write, skip the issue
    python -m flake_digest.issue --dry-run     # print the body, write nothing
"""
import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from common.issue import resolve_write_token, rewrite_issue
from flake_digest import store
from flake_digest.config import load_config
from flake_digest.markdown_formatter import ensure_render_safe, render_issue_body
from flake_digest.reports import write_reports
from flake_digest.runner import fold_window

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--no-publish", action="store_true",
                    help="write state and reports but leave the issue alone")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the rendered body; write and publish nothing")
    args = ap.parse_args()

    cfg = load_config()
    state = store.load_state()
    summary = fold_window(state, cfg,
                          progress=lambda m: print(m, file=sys.stderr))
    print(f"{summary['fetched']} new builds folded, {summary['known']} already "
          f"known, {summary['pending']} still running, "
          f"{len(summary['new_occurrences'])} new occurrences",
          file=sys.stderr)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = render_issue_body(state, cfg, now)
    ensure_render_safe(body, "issue body")

    if args.dry_run:
        print(body)
        return 0

    store.save_state(state)
    pages = write_reports(state, REPORTS_DIR)
    print(f"wrote state and {len(pages)} report pages", file=sys.stderr)

    if args.no_publish:
        return 0
    number = cfg["issue"].get("number")
    if not number:
        print("issue.number not set in config; nothing published", file=sys.stderr)
        return 0
    token = resolve_write_token(os.environ.get("GH_TOKEN"))
    if not token:
        print("Set ISSUE_TOKEN (or GH_TOKEN) to update the issue.", file=sys.stderr)
        return 1
    rewrite_issue(cfg["issue"]["repo"], number, body, token)
    print(f"updated {cfg['issue']['repo']} issue {number}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
