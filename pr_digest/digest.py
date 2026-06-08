"""Daily digest: query upstream PRs, bucket, post to Slack."""
import os
import re
from datetime import datetime, timezone

from pr_digest.config import load_config
from pr_digest.github_client import GitHubClient, filtered_size
from pr_digest.slack_formatter import build_digest_blocks, post_to_slack

# Match `WIP` as a standalone word so titles like "fix swipe" aren't dropped.
# Catches "[WIP]", "WIP:", "(wip)", " wip ", etc.
_WIP_RE = re.compile(r"\bwip\b", re.IGNORECASE)

# Prow-style /lgtm at the start of any line in a comment body.
_LGTM_RE = re.compile(r"^\s*/lgtm\b", re.IGNORECASE | re.MULTILINE)
_LGTM_CANCEL_RE = re.compile(r"^\s*/lgtm\s+cancel\b", re.IGNORECASE | re.MULTILINE)


def drop_wip(items: list[dict]) -> list[dict]:
    """Filter out PRs whose title flags them as work-in-progress."""
    return [it for it in items if not _WIP_RE.search(it["title"])]


def _has_community_lgtm(
    comments: list[dict], team_members: set[str], pr_author: str
) -> bool:
    """True if at least one team member (not the PR author) has an active
    `/lgtm` comment.

    Most team members aren't in KServe's OWNERS as reviewers, so their /lgtm
    comments don't apply Prow's lgtm label — but the intent is the same
    (technical review signed off) and approvers should be able to see it.

    Per-author latest-wins: if `alice` says /lgtm then /lgtm cancel, alice's
    state is cancelled. If she then re-posts /lgtm, she's active again.

    Handle matching is case-insensitive (GitHub handles are too).
    """
    members_lc = {m.lower() for m in team_members}
    author_lc = pr_author.lower()
    member_state: dict[str, bool] = {}
    for c in sorted(comments, key=lambda c: c.get("created_at", "")):
        login = c.get("user", {}).get("login")
        if not login:
            continue
        login_lc = login.lower()
        if login_lc not in members_lc or login_lc == author_lc:
            continue
        body = c.get("body") or ""
        if _LGTM_CANCEL_RE.search(body):
            member_state[login_lc] = False
        elif _LGTM_RE.search(body):
            member_state[login_lc] = True
    return any(member_state.values())


def _parse_pr_url(api_url: str) -> tuple[str, str, int]:
    """Parse https://api.github.com/repos/owner/repo/pulls/123 -> (owner, repo, 123)."""
    parts = api_url.rstrip("/").split("/")
    return parts[-4], parts[-3], int(parts[-1])


def enrich_pr(
    client: GitHubClient,
    item: dict,
    exclude_patterns: list[str],
    team_members: set[str],
) -> dict:
    """Take a search-result item, enrich with effective size + metadata."""
    owner, repo, number = _parse_pr_url(item["pull_request"]["url"])
    files = client.get_pr_files(owner, repo, number)
    size, file_count = filtered_size(files, exclude_patterns)
    raw_file_count = len(files)

    labels = {label["name"] for label in item.get("labels", [])}
    has_label_lgtm = "lgtm" in labels
    pr_author = item["user"]["login"]

    # Skip the extra comment fetch if the label is already present.
    if has_label_lgtm:
        community_lgtm = False
    else:
        comments = client.get_pr_comments(owner, repo, number)
        community_lgtm = _has_community_lgtm(comments, team_members, pr_author)

    now = datetime.now(timezone.utc)
    created = datetime.fromisoformat(item["created_at"].replace("Z", "+00:00"))
    updated = datetime.fromisoformat(item["updated_at"].replace("Z", "+00:00"))
    age = (now - created).days
    idle = (now - updated).days

    return {
        "title": item["title"],
        "url": item["html_url"],
        "number": number,
        "repo": f"{owner}/{repo}",
        "author": pr_author,
        "size": size,
        "file_count": file_count,
        "raw_file_count": raw_file_count,
        "lgtm": has_label_lgtm,
        "community_lgtm": community_lgtm,
        "approved": "approved" in labels,
        "age_days": age,
        "idle_days": idle,
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }


def bucket_prs(
    enriched: list[dict], max_size: int, max_files: int
) -> tuple[list[dict], list[dict], list[dict]]:
    """Split into (ready, fast, deep). Approved PRs drop out.

    `ready` = (lgtm-label OR community-lgtm) AND not approved, regardless of
    size — this is the bottleneck signal we most want surfaced. Pulling it
    out of the size-based lanes keeps it from getting buried in deep review.
    """
    actionable = [p for p in enriched if not p["approved"]]
    ready = [p for p in actionable if p["lgtm"] or p.get("community_lgtm")]
    unstamped = [p for p in actionable if not (p["lgtm"] or p.get("community_lgtm"))]
    fast, deep = [], []
    for p in unstamped:
        if p["size"] <= max_size and p["file_count"] <= max_files:
            fast.append(p)
        else:
            deep.append(p)
    ready.sort(key=lambda x: -x["age_days"])  # oldest first
    fast.sort(key=lambda x: -x["age_days"])
    deep.sort(key=lambda x: -x["age_days"])
    return ready, fast, deep


def squad_for_author(author: str, squads: dict[str, list[str]]) -> str | None:
    """Squad name that owns this author (case-insensitive), or None."""
    author_lc = author.lower()
    for name, handles in squads.items():
        if author_lc in {h.lower() for h in (handles or [])}:
            return name
    return None


def partition_by_squad(
    enriched: list[dict], squads: dict[str, list[str]]
) -> list[tuple[str, list[dict]]]:
    """Group enriched PRs by squad, preserving config order. PRs whose author
    isn't in any squad land in a trailing '(unassigned)' group."""
    groups: dict[str, list[dict]] = {name: [] for name in squads}
    unassigned: list[dict] = []
    for p in enriched:
        name = squad_for_author(p["author"], squads)
        (groups[name] if name else unassigned).append(p)
    sections = [(name, prs) for name, prs in groups.items()]
    if unassigned:
        sections.append(("(unassigned)", unassigned))
    return sections


def build_squad_sections(
    enriched: list[dict], squads: dict[str, list[str]], max_size: int, max_files: int
) -> list[tuple[str, list[dict], list[dict], list[dict]]]:
    """For each squad, bucket its PRs. Returns (squad, ready, fast, deep) tuples."""
    sections = []
    for name, prs in partition_by_squad(enriched, squads):
        ready, fast, deep = bucket_prs(prs, max_size, max_files)
        sections.append((name, ready, fast, deep))
    return sections


def main() -> None:
    config = load_config()
    token = os.environ["GH_TOKEN"]
    webhook = os.environ["SLACK_WEBHOOK"]

    client = GitHubClient(token)
    team_members = set(config["team_members"])
    items = drop_wip(client.search_open_prs(config["repos"], config["team_members"]))
    enriched = [
        enrich_pr(client, item, config["exclude_paths"], team_members)
        for item in items
    ]

    sections = build_squad_sections(
        enriched,
        config["squads"],
        config["thresholds"]["fast_lane_max_size"],
        config["thresholds"]["fast_lane_max_files"],
    )

    blocks = build_digest_blocks(sections)
    post_to_slack(webhook, blocks)
    summary = ", ".join(
        f"{name}: {len(r)}/{len(f)}/{len(d)}" for name, r, f, d in sections
    )
    print(f"Posted digest (ready/fast/deep per squad) — {summary}")


if __name__ == "__main__":
    main()
