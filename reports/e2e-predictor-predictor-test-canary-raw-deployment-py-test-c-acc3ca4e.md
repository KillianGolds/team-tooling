`predictor/test_canary_raw_deployment.py::test_canary_promote`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1
**First seen:** 2026-07-31T01:59:57+00:00 · **Last seen:** 2026-07-31T01:59:57+00:00

### suspected (same_base) at `95a1b4eadfa6`
- **FAIL** None · build `2082897818745311232` · branch `master` · base `76da12e77e42` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1831/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2082897818745311232)
  - `RuntimeError: Timeout to start the InferenceService isvc-canary-promote for expected generation 2.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.i`
- **PASS** 2026-07-31T01:59:57+00:00 · build `2082992606890954752` · branch `master` · base `76da12e77e42` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1831/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2082992606890954752)
