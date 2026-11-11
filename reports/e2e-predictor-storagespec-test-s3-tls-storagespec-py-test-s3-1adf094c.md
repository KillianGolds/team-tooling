`storagespec/test_s3_tls_storagespec.py::test_s3_tls_global_custom_cert_storagespec_kserve`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1
**First seen:** 2026-10-19T15:49:33+00:00 · **Last seen:** 2026-10-30T21:38:45+00:00 · **Tracking since:** 2026-08-21T05:23:20+00:00

### confirmed (same_base) at `c5fd7514b2f6`
- **FAIL** 2026-10-19T14:43:50+00:00 · build `2112171428651470848` · branch `master` · base `6de44e751514` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2099/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2112171428651470848)
  - `RuntimeError: Exception when calling CustomObjectsApi->create_namespaced_custom_object:                 (500)`
- **PASS** 2026-10-19T15:49:33+00:00 · build `2112194390419050496` · branch `master` · base `6de44e751514` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2099/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2112194390419050496)

### suspected (base_moved) at `642956109907`
- **FAIL** 2026-10-30T21:38:45+00:00 · build `2116252518072717312` · branch `master` · base `dbd2476df3bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2116252518072717312)
  - `RuntimeError: Expected inferenceservice isvc-sklearn-s3-tls-global-pass to have model transition status 'UpToDate' after timeout, but got 'InProgress'`
- **PASS** 2026-10-30T16:02:53+00:00 · build `2116180223027318784` · branch `master` · base `277d961b85da` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2116180223027318784)
