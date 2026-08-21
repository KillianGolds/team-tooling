`predictor/test_sklearn.py::test_sklearn_kserve`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0
**First seen:** 2026-08-21T05:23:20+00:00 · **Last seen:** 2026-08-21T05:23:20+00:00

### confirmed (same_base) at `25570f3b9981`
- **FAIL** 2026-08-21T04:22:59+00:00 · build `2090617650039230464` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2090617650039230464)
  - `RuntimeError: Timeout to start the InferenceService isvc-sklearn.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'InferenceSer`
- **PASS** 2026-08-21T05:23:20+00:00 · build `2090656127074177024` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2090656127074177024)
