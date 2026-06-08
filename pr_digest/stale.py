"""Weekly stale alert: PRs sitting without activity get an @-mention.

Grouped by squad, like the daily digest, but filtered to idle PRs only.
"""
import os

from pr_digest.config import load_config
from pr_digest.digest import drop_wip, enrich_pr, partition_by_squad
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

    stale_sections: list[tuple[str, list[dict]]] = []
    for name, prs in partition_by_squad(stale, config["squads"]):
        prs.sort(key=lambda x: -x["idle_days"])
        stale_sections.append((name, prs))

    approver_slack_ids = [a["slack"] for a in config["approvers"] if a.get("slack")]

    blocks = build_stale_blocks(stale_sections, approver_slack_ids)
    post_to_slack(webhook, blocks, fallback="Stale upstream PR alert")
    print(f"Posted stale alert: {sum(len(p) for _, p in stale_sections)} PR(s)")


if __name__ == "__main__":
    main()
