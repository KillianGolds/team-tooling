"""Window aging: the two-floor prune, recomputed aggregates, ledger-derived
denominators with the legacy fallback, and first_seen_ever survival."""
import copy
import json

from flake_digest import store
from flake_digest.aging import (
    IDEMPOTENCY_MARGIN_DAYS,
    prune,
    window_runs,
)
from flake_digest.flakes import record_build
from flake_digest.markdown_formatter import render_issue_body, render_report_page
from flake_digest.model import FlakeRecord
from flake_digest.runner import WINDOW_PAD_DAYS
from flake_digest.gcs_source import min_build_id_for

REPO = "opendatahub-io/kserve"
SHA = "a" * 40
CFG = {"issue": {"repo": "KillianGolds/team-tooling", "number": 2},
       "window_days": 30}
NOW_MS = 1_789_000_000_000
DAY = 86_400_000


def _key(job, age_days, seq=0):
    bid = min_build_id_for(NOW_MS - int(age_days * DAY)) + seq
    return f"midstream:{REPO}:{job}:{bid}"


def _iso(age_days):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(
        (NOW_MS - age_days * DAY) / 1000, tz=timezone.utc).isoformat()


def _occ(age_days, classification="confirmed"):
    return {
        "sha": SHA, "classification": classification, "tag": "same_base",
        "fail": {"build_id": "100", "url": "https://prow/f",
                 "timestamp": _iso(age_days + 0.1), "outcome": "fail",
                 "branch": "master", "job_name": "j", "base_sha": "1" * 40,
                 "no_results_reason": None, "failure_message": "E: boom"},
        "pass": {"build_id": "101", "url": "https://prow/p",
                 "timestamp": _iso(age_days), "outcome": "pass",
                 "branch": "master", "job_name": "j", "base_sha": "1" * 40},
    }


def _rec(occs, nodeid="a.py::t", job="e2e-predictor", ever=None):
    times = sorted(o["fail"]["timestamp"] for o in occs)
    d = FlakeRecord(origin="midstream", repo=REPO, job=job,
                    nodeid=nodeid).to_dict()
    d.update(confirmed_count=sum(o["classification"] == "confirmed" for o in occs),
             suspected_count=sum(o["classification"] == "suspected" for o in occs),
             shas_flaked=[o["sha"] for o in occs], occurrences=occs,
             first_seen=times[0], last_seen=times[-1],
             first_seen_ever=ever or times[0],
             last_failure_url="https://prow/f")
    return d


def _prune(state):
    return prune(state, NOW_MS, 30, 56)


# --- the two floors ---

def test_build_past_data_floor_but_inside_listing_window_stays_remembered():
    # THE trap: forgetting it would let the listing refold and double-count
    state = store.empty_state()
    boundary = _key("e2e-predictor", 31)
    ancient = _key("e2e-predictor", 30 + WINDOW_PAD_DAYS + IDEMPOTENCY_MARGIN_DAYS + 1)
    state["processed_builds"][boundary] = {"run": True, "discarded": False,
                                           "result": "SUCCESS"}
    state["processed_builds"][ancient] = {"run": True, "discarded": False,
                                          "result": "SUCCESS"}
    out = _prune(state)
    assert boundary in state["processed_builds"]
    assert ancient not in state["processed_builds"]
    assert out["builds"] == 1


def test_legacy_true_entries_prune_by_key_time_too():
    state = store.empty_state()
    state["processed_builds"][_key("e2e-raw", 99)] = True
    _prune(state)
    assert state["processed_builds"] == {}


def test_timings_keep_their_own_longer_retention():
    state = store.empty_state()
    state["build_timings"][_key("e2e-raw", 40)] = {"test_phase_s": 1.0}
    state["build_timings"][_key("e2e-raw", 70)] = {"test_phase_s": 2.0}
    out = _prune(state)
    assert out["timings"] == 1
    assert len(state["build_timings"]) == 1  # 40d kept under 56d retention


# --- occurrence pruning and recompute ---

def test_aged_occurrences_leave_and_counts_recompute_conserved():
    occs = [_occ(45, "confirmed"), _occ(10, "suspected"), _occ(5, "confirmed")]
    state = store.empty_state()
    rec = _rec(occs)
    state["flakes"]["k"] = rec
    out = _prune(state)
    kept = state["flakes"]["k"]
    assert out["occurrences"] == 1
    assert kept["confirmed_count"] == 1 and kept["suspected_count"] == 1
    assert len(kept["occurrences"]) == 2
    assert kept["first_seen"] == _iso(10)  # window-relative now


def test_record_emptied_by_pruning_is_dropped():
    state = store.empty_state()
    state["flakes"]["k"] = _rec([_occ(60)])
    out = _prune(state)
    assert state["flakes"] == {} and out["records"] == 1


