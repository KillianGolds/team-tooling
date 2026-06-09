"""Tests for bucketing + community-LGTM detection — the parts most likely to need tuning."""
from pr_digest.digest import (
    _has_community_lgtm,
    bucket_prs,
    partition_by_squad,
    squad_for_author,
)
from pr_digest.github_client import filtered_size
from pr_digest.markdown_formatter import build_digest_markdown
from pr_digest.slack_formatter import age_badge, size_label


def _pr(
    size=100, file_count=2, lgtm=False, community_lgtm=False,
    approved=False, age=1, title="test", author="alice",
):
    return {
        "title": title, "url": "http://x", "number": 1, "repo": "x/y",
        "author": author, "size": size, "file_count": file_count,
        "lgtm": lgtm, "community_lgtm": community_lgtm, "approved": approved,
        "age_days": age, "created_at": "2024-01-01T00:00:00Z",
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


def test_markdown_empty_digest_says_so():
    md = build_digest_markdown([])
    assert "No open upstream PRs" in md


def test_markdown_with_squad_renders_headers_and_links():
    pr = _md_pr(lgtm=True, title="fix(x): test", age=10, author="alice")
    md = build_digest_markdown([("llm-d", [pr], [], [])])
    assert "## 🧩 llm-d" in md
    assert "🟢 Ready for approver stamp" in md
    assert "fix(x): test" in md
    assert "https://github.com/kserve/kserve/pull/42" in md
    assert "alice" in md


def test_markdown_squad_with_nothing_open_renders_nothing_open_line():
    # When some squads have PRs and others don't, the empty one still gets its
    # own header so people can see "yes we checked, nothing for your squad".
    busy = _md_pr(lgtm=True, age=5)
    md = build_digest_markdown([("llm-d", [busy], [], []), ("kserve", [], [], [])])
    assert "## 🧩 kserve" in md
    assert "nothing open" in md


def test_markdown_all_excluded_label_threads_through():
    pr = _md_pr(title="docs only", size=0, file_count=0, age=2)
    pr["raw_file_count"] = 2
    md = build_digest_markdown([("llm-d", [], [pr], [])])
    assert "2 files, all excluded" in md


def test_markdown_link_uses_files_subpath_to_suppress_cross_refs():
    # /files suffix breaks GitHub's PR cross-reference detection while still
    # navigating to the PR (Files changed tab). Stops the bot leaving
    # "github-actions[bot] mentioned this PR" events on upstream kserve PRs.
    pr = _md_pr(title="hello", age=1)
    md = build_digest_markdown([("llm-d", [], [pr], [])])
    assert "[#42 hello](https://github.com/kserve/kserve/pull/42/files)" in md
