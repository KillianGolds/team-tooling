"""Tests for SHA extraction and resolution. Wrong grouping keys fabricate
or hide flake pairs, so unrecognized formats must resolve to None (build
unclassifiable), never a guess."""
from flake_digest.gcs_source import (
    _parse_directory_entry,
    _resolve_head,
    base_sha_from_started,
    build_id_unix_ms,
    classify_no_results,
    head_sha_from_started,
    min_build_id_for,
    normalize_job,
)

BASE = "f0f22545cfd2410a2e3c70851f299e72dc674712"
HEAD = "7d2132c0212658ed5a7c238277f72f1db7485c64"
OTHER = "9c3064a109dceca0dc382247c0c9139664668729"


def _started(spec):
    # real shape observed on PR 1505: pull/repo-commit exist but must be
    # ignored (pull is the PR number, repo-commit is the merged commit)
    return {
        "timestamp": 1783081961,
        "pull": "1505",
        "repos": {"opendatahub-io/kserve": spec},
        "repo-commit": "4cb4961cb1882539931f239dc0e6e99bbcaafa2c",
        "repo-version": "4cb4961cb1882539931f239dc0e6e99bbcaafa2c",
    }


def test_single_pr_entry():
    assert head_sha_from_started(_started(f"master:{BASE},1505:{HEAD}"), 1505) == HEAD


def test_multiple_pr_entries_batch_run():
    spec = f"master:{BASE},1505:{HEAD},1506:{OTHER}"
    assert head_sha_from_started(_started(spec), 1505) == HEAD
    assert head_sha_from_started(_started(spec), 1506) == OTHER


def test_non_master_branch():
    spec = f"release-v0.17:{BASE},1648:{HEAD}"
    assert head_sha_from_started(_started(spec), 1648) == HEAD


def test_pr_not_in_spec_is_unclassifiable():
    assert head_sha_from_started(_started(f"master:{BASE},1505:{HEAD}"), 9999) is None


def test_malformed_sha_is_unclassifiable_not_guessed():
    assert head_sha_from_started(_started(f"master:{BASE},1505:abc123"), 1505) is None
    assert head_sha_from_started(_started(f"master:{BASE},1505:"), 1505) is None


def test_missing_or_odd_repos_is_unclassifiable():
    assert head_sha_from_started({}, 1505) is None
    assert head_sha_from_started({"repos": {}}, 1505) is None
    assert head_sha_from_started({"repos": {"o/k": 12345}}, 1505) is None


# --- base SHA ---

def test_base_sha_single_pr_entry():
    assert base_sha_from_started(_started(f"master:{BASE},1505:{HEAD}"), 1505) == BASE


def test_base_sha_non_master_branch():
    spec = f"release-v0.17:{BASE},1648:{HEAD}"
    assert base_sha_from_started(_started(spec), 1648) == BASE


def test_base_sha_skips_other_pr_entries_in_batch():
    # 1506's numeric ref is another PR, not the branch
    spec = f"master:{BASE},1505:{HEAD},1506:{OTHER}"
    assert base_sha_from_started(_started(spec), 1505) == BASE


def test_base_sha_unrecognized_is_none():
    assert base_sha_from_started(_started(f"1505:{HEAD}"), 1505) is None
    assert base_sha_from_started(_started(f"master:short,1505:{HEAD}"), 1505) is None


# --- head resolution: started.json vs finished.json revision ---

def test_resolve_agreeing_sources_is_verified():
    assert _resolve_head(HEAD, HEAD) == (HEAD, True, False)


def test_resolve_single_source_is_usable_but_unverified():
    assert _resolve_head(HEAD, None) == (HEAD, False, False)
    assert _resolve_head(None, HEAD) == (HEAD, False, False)


def test_resolve_disagreeing_sources_is_a_conflict_not_a_choice():
    sha, verified, conflict = _resolve_head(HEAD, OTHER)
    assert sha is None and not verified and conflict


def test_resolve_nothing_is_nothing():
    assert _resolve_head(None, None) == (None, False, False)


# --- job normalization: keys must survive branch renames ---

REPO = "opendatahub-io/kserve"


def test_normalize_master_job():
    job = "pull-ci-opendatahub-io-kserve-master-e2e-predictor"
    assert normalize_job(job, REPO) == ("e2e-predictor", "master")


def test_normalize_hyphenated_branch():
    # both shapes exist in the wild; the branch rename must not orphan rows
    job = "pull-ci-opendatahub-io-kserve-stable-2.x-e2e-raw"
    assert normalize_job(job, REPO) == ("e2e-raw", "stable-2.x")
    job = "pull-ci-opendatahub-io-kserve-release-v0.17-e2e-graph"
    assert normalize_job(job, REPO) == ("e2e-graph", "release-v0.17")


def test_normalize_multiword_target():
    job = "pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service"
    assert normalize_job(job, REPO) == ("e2e-llm-inference-service", "master")


def test_normalize_unrecognized_shapes_are_none_not_guesses():
    assert normalize_job("pull-ci-other-repo-master-e2e-predictor", REPO) is None
    assert normalize_job("pull-ci-opendatahub-io-kserve-master-images", REPO) is None
    assert normalize_job("periodic-something-e2e-predictor", REPO) is None


# --- no_results_reason from the build log ---

def test_no_results_timeout():
    log = "...\n{'component':'entrypoint'} Process did not finish before 2h0m0s timeout\n"
    assert classify_no_results(log) == "timeout"


def test_no_results_setup_death_never_reached_pytest():
    log = "provisioning hosted cluster...\nerror: cluster not ready\n"
    assert classify_no_results(log) == "setup_failure"


def test_no_results_pytest_reached_but_no_file_is_unknown():
    log = "provisioning...\nStarting E2E tests\ncollected 61 items\n"
    assert classify_no_results(log) == "unknown"


def test_no_results_missing_log_is_unknown():
    assert classify_no_results(None) == "unknown"


# --- snowflake build-id windowing ---

def test_build_id_time_mapping_matches_live_observation():
    # PR 1505 predictor build: started.json said 1783081961 (unix s); the
    # id decoded to within 7s of that when checked live
    ms = build_id_unix_ms(2073022082035224576)
    assert abs(ms / 1000 - 1783081961) < 60


def test_min_build_id_round_trips():
    ms = 1783081961000
    assert build_id_unix_ms(min_build_id_for(ms)) == ms
    # a real build from that moment sorts at/after the derived floor
    assert 2073022082035224576 >= min_build_id_for(1783081961000 - 60_000)


def test_parse_directory_entry():
    job = "pull-ci-opendatahub-io-kserve-master-e2e-predictor"
    content = ("gs://test-platform-results/pr-logs/pull/opendatahub-io_kserve/"
               f"1591/{job}/2064008614057611264")
    assert _parse_directory_entry(content, "opendatahub-io/kserve", job) == \
        (1591, "2064008614057611264")


def test_parse_directory_entry_rejects_odd_shapes():
    job = "pull-ci-opendatahub-io-kserve-master-e2e-predictor"
    assert _parse_directory_entry("", "opendatahub-io/kserve", job) is None
    assert _parse_directory_entry("gs://x/pr-logs/pull/o_k/notanumber/j/1",
                                  "opendatahub-io/kserve", job) is None
    other = ("gs://test-platform-results/pr-logs/pull/opendatahub-io_kserve/"
             "1591/some-other-job/2064008614057611264")
    assert _parse_directory_entry(other, "opendatahub-io/kserve", job) is None
