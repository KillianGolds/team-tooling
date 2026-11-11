`predictor/test_raw_deployment.py::test_raw_deployment_runtime_kserve`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 0
**First seen:** 2026-10-21T13:46:52+00:00 · **Last seen:** 2026-11-06T23:49:37+00:00 · **Tracking since:** 2026-09-03T20:06:48+00:00

### confirmed (same_base) at `5b3411083e25`
- **FAIL** 2026-10-21T03:01:58+00:00 · build `2112715057002450944` · branch `master` · base `e3b46b4b4e65` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2115/pull-ci-opendatahub-io-kserve-master-e2e-raw/2112715057002450944)
  - `RuntimeError: Timeout to start the InferenceService raw-sklearn-runtime-21f02.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': `
- **PASS** 2026-10-21T13:46:52+00:00 · build `2112887235861811200` · branch `master` · base `e3b46b4b4e65` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2115/pull-ci-opendatahub-io-kserve-master-e2e-raw/2112887235861811200)

### confirmed (same_base) at `240f791134f1`
- **FAIL** 2026-11-06T18:12:27+00:00 · build `2118753183047094272` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118753183047094272)
  - `kubernetes.client.exceptions.ServiceException: (500)`
- **PASS** 2026-11-06T23:49:37+00:00 · build `2118836581988044800` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118836581988044800)
