"""Detection + state tests: same-SHA pairing, confirmed/suspected
classification, discards, evidence bundles, idempotency, run denominators,
truncation adjacency, and store round-tripping."""
import json
from pathlib import Path

from flake_digest import store
from flake_digest.flakes import record_build
# model imported as a module: a top-level name starting with "Test" would
# trip pytest's collector
from flake_digest import model
from flake_digest.model import JOB_LEVEL_NODEID, RunMeta
from flake_digest.parser import parse_e2e_results

SHA_A = "a" * 40
SHA_B = "b" * 40
BASE_1 = "1" * 40
BASE_2 = "2" * 40
NODE = "predictor/test_autogluon.py::test_autogluon_runtime_kserve_v1"
REPO = "opendatahub-io/kserve"
JOB = "e2e-predictor"  # normalized target, never the full Prow name
KEY = f"midstream|{REPO}|{JOB}|{NODE}"


def _result(nodeid=NODE, outcome="passed", sha=SHA_A, build_id="1"):
    run = RunMeta(origin="midstream", repo=REPO, job=JOB, sha=sha,
                  build_id=build_id, url=f"https://prow/{build_id}",
                  timestamp="2026-07-01T00:00:00+00:00")
    return model.TestResult(run=run, nodeid=nodeid, outcome=outcome)


def _record(state, build_id, outcome, sha=SHA_A, base_sha=BASE_1,
            sha_verified=True, discard=False,
            ts="2026-07-01T00:00:00+00:00", job_result=None, nodeid=NODE):
    return record_build(
        state, origin="midstream", repo=REPO, job=JOB,
        build_key=f"midstream:{REPO}:{JOB}:{build_id}", sha=sha,
        base_sha=base_sha, sha_verified=sha_verified,
        discard=discard, has_results=bool(outcome),
        timestamp=ts, url=f"https://prow/{build_id}", job_result=job_result,
        test_results=[_result(nodeid=nodeid, outcome=outcome, sha=sha,
                              build_id=build_id)] if outcome else [],
    )


def _flake(state, key=KEY):
    return state["flakes"][key]


# --- pairing basics ---

def test_fail_then_pass_same_sha_is_one_confirmed_occurrence():
    state = store.empty_state()
    _record(state, "100", "failed", ts="2026-07-01T00:00:00+00:00")
    out = _record(state, "101", "passed", ts="2026-07-01T02:00:00+00:00")
    assert out["new_occurrences"] == [KEY]
    rec = _flake(state)
    assert rec["confirmed_count"] == 1 and rec["suspected_count"] == 0
    assert rec["shas_flaked"] == [SHA_A]
    assert rec["last_failure_url"] == "https://prow/100"
    assert rec["first_seen"] == "2026-07-01T02:00:00+00:00"  # pair completion


def test_pass_then_fail_also_counts():
    state = store.empty_state()
    _record(state, "100", "passed")
    out = _record(state, "101", "failed")
    assert len(out["new_occurrences"]) == 1
    assert _flake(state)["last_failure_url"] == "https://prow/101"


def test_error_outcome_counts_as_the_failing_side():
    state = store.empty_state()
    _record(state, "100", "error")
    assert len(_record(state, "101", "passed")["new_occurrences"]) == 1


def test_fail_fail_or_pass_pass_is_not_a_flake():
    state = store.empty_state()
    _record(state, "100", "failed")
    assert _record(state, "101", "failed")["new_occurrences"] == []
    _record(state, "102", "passed")
    assert _record(state, "103", "passed")["new_occurrences"] == []
    rec = _flake(state)
    assert rec["confirmed_count"] + rec["suspected_count"] == 1


def test_different_shas_never_pair():
    state = store.empty_state()
    _record(state, "100", "failed", sha=SHA_A)
    assert _record(state, "101", "passed", sha=SHA_B)["new_occurrences"] == []
    assert state["flakes"] == {}


def test_neutral_outcomes_sit_on_neither_side():
    state = store.empty_state()
    _record(state, "100", "failed")
    assert _record(state, "101", "skipped")["new_occurrences"] == []
    assert _record(state, "102", "xfailed")["new_occurrences"] == []
    assert state["flakes"] == {}


