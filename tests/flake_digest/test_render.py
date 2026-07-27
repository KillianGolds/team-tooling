"""Rendering tests: collision-free report filenames, derived-state
regeneration, cross-ref assertions, and the issue body's shape."""
import pytest

from flake_digest import store
from flake_digest.flakes import record_build
from flake_digest.markdown_formatter import (
    ensure_render_safe,
    render_issue_body,
    render_report_page,
    report_filename,
)
from flake_digest.model import JOB_LEVEL_NODEID
from flake_digest.reports import write_reports

SHA = "a" * 40
BASE = "1" * 40
REPO = "opendatahub-io/kserve"
CFG = {"issue": {"repo": "KillianGolds/team-tooling", "number": None}}


def _rec(nodeid, job="e2e-predictor", confirmed=0, suspected=1):
    return {
        "origin": "midstream", "repo": REPO, "job": job, "nodeid": nodeid,
        "confirmed_count": confirmed, "suspected_count": suspected,
        "runs": 0, "shas_flaked": [SHA],
        "first_seen": "2026-06-12T10:00:00+00:00",
        "last_seen": "2026-06-12T21:00:00+00:00",
        "last_failure_url": "https://prow.ci.openshift.org/view/gs/x",
        "occurrences": [{
            "sha": SHA, "classification": "suspected", "tag": "base_moved",
            "fail": {"build_id": "100", "url": "https://prow.ci.openshift.org/view/gs/f",
                     "timestamp": "2026-06-12T10:00:00+00:00", "outcome": "fail",
                     "branch": "master", "job_name": "pull-ci-x-master-e2e-predictor",
                     "no_results_reason": None,
                     "failure_message": "AssertionError: boom"},
            "pass": {"build_id": "101", "url": "https://prow.ci.openshift.org/view/gs/p",
                     "timestamp": "2026-06-12T21:00:00+00:00", "outcome": "pass",
                     "branch": "master", "job_name": "pull-ci-x-master-e2e-predictor"},
        }],
    }


def _state(*recs):
    state = store.empty_state()
    for r in recs:
        state["flakes"][f"{r['origin']}|{r['repo']}|{r['job']}|{r['nodeid']}"] = r
    state["job_runs"][f"midstream|{REPO}|e2e-predictor"] = 42
    return state


# --- filenames ---

def test_near_identical_parametrized_nodeids_get_distinct_filenames():
    # the slug flattens exactly the punctuation that distinguishes these
    a = _rec("llmisvc/test_llm.py::test_svc[cpu-router-managed-workload-llmd-simulator1]")
    b = _rec("llmisvc/test_llm.py::test_svc[cpu-router-managed-workload-llmd-simulator2]")
    c = _rec("llmisvc/test_llm.py::test_svc[cpu-router.managed.workload.llmd.simulator1]")
    names = {report_filename(a), report_filename(b), report_filename(c)}
    assert len(names) == 3


def test_filenames_are_filesystem_legal():
    name = report_filename(_rec("predictor/test_x.py::test_y[a/b::c|d]"))
    assert "/" not in name and ":" not in name and "[" not in name
    assert name.endswith(".md")


def test_same_record_always_maps_to_the_same_filename():
    assert report_filename(_rec("a.py::t")) == report_filename(_rec("a.py::t"))


# --- report pages ---

def test_full_nodeid_is_the_first_line_of_the_page():
    nodeid = "llmisvc/test_llm.py::test_svc[cpu-router-managed-workload-llmd-simulator1]"
    page = render_report_page(_rec(nodeid), runs=42, discarded=1)
    assert page.splitlines()[0] == f"`{nodeid}`"


def test_page_carries_both_sides_and_the_failure():
    page = render_report_page(_rec("a.py::t"), runs=42, discarded=0)
    assert "https://prow.ci.openshift.org/view/gs/f" in page
    assert "https://prow.ci.openshift.org/view/gs/p" in page
    assert "AssertionError: boom" in page
    assert "base_moved" in page


def test_reports_dir_is_wiped_not_written_over(tmp_path):
    out = tmp_path / "reports"
    out.mkdir()
    (out / "stale-page-from-old-key-deadbeef.md").write_text("old")
    written = write_reports(_state(_rec("a.py::t")), out)
    assert len(written) == 1
    assert not (out / "stale-page-from-old-key-deadbeef.md").exists()
    assert (out / written[0]).exists()


