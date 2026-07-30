"""Stage-1 grouping: parametrization collapse, the job-level wave rule
with near-miss decline logging, truncation, and the page-churn invariant."""
import copy

from flake_digest import store
from flake_digest.gcs_source import min_build_id_for
from flake_digest.grouping import WAVE_WINDOW_SECONDS, compute_incidents
from flake_digest.markdown_formatter import (
    _display_nodeid,
    ensure_render_safe,
    render_issue_body,
)
from flake_digest.model import JOB_LEVEL_NODEID
from flake_digest.reports import build_pages

REPO = "opendatahub-io/kserve"
SHA = "a" * 40
BASE = "1" * 40
CFG = {"issue": {"repo": "KillianGolds/team-tooling", "number": 2}}
T0_MS = 1_783_900_000_000  # arbitrary fixed moment; ids derive from it


def _bid(offset_s: float) -> str:
    return str(min_build_id_for(T0_MS + int(offset_s * 1000)))


def _url(pr, job, bid):
    return (f"https://prow.ci.openshift.org/view/gs/test-platform-results/"
            f"pr-logs/pull/opendatahub-io_kserve/{pr}/"
            f"pull-ci-opendatahub-io-kserve-master-{job}/{bid}")


def _occ(pr, job, fail_bid, pass_bid, classification="confirmed",
         tag="same_base", reason=None):
    return {
        "sha": SHA, "classification": classification, "tag": tag,
        "fail": {"build_id": fail_bid, "url": _url(pr, job, fail_bid),
                 "timestamp": "2026-07-24T00:58:13+00:00", "outcome": "fail",
                 "branch": "master", "job_name": f"pull-ci-x-master-{job}",
                 "base_sha": BASE, "no_results_reason": reason,
                 "failure_message": "AssertionError: boom"},
        "pass": {"build_id": pass_bid, "url": _url(pr, job, pass_bid),
                 "timestamp": "2026-07-23T21:10:26+00:00", "outcome": "pass",
                 "branch": "master", "job_name": f"pull-ci-x-master-{job}",
                 "base_sha": BASE},
    }


def _rec(nodeid, job, occs):
    confirmed = sum(o["classification"] == "confirmed" for o in occs)
    return {"origin": "midstream", "repo": REPO, "job": job, "nodeid": nodeid,
            "confirmed_count": confirmed,
            "suspected_count": len(occs) - confirmed,
            "runs": 0, "shas_flaked": [o["sha"] for o in occs],
            "first_seen": "2026-07-23T21:10:26+00:00",
            "last_seen": "2026-07-24T00:58:13+00:00",
            "last_failure_url": occs[0]["fail"]["url"],
            "occurrences": occs}


def _state(*recs):
    state = store.empty_state()
    for r in recs:
        state["flakes"][f"{r['origin']}|{r['repo']}|{r['job']}|{r['nodeid']}"] = r
    state["job_runs"][f"midstream|{REPO}|e2e-llm-inference-service"] = 42
    return state


def _param_siblings(n, fail_bid, pass_bid, job="e2e-llm-inference-service"):
    return [_rec(f"llmisvc/test_llm.py::test_svc[variant-{i}]", job,
                 [_occ(1730, job, fail_bid, pass_bid)]) for i in range(n)]


# --- rule 1: parametrization collapse ---

def test_param_siblings_on_one_build_pair_are_one_incident():
    state = _state(*_param_siblings(3, _bid(0), _bid(3600)))
    incidents, singletons = compute_incidents(state)
    assert len(incidents) == 1
    assert incidents[0]["kind"] == "params"
    assert incidents[0]["confirmed"] == 3 and incidents[0]["suspected"] == 0
    assert len(incidents[0]["record_keys"]) == 3
    assert singletons == []


def test_different_function_sharing_the_pair_stays_separate():
    # merge-bias: two functions on one build might be one cause or two
    # co-occurring flakes; without message evidence, don't merge
    fail, ok = _bid(0), _bid(3600)
    other = _rec("llmisvc/test_llm_stop.py::test_stop", "e2e-llm-inference-service",
                 [_occ(1730, "e2e-llm-inference-service", fail, ok)])
    state = _state(*_param_siblings(3, fail, ok), other)
    incidents, singletons = compute_incidents(state)
    assert len(incidents) == 1
    assert [s["rec"]["nodeid"] for s in singletons] == \
        ["llmisvc/test_llm_stop.py::test_stop"]


def test_same_function_different_pair_does_not_group():
    a = _rec("llmisvc/test_llm.py::test_svc[x]", "e2e-llm-inference-service",
             [_occ(1730, "e2e-llm-inference-service", _bid(0), _bid(3600))])
    b = _rec("llmisvc/test_llm.py::test_svc[y]", "e2e-llm-inference-service",
             [_occ(1730, "e2e-llm-inference-service", _bid(7200), _bid(9000))])
    incidents, singletons = compute_incidents(_state(a, b))
    assert incidents == [] and len(singletons) == 2


# --- rule 2: waves ---

def _wave_recs(pr, jobs, t0=0.0, reason="setup_failure", spacing=0.03):
    return [_rec(JOB_LEVEL_NODEID, job,
                 [_occ(pr, job, _bid(t0 + i * spacing), _bid(t0 + 90000),
                       classification="suspected", tag="base_moved",
                       reason=reason)])
            for i, job in enumerate(jobs)]


