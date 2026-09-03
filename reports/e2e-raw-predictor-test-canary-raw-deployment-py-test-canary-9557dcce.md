`predictor/test_canary_raw_deployment.py::test_canary_create`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1
**First seen:** 2026-09-03T20:06:48+00:00 · **Last seen:** 2026-09-03T20:06:48+00:00

### suspected (base_moved) at `8030d8e9f191`
- **FAIL** 2026-09-03T20:06:48+00:00 · build `2095574797189648384` · branch `master` · base `891090a15e48` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095574797189648384)
  - `RuntimeError: Timeout to start the InferenceService isvc-canary-create.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Infere`
- **PASS** 2026-09-02T23:56:19+00:00 · build `2095284803698954240` · branch `master` · base `600482b1793a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095284803698954240)
