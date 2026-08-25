`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_canary_service_backend[cluster_cpu-service]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 2
**First seen:** 2026-07-23T10:45:30+00:00 · **Last seen:** 2026-08-25T16:47:09+00:00

### suspected (base_moved) at `8c8d651344da`
- **FAIL** 2026-07-21T23:44:50+00:00 · build `2079685052370784256` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079685052370784256)
  - `AssertionError: stable phase: promote: error rate 15.0% exceeds 0.0%`
- **PASS** 2026-07-23T10:45:30+00:00 · build `2080218582658060288` · branch `master` · base `8397970c6400` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1791/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080218582658060288)

### confirmed (same_base) at `0b1a28ea4e47`
- **FAIL** 2026-07-28T15:56:54+00:00 · build `2082110756941205504` · branch `release-v0.17` · base `01e23b511968` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1814/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2082110756941205504)
  - `TimeoutError: canary-v2 weight=None, expected 3 (from canary-v1)`
- **PASS** 2026-07-28T17:43:08+00:00 · build `2082135667353063424` · branch `release-v0.17` · base `01e23b511968` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1814/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2082135667353063424)

### suspected (base_moved) at `bb4b028f05cc`
- **FAIL** 2026-07-29T04:14:23+00:00 · build `2082291563362258944` · branch `master` · base `a638c0dd552d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1827/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082291563362258944)
  - `TimeoutError: canary-v2 weight=1, expected 3 (from canary-v1)`
- **PASS** 2026-07-29T13:22:47+00:00 · build `2082424973384749056` · branch `master` · base `1995336861fa` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1827/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082424973384749056)

### confirmed (same_base) at `dfb3fd0aa3e5`
- **FAIL** 2026-08-25T16:47:09+00:00 · build `2092261395939725312` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092261395939725312)
  - `AssertionError: stable phase: promote: error rate 15.0% exceeds 0.0%`
- **PASS** 2026-08-25T13:09:35+00:00 · build `2092210654617276416` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092210654617276416)
