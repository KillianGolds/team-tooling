`predictor/test_canary_raw_deployment.py::test_canary_rollback`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 4 · **Suspected:** 0
**First seen:** 2026-10-21T13:46:52+00:00 · **Last seen:** 2026-11-06T23:49:37+00:00 · **Tracking since:** 2026-09-03T20:06:48+00:00

### confirmed (same_base) at `5b3411083e25`
- **FAIL** 2026-10-21T03:01:58+00:00 · build `2112715057002450944` · branch `master` · base `e3b46b4b4e65` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2115/pull-ci-opendatahub-io-kserve-master-e2e-raw/2112715057002450944)
  - `RuntimeError: Timeout to start the InferenceService isvc-canary-rollback.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Infe`
- **PASS** 2026-10-21T13:46:52+00:00 · build `2112887235861811200` · branch `master` · base `e3b46b4b4e65` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2115/pull-ci-opendatahub-io-kserve-master-e2e-raw/2112887235861811200)

### confirmed (same_base) at `33a0df575200`
- **FAIL** 2026-10-28T11:50:48+00:00 · build `2115384979922882560` · branch `master` · base `958de5310307` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-raw/2115384979922882560)
  - `TimeoutError: Deployment isvc-canary-rollback-v2-predictor not ready within 120s`
- **PASS** 2026-10-28T13:11:19+00:00 · build `2115416140665589760` · branch `master` · base `958de5310307` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-raw/2115416140665589760)

### confirmed (same_base) at `631682ef03a1`
- **FAIL** 2026-11-02T16:30:29+00:00 · build `2117275205809213440` · branch `master` · base `4564a985cd5f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-raw/2117275205809213440)
  - `RuntimeError: Timeout to start the InferenceService isvc-canary-rollback for expected generation 2.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.`
- **PASS** 2026-11-02T17:40:14+00:00 · build `2117294070505148416` · branch `master` · base `4564a985cd5f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-raw/2117294070505148416)

### confirmed (same_base) at `240f791134f1`
- **FAIL** 2026-11-06T18:12:27+00:00 · build `2118753183047094272` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118753183047094272)
  - `kubernetes.client.exceptions.ServiceException: (500)`
- **PASS** 2026-11-06T23:49:37+00:00 · build `2118836581988044800` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118836581988044800)
