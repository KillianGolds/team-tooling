"""Render PR lists as Slack Block Kit messages, grouped by squad."""
import requests

# Type alias for readability: (squad_name, ready, fast, deep)
SquadSection = tuple[str, list[dict], list[dict], list[dict]]

# Graduated age severity so the genuinely ancient PRs stand out instead of every
# >7d PR wearing an identical ⚠️. Tune these as the team's backlog shape changes.
WARN_AGE_DAYS = 7      # ⚠️ at/after this many days old
URGENT_AGE_DAYS = 30   # 🔴 at/after this many days old


def age_badge(age_days: int) -> str:
    if age_days >= URGENT_AGE_DAYS:
        return f"🔴 {age_days}d"
    if age_days >= WARN_AGE_DAYS:
        return f"⚠️ {age_days}d"
    return f"{age_days}d old"


def size_label(pr: dict) -> str:
    """Human size string. When every file was excluded (docs/generated/vendored),
    say so instead of showing a misleading '0 lines, 0 files'."""
    if pr["size"] == 0 and pr["file_count"] == 0:
        raw = pr.get("raw_file_count", 0)
        if raw:
            return f"{raw} file{'s' if raw != 1 else ''}, all excluded"
        return "no reviewable changes"
    return f"{pr['size']} lines, {pr['file_count']} files"


def _format_pr_line(pr: dict) -> str:
    title = pr["title"]
    if len(title) > 80:
        title = title[:77] + "..."

    badges = []
    if pr["lgtm"] and not pr["approved"]:
        badges.append("🟢 LGTM")
    elif pr.get("community_lgtm") and not pr["approved"]:
        badges.append("🟢 LGTM (comment)")
    badges.append(age_badge(pr["age_days"]))

    badge_str = " · ".join(badges)
    return (
        f"• <{pr['url']}|{title}> · "
        f"{size_label(pr)} · "
        f"by `{pr['author']}` · {badge_str}"
    )


def _section(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def _chunked_sections(lines: list[str], chunk_size: int = 15) -> list[dict]:
    """Slack blocks have a 3000-char limit per section. Chunk to be safe."""
    out = []
    for i in range(0, len(lines), chunk_size):
        out.append(_section("\n".join(lines[i:i + chunk_size])))
    return out


def _squad_blocks(name: str, ready: list[dict], fast: list[dict], deep: list[dict]) -> list[dict]:
    """One squad's section: header line, then ready/fast/deep sub-sections."""
    blocks: list[dict] = [_section(
        f"*🧩 {name}*  _({len(ready)} ready · {len(fast)} fast · {len(deep)} deep)_"
    )]
    if not (ready or fast or deep):
        blocks.append(_section("_🎉 nothing open_"))
        return blocks

    if ready:
        blocks.append(_section(
            "*🟢 Ready for approver stamp*  _(LGTM'd, awaiting /approve — any size)_"
        ))
        blocks.extend(_chunked_sections([_format_pr_line(p) for p in ready]))
    if fast:
        blocks.append(_section("*Fast lane*  _(small, awaiting LGTM)_"))
        blocks.extend(_chunked_sections([_format_pr_line(p) for p in fast]))
    if deep:
        blocks.append(_section("*Deep review*  _(larger PRs, awaiting LGTM)_"))
        blocks.extend(_chunked_sections([_format_pr_line(p) for p in deep]))
    return blocks


def build_digest_blocks(sections: list[SquadSection]) -> list[dict]:
    """Daily digest, grouped by squad. Each squad shows ready/fast/deep."""
    t_ready = sum(len(r) for _, r, _, _ in sections)
    t_fast = sum(len(f) for _, _, f, _ in sections)
    t_deep = sum(len(d) for _, _, _, d in sections)

    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "📋 Upstream PR Digest"}},
        {
            "type": "context",
            "elements": [{
                "type": "mrkdwn",
                "text": (
                    f"_{t_ready} ready for stamp · {t_fast} fast-lane · "
                    f"{t_deep} deep-review · grouped by squad, oldest first_"
                ),
            }],
        },
        {"type": "divider"},
    ]

    if t_ready + t_fast + t_deep == 0:
        blocks.append(_section("🎉 No open upstream PRs from the team. Nice."))
        return blocks

    for i, (name, ready, fast, deep) in enumerate(sections):
        if i > 0:
            blocks.append({"type": "divider"})
        blocks.extend(_squad_blocks(name, ready, fast, deep))

    return blocks


def build_stale_blocks(
    stale_sections: list[tuple[str, list[dict]]], approver_slack_ids: list[str]
) -> list[dict]:
    """Weekly stale alert, grouped by squad. Tags approvers explicitly."""
    total = sum(len(prs) for _, prs in stale_sections)
    blocks: list[dict] = [
        {"type": "header", "text": {"type": "plain_text", "text": "⏰ Stale Upstream PRs"}},
    ]

    if total == 0:
        blocks.append(_section("Nothing stale this week 🎉"))
        return blocks

    blocks.append({
        "type": "context",
        "elements": [{
            "type": "mrkdwn",
            "text": f"_{total} PR(s) without activity. Worth a look at standup._",
        }],
    })

    if approver_slack_ids:
        mentions = " ".join(f"<@{sid}>" for sid in approver_slack_ids)
        blocks.append(_section(f"cc {mentions}"))

    for name, prs in stale_sections:
        if not prs:
            continue
        blocks.append({"type": "divider"})
        blocks.append(_section(f"*🧩 {name}*  _({len(prs)} stale)_"))
        blocks.extend(_chunked_sections([_format_pr_line(p) for p in prs]))

    return blocks


def post_to_slack(webhook_url: str, blocks: list[dict], fallback: str = "Upstream PR digest") -> None:
    payload = {"text": fallback, "blocks": blocks}
    r = requests.post(webhook_url, json=payload, timeout=15)
    r.raise_for_status()
