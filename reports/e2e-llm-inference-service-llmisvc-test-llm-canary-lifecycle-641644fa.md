`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_force_stop_route_owner`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0
**First seen:** 2026-08-23T12:14:39+00:00 · **Last seen:** 2026-08-23T12:14:39+00:00

### confirmed (same_base) at `8665cd94c538`
- **FAIL** 2026-08-23T08:58:02+00:00 · build `2091424294914494464` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091424294914494464)
  - `AssertionError: force-stop route owner: traffic should shift to v2: error rate 3.3% exceeds 0.0%`
- **PASS** 2026-08-23T12:14:39+00:00 · build `2091475409479667712` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091475409479667712)
