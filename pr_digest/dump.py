"""Dump open PRs to a text file — same query + bucketing as the Slack digest.

Usage:
    python -m pr_digest.dump                          # use squads from config
    python -m pr_digest.dump --all-authors            # skip the team filter
    python -m pr_digest.dump --output out.txt
    python -m pr_digest.dump --limit 20               # enrich only first 20 PRs
"""
import argparse
import os
import sys
from datetime import datetime, timezone

from pr_digest.config import load_config
from pr_digest.digest import build_digest_sections, drop_wip, enrich_pr
from common.github_client import GitHubClient
from pr_digest.slack_formatter import age_badge, size_label


def _format_pr(pr: dict) -> str:
    title = pr["title"]
    if len(title) > 72:
        title = title[:69] + "..."
    flags = []
    if pr["lgtm"] and not pr["approved"]:
        flags.append("LGTM")
    elif pr.get("community_lgtm") and not pr["approved"]:
        flags.append("LGTM (comment)")
    flags.append(age_badge(pr["age_days"]))
    if pr.get("community_assignee"):
        flags.append(f"reviewing: {pr['community_assignee']}")
    flag_str = " · ".join(flags)
    return (
        f"  #{pr['number']:<6} {title}\n"
        f"         {size_label(pr)} · by {pr['author']} · {flag_str}\n"
        f"         {pr['url']}\n"
    )


def _bucket_block(label: str, prs: list[dict]) -> list[str]:
    out = [f"  {label}: {len(prs)}", "  " + "-" * 74]
    if prs:
        out.extend(_format_pr(p) for p in prs)
    else:
        out.append("    (none)\n")
    return out


def render(
    community_buckets: tuple[list[dict], list[dict], list[dict]],
    squad_sections: list[tuple[str, list[dict], list[dict], list[dict]]],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    cr, cf, cd = community_buckets
    sr = sum(len(r) for _, r, _, _ in squad_sections)
    sf = sum(len(f) for _, _, f, _ in squad_sections)
    sd = sum(len(d) for _, _, _, d in squad_sections)
    t_ready = sr + len(cr)
    t_fast = sf + len(cf)
    t_deep = sd + len(cd)

    out: list[str] = [
        f"Upstream PR Digest — {now}",
        "=" * 78,
        (
            f"{t_ready} ready for stamp · {t_fast} fast-lane · "
            f"{t_deep} deep-review · grouped by squad, oldest first"
        ),
        "",
    ]

    # Community section first if non-empty.
    community_total = len(cr) + len(cf) + len(cd)
    if community_total:
        out.append("=" * 78)
        out.append(
            f"COMMUNITY PRs we're helping land  "
            f"({len(cr)} ready · {len(cf)} fast · {len(cd)} deep)"
        )
        out.append("  (team member assigned or reviewing, external author)")
        out.append("=" * 78)
        out.extend(_bucket_block("READY FOR APPROVER STAMP — LGTM'd, awaiting /approve", cr))
        out.append("")
        out.extend(_bucket_block("FAST LANE — Awaiting LGTM", cf))
        out.append("")
        out.extend(_bucket_block("DEEP REVIEW — Awaiting LGTM", cd))
        out.append("")

    for name, ready, fast, deep in squad_sections:
        n = len(ready) + len(fast) + len(deep)
        out.append("=" * 78)
        out.append(f"SQUAD: {name}  ({len(ready)} ready · {len(fast)} fast · {len(deep)} deep)")
        out.append("=" * 78)
        if n == 0:
            out.append("  (nothing open)\n")
            continue
        out.extend(_bucket_block("READY FOR APPROVER STAMP — LGTM'd, awaiting /approve", ready))
        out.append("")
        out.extend(_bucket_block("FAST LANE — Awaiting LGTM", fast))
        out.append("")
        out.extend(_bucket_block("DEEP REVIEW — Awaiting LGTM", deep))
        out.append("")

    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--all-authors", action="store_true",
        help="Skip team filter — query ALL open PRs in the configured repos.",
    )
    parser.add_argument(
        "--output", "-o", default="digest_output.txt",
        help="Path to write the digest (default: digest_output.txt).",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Only enrich the first N PRs returned by search (for quick smoke tests).",
    )
    args = parser.parse_args()

    token = os.environ.get("GH_TOKEN")
    if not token:
        print("Set GH_TOKEN before running.", file=sys.stderr)
        sys.exit(1)

    config = load_config()
    team_members = set(config["team_members"])
    authors = [] if args.all_authors else config["team_members"]
    client = GitHubClient(token)

    scope = "all authors" if args.all_authors else f"{len(authors)} team member(s)"
    print(f"Searching {config['repos']} — {scope}...", file=sys.stderr)
    raw = client.search_open_prs(config["repos"], authors)
    items = drop_wip(raw)
    dropped = len(raw) - len(items)
    print(
        f"Found {len(raw)} open PR(s)" + (f" (dropped {dropped} WIP)." if dropped else "."),
        file=sys.stderr,
    )

    if args.limit and len(items) > args.limit:
        items = items[: args.limit]
        print(f"Limiting enrichment to first {len(items)}.", file=sys.stderr)

    enriched = []
    for i, item in enumerate(items, 1):
        if i % 5 == 0 or i == len(items):
            print(f"  enriching {i}/{len(items)}...", file=sys.stderr)
        enriched.append(enrich_pr(client, item, config["exclude_paths"], team_members))

    community_buckets, squad_sections = build_digest_sections(
        enriched,
        config["squads"],
        config["thresholds"]["fast_lane_max_size"],
        config["thresholds"]["fast_lane_max_files"],
        config["thresholds"]["community_idle_cap_days"],
    )

    with open(args.output, "w") as f:
        f.write(render(community_buckets, squad_sections))

    cr, cf, cd = community_buckets
    parts = [f"community {len(cr)}/{len(cf)}/{len(cd)}"] + [
        f"{name} {len(r)}/{len(f)}/{len(d)}" for name, r, f, d in squad_sections
    ]
    print(f"Wrote {args.output} — ready/fast/deep: {', '.join(parts)}", file=sys.stderr)


if __name__ == "__main__":
    main()
