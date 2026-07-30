`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_late_join`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 2 · **Runs seen:** 376
**First seen:** 2026-07-23T10:45:30+00:00 · **Last seen:** 2026-07-30T02:21:37+00:00

### suspected (base_moved) at `8c8d651344da`
- **FAIL** 2026-07-21T23:44:50+00:00 · build `2079685052370784256` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079685052370784256)
  - `AssertionError: late-join: error rate 0.8% exceeds 0.0%`
- **PASS** 2026-07-23T10:45:30+00:00 · build `2080218582658060288` · branch `master` · base `8397970c6400` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1791/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080218582658060288)

### suspected (base_moved) at `c78d978f49c3`
- **FAIL** 2026-07-30T02:21:37+00:00 · build `2082624433679241216` · branch `master` · base `dd8f478dbbf4` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1803/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082624433679241216)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-07-28T16:21:31+00:00 · build `2082106778211848192` · branch `master` · base `b62b4c92b12e` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1803/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082106778211848192)
