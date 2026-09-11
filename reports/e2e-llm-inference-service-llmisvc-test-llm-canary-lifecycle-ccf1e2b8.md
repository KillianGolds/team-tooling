`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_rollback`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 3 · **Suspected:** 1
**First seen:** 2026-08-20T18:23:04+00:00 · **Last seen:** 2026-08-31T13:40:12+00:00 · **Tracking since:** 2026-07-23T05:22:02+00:00

### confirmed (same_base) at `a44277a09bee`
- **FAIL** 2026-08-20T15:01:21+00:00 · build `2090424567238496256` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090424567238496256)
  - `AssertionError: rollback: stable phase promoted: error rate 26.7% exceeds 0.0%`
- **PASS** 2026-08-20T18:23:04+00:00 · build `2090483028374589440` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090483028374589440)

### confirmed (same_base) at `af44e8071612`
- **FAIL** 2026-08-21T15:08:51+00:00 · build `2090793497480138752` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090793497480138752)
  - `TimeoutError: roll-v1 weight=None, expected 0 (from roll-v2)`
- **PASS** 2026-08-21T17:39:53+00:00 · build `2090819137134661632` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090819137134661632)

### confirmed (same_base) at `dfb3fd0aa3e5`
- **FAIL** 2026-08-25T16:47:09+00:00 · build `2092261395939725312` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092261395939725312)
  - `AssertionError: rollback: stable phase promoted: error rate 3.2% exceeds 0.0%`
- **PASS** 2026-08-25T13:09:35+00:00 · build `2092210654617276416` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092210654617276416)

### suspected (base_moved) at `419a52e4ab43`
- **FAIL** 2026-08-31T13:40:12+00:00 · build `2094389340732919808` · branch `master` · base `843270d4005f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1923/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2094389340732919808)
  - `TimeoutError: roll-v2 weight=9, expected 0 (from roll-v1)`
- **PASS** None · build `2093074056118013952` · branch `master` · base `68aeded1b0d8` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1923/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2093074056118013952)
