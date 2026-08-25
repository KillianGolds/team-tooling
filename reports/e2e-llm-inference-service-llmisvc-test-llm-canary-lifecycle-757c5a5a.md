`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_three_member_group`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 1
**First seen:** 2026-07-21T08:33:50+00:00 · **Last seen:** 2026-08-25T16:47:09+00:00

### suspected (base_moved) at `d71d8d162079`
- **FAIL** 2026-07-21T08:33:50+00:00 · build `2079458353657942016` · branch `master` · base `e9669aae71d5` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079458353657942016)
  - `AssertionError: three-member group: error rate 4.9% exceeds 0.0%`
- **PASS** 2026-07-21T06:33:12+00:00 · build `2079427127505063936` · branch `master` · base `330fb196192d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079427127505063936)

### confirmed (same_base) at `a347f5da5704`
- **FAIL** 2026-08-19T20:56:05+00:00 · build `2090155896364601344` · branch `master` · base `e668a9cada09` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1901/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2090155896364601344)
  - `AssertionError: tri-v3 received no traffic (61 total)`
- **PASS** 2026-08-19T23:53:58+00:00 · build `2090198528688132096` · branch `master` · base `e668a9cada09` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1901/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2090198528688132096)

### confirmed (same_base) at `dfb3fd0aa3e5`
- **FAIL** 2026-08-25T16:47:09+00:00 · build `2092261395939725312` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092261395939725312)
  - `AssertionError: three-member group: error rate 1.6% exceeds 0.0%`
- **PASS** 2026-08-25T13:09:35+00:00 · build `2092210654617276416` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092210654617276416)
