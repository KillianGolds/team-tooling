"""Per-invocation results files: selection, per-build trust, and merge.

Real shapes recorded live 2026-07-28: e2e-raw writes e2e_results-raw.json
plus e2e_results-rawcipn.json; predictor writes a single
e2e_results-predictor_or_kserve_on_openshift.json; historical builds have
the bare e2e_results.json. The junit twin is junit_e2e-<suffix>.xml.
"""
import json

from flake_digest.gcs_source import ProwBuild, select_results_paths
from flake_digest.runner import file_disposition, parse_build_results

REPO = "opendatahub-io/kserve"
SHA = "a" * 40
ENTRY = {"repo": REPO, "job_pattern": r".*",
         "job_level_only": ["e2e-kserve-module"],
         "bare_untrusted_until_migrated": ["e2e-raw"]}

P = "pr-logs/pull/opendatahub-io_kserve/1/job/100/artifacts/x/x/artifacts/"


def _results_json(*tests):
    return json.dumps({
        "environment": {},
        "summary": {"total": len(tests), "collected": len(tests)},
        "tests": [{"nodeid": nid, "outcome": outcome,
                   "setup": {"duration": 0.001, "outcome": "passed"},
                   "call": {"duration": 1.0, "outcome": outcome},
                   "teardown": {"duration": 0.001, "outcome": "passed"}}
                  for nid, outcome in tests],
    }).encode()


def _build(target="e2e-raw", files=()):
    return ProwBuild(repo=REPO, job=f"pull-ci-x-master-{target}",
                     build_id="100", prefix=P, url="u", target=target,
                     branch="master", sha=SHA, sha_verified=True,
                     result="FAILURE", timestamp="2026-07-28T00:00:00+00:00",
                     has_results_file=bool(files),
                     results_files=list(files))


# --- selection ---

def test_bare_only_build_selects_the_bare_file():
    paths = [P + "e2e_results.json", P + "junit_e2e.xml", P + "build-log.txt"]
    assert select_results_paths(paths) == [P + "e2e_results.json"]


def test_suffixed_only_build_selects_all_suffixed():
    paths = [P + "e2e_results-raw.json", P + "e2e_results-rawcipn.json",
             P + "junit_e2e-raw.xml", P + "junit_operator.xml",
             P + "prowjob_junit.xml"]
    assert select_results_paths(paths) == [P + "e2e_results-raw.json",
                                           P + "e2e_results-rawcipn.json"]


def test_mixed_build_ignores_the_bare_file():
    # migration transition: counting bare alongside suffixed double-counts
    paths = [P + "e2e_results.json", P + "e2e_results-raw.json"]
    assert select_results_paths(paths) == [P + "e2e_results-raw.json"]


def test_non_results_files_never_match():
    assert select_results_paths([P + "junit_operator.xml",
                                 P + "prowjob_junit.xml",
                                 P + "must-gather.tar"]) == []


# --- per-build trust ---

def test_historical_clobbered_raw_build_stays_job_level_only():
    b = _build("e2e-raw", [(P + "e2e_results.json", _results_json())])
    assert file_disposition(ENTRY, b) == "bare_untrusted"
    assert parse_build_results(ENTRY, b) == []


def test_migrated_raw_build_gets_test_level_rows():
    b = _build("e2e-raw", [
        (P + "e2e_results-raw.json", _results_json(("raw/a.py::t1", "failed"))),
        (P + "e2e_results-rawcipn.json", _results_json(("raw/b.py::t2", "passed"))),
    ])
    assert file_disposition(ENTRY, b) == "parse"
    results = parse_build_results(ENTRY, b)
    assert {r.nodeid for r in results} == {"raw/a.py::t1", "raw/b.py::t2"}


def test_bare_file_on_a_normal_target_still_parses():
    b = _build("e2e-predictor", [(P + "e2e_results.json",
                                  _results_json(("p/a.py::t", "passed")))])
    assert file_disposition(ENTRY, b) == "parse"
    assert len(parse_build_results(ENTRY, b)) == 1


def test_job_level_only_target_never_parses():
    b = _build("e2e-kserve-module", [(P + "e2e_results-x.json",
                                      _results_json(("m/a.py::t", "passed")))])
    assert file_disposition(ENTRY, b) == "job_level_only"
    assert parse_build_results(ENTRY, b) == []


# --- merge ---

def test_merge_unions_nodeids_across_invocations():
    b = _build("e2e-predictor", [
        (P + "e2e_results-a.json", _results_json(("a.py::t1", "passed"),
                                                 ("a.py::t2", "failed"))),
        (P + "e2e_results-b.json", _results_json(("b.py::t3", "passed"))),
    ])
    results = parse_build_results(ENTRY, b)
    assert {r.nodeid for r in results} == {"a.py::t1", "a.py::t2", "b.py::t3"}


def test_nodeid_in_two_files_keeps_the_non_pass_and_logs(capsys):
    b = _build("e2e-predictor", [
        (P + "e2e_results-a.json", _results_json(("a.py::t", "passed"))),
        (P + "e2e_results-b.json", _results_json(("a.py::t", "failed"))),
    ])
    results = parse_build_results(ENTRY, b)
    assert len(results) == 1 and results[0].outcome == "failed"
    assert "more than one results file" in capsys.readouterr().err


def test_non_pass_is_kept_regardless_of_file_order(capsys):
    b = _build("e2e-predictor", [
        (P + "e2e_results-a.json", _results_json(("a.py::t", "failed"))),
        (P + "e2e_results-b.json", _results_json(("a.py::t", "passed"))),
    ])
    results = parse_build_results(ENTRY, b)
    assert len(results) == 1 and results[0].outcome == "failed"