# --- cross-ref and size assertions ---

def test_prow_urls_pass_the_cross_ref_check():
    # prow paths contain "pull/<repo-slug>/<n>", which is safe: the slug
    # sits between pull/ and the digits
    ensure_render_safe(
        "see https://prow.ci.openshift.org/view/gs/test-platform-results/"
        "pr-logs/pull/opendatahub-io_kserve/1613/pull-ci-x/2065", "t")


def test_bare_issue_reference_is_rejected():
    with pytest.raises(ValueError, match="cross-reference"):
        ensure_render_safe("fixed in #1564", "t")


def test_github_pull_url_is_rejected():
    with pytest.raises(ValueError, match="cross-reference"):
        ensure_render_safe("https://github.com/kserve/kserve/pull/1564", "t")


def test_oversize_body_fails_loudly():
    with pytest.raises(ValueError, match="exceeds"):
        ensure_render_safe("x" * 50_001, "t")


# --- issue body ---

def _body(*recs):
    return render_issue_body(_state(*recs), CFG, "2026-07-24 17:00 UTC")


def test_body_passes_its_own_assertions_and_links_evidence():
    rec = _rec("predictor/test_sklearn.py::test_sklearn_runtime_kserve")
    body = _body(rec)
    ensure_render_safe(body, "issue body")
    assert report_filename(rec) in body
    assert "blob/main/reports/" in body


def test_body_states_the_methodology_caveats():
    body = _body(_rec("a.py::t"))
    assert "not\nflake rates" in body or "not flake rates" in body.replace("\n", " ")
    assert "base_moved" in body
    assert "presubmit" in body
    assert "2026-07-24 17:00 UTC" in body


def test_suspected_and_confirmed_are_separate_columns_never_summed():
    body = _body(_rec("a.py::t", confirmed=2, suspected=3))
    assert "| 3 | 2 |" in body  # suspected then confirmed, not 5 anywhere


def test_ranking_puts_confirmed_above_noisier_suspected():
    gold = _rec("gold.py::t", confirmed=5, suspected=0)
    noisy = _rec("noisy.py::t", confirmed=0, suspected=12)
    body = _body(noisy, gold)
    assert body.index("gold.py::t") < body.index("noisy.py::t")


def test_runs_denominator_joined_from_job_runs():
    body = _body(_rec("a.py::t"))
    assert "| 42 |" in body


def test_confirmed_section_honest_when_empty():
    assert "None yet" in _body(_rec("a.py::t", confirmed=0))


def test_job_level_rows_render_for_every_job_seen():
    state = _state(_rec("a.py::t"))
    state["job_runs"][f"midstream|{REPO}|e2e-raw"] = 7
    state["discarded"][f"midstream|{REPO}|e2e-raw"] = 1
    body = render_issue_body(state, CFG, "now")
    assert "| e2e-raw | 0 | 0 | 7 | 1 |" in body


def test_job_level_record_from_live_pipeline_renders(tmp_path):
    # end to end through record_build, not a hand-built record
    state = store.empty_state()
    for bid, res in (("200", "FAILURE"), ("201", "SUCCESS")):
        record_build(state, origin="midstream", repo=REPO, job="e2e-graph",
                     build_key=f"midstream:{REPO}:e2e-graph:{bid}", sha=SHA,
                     base_sha=BASE, sha_verified=True, has_results=(bid == "201"),
                     no_results_reason="timeout" if bid == "200" else None,
                     branch="master", job_name="pull-ci-x-master-e2e-graph",
                     timestamp="2026-07-01T00:00:00+00:00",
                     url="https://prow.ci.openshift.org/view/gs/x",
                     job_result=res)
    body = render_issue_body(state, CFG, "now")
    ensure_render_safe(body, "issue body")
    rec = state["flakes"][f"midstream|{REPO}|e2e-graph|{JOB_LEVEL_NODEID}"]
    page = render_report_page(rec, runs=2, discarded=0)
    ensure_render_safe(page, "page")
    assert "timeout" in page