def test_keys_carry_the_repo():
    state = store.empty_state()
    _record(state, "100", "failed")
    _record(state, "101", "passed")
    assert list(state["flakes"]) == [KEY]
    assert f"midstream|{REPO}|{JOB}" in state["job_runs"]
    assert all(k.startswith(f"midstream|{REPO}|") for k in state["sha_index"])


# --- classification ---

def test_base_moved_pair_is_suspected():
    state = store.empty_state()
    _record(state, "100", "failed", base_sha=BASE_1)
    _record(state, "101", "passed", base_sha=BASE_2)
    rec = _flake(state)
    assert rec["confirmed_count"] == 0 and rec["suspected_count"] == 1
    assert rec["occurrences"][0]["classification"] == "suspected"
    assert rec["occurrences"][0]["tag"] == "base_moved"


def test_unknown_base_is_suspected_not_confirmed():
    state = store.empty_state()
    _record(state, "100", "failed", base_sha=None)
    _record(state, "101", "passed", base_sha=BASE_1)
    occ = _flake(state)["occurrences"][0]
    assert occ["classification"] == "suspected"
    assert occ["tag"] == "base_unknown"


def test_unverified_head_on_either_side_is_suspected():
    state = store.empty_state()
    _record(state, "100", "failed", sha_verified=False)
    _record(state, "101", "passed", sha_verified=True)
    assert _flake(state)["occurrences"][0]["classification"] == "suspected"


def test_job_level_pair_without_results_files_is_suspected():
    state = store.empty_state()
    # infra failure: job FAILURE, no results file on the failing side
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:200", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=False,
                 timestamp="2026-07-01T00:00:00+00:00", url="https://prow/200",
                 job_result="FAILURE")
    out = record_build(state, origin="midstream", repo=REPO, job=JOB,
                       build_key=f"midstream:{REPO}:{JOB}:201", sha=SHA_A,
                       base_sha=BASE_1, sha_verified=True, has_results=True,
                       timestamp="2026-07-01T01:00:00+00:00", url="https://prow/201",
                       job_result="SUCCESS")
    key = f"midstream|{REPO}|{JOB}|{JOB_LEVEL_NODEID}"
    assert out["new_occurrences"] == [key]
    occ = state["flakes"][key]["occurrences"][0]
    assert occ["classification"] == "suspected"
    assert occ["tag"] == "same_base"


def test_job_level_pair_with_full_evidence_is_confirmed():
    state = store.empty_state()
    for bid, res in (("200", "FAILURE"), ("201", "SUCCESS")):
        record_build(state, origin="midstream", repo=REPO, job=JOB,
                     build_key=f"midstream:{REPO}:{JOB}:{bid}", sha=SHA_A,
                     base_sha=BASE_1, sha_verified=True, has_results=True,
                     timestamp="2026-07-01T00:00:00+00:00",
                     url=f"https://prow/{bid}", job_result=res)
    key = f"midstream|{REPO}|{JOB}|{JOB_LEVEL_NODEID}"
    assert state["flakes"][key]["confirmed_count"] == 1


def test_discarded_build_is_counted_never_paired():
    state = store.empty_state()
    out = _record(state, "100", "failed", sha=None, discard=True,
                  job_result="FAILURE")
    assert out["discarded"]
    assert state["discarded"] == {f"midstream|{REPO}|{JOB}": 1}
    assert state["sha_index"] == {}
    # a later pass at the same sha finds nothing to pair with
    assert _record(state, "101", "passed")["new_occurrences"] == []


def test_origin_without_a_classifier_stays_suspected():
    # the classifier seam: an origin with no predicate can never produce
    # confirmed, only clearly-tagged suspected
    state = store.empty_state()
    for bid, outcome in (("100", "failed"), ("101", "passed")):
        run = RunMeta(origin="konflux", repo=REPO, job=JOB, sha=SHA_A,
                      build_id=bid, url=f"https://x/{bid}",
                      timestamp="2026-07-01T00:00:00+00:00")
        record_build(state, origin="konflux", repo=REPO, job=JOB,
                     build_key=f"konflux:{REPO}:{JOB}:{bid}", sha=SHA_A,
                     base_sha=BASE_1, sha_verified=True, has_results=True,
                     timestamp="2026-07-01T00:00:00+00:00", url=f"https://x/{bid}",
                     test_results=[model.TestResult(run=run, nodeid=NODE,
                                                    outcome=outcome)])
    occ = state["flakes"][f"konflux|{REPO}|{JOB}|{NODE}"]["occurrences"][0]
    assert occ["classification"] == "suspected"
    assert occ["tag"] == "no_classifier_for_origin"


