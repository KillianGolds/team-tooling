`predictor/test_canary_raw_deployment.py::test_canary_promote`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1
**First seen:** 2026-10-30T21:38:45+00:00 · **Last seen:** 2026-10-30T21:38:45+00:00 · **Tracking since:** 2026-07-31T01:59:57+00:00

### suspected (base_moved) at `642956109907`
- **FAIL** 2026-10-30T21:38:45+00:00 · build `2116252518072717312` · branch `master` · base `dbd2476df3bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2116252518072717312)
  - `RuntimeError: Timeout to start the InferenceService isvc-canary-promote.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Infer`
- **PASS** 2026-10-30T16:02:53+00:00 · build `2116180223027318784` · branch `master` · base `277d961b85da` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2116180223027318784)
