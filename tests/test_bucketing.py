"""Tests for bucketing + community-LGTM detection — the parts most likely to need tuning."""
from pr_digest.digest import (
    _first_team_commenter,
    _has_community_lgtm,
    bucket_prs,
    filter_community_by_idle,
    partition_by_squad,
    partition_for_digest,
    squad_for_author,
)
from pr_digest.github_client import filtered_size
from pr_digest.markdown_formatter import build_digest_markdown
from pr_digest.slack_formatter import age_badge, size_label


def _pr(
    size=100, file_count=2, lgtm=False, community_lgtm=False,
    approved=False, age=1, idle=None, title="test", author="alice",
    assignees=None, team_participant=None,
):
    return {
        "title": title, "url": "http://x", "number": 1, "repo": "x/y",
        "author": author, "assignees": assignees or [],
        "size": size, "file_count": file_count,
        "lgtm": lgtm, "community_lgtm": community_lgtm,
        "team_participant": team_participant, "approved": approved,
        "age_days": age,
        "idle_days": age if idle is None else idle,
        "created_at": "2024-01-01T00:00:00Z",
    }


def _comment(login, body, at="2024-01-01T00:00:00Z"):
    return {"user": {"login": login}, "body": body, "created_at": at}


# --- bucket_prs ---

def test_small_unstamped_pr_goes_to_fast_lane():
    ready, fast, deep = bucket_prs([_pr(size=100, file_count=2)], 500, 5)
    assert not ready and len(fast) == 1 and not deep


def test_large_unstamped_pr_goes_to_deep_lane():
    ready, fast, deep = bucket_prs([_pr(size=600)], 500, 5)
    assert not ready and not fast and len(deep) == 1


def test_many_files_forces_deep_lane_even_if_small():
    ready, fast, deep = bucket_prs([_pr(size=10, file_count=20)], 500, 5)
    assert not ready and not fast and len(deep) == 1


def test_approved_prs_are_excluded():
    ready, fast, deep = bucket_prs([_pr(approved=True, lgtm=True)], 500, 5)
    assert not ready and not fast and not deep


def test_lgtm_label_goes_to_ready_regardless_of_size():
    ready, fast, deep = bucket_prs([_pr(lgtm=True, size=2000, file_count=50)], 500, 5)
    assert len(ready) == 1 and not fast and not deep


def test_community_lgtm_goes_to_ready_regardless_of_size():
    ready, fast, deep = bucket_prs(
        [_pr(community_lgtm=True, size=2000, file_count=50)], 500, 5,
    )
    assert len(ready) == 1 and not fast and not deep


def test_small_lgtmd_pr_does_not_appear_in_fast_lane():
    # Ready pulls it out of the size-based lanes entirely.
    ready, fast, deep = bucket_prs([_pr(lgtm=True, size=100, file_count=2)], 500, 5)
    assert len(ready) == 1 and not fast and not deep


def test_oldest_first_sorting():
    prs = [_pr(age=1, title="new"), _pr(age=10, title="old"), _pr(age=5, title="mid")]
    _, fast, _ = bucket_prs(prs, 500, 5)
    assert [p["title"] for p in fast] == ["old", "mid", "new"]


def test_filtered_size_excludes_generated_files():
    files = [
        {"filename": "main.go", "additions": 50, "deletions": 10},
        {"filename": "zz_generated_types.go", "additions": 1000, "deletions": 500},
        {"filename": "go.sum", "additions": 200, "deletions": 100},
    ]
    patterns = ["**/zz_generated_*.go", "go.sum"]
    size, count = filtered_size(files, patterns)
    assert size == 60  # only main.go counted
    assert count == 1


# --- _has_community_lgtm ---

def test_community_lgtm_team_member_comment():
    comments = [_comment("alice", "/lgtm")]
    assert _has_community_lgtm(comments, {"alice", "bob"}, pr_author="carol")


def test_community_lgtm_ignores_pr_author_self_lgtm():
    comments = [_comment("carol", "/lgtm")]
    assert not _has_community_lgtm(comments, {"alice", "carol"}, pr_author="carol")


def test_community_lgtm_ignores_non_team_members():
    comments = [_comment("stranger", "/lgtm")]
    assert not _has_community_lgtm(comments, {"alice", "bob"}, pr_author="carol")


def test_community_lgtm_cancellation():
    comments = [
        _comment("alice", "/lgtm", at="2024-01-01T00:00:00Z"),
        _comment("alice", "/lgtm cancel", at="2024-01-02T00:00:00Z"),
    ]
    assert not _has_community_lgtm(comments, {"alice"}, pr_author="carol")