# --- evidence bundles ---

def test_occurrence_carries_both_sides_of_the_evidence():
    state = store.empty_state()
    _record(state, "100", "failed", ts="2026-07-01T00:00:00+00:00")
    _record(state, "101", "passed", ts="2026-07-01T02:00:00+00:00")
    occ = _flake(state)["occurrences"][0]
    assert occ["sha"] == SHA_A
    assert occ["fail"]["build_id"] == "100"
    assert occ["fail"]["url"] == "https://prow/100"
    assert occ["pass"]["build_id"] == "101"
    assert occ["pass"]["url"] == "https://prow/101"
    assert occ["fail"]["timestamp"] < occ["pass"]["timestamp"]


def test_failure_message_lands_on_the_fail_side():
    state = store.empty_state()
    run = RunMeta(origin="midstream", repo=REPO, job=JOB, sha=SHA_A,
                  build_id="100", url="https://prow/100",
                  timestamp="2026-07-01T00:00:00+00:00")
    failing = model.TestResult(run=run, nodeid=NODE, outcome="failed",
                               failure_message="AssertionError: boom")
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:100", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=True,
                 timestamp="2026-07-01T00:00:00+00:00", url="https://prow/100",
                 test_results=[failing])
    _record(state, "101", "passed")
    occ = _flake(state)["occurrences"][0]
    assert occ["fail"]["failure_message"] == "AssertionError: boom"
    assert "failure_message" not in occ["pass"]


def test_second_sha_pair_appends_a_second_occurrence():
    state = store.empty_state()
    _record(state, "100", "failed", sha=SHA_A)
    _record(state, "101", "passed", sha=SHA_A)
    _record(state, "102", "failed", sha=SHA_B, ts="2026-07-02T00:00:00+00:00")
    _record(state, "103", "passed", sha=SHA_B, ts="2026-07-02T01:00:00+00:00")
    rec = _flake(state)
    assert rec["confirmed_count"] == 2
    assert [o["sha"] for o in rec["occurrences"]] == [SHA_A, SHA_B]
    assert rec["last_seen"] == "2026-07-02T01:00:00+00:00"


# --- truncation adjacency ---

FIXTURES = Path(__file__).parent / "fixtures"


def _parsed_fixture(name, build_id, sha=SHA_A):
    run = RunMeta(origin="midstream", repo=REPO, job=JOB, sha=sha,
                  build_id=build_id, url=f"https://prow/{build_id}",
                  timestamp="2026-07-01T00:00:00+00:00")
    return parse_e2e_results((FIXTURES / name).read_bytes(), run)


def test_result_present_in_truncated_run_may_pair():
    # the truncated fixture really failed test_torchserve; that observation
    # is real and pairs with a later pass
    state = store.empty_state()
    results = _parsed_fixture("truncated_maxfail.json", "100")
    assert all(r.truncated for r in results)
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:100", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=True,
                 timestamp="2026-07-01T00:00:00+00:00", url="https://prow/100",
                 test_results=results)
    out = _record(state, "101", "passed",
                  nodeid="test/e2e/predictor/test_torchserve.py::test_torchserve")
    assert len(out["new_occurrences"]) == 1


def test_absence_from_truncated_run_creates_no_observation():
    # test_paddle never ran in the truncated fixture (absent from tests[]);
    # nothing may treat that absence as a pass, so a later failure of it
    # has nothing to pair with
    state = store.empty_state()
    results = _parsed_fixture("truncated_maxfail.json", "100")
    absent = "test/e2e/predictor/test_paddle.py::test_paddle"
    assert absent not in {r.nodeid for r in results}
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:100", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=True,
                 timestamp="2026-07-01T00:00:00+00:00", url="https://prow/100",
                 test_results=results)
    out = _record(state, "101", "failed", nodeid=absent)
    assert out["new_occurrences"] == []
    assert not any(absent in k for k in state["flakes"])


