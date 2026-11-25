"""Headroom stats: successes-only medians, ceiling counts, the trend
gate, and the rendered section."""
from flake_digest import store
from flake_digest.gcs_source import min_build_id_for
from flake_digest.headroom import (
    STEP_CEILING_S,
    _percentile,
    compute_headroom,
    thin_headroom,
)
from flake_digest.markdown_formatter import ensure_render_safe, render_issue_body

REPO = "opendatahub-io/kserve"
CFG = {"issue": {"repo": "KillianGolds/team-tooling", "number": 2},
       "window_days": 30}
NOW_MS = 1_789_000_000_000
DAY = 86_400_000
JK = f"midstream|{REPO}|e2e-predictor"


def _key(job, age_days, seq=0):
    bid = min_build_id_for(NOW_MS - int(age_days * DAY)) + seq
    return f"midstream:{REPO}:{job}:{bid}"


def _add(state, job, age_days, phase, result="SUCCESS", seq=0):
    state["build_timings"][_key(job, age_days, seq)] = {
        "test_phase_s": phase, "result": result}


def test_stats_come_from_recent_successes_only():
    state = store.empty_state()
    for i, phase in enumerate([600.0, 1200.0, 1800.0]):
        _add(state, "e2e-predictor", 2, phase, seq=i)
    _add(state, "e2e-predictor", 3, 7000.0, result="FAILURE")
    _add(state, "e2e-predictor", 4, 500.0, result="ABORTED")
    row = compute_headroom(state, NOW_MS)[JK]
    assert row["successes"] == 3
    assert row["median_s"] == 1200.0
    assert row["max_s"] == 1800.0
    assert row["at_ceiling"] == 0


def test_ceiling_reach_counts_any_result_in_the_recent_window():
    state = store.empty_state()
    _add(state, "e2e-predictor", 2, 7205.0, result="FAILURE")
    _add(state, "e2e-predictor", 20, 7300.0, result="FAILURE", seq=1)  # prior
    row = compute_headroom(state, NOW_MS)[JK]
    assert row["at_ceiling"] == 1
    assert row["successes"] == 0 and row["median_s"] is None


def test_prior_window_feeds_the_trend_not_the_stats():
    state = store.empty_state()
    for i in range(5):
        _add(state, "e2e-predictor", 2, 1800.0, seq=i)
        _add(state, "e2e-predictor", 20, 1500.0, seq=10 + i)
    row = compute_headroom(state, NOW_MS)[JK]
    assert row["median_s"] == 1800.0
    assert row["trend_s"] == 300.0


def test_trend_needs_five_samples_a_side():
    state = store.empty_state()
    for i in range(5):
        _add(state, "e2e-predictor", 2, 1800.0, seq=i)
    for i in range(4):
        _add(state, "e2e-predictor", 20, 1500.0, seq=10 + i)
    assert compute_headroom(state, NOW_MS)[JK]["trend_s"] is None


def test_phase_less_and_stale_entries_are_invisible():
    state = store.empty_state()
    state["build_timings"][_key("e2e-predictor", 2)] = {
        "test_phase_s": None, "result": "SUCCESS"}
    _add(state, "e2e-predictor", 40, 1800.0, seq=1)  # outside both windows
    assert compute_headroom(state, NOW_MS) == {}


def test_percentile_is_nearest_rank():
    assert _percentile([], 50) is None
    assert _percentile([1.0, 2.0, 3.0, 4.0], 50) == 2.0
    assert _percentile([1.0, 2.0, 3.0, 4.0], 90) == 4.0
    assert _percentile(sorted(range(1, 101)), 90) == 90


def test_thin_headroom_flags_high_p90_and_ceiling_reaches():
    comfortable = {"successes": 9, "median_s": 600.0, "p90_s": 900.0,
                   "max_s": 950.0, "at_ceiling": 0, "trend_s": None}
    creeping = dict(comfortable, p90_s=STEP_CEILING_S * 0.8)
    killed = dict(comfortable, at_ceiling=2)
    stats = {"a|r|ok": comfortable, "a|r|creep": creeping, "a|r|kill": killed}
    assert thin_headroom(stats) == ["a|r|creep", "a|r|kill"]


def test_body_renders_the_headroom_section_worst_first():
    state = store.empty_state()
    for i in range(6):
        _add(state, "e2e-predictor", 2, 1200.0, seq=i)
        _add(state, "e2e-kserve-module", 2, 6000.0, seq=10 + i)
    _add(state, "e2e-raw", 2, 7210.0, result="FAILURE", seq=20)
    body = render_issue_body(state, CFG, "now", now_ms=NOW_MS)
    ensure_render_safe(body, "test body")
    assert "### Runtime headroom" in body
    assert "| e2e-kserve-module | 6 | 1h40m | 1h40m | 1h40m | 0 | n/a |" in body
    assert "| e2e-raw | 0 | n/a | n/a | n/a | 1 | n/a |" in body
    lines = body.splitlines()
    module_at = next(i for i, l in enumerate(lines)
                     if l.startswith("| e2e-kserve-module | 6"))
    predictor_at = next(i for i, l in enumerate(lines)
                        if l.startswith("| e2e-predictor | 6"))
    assert module_at < predictor_at  # least headroom on top
    assert "Headroom looks thin for: e2e-kserve-module, e2e-raw." in body


def test_no_timings_means_no_headroom_section():
    body = render_issue_body(store.empty_state(), CFG, "now", now_ms=NOW_MS)
    assert "Runtime headroom" not in body
