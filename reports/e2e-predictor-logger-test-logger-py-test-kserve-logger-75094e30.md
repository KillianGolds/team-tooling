`logger/test_logger.py::test_kserve_logger`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0 · **Runs seen:** 346
**First seen:** 2026-07-18T00:56:46+00:00 · **Last seen:** 2026-07-18T00:56:46+00:00

### confirmed (same_base) at `392d2a984291`
- **FAIL** 2026-07-17T22:53:53+00:00 · build `2078212106326380544` · branch `release-v0.17` · base `4e873979b7bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1761/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2078212106326380544)
  - `httpx.HTTPStatusError: , '503 Service Unavailable' for url 'https://isvc-logger-kserve-ci-e2e-test.apps.3949245586afe1682e3b.openshift-ci-aws.rhaiseng.com/v1/models/isvc-logger:predict'`
- **PASS** 2026-07-18T00:56:46+00:00 · build `2078252497595535360` · branch `release-v0.17` · base `4e873979b7bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1761/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2078252497595535360)
