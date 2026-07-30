`predictor/test_autogluon.py::test_autogluon_runtime_kserve_v2`

**Job:** e2e-predictor · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 3
**First seen:** 2026-07-17T12:18:17+00:00 · **Last seen:** 2026-07-22T06:34:03+00:00

### suspected (base_moved) at `adea8f1a265f`
- **FAIL** 2026-07-16T16:10:34+00:00 · build `2077773162627469312` · branch `master` · base `6d99456d493a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1744/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2077773162627469312)
  - `RuntimeError: No service found with labels: {'app': 'istio-ingressgateway', 'istio': 'ingressgateway'}`
- **PASS** 2026-07-17T12:18:17+00:00 · build `2078075821284659200` · branch `master` · base `522fde6b4021` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1744/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2078075821284659200)

### suspected (base_moved) at `3f6dcd734dc6`
- **FAIL** 2026-07-10T10:29:15+00:00 · build `2075510059198058496` · branch `master` · base `b939e7006ceb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2075510059198058496)
  - `RuntimeError: No service found with labels: {'app': 'istio-ingressgateway', 'istio': 'ingressgateway'}`
- **PASS** 2026-07-18T08:30:35+00:00 · build `2078380559356137472` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2078380559356137472)

### suspected (base_moved) at `c8e2a2d72abf`
- **FAIL** 2026-07-15T07:20:24+00:00 · build `2077248409697259520` · branch `master` · base `687fc3439bce` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1732/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2077248409697259520)
  - `RuntimeError: No service found with labels: {'app': 'istio-ingressgateway', 'istio': 'ingressgateway'}`
- **PASS** 2026-07-22T06:34:03+00:00 · build `2079802182672060416` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1732/pull-ci-opendatahub-io-kserve-master-e2e-predictor/2079802182672060416)

### confirmed (same_base) at `392d2a984291`
- **FAIL** 2026-07-17T22:53:53+00:00 · build `2078212106326380544` · branch `release-v0.17` · base `4e873979b7bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1761/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2078212106326380544)
  - `RuntimeError: Timeout to start the InferenceService isvc-autogluon-v2.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Inferen`
- **PASS** 2026-07-18T00:56:46+00:00 · build `2078252497595535360` · branch `release-v0.17` · base `4e873979b7bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1761/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-predictor/2078252497595535360)