def test_community_lgtm_re_lgtm_after_cancel():
    comments = [
        _comment("alice", "/lgtm", at="2024-01-01T00:00:00Z"),
        _comment("alice", "/lgtm cancel", at="2024-01-02T00:00:00Z"),
        _comment("alice", "/lgtm", at="2024-01-03T00:00:00Z"),
    ]
    assert _has_community_lgtm(comments, {"alice"}, pr_author="carol")


def test_community_lgtm_case_insensitive_handles():
    # Config has "KillianGolds", commenter login comes back as "killiangolds"
    comments = [_comment("killiangolds", "/lgtm")]
    assert _has_community_lgtm(comments, {"KillianGolds"}, pr_author="carol")


def test_community_lgtm_one_active_is_enough():
    # alice cancels but bob still has an active /lgtm — counts.
    comments = [
        _comment("alice", "/lgtm", at="2024-01-01T00:00:00Z"),
        _comment("alice", "/lgtm cancel", at="2024-01-02T00:00:00Z"),
        _comment("bob", "/lgtm", at="2024-01-03T00:00:00Z"),
    ]
    assert _has_community_lgtm(comments, {"alice", "bob"}, pr_author="carol")


def test_community_lgtm_lgtm_substring_in_text_doesnt_count():
    # /lgtm has to be at start of a line, not mid-sentence.
    comments = [_comment("alice", "I'd say /lgtm but I have concerns")]
    assert not _has_community_lgtm(comments, {"alice"}, pr_author="carol")


# --- _first_team_commenter ---


def test_first_team_commenter_returns_earliest_team_member():
    comments = [
        _comment("stranger", "hi", at="2024-01-01T00:00:00Z"),
        _comment("bartoszmajsak", "lgtm-ish", at="2024-01-02T00:00:00Z"),
        _comment("pierDipi", "also looks good", at="2024-01-03T00:00:00Z"),
    ]
    result = _first_team_commenter(comments, {"bartoszmajsak", "pierDipi"}, pr_author="external")
    assert result == "bartoszmajsak"


def test_first_team_commenter_ignores_pr_author():
    comments = [_comment("carol", "thanks for the review", at="2024-01-01T00:00:00Z")]
    assert _first_team_commenter(comments, {"carol"}, pr_author="carol") is None


def test_first_team_commenter_returns_none_when_no_team_member_commented():
    comments = [_comment("stranger", "hi")]
    assert _first_team_commenter(comments, {"bartoszmajsak"}, pr_author="external") is None


def test_first_team_commenter_case_insensitive():
    comments = [_comment("BARTOSZMAJSAK", "comment", at="2024-01-01T00:00:00Z")]
    result = _first_team_commenter(comments, {"bartoszmajsak"}, pr_author="external")
    assert result == "BARTOSZMAJSAK"  # returns canonical case from API


# --- squad partitioning ---

SQUADS = {"llm-d": ["pierDipi", "KillianGolds"], "kserve": ["spolti", "Jooho"]}


def test_squad_for_author_found():
    assert squad_for_author("pierDipi", SQUADS) == "llm-d"
    assert squad_for_author("spolti", SQUADS) == "kserve"


def test_squad_for_author_case_insensitive():
    assert squad_for_author("killiangolds", SQUADS) == "llm-d"
    assert squad_for_author("JOOHO", SQUADS) == "kserve"


def test_squad_for_author_unknown_returns_none():
    assert squad_for_author("stranger", SQUADS) is None


def test_partition_preserves_squad_order_and_groups():
    prs = [
        _pr(author="spolti", title="k1"),
        _pr(author="pierDipi", title="l1"),
        _pr(author="KillianGolds", title="l2"),
    ]
    sections = partition_by_squad(prs, SQUADS)
    assert [name for name, _ in sections] == ["llm-d", "kserve"]
    llmd_titles = [p["title"] for p in sections[0][1]]
    kserve_titles = [p["title"] for p in sections[1][1]]
    assert llmd_titles == ["l1", "l2"]
    assert kserve_titles == ["k1"]


def test_partition_unassigned_author_goes_to_trailing_group():
    prs = [_pr(author="stranger", title="x")]
    sections = partition_by_squad(prs, SQUADS)
    assert sections[-1][0] == "(unassigned)"
    assert sections[-1][1][0]["title"] == "x"


def test_partition_empty_squads_still_listed():
    sections = partition_by_squad([_pr(author="pierDipi")], SQUADS)
    names = [name for name, _ in sections]
    assert "kserve" in names  # empty but still present
    assert dict(sections)["kserve"] == []


