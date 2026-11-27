`logger/test_raw_logger.py::test_kserve_logger`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1
**First seen:** 2026-11-05T22:57:44+00:00 · **Last seen:** 2026-11-06T23:49:37+00:00 · **Tracking since:** 2026-08-19T06:08:28+00:00

### suspected (base_moved) at `9428f159de71`
- **FAIL** 2026-11-05T21:09:13+00:00 · build `2118436907724574720` · branch `master` · base `77be385bdaa4` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118436907724574720)
  - `assert 'org.kubeflow.serving.inference.request' in "b''"`
- **PASS** 2026-11-05T22:57:44+00:00 · build `2118460200041058304` · branch `master` · base `ff80abbf7ac0` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118460200041058304)

### confirmed (same_base) at `240f791134f1`
- **FAIL** 2026-11-06T18:12:27+00:00 · build `2118753183047094272` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118753183047094272)
  - `kubernetes.client.exceptions.ServiceException: (500)`
- **PASS** 2026-11-06T23:49:37+00:00 · build `2118836581988044800` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2147/pull-ci-opendatahub-io-kserve-master-e2e-raw/2118836581988044800)
