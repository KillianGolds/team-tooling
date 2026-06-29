"""Update the always-current GitHub issue with the latest PR digest.

The issue is a single pinned location anyone can open to see the team's
open upstream PRs without waiting for the weekly Slack ping. Runs on a
schedule (every few hours) and rewrites the issue body in place, so the
URL stays permanent.

Usage:
    python -m pr_digest.issue              # update the configured issue
    python -m pr_digest.issue --dry-run    # print Markdown to stdout, no update
"""
import argparse
import os
import sys

from pr_digest.config import load_config
from pr_digest.digest import build_digest_sections, drop_wip, enrich_pr
from common.github_client import GitHubClient
from pr_digest.markdown_formatter import build_digest_markdown


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print the rendered Markdown to stdout instead of updating the issue.",
    )
    args = parser.parse_args()

    config = load_config()
    issue_cfg = config.get("issue")
    if not args.dry_run and not issue_cfg:
        print(
            "config.yml needs an `issue:` section with `repo:` and `number:` "
            "to update the live issue. Run with --dry-run to preview without updating.",
            file=sys.stderr,
        )
        sys.exit(1)

    read_token = os.environ.get("GH_TOKEN")
    if not read_token:
        print("Set GH_TOKEN to read upstream PRs.", file=sys.stderr)
        sys.exit(1)

    read_client = GitHubClient(read_token)
    team_members = set(config["team_members"])
    items = drop_wip(read_client.search_open_prs(config["repos"], config["team_members"]))
    enriched = [
        enrich_pr(read_client, item, config["exclude_paths"], team_members)
        for item in items
    ]

    community_buckets, squad_sections = build_digest_sections(
        enriched,
        config["squads"],
        config["thresholds"]["fast_lane_max_size"],
        config["thresholds"]["fast_lane_max_files"],
        config["thresholds"]["community_idle_cap_days"],
    )

    body = build_digest_markdown(community_buckets, squad_sections)

    if args.dry_run:
        print(body)
        return

    # Issue updates use a separately-scoped token: in CI the Action's built-in
    # GITHUB_TOKEN (issues:write on this repo), locally a PAT with the same
    # scope. Falls back to GH_TOKEN if ISSUE_TOKEN isn't set.
    write_token = os.environ.get("ISSUE_TOKEN") or read_token
    write_client = GitHubClient(write_token)

    owner, repo = issue_cfg["repo"].split("/", 1)
    write_client.update_issue_body(owner, repo, issue_cfg["number"], body)

    cr, cf, cd = community_buckets
    parts = [f"community: {len(cr)}/{len(cf)}/{len(cd)}"] + [
        f"{name}: {len(r)}/{len(f)}/{len(d)}" for name, r, f, d in squad_sections
    ]
    print(f"Updated {issue_cfg['repo']}#{issue_cfg['number']}: {', '.join(parts)}")


if __name__ == "__main__":
    main()
