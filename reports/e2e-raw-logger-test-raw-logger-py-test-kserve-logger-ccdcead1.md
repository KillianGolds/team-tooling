`logger/test_raw_logger.py::test_kserve_logger`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 2
**First seen:** 2026-08-19T06:08:28+00:00 · **Last seen:** 2026-09-03T20:06:48+00:00

### suspected (base_moved) at `79b2b36dbb1e`
- **FAIL** 2026-08-19T06:08:28+00:00 · build `2089927799828647936` · branch `master` · base `7cdc60a71936` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1883/pull-ci-opendatahub-io-kserve-master-e2e-raw/2089927799828647936)
  - `httpx.HTTPStatusError: , '503 Service Unavailable' for url 'https://isvc-logger-raw-334d0-kserve-ci-e2e-test.apps.415da5babb363caaf10c.openshift-ci-aws.rhaiseng.com/v1/models/isvc-logger-raw-334d0:pre`
- **PASS** 2026-08-19T00:59:50+00:00 · build `2089862668805476352` · branch `master` · base `543daebedf8f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1883/pull-ci-opendatahub-io-kserve-master-e2e-raw/2089862668805476352)

### suspected (base_moved) at `8030d8e9f191`
- **FAIL** 2026-09-03T20:06:48+00:00 · build `2095574797189648384` · branch `master` · base `891090a15e48` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095574797189648384)
  - `httpx.HTTPStatusError: , '503 Service Unavailable' for url 'https://isvc-logger-raw-82ede-kserve-ci-e2e-test.apps.3cb87a904176b12a8e04.openshift-ci-aws.rhaiseng.com/v1/models/isvc-logger-raw-82ede:pre`
- **PASS** 2026-09-02T23:56:19+00:00 · build `2095284803698954240` · branch `master` · base `600482b1793a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095284803698954240)