# --- display helpers ---

def test_age_badge_tiers():
    assert age_badge(3) == "3d old"          # fresh: no emoji
    assert age_badge(7).startswith("⚠️")      # warn boundary
    assert age_badge(29).startswith("⚠️")
    assert age_badge(30).startswith("🔴")     # urgent boundary
    assert age_badge(416).startswith("🔴")


def test_size_label_normal():
    assert size_label({"size": 120, "file_count": 3}) == "120 lines, 3 files"


def test_size_label_all_excluded_shows_raw_count():
    assert size_label({"size": 0, "file_count": 0, "raw_file_count": 1}) == "1 file, all excluded"
    assert size_label({"size": 0, "file_count": 0, "raw_file_count": 4}) == "4 files, all excluded"


def test_size_label_all_excluded_without_raw_count():
    assert size_label({"size": 0, "file_count": 0}) == "no reviewable changes"


# --- markdown renderer ---

def _md_pr(**overrides):
    base = _pr()
    base.update({"url": "https://github.com/kserve/kserve/pull/42", "number": 42})
    base.update(overrides)
    return base


_EMPTY_COMMUNITY: tuple[list, list, list] = ([], [], [])


def test_markdown_empty_digest_says_so():
    md = build_digest_markdown(_EMPTY_COMMUNITY, [])
    assert "No open upstream PRs" in md


def test_markdown_with_squad_renders_headers_and_links():
    pr = _md_pr(lgtm=True, title="fix(x): test", age=10, author="alice")
    md = build_digest_markdown(_EMPTY_COMMUNITY, [("llm-d", [pr], [], [])])
    assert "## 🧩 llm-d" in md
    assert "🟢 Ready for approver stamp" in md
    assert "fix(x): test" in md
    assert "https://github.com/kserve/kserve/pull/42" in md
    assert "alice" in md


def test_markdown_squad_with_nothing_open_renders_nothing_open_line():
    # When some squads have PRs and others don't, the empty one still gets its
    # own header so people can see "yes we checked, nothing for your squad".
    busy = _md_pr(lgtm=True, age=5)
    md = build_digest_markdown(
        _EMPTY_COMMUNITY,
        [("llm-d", [busy], [], []), ("kserve", [], [], [])],
    )
    assert "## 🧩 kserve" in md
    assert "nothing open" in md


def test_markdown_all_excluded_label_threads_through():
    pr = _md_pr(title="docs only", size=0, file_count=0, age=2)
    pr["raw_file_count"] = 2
    md = build_digest_markdown(_EMPTY_COMMUNITY, [("llm-d", [], [pr], [])])
    assert "2 files, all excluded" in md


def test_markdown_link_uses_files_subpath_to_suppress_cross_refs():
    # /files suffix breaks GitHub's PR cross-reference detection while still
    # navigating to the PR (Files changed tab). Stops the bot leaving
    # "github-actions[bot] mentioned this PR" events on upstream kserve PRs.
    pr = _md_pr(title="hello", age=1)
    md = build_digest_markdown(_EMPTY_COMMUNITY, [("llm-d", [], [pr], [])])
    assert "[#42 hello](https://github.com/kserve/kserve/pull/42/files)" in md


# --- partition_for_digest ---


def test_partition_for_digest_team_authored_goes_to_squad():
    pr = _pr(author="pierDipi")
    community, sections = partition_for_digest([pr], SQUADS)
    assert community == []
    assert dict(sections)["llm-d"] == [pr]


def test_partition_for_digest_external_with_team_assignee_goes_to_community():
    pr = _pr(author="external-contributor", assignees=["KillianGolds"])
    community, sections = partition_for_digest([pr], SQUADS)
    assert len(community) == 1
    assert community[0]["community_assignee"] == "KillianGolds"


def test_partition_for_digest_external_without_team_assignee_still_goes_to_community():
    # `involves:` search guarantees the team is engaged (commenter/mention),
    # even when nobody is formally assigned. PR still belongs in community.
    pr = _pr(author="external-contributor", assignees=[])
    community, sections = partition_for_digest([pr], SQUADS)
    assert len(community) == 1
    assert "community_assignee" not in community[0]


def test_partition_for_digest_author_precedence_over_assignee():
    # llm-d author assigned to a kserve teammate still stays in llm-d.
    pr = _pr(author="pierDipi", assignees=["spolti"])
    community, sections = partition_for_digest([pr], SQUADS)
    assert community == []
    assert dict(sections)["llm-d"] == [pr]


