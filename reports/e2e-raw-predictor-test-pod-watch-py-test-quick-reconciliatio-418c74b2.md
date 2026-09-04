`predictor/test_pod_watch.py::test_quick_reconciliation_on_init_container_failure`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0
**First seen:** 2026-09-03T21:58:14+00:00 · **Last seen:** 2026-09-03T21:58:14+00:00

### confirmed (same_base) at `8030d8e9f191`
- **FAIL** 2026-09-03T21:58:14+00:00 · build `2095605686481195008` · branch `master` · base `891090a15e48` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095605686481195008)
  - `AssertionError: ISVC isvc-init-fail-489878 did not report failure status within timeout. The init container failure should trigger quick reconciliation and status update.`
- **PASS** 2026-09-03T20:06:48+00:00 · build `2095574797189648384` · branch `master` · base `891090a15e48` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095574797189648384)