def test_first_seen_ever_survives_while_first_seen_advances():
    state = store.empty_state()
    state["flakes"]["k"] = _rec([_occ(45), _occ(5)], ever=_iso(80))
    _prune(state)
    kept = state["flakes"]["k"]
    assert kept["first_seen"] == _iso(5)
    assert kept["first_seen_ever"] == _iso(80)


def test_prune_twice_is_prune_once():
    state = store.empty_state()
    state["flakes"]["k"] = _rec([_occ(45), _occ(5)])
    state["processed_builds"][_key("e2e-raw", 99)] = True
    state["sha_index"]["x"] = {"pass": None, "counted": False,
                               "fail": _occ(50)["fail"]}
    _prune(state)
    frozen = json.dumps(state, sort_keys=True)
    out = _prune(state)
    assert not any(out.values())
    assert json.dumps(state, sort_keys=True) == frozen


def test_stale_sha_entries_drop_and_recent_stay():
    state = store.empty_state()
    state["sha_index"]["old"] = {"pass": None, "counted": False,
                                 "fail": _occ(40)["fail"]}
    state["sha_index"]["new"] = {"pass": None, "counted": False,
                                 "fail": _occ(3)["fail"]}
    out = _prune(state)
    assert "old" not in state["sha_index"] and "new" in state["sha_index"]
    assert out["sha_entries"] == 1


# --- windowed denominators ---

def test_denominators_derive_from_the_ledger_per_job():
    state = store.empty_state()
    for i in range(3):
        state["processed_builds"][_key("e2e-graph", 5, i)] = {
            "run": True, "discarded": False, "result": "SUCCESS"}
    state["processed_builds"][_key("e2e-graph", 6)] = {
        "run": False, "discarded": False, "result": "ABORTED"}
    state["processed_builds"][_key("e2e-raw", 7)] = {
        "run": True, "discarded": True, "result": "FAILURE"}
    state["processed_builds"][_key("e2e-graph", 40)] = {
        "run": True, "discarded": False, "result": "SUCCESS"}  # outside window
    runs, discarded, derived = window_runs(state, NOW_MS, 30)
    assert derived
    assert runs == {f"midstream|{REPO}|e2e-graph": 3,
                    f"midstream|{REPO}|e2e-raw": 1}
    assert discarded == {f"midstream|{REPO}|e2e-raw": 1}


def test_legacy_entry_in_window_forces_counter_fallback():
    state = store.empty_state()
    state["processed_builds"][_key("e2e-graph", 5)] = True  # pre-v4
    state["job_runs"]["legacy"] = 42
    runs, _, derived = window_runs(state, NOW_MS, 30)
    assert not derived and runs == {"legacy": 42}


def test_legacy_entry_outside_window_does_not_force_fallback():
    state = store.empty_state()
    state["processed_builds"][_key("e2e-graph", 33)] = True
    _, _, derived = window_runs(state, NOW_MS, 30)
    assert derived


def test_record_build_writes_the_ledger_shape():
    state = store.empty_state()
    key = _key("e2e-predictor", 1)
    record_build(state, origin="midstream", repo=REPO, job="e2e-predictor",
                 build_key=key, sha=SHA, timestamp=_iso(1), url="u",
                 job_result="FAILURE")
    assert state["processed_builds"][key] == {
        "run": True, "discarded": False, "result": "FAILURE"}


# --- rendering ---

def test_body_states_the_rolling_window_and_derived_denominators():
    state = store.empty_state()
    for i in range(4):
        state["processed_builds"][_key("e2e-predictor", 2, i)] = {
            "run": True, "discarded": False, "result": "SUCCESS"}
    state["flakes"][f"midstream|{REPO}|e2e-predictor|a.py::t"] = _rec([_occ(5)])
    body = render_issue_body(state, CFG, "now", now_ms=NOW_MS)
    assert "rolling 30-day" in body
    assert "| 4 |" in body  # ledger-derived denominator
    assert "pre-ledger history" not in body


def test_body_footnotes_the_legacy_fallback():
    state = store.empty_state()
    state["processed_builds"][_key("e2e-predictor", 2)] = True
    state["job_runs"][f"midstream|{REPO}|e2e-predictor"] = 42
    state["flakes"][f"midstream|{REPO}|e2e-predictor|a.py::t"] = _rec([_occ(5)])
    body = render_issue_body(state, CFG, "now", now_ms=NOW_MS)
    assert "| 42 |" in body
    assert "pre-ledger history" in body


def test_page_shows_tracking_since_when_older_than_window():
    page = render_report_page(_rec([_occ(5)], ever=_iso(80)))
    assert "Tracking since" in page and _iso(80) in page
    page2 = render_report_page(_rec([_occ(5)]))
    assert "Tracking since" not in page2