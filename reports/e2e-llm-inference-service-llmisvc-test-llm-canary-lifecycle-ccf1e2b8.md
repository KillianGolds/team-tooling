`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_rollback`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 2 · **Runs seen:** 378
**First seen:** 2026-07-23T05:22:02+00:00 · **Last seen:** 2026-07-29T13:22:47+00:00

### suspected (base_moved) at `f1b7a0bc458c`
- **FAIL** 2026-07-23T02:57:06+00:00 · build `2080097507211218944` · branch `master` · base `ef08a0e7ae61` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080097507211218944)
  - `TimeoutError: roll-v2 weight=None, expected 0 (from roll-v1)`
- **PASS** 2026-07-23T05:22:02+00:00 · build `2080130341724491776` · branch `master` · base `d6f7e22abf87` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080130341724491776)

### suspected (base_moved) at `bb4b028f05cc`
- **FAIL** 2026-07-29T04:14:23+00:00 · build `2082291563362258944` · branch `master` · base `a638c0dd552d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1827/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082291563362258944)
  - `AssertionError: rollback: stable phase promoted: error rate 3.3% exceeds 0.0%`
- **PASS** 2026-07-29T13:22:47+00:00 · build `2082424973384749056` · branch `master` · base `1995336861fa` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1827/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082424973384749056)
