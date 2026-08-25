`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_force_stop_route_owner`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 0
**First seen:** 2026-08-23T12:14:39+00:00 · **Last seen:** 2026-08-25T08:19:41+00:00

### confirmed (same_base) at `8665cd94c538`
- **FAIL** 2026-08-23T08:58:02+00:00 · build `2091424294914494464` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091424294914494464)
  - `AssertionError: force-stop route owner: traffic should shift to v2: error rate 3.3% exceeds 0.0%`
- **PASS** 2026-08-23T12:14:39+00:00 · build `2091475409479667712` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091475409479667712)

### confirmed (same_base) at `3b04662cef69`
- **FAIL** 2026-08-25T06:25:17+00:00 · build `2092109408556290048` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092109408556290048)
  - `AssertionError: force-stop route owner: traffic should shift to v2: error rate 6.7% exceeds 0.0%`
- **PASS** 2026-08-25T08:19:41+00:00 · build `2092142627129397248` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092142627129397248)
