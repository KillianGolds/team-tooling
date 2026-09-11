`predictor/test_pod_watch.py::test_event_storm_prevention_init_container_isolation`

**Job:** e2e-raw · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 2
**First seen:** 2026-09-03T20:06:48+00:00 · **Last seen:** 2026-09-11T12:54:23+00:00

### suspected (base_moved) at `8030d8e9f191`
- **FAIL** 2026-09-03T20:06:48+00:00 · build `2095574797189648384` · branch `master` · base `891090a15e48` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095574797189648384)
  - `RuntimeError: Timeout to start the InferenceService isvc-primary-03e942.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Infer`
- **PASS** 2026-09-02T23:56:19+00:00 · build `2095284803698954240` · branch `master` · base `600482b1793a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-raw/2095284803698954240)

### suspected (base_moved) at `43d96abed423`
- **FAIL** 2026-09-10T18:32:34+00:00 · build `2098089615054344192` · branch `master` · base `48637f2611fb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-raw/2098089615054344192)
  - `RuntimeError: Timeout to start the InferenceService isvc-primary-d0c194.                                The InferenceService is as following: {'apiVersion': 'serving.kserve.io/v1beta1', 'kind': 'Infer`
- **PASS** 2026-09-11T12:54:23+00:00 · build `2098377668608135168` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-raw/2098377668608135168)