def test_partition_for_digest_skips_non_team_assignees_for_marker():
    # External author with only a bot assignee: no `community_assignee` set.
    pr = _pr(author="external", assignees=["openshift-ci[bot]"])
    community, sections = partition_for_digest([pr], SQUADS)
    assert len(community) == 1
    assert "community_assignee" not in community[0]


def test_partition_for_digest_first_team_assignee_wins():
    pr = _pr(author="external", assignees=["openshift-ci[bot]", "pierDipi", "spolti"])
    community, sections = partition_for_digest([pr], SQUADS)
    assert community[0]["community_assignee"] == "pierDipi"


def test_partition_for_digest_falls_back_to_team_participant_when_no_assignee():
    # External author, no formal assignee, but KillianGolds commented.
    # The marker should still surface him as the team handle engaged.
    pr = _pr(author="external", assignees=[], team_participant="KillianGolds")
    community, sections = partition_for_digest([pr], SQUADS)
    assert len(community) == 1
    assert community[0]["community_assignee"] == "KillianGolds"


def test_partition_for_digest_assignee_beats_participant():
    # Both set: formal assignment is stronger signal, wins.
    pr = _pr(
        author="external",
        assignees=["pierDipi"],
        team_participant="spolti",
    )
    community, sections = partition_for_digest([pr], SQUADS)
    assert community[0]["community_assignee"] == "pierDipi"


def test_partition_for_digest_ignores_non_team_participant():
    # team_participant set but isn't on any squad (defensive): no marker.
    pr = _pr(author="external", team_participant="some-external-stranger")
    community, sections = partition_for_digest([pr], SQUADS)
    assert "community_assignee" not in community[0]


# --- Community section rendering ---


def test_markdown_community_section_renders_at_top_when_non_empty():
    pr = _md_pr(author="external", age=5)
    pr["community_assignee"] = "KillianGolds"
    md = build_digest_markdown(([], [pr], []), [])
    assert "🤝 Community PRs we're helping land" in md
    assert "👀 reviewing: `KillianGolds`" in md
    # Community section appears before the squad sections.
    assert md.index("Community PRs") < md.index("---", md.index("Community PRs"))


def test_markdown_community_section_omitted_when_empty():
    pr = _md_pr(lgtm=True, author="pierDipi", age=5)
    md = build_digest_markdown(_EMPTY_COMMUNITY, [("llm-d", [pr], [], [])])
    assert "Community PRs we're helping land" not in md


def test_markdown_community_assignee_marker_absent_for_team_authored_prs():
    # Team-authored squad PRs don't carry the marker even if they happen to
    # have an assignee field set somewhere.
    pr = _md_pr(author="pierDipi", age=5)
    md = build_digest_markdown(_EMPTY_COMMUNITY, [("llm-d", [], [pr], [])])
    assert "👀 reviewing:" not in md


def test_markdown_community_pr_without_assignee_renders_no_marker():
    # When `involves:` catches a PR via commenter/mention but no team member
    # is formally assigned, the line renders without the per-line marker.
    # The section header alone provides context.
    pr = _md_pr(author="external", age=5)
    md = build_digest_markdown(([], [pr], []), [])
    assert "🤝 Community PRs we're helping land" in md
    assert "👀 reviewing:" not in md


# --- filter_community_by_idle ---


def test_filter_community_drops_old_unassigned_prs():
    # No team_assignee, older than the cap: dropped.
    pr = _pr(author="external", age=120)
    assert filter_community_by_idle([pr], idle_cap_days=90) == []


def test_filter_community_keeps_recent_unassigned_prs():
    pr = _pr(author="external", age=30)
    assert filter_community_by_idle([pr], idle_cap_days=90) == [pr]


def test_filter_community_keeps_old_pr_with_formal_assignee():
    # Formal assignment (handle is in pr["assignees"]) beats the age cap.
    pr = _pr(author="external", age=400, assignees=["KillianGolds"])
    pr["community_assignee"] = "KillianGolds"
    assert filter_community_by_idle([pr], idle_cap_days=90) == [pr]


def test_filter_community_drops_old_pr_when_marker_is_from_commenter_only():
    # community_assignee came from a comment (not formal assignment): the
    # cap-bypass shouldn't apply. A comment from years ago is noise, not
    # active shepherding.
    pr = _pr(author="external", age=400, assignees=[])
    pr["community_assignee"] = "KillianGolds"  # from team_participant
    assert filter_community_by_idle([pr], idle_cap_days=90) == []


def test_filter_community_boundary_at_cap_is_kept():
    # age == cap is kept (cap is inclusive upper bound).
    pr = _pr(author="external", age=90)
    assert filter_community_by_idle([pr], idle_cap_days=90) == [pr]