def test_cron1_wave_is_one_incident_with_five_jobs():
    jobs = ["e2e-graph", "e2e-kserve-module", "e2e-llm-inference-service",
            "e2e-predictor", "e2e-raw"]
    incidents, singletons = compute_incidents(_state(*_wave_recs(1684, jobs)))
    assert len(incidents) == 1
    inc = incidents[0]
    assert inc["kind"] == "wave" and inc["jobs"] == sorted(jobs)
    assert inc["suspected"] == 5 and inc["confirmed"] == 0
    assert singletons == []


def test_same_window_different_pr_does_not_join_and_logs():
    logs = []
    jobs = ["e2e-graph", "e2e-predictor"]
    outsider = _wave_recs(9999, ["e2e-raw"], t0=1.0)[0]
    incidents, singletons = compute_incidents(
        _state(*_wave_recs(1684, jobs), outsider), log=logs.append)
    assert len(incidents) == 1 and len(incidents[0]["jobs"]) == 2
    assert [s["rec"]["job"] for s in singletons] == ["e2e-raw"]
    assert any("two different PRs" in m for m in logs)


def test_same_pr_and_reason_outside_window_declines_and_logs():
    logs = []
    late = _wave_recs(1684, ["e2e-raw"], t0=WAVE_WINDOW_SECONDS + 300)[0]
    incidents, singletons = compute_incidents(
        _state(*_wave_recs(1684, ["e2e-graph", "e2e-predictor"]), late),
        log=logs.append)
    assert len(incidents) == 1
    assert [s["rec"]["job"] for s in singletons] == ["e2e-raw"]
    assert any("outside" in m for m in logs)


def test_different_reason_never_waves_together():
    a = _wave_recs(1684, ["e2e-graph"], reason="setup_failure")[0]
    b = _wave_recs(1684, ["e2e-predictor"], t0=0.5, reason="timeout")[0]
    incidents, _ = compute_incidents(_state(a, b))
    assert incidents == []


def test_singleton_stays_singleton():
    state = _state(_rec("llmisvc/test_llm.py::test_svc[x]",
                        "e2e-llm-inference-service",
                        [_occ(1730, "e2e-llm-inference-service",
                              _bid(0), _bid(3600))]))
    incidents, singletons = compute_incidents(state)
    assert incidents == [] and len(singletons) == 1


# --- rendering ---

def test_confirmed_section_renders_incident_plus_singleton():
    fail, ok = _bid(0), _bid(3600)
    other = _rec("llmisvc/test_llm_stop.py::test_stop", "e2e-llm-inference-service",
                 [_occ(1730, "e2e-llm-inference-service", fail, ok)])
    body = render_issue_body(_state(*_param_siblings(3, fail, ok), other),
                             CFG, "now")
    ensure_render_safe(body, "issue body")
    assert "**test_llm.py::test_svc (3 parametrizations)**" in body
    assert "3 confirmed" in body and "3 pages under reports/" in body
    # the singleton renders exactly as before, its own line
    assert "`test_llm_stop.py::test_stop` in e2e-llm-inference-service: 1 confirmed" in body


def test_wave_section_renders_one_row_for_the_wave():
    jobs = ["e2e-graph", "e2e-kserve-module", "e2e-llm-inference-service",
            "e2e-predictor", "e2e-raw"]
    body = render_issue_body(_state(*_wave_recs(1684, jobs)), CFG, "now")
    ensure_render_safe(body, "issue body")
    assert "### Job-level incidents (waves)" in body
    assert "**5-job wave, setup_failure**" in body
    assert body.count("5-job wave") == 1


def test_no_waves_means_no_wave_section():
    state = _state(*_param_siblings(2, _bid(0), _bid(3600)))
    assert "waves" not in render_issue_body(state, CFG, "now")


def test_wave_cap_shows_six_and_counts_the_rest_correctly():
    # nine distinct waves across the same two job-level records, the way
    # real state holds them: many occurrences per record
    def occs(job, skew):
        return [_occ(2000 + i, job, _bid(i * 90000 + skew),
                     _bid(i * 90000 + 80000), classification="suspected",
                     tag="base_moved", reason="setup_failure")
                for i in range(9)]
    recs = [_rec(JOB_LEVEL_NODEID, "e2e-graph", occs("e2e-graph", 0)),
            _rec(JOB_LEVEL_NODEID, "e2e-raw", occs("e2e-raw", 0.03))]
    body = render_issue_body(_state(*recs), CFG, "now")
    ensure_render_safe(body, "issue body")
    assert body.count("-job wave, setup_failure**") == 6
    assert "3 older wave(s) in the window not listed" in body
    # the pointer names real destinations, not per-wave pages
    assert "job-level page" in body and "flakes_state.json" in body


# --- truncation ---

def test_param_tails_stay_visibly_distinct():
    a = ("test_llm_inference_service[cluster_cpu-cluster_single_node-router-"
         "managed-workload-llmd-simulator1]")
    b = ("test_llm_inference_service[cluster_cpu-cluster_single_node-router-"
         "managed-workload-llmd-simulator2]")
    da, db = _display_nodeid("x/" + a), _display_nodeid("x/" + b)
    assert da != db
    assert "…" in da and len(da) <= 70
    assert da.endswith("simulator1]") and db.endswith("simulator2]")


def test_short_nodeids_render_untouched():
    assert _display_nodeid("p/test_a.py::test_b") == "test_a.py::test_b"


# --- page-churn invariant ---

def test_denominator_only_change_produces_zero_page_diffs():
    state_a = _state(*_param_siblings(2, _bid(0), _bid(3600)))
    state_b = copy.deepcopy(state_a)
    state_b["job_runs"] = {k: v + 17 for k, v in state_b["job_runs"].items()}
    state_b["discarded"]["midstream|x|e2e-graph"] = 3
    assert build_pages(state_a) == build_pages(state_b)