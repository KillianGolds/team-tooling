"""Weekly stale alert: PRs sitting without activity get an @-mention.

Includes a Community PRs section at the top (cross-team PRs the team has
taken on) and squad sections below. A cross-team PR a teammate volunteered
to help land that's been idle two weeks is exactly the signal we want
surfaced, so community PRs go through the same idle filter as team-authored.
"""
import os

from pr_digest.config import load_config
from pr_digest.digest import (
    drop_wip,
    enrich_pr,
    filter_community_by_idle,
    partition_for_digest,
)
from pr_digest.github_client import GitHubClient
from pr_digest.slack_formatter import build_stale_blocks, post_to_slack


def main() -> None:
    config = load_config()
    token = os.environ["GH_TOKEN"]
    webhook = os.environ["SLACK_WEBHOOK"]
    stale_days = config["thresholds"]["stale_days"]

    client = GitHubClient(token)
    team_members = set(config["team_members"])
    items = drop_wip(client.search_open_prs(config["repos"], config["team_members"]))
    enriched = [
        enrich_pr(client, item, config["exclude_paths"], team_members)
        for item in items
    ]

    # Staleness = no activity (updated_at) for stale_days, not creation age.
    # A 200-day-old PR that got a comment yesterday isn't "stale" — it's slow.
    stale = [
        p for p in enriched
        if p["idle_days"] >= stale_days and not p["approved"]
    ]

    community_stale, squad_partitions = partition_for_digest(stale, config["squads"])
    # Apply the same idle-age cap the digest uses: skip ancient community PRs
    # where nobody formally assigned themselves (would be noise).
    community_stale = filter_community_by_idle(
        community_stale, config["thresholds"]["community_idle_cap_days"]
    )
    community_stale.sort(key=lambda x: -x["idle_days"])

    stale_sections: list[tuple[str, list[dict]]] = []
    for name, prs in squad_partitions:
        prs.sort(key=lambda x: -x["idle_days"])
        stale_sections.append((name, prs))

    approver_slack_ids = [a["slack"] for a in config["approvers"] if a.get("slack")]

    blocks = build_stale_blocks(community_stale, stale_sections, approver_slack_ids)
    post_to_slack(webhook, blocks, fallback="Stale upstream PR alert")
    total = len(community_stale) + sum(len(p) for _, p in stale_sections)
    print(f"Posted stale alert: {total} PR(s)")


if __name__ == "__main__":
    main()
