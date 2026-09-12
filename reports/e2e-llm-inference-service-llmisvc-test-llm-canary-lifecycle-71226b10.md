`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_canary_service_backend[cluster_cpu-service]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 3 · **Suspected:** 1
**First seen:** 2026-08-25T16:47:09+00:00 · **Last seen:** 2026-09-12T00:16:56+00:00 · **Tracking since:** 2026-07-23T10:45:30+00:00

### confirmed (same_base) at `dfb3fd0aa3e5`
- **FAIL** 2026-08-25T16:47:09+00:00 · build `2092261395939725312` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092261395939725312)
  - `AssertionError: stable phase: promote: error rate 15.0% exceeds 0.0%`
- **PASS** 2026-08-25T13:09:35+00:00 · build `2092210654617276416` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092210654617276416)

### confirmed (same_base) at `30c2946f5be3`
- **FAIL** 2026-08-26T17:13:58+00:00 · build `2092634091923968000` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092634091923968000)
  - `AssertionError: stable phase: baseline: error rate 2.4% exceeds 0.0%`
- **PASS** 2026-08-26T20:48:41+00:00 · build `2092680786200236032` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092680786200236032)

### suspected (same_base) at `07d08a58b85f`
- **FAIL** 2026-09-08T18:05:28+00:00 · build `2097351599394394113` · branch `master` · base `27aea1fa6937` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1955/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2097351599394394113)
  - `TimeoutError: canary-v1 weight=7, expected 0 (from canary-v2)`
- **PASS** None · build `2097407809367838720` · branch `master` · base `27aea1fa6937` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1955/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2097407809367838720)

### confirmed (same_base) at `9447f454698d`
- **FAIL** 2026-09-11T21:39:25+00:00 · build `2098495862442299392` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098495862442299392)
  - `AssertionError: stable phase: promote: error rate 27.5% exceeds 0.0%`
- **PASS** 2026-09-12T00:16:56+00:00 · build `2098534481253109760` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098534481253109760)
