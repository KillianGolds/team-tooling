`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_canary_service_backend[cluster_cpu-service]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1 · **Runs seen:** 361
**First seen:** 2026-07-23T10:45:30+00:00 · **Last seen:** 2026-07-23T10:45:30+00:00

### suspected (base_moved) at `8c8d651344da`
- **FAIL** 2026-07-21T23:44:50+00:00 · build `2079685052370784256` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079685052370784256)
  - `AssertionError: stable phase: promote: error rate 15.0% exceeds 0.0%`
- **PASS** 2026-07-23T10:45:30+00:00 · build `2080218582658060288` · branch `master` · base `8397970c6400` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1791/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080218582658060288)
