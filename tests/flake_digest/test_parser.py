"""Parser tests against synthetic fixtures reproducing the artifact shapes
we found on both CI lines: xdist pass/fail, sequential pass, skip with no
call phase, fixture error crashing under setup, maxfail truncation, and
heavy -m deselection without truncation."""
import json
from pathlib import Path

import pytest

from flake_digest.model import RunMeta
from flake_digest.parser import is_truncated, parse_e2e_results

FIXTURES = Path(__file__).parent / "fixtures"

RUN = RunMeta(
    origin="upstream",
    repo="kserve/kserve",
    job="predictor-kustomize",
    sha="c14d8b686aaf7a1a2e3ee740c1b1a2b3c4d5e6f7",
    build_id="9912345678:1",
    url="https://github.com/kserve/kserve/actions/runs/9912345678",
    timestamp="2026-07-01T12:00:00Z",
)


def _parse(fixture_name, run=RUN):
    return parse_e2e_results((FIXTURES / fixture_name).read_bytes(), run)


def _by_nodeid(results):
    return {r.nodeid: r for r in results}


# --- xdist run with mixed outcomes ---

def test_xdist_all_entries_emitted():
    assert len(_parse("xdist_mixed.json")) == 5


def test_xdist_passing_test_classified_pass_despite_longrepr_banner():
    # every phase carries a [gwN] banner; must not read as failure
    r = _by_nodeid(_parse("xdist_mixed.json"))["test/e2e/predictor/test_sklearn.py::test_sklearn"]
    assert r.is_pass and not r.is_non_pass


def test_xdist_failed_test_is_non_pass_with_crash_message():
    r = _by_nodeid(_parse("xdist_mixed.json"))[
        "test/e2e/predictor/test_torchserve.py::test_torchserve_v2"
    ]
    assert r.is_non_pass
    assert "did not become Ready" in r.failure_message


def test_xdist_duration_comes_from_call_phase():
    r = _by_nodeid(_parse("xdist_mixed.json"))["test/e2e/predictor/test_sklearn.py::test_sklearn"]
    assert r.duration == 41.2


def test_xfailed_and_xpassed_are_neutral():
    results = _by_nodeid(_parse("xdist_mixed.json"))
    xfailed = results["test/e2e/predictor/test_paddle.py::test_paddle_grpc"]
    xpassed = results["test/e2e/predictor/test_xgboost.py::test_xgboost_headers"]
    for r in (xfailed, xpassed):
        assert r.is_neutral and not r.is_pass and not r.is_non_pass


def test_complete_run_is_not_truncated():
    assert all(not r.truncated for r in _parse("xdist_mixed.json"))


# --- sequential (-n 0) run: no longrepr on passing phases ---

def test_sequential_run_parses_with_same_rules():
    results = _parse("sequential_pass.json")
    assert len(results) == 2
    assert all(r.is_pass for r in results)
    assert results[0].duration == 421.5


# --- skips: no call key at all ---

def test_skipped_tests_are_emitted_not_dropped():
    results = _parse("skip_no_call.json")
    skipped = [r for r in results if r.outcome == "skipped"]
    assert len(skipped) == 2


def test_skipped_test_is_neutral_with_setup_duration():
    r = _by_nodeid(_parse("skip_no_call.json"))["test/e2e/predictor/test_grpc.py::test_sklearn_grpc"]
    assert r.is_neutral
    assert r.duration == 0.0004
    assert r.failure_message is None


# --- fixture errors: crash lives under setup, no call key ---

def test_fixture_error_is_emitted_as_non_pass():
    r = _by_nodeid(_parse("fixture_error.json"))[
        "test/e2e/graph/test_inference_graph.py::test_ig_switch"
    ]
    assert r.outcome == "error"
    assert r.is_non_pass


def test_fixture_error_message_comes_from_setup_crash():
    r = _by_nodeid(_parse("fixture_error.json"))[
        "test/e2e/graph/test_inference_graph.py::test_ig_switch"
    ]
    assert "namespace kserve-ci-e2e-test not ready" in r.failure_message
    assert r.duration == 120.5


# --- truncation (--maxfail) vs plain deselection ---

def test_maxfail_run_marks_every_result_truncated():
    results = _parse("truncated_maxfail.json")
    assert len(results) == 6
    assert all(r.truncated for r in results)


def test_heavy_deselection_alone_is_not_truncation():
    # collected 30, deselected 28, total 2: everything selected did run
    assert all(not r.truncated for r in _parse("deselected_clean.json"))


def test_is_truncated_handles_missing_deselected_key():
    assert is_truncated({"collected": 10, "total": 8})
    assert not is_truncated({"collected": 10, "total": 10})


def test_is_truncated_empty_summary_is_false():
    assert not is_truncated({})


# --- run identity comes from RunMeta, not file contents ---

def test_results_carry_the_fetcher_supplied_run_meta():
    other = RunMeta(
        origin="midstream",
        repo="opendatahub-io/kserve",
        job="pull-ci-opendatahub-io-kserve-master-e2e-predictor",
        sha="caebcfbeb0123456789abcdef0123456789abcde",
        build_id="1808891234567890944",
        url="https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/...",
        timestamp="2026-07-02T03:14:15Z",
    )
    results = _parse("xdist_mixed.json", run=other)
    assert all(r.run == other for r in results)
    # the file's own `created` float must not leak into timing
    assert results[0].run.timestamp == "2026-07-02T03:14:15Z"


# --- malformed input ---

def test_malformed_json_raises_for_caller_to_classify():
    with pytest.raises(json.JSONDecodeError):
        parse_e2e_results(b"<html>502 Bad Gateway</html>", RUN)


def test_empty_tests_list_yields_no_results():
    raw = json.dumps({"summary": {"collected": 0, "total": 0}, "tests": []})
    assert parse_e2e_results(raw, RUN) == []
