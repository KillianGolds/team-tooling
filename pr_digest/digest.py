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


def _first_team_commenter(
    comments: list[dict], team_members: set[str], pr_author: str
) -> str | None:
    """First team member who commented on the PR (excluding the PR author).

    Returns the commenter's canonical login (whatever case the API returned),
    or None. Used to identify a team participant when no formal assignee
    exists, so the digest can still show '👀 reviewing: handle' on community
    PRs that the team is engaged in via comments rather than assignment.
    """
    members_lc = {m.lower() for m in team_members}
    author_lc = pr_author.lower()
    for c in sorted(comments, key=lambda c: c.get("created_at", "")):
        login = c.get("user", {}).get("login")
        if not login:
            continue
        login_lc = login.lower()
        if login_lc not in members_lc or login_lc == author_lc:
            continue
        return login
    return None


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
    author_is_team = pr_author.lower() in {m.lower() for m in team_members}

    # Fetch comments unless author is on team AND label is set: in that case
    # the PR is going to a squad section with the lgtm label already shown,
    # so neither community_lgtm nor team_participant changes anything.
    team_participant: str | None = None
    if has_label_lgtm and author_is_team:
        community_lgtm = False
    else:
        comments = client.get_pr_comments(owner, repo, number)
        community_lgtm = _has_community_lgtm(comments, team_members, pr_author)
        team_participant = _first_team_commenter(comments, team_members, pr_author)

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
        "assignees": [a["login"] for a in (item.get("assignees") or [])],
        "size": size,
        "file_count": file_count,
        "raw_file_count": raw_file_count,
        "lgtm": has_label_lgtm,
        "community_lgtm": community_lgtm,
        "team_participant": team_participant,
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
    """Group enriched PRs by squad based on author, preserving config order.
    PRs whose author isn't in any squad land in a trailing '(unassigned)' group.

    Low-level primitive. For digest output, use partition_for_digest instead,
    which also pulls cross-team PRs (team-member assignee, external author)
    into a separate Community list.
    """
    groups: dict[str, list[dict]] = {name: [] for name in squads}
    unassigned: list[dict] = []
    for p in enriched:
        name = squad_for_author(p["author"], squads)
        (groups[name] if name else unassigned).append(p)
    sections = [(name, prs) for name, prs in groups.items()]
    if unassigned:
        sections.append(("(unassigned)", unassigned))
    return sections


def partition_for_digest(
    enriched: list[dict], squads: dict[str, list[str]]
) -> tuple[list[dict], list[tuple[str, list[dict]]]]:
    """Split enriched PRs into a community list + squad sections.

    - Team-authored (author is on a squad): goes to that squad's list.
    - External author: goes to the Community list. We know a team member is
      engaged because the search uses `involves:` (author / assignee /
      mentioned / commenter). If a team member is also a formal assignee,
      set `pr["community_assignee"]` to their handle so the formatter can
      show "📌 taken by". When no team member is explicitly assigned, we
      just let the section header carry the framing.
    - Anything else: should not happen since the search is scoped to team
      handles, but we keep an "(unassigned)" safety net.

    Author takes precedence over assignee: a PR Killian authored stays in
    llm-d even if a kserve teammate is also assigned. When multiple team
    members are assigned, the first one in `pr["assignees"]` order wins
    (GitHub's order, not config order).

    Returns (community_prs, squad_sections) where squad_sections matches
    partition_by_squad's shape.
    """
    community: list[dict] = []
    groups: dict[str, list[dict]] = {name: [] for name in squads}
    unassigned: list[dict] = []
    for p in enriched:
        author_squad = squad_for_author(p["author"], squads)
        if author_squad:
            groups[author_squad].append(p)
            continue
        # External author. Set the marker handle from the formal assignee
        # first; if none, fall back to the first team member who commented.
        # Either way the marker shows up as "👀 reviewing: handle".
        team_assignee = next(
            (a for a in p.get("assignees", []) if squad_for_author(a, squads)),
            None,
        )
        if team_assignee:
            p["community_assignee"] = team_assignee
        elif p.get("team_participant") and squad_for_author(p["team_participant"], squads):
            p["community_assignee"] = p["team_participant"]
        community.append(p)
    sections = [(name, prs) for name, prs in groups.items()]
    if unassigned:
        sections.append(("(unassigned)", unassigned))
    return community, sections


def _has_formal_team_assignee(p: dict) -> bool:
    """True if the marker handle came from the formal `assignees` field
    (someone clicked 'Assign yourself') rather than from comment-based
    fallback. Formal assignment is a stronger shepherding signal."""
    handle = p.get("community_assignee")
    return bool(handle) and handle in p.get("assignees", [])


def filter_community_by_idle(
    community_prs: list[dict], idle_cap_days: int
) -> list[dict]:
    """Drop community PRs older than the cap (by age, not idleness).

    Exception: PRs with a *formal* team assignee (`community_assignee` came
    from `pr['assignees']`, not from a comment) bypass the cap. Explicit
    self-assignment is a stronger signal of active shepherding than a
    comment from years ago.

    Rationale: `involves:` search catches every PR where a team handle ever
    appeared as author / assignee / commenter / mention. Without a cap, that
    pulls in PRs from years ago where someone left a single comment. We use
    `age_days` (not `idle_days`) because ancient PRs often still get bot
    updates that mask their true staleness — age is the cleaner signal of
    "this is not active shepherding material."

    The parameter name kept the `_idle_` shape for back-compat with config;
    semantics shifted to age. Worth renaming in config.yml when convenient.
    """
    return [
        p for p in community_prs
        if _has_formal_team_assignee(p) or p["age_days"] <= idle_cap_days
    ]


def build_digest_sections(
    enriched: list[dict],
    squads: dict[str, list[str]],
    max_size: int,
    max_files: int,
    community_idle_cap_days: int = 90,
) -> tuple[
    tuple[list[dict], list[dict], list[dict]],
    list[tuple[str, list[dict], list[dict], list[dict]]],
]:
    """Returns (community_buckets, squad_sections).

    community_buckets = (ready, fast, deep) for the cross-team Community
    section that renders at the top.
    squad_sections is a list of (squad_name, ready, fast, deep) tuples.

    `community_idle_cap_days` filters out community PRs idle longer than this,
    unless they have an explicit team assignee.
    """
    community_prs, squad_partitions = partition_for_digest(enriched, squads)
    community_prs = filter_community_by_idle(community_prs, community_idle_cap_days)
    community_buckets = bucket_prs(community_prs, max_size, max_files)
    squad_sections = []
    for name, prs in squad_partitions:
        ready, fast, deep = bucket_prs(prs, max_size, max_files)
        squad_sections.append((name, ready, fast, deep))
    return community_buckets, squad_sections


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

    community_buckets, squad_sections = build_digest_sections(
        enriched,
        config["squads"],
        config["thresholds"]["fast_lane_max_size"],
        config["thresholds"]["fast_lane_max_files"],
        config["thresholds"]["community_idle_cap_days"],
    )

    blocks = build_digest_blocks(community_buckets, squad_sections)
    post_to_slack(webhook, blocks)
    cr, cf, cd = community_buckets
    parts = [f"community: {len(cr)}/{len(cf)}/{len(cd)}"] + [
        f"{name}: {len(r)}/{len(f)}/{len(d)}" for name, r, f, d in squad_sections
    ]
    print(f"Posted digest (ready/fast/deep): {', '.join(parts)}")


if __name__ == "__main__":
    main()
