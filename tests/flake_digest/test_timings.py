"""Duration retention: per-build timing aggregates, partiality honesty,
and the schema bump. No rendering exists yet on purpose; this only
starts the history clock."""
import json

import pytest

from flake_digest import store
from flake_digest.flakes import record_build
from flake_digest.gcs_source import ProwBuild
# model imported as a module: a top-level name starting with "Test" would
# trip pytest's collector
from flake_digest import model
from flake_digest.model import RunMeta
from flake_digest.runner import build_timing, parse_build_results

REPO = "opendatahub-io/kserve"
SHA = "a" * 40
ENTRY = {"repo": REPO, "job_pattern": r".*",
         "job_level_only": [], "bare_untrusted_until_migrated": []}
P = "pr-logs/pull/opendatahub-io_kserve/1/job/100/artifacts/x/x/artifacts/"


def _build(files=(), paths=None, result="SUCCESS",
           started=1_784_000_000, finished=1_784_005_820):
    return ProwBuild(repo=REPO, job="pull-ci-x-master-e2e-predictor",
                     build_id="100", prefix=P, url="u",
                     target="e2e-predictor", branch="master", sha=SHA,
                     sha_verified=True, result=result,
                     timestamp="2026-07-30T00:00:00+00:00",
                     started_unix=started, finished_unix=finished,
                     has_results_file=bool(files),
                     results_files=list(files),
                     result_paths=list(paths if paths is not None
                                       else [p for p, _ in files]))


def _result(nodeid, duration, truncated=False):
    run = RunMeta(origin="midstream", repo=REPO, job="e2e-predictor",
                  sha=SHA, build_id="100", url="u", timestamp="t")
    return model.TestResult(run=run, nodeid=nodeid, outcome="passed",
                            duration=duration, truncated=truncated)


def test_results_bearing_build_gets_the_aggregate():
    b = _build(files=[(P + "e2e_results.json", b"{}")])
    t = build_timing(b, [_result("a::t1", 40.25), _result("a::t2", 2.0),
                         _result("a::t3", None)])
    assert t["tests_total_s"] == 42.25  # None durations skipped, not zeroed
    assert t["test_count"] == 3
    assert t["wall_clock_s"] == 5820
    assert t["result"] == "SUCCESS" and t["truncated"] is False
    assert t["files_parsed"] == 1 and t["files_expected"] == 1


def test_build_without_results_gets_no_entry():
    assert build_timing(_build(), []) is None
    state = store.empty_state()
    record_build(state, origin="midstream", repo=REPO, job="e2e-predictor",
                 build_key="midstream:r:j:100", sha=SHA, timestamp="t",
                 url="u", job_result="FAILURE", timing=None)
    assert state["build_timings"] == {}


def test_truncated_run_totals_are_marked_incomparable():
    b = _build(files=[(P + "e2e_results.json", b"{}")])
    t = build_timing(b, [_result("a::t1", 10.0, truncated=True),
                         _result("a::t2", 5.0, truncated=True)])
    assert t["truncated"] is True


def test_partial_fetch_shows_in_files_parsed_vs_expected():
    # listed two invocation files, one vanished between list and fetch;
    # the total under-reports and must say so
    b = _build(files=[(P + "e2e_results-raw.json", b"{}")],
               paths=[P + "e2e_results-raw.json",
                      P + "e2e_results-rawcipn.json"])
    t = build_timing(b, [_result("a::t1", 10.0)])
    assert t["files_parsed"] == 1 and t["files_expected"] == 2


def test_corrupt_invocation_file_stays_loud_not_partial():
    good = json.dumps({"summary": {"total": 1, "collected": 1},
                       "tests": [{"nodeid": "a::t", "outcome": "passed",
                                  "setup": {"duration": 0.1, "outcome": "passed"},
                                  "call": {"duration": 1.0, "outcome": "passed"},
                                  "teardown": {"duration": 0.1,
                                               "outcome": "passed"}}]}).encode()
    b = _build(files=[(P + "e2e_results-a.json", good),
                      (P + "e2e_results-b.json", b"<html>502</html>")])
    with pytest.raises(json.JSONDecodeError):
        parse_build_results(ENTRY, b)


def test_timing_lands_in_state_and_refold_changes_nothing():
    state = store.empty_state()
    timing = {"tests_total_s": 42.0, "test_count": 3, "wall_clock_s": 5820,
              "result": "SUCCESS", "truncated": False,
              "files_parsed": 1, "files_expected": 1}
    kwargs = dict(origin="midstream", repo=REPO, job="e2e-predictor",
                  build_key="midstream:r:j:100", sha=SHA, timestamp="t",
                  url="u", job_result="SUCCESS", timing=timing)
    record_build(state, **kwargs)
    assert state["build_timings"]["midstream:r:j:100"] == timing
    before = json.dumps(state, sort_keys=True)
    out = record_build(state, **kwargs)
    assert out["skipped"]
    assert json.dumps(state, sort_keys=True) == before


def test_schema_v2_documents_build_timings():
    schema = store.empty_state()["_schema"]
    assert schema["version"] == 2
    for field in ("tests_total_s", "wall_clock_s", "files_parsed", "truncated"):
        assert field in schema["keys"]["build_timings"]