# --- job-level basics, idempotency, denominators ---

def test_aborted_build_is_not_a_data_point():
    state = store.empty_state()
    out = _record(state, "200", None, job_result="ABORTED")
    assert not out["run_counted"]
    assert state["job_runs"] == {}
    assert state["sha_index"] == {}


def test_unclassifiable_build_counts_run_but_never_pairs():
    state = store.empty_state()
    out = record_build(state, origin="midstream", repo=REPO, job=JOB,
                       build_key=f"midstream:{REPO}:{JOB}:300", sha=None,
                       timestamp=None, url="u", job_result="FAILURE")
    assert out["run_counted"]
    assert state["sha_index"] == {}


def test_reprocessing_a_build_changes_nothing():
    state = store.empty_state()
    _record(state, "100", "failed")
    _record(state, "101", "passed")
    before = json.dumps(state, sort_keys=True)
    out = _record(state, "100", "failed")
    assert out["skipped"] and out["new_occurrences"] == []
    assert json.dumps(state, sort_keys=True) == before


def test_runs_increment_per_completed_build_per_job():
    state = store.empty_state()
    _record(state, "100", "failed", job_result="FAILURE")
    _record(state, "101", "passed", job_result="SUCCESS")
    _record(state, "102", None, job_result="ABORTED")
    assert state["job_runs"] == {f"midstream|{REPO}|{JOB}": 2}


def test_evidence_sides_carry_branch_and_full_job_name():
    state = store.empty_state()
    for bid, outcome in (("100", "failed"), ("101", "passed")):
        record_build(
            state, origin="midstream", repo=REPO, job=JOB,
            build_key=f"midstream:{REPO}:{JOB}:{bid}", sha=SHA_A,
            base_sha=BASE_1, sha_verified=True, has_results=True,
            branch="master",
            job_name="pull-ci-opendatahub-io-kserve-master-e2e-predictor",
            timestamp="2026-07-01T00:00:00+00:00", url=f"https://prow/{bid}",
            test_results=[_result(outcome=outcome, build_id=bid)])
    occ = _flake(state)["occurrences"][0]
    for side in ("fail", "pass"):
        assert occ[side]["branch"] == "master"
        assert occ[side]["job_name"].endswith("-master-e2e-predictor")


def test_no_results_reason_reaches_the_job_level_evidence():
    state = store.empty_state()
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:200", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=False,
                 no_results_reason="timeout",
                 timestamp="2026-07-01T00:00:00+00:00", url="https://prow/200",
                 job_result="FAILURE")
    record_build(state, origin="midstream", repo=REPO, job=JOB,
                 build_key=f"midstream:{REPO}:{JOB}:201", sha=SHA_A,
                 base_sha=BASE_1, sha_verified=True, has_results=True,
                 timestamp="2026-07-01T01:00:00+00:00", url="https://prow/201",
                 job_result="SUCCESS")
    key = f"midstream|{REPO}|{JOB}|{JOB_LEVEL_NODEID}"
    occ = state["flakes"][key]["occurrences"][0]
    assert occ["fail"]["no_results_reason"] == "timeout"


# --- store round trip ---

def test_state_round_trips_through_disk(tmp_path):
    state = store.empty_state()
    _record(state, "100", "failed")
    _record(state, "101", "passed")
    path = tmp_path / "flakes_state.json"
    store.save_state(state, path)
    assert store.load_state(path) == state


def test_load_missing_file_gives_empty_state(tmp_path):
    assert store.load_state(tmp_path / "nope.json") == store.empty_state()


def test_state_file_is_self_describing(tmp_path):
    # the committed JSON is a public interface; outside readers get the
    # key grammar and class meanings from the file itself
    state = store.empty_state()
    path = tmp_path / "flakes_state.json"
    store.save_state(state, path)
    schema = store.load_state(path)["_schema"]
    assert schema["version"] == store.SCHEMA_VERSION
    assert "origin|repo|job|nodeid" in schema["keys"]["flakes"]
    assert "sha_index" in schema["keys"]
    assert "confirmed" in schema["classes"] and "suspected" in schema["classes"]
