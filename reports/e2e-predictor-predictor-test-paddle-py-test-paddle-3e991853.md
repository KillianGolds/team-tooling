`predictor/test_paddle.py::test_paddle`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 0
**First seen:** 2026-08-21T05:23:20+00:00 · **Last seen:** 2026-08-23T11:36:37+00:00

### confirmed (same_base) at `25570f3b9981`
- **FAIL** 2026-08-21T04:22:59+00:00 · build `2090617650039230464` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2090617650039230464)
  - `RuntimeError: Timeout to start the InferenceService isvc-paddle.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'InferenceServ`
- **PASS** 2026-08-21T05:23:20+00:00 · build `2090656127074177024` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2090656127074177024)

### confirmed (same_base) at `8665cd94c538`
- **FAIL** 2026-08-23T09:49:39+00:00 · build `2091424294952243200` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2091424294952243200)
  - `RuntimeError: Timeout to start the InferenceService isvc-paddle.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'InferenceServ`
- **PASS** 2026-08-23T11:36:37+00:00 · build `2091475409517416448` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2091475409517416448)
