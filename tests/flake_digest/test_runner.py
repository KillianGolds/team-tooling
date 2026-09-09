"""fold_window tests with the network monkeypatched: known builds must be
skipped before any fetch, and still-running builds must stay unmarked so a
later run can pick up their result."""
from flake_digest import runner, store
from flake_digest.gcs_source import ProwBuild

REPO = "opendatahub-io/kserve"
JOB = "pull-ci-opendatahub-io-kserve-master-e2e-predictor"
CFG = {"window_days": 30,
       "midstream": [{"repo": REPO,
                      "job_pattern": r"^pull-ci-.*-e2e-.*$",
                      "job_level_only": [],
                      "bare_untrusted_until_migrated": []}]}
SHA = "a" * 40


def _wire(monkeypatch, builds, fetch_log):
    monkeypatch.setattr(runner, "list_job_directories", lambda repo, pat: [JOB])
    monkeypatch.setattr(runner, "list_recent_builds",
                        lambda repo, job, floor: [(1, bid) for bid in builds])

    def fake_fetch(repo, pr, job, bid):
        fetch_log.append(bid)
        return builds[bid]
    monkeypatch.setattr(runner, "fetch_build", fake_fetch)


def _build(bid, result="SUCCESS"):
    return ProwBuild(repo=REPO, job=JOB, build_id=bid, prefix="p/", url="u",
                     target="e2e-predictor", branch="master", sha=SHA,
                     sha_verified=True, result=result,
                     timestamp="2026-07-27T00:00:00+00:00")


def test_processed_builds_are_skipped_without_a_fetch(monkeypatch):
    fetched = []
    _wire(monkeypatch, {"100": _build("100"), "101": _build("101")}, fetched)
    state = store.empty_state()
    store.mark_processed(state, runner.build_key(REPO, "e2e-predictor", "100"))
    summary = runner.fold_window(state, CFG)
    assert fetched == ["101"]
    assert summary["known"] == 1 and summary["fetched"] == 1


def test_running_build_with_results_already_uploaded_stays_unmarked(monkeypatch):
    # results files upload per step while the build runs; folding on
    # their presence froze a running build with a null job result
    fetched = []
    running = _build("100", result=None)
    running.has_results_file = True
    running.results_files = [("p/e2e_results-x.json", b"{}")]
    _wire(monkeypatch, {"100": running}, fetched)
    state = store.empty_state()
    summary = runner.fold_window(state, CFG)
    assert summary["pending"] == 1 and summary["fetched"] == 0
    assert not store.is_processed(state, runner.build_key(REPO, "e2e-predictor", "100"))


def test_freshly_finished_build_waits_a_cycle(monkeypatch):
    # finished.json lands before the artifact tree finishes uploading; a
    # build folded in that window loses its data forever
    import time
    fetched = []
    fresh = _build("100")
    fresh.finished_unix = int(time.time()) - 60
    settled = _build("101")
    settled.finished_unix = int(time.time()) - 3600
    _wire(monkeypatch, {"100": fresh, "101": settled}, fetched)
    state = store.empty_state()
    summary = runner.fold_window(state, CFG)
    assert summary["pending"] == 1 and summary["fetched"] == 1
    assert not store.is_processed(state, runner.build_key(REPO, "e2e-predictor", "100"))
    assert store.is_processed(state, runner.build_key(REPO, "e2e-predictor", "101"))


def test_still_running_build_stays_unmarked_for_the_next_run(monkeypatch):
    fetched = []
    running = _build("100", result=None)
    _wire(monkeypatch, {"100": running}, fetched)
    state = store.empty_state()
    summary = runner.fold_window(state, CFG)
    assert summary["pending"] == 1
    assert not store.is_processed(state, runner.build_key(REPO, "e2e-predictor", "100"))
    # next run fetches it again, now finished
    _wire(monkeypatch, {"100": _build("100", result="FAILURE")}, fetched)
    summary = runner.fold_window(state, CFG)
    assert summary["fetched"] == 1
    assert store.is_processed(state, runner.build_key(REPO, "e2e-predictor", "100"))