`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-managed-workload-llmd-simulator1]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 4 · **Runs seen:** 371
**First seen:** 2026-07-20T15:54:50+00:00 · **Last seen:** 2026-07-22T09:31:44+00:00

### suspected (base_moved) at `54f1a2337f66`
- **FAIL** 2026-07-19T21:54:33+00:00 · build `2078924338689478656` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1770/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078924338689478656)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'WorkloadsReady', 'Ready'}, got [{'lastTransitionTime': '2026-07-19T20:59:47Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-20T15:54:50+00:00 · build `2079207692374642688` · branch `master` · base `dfa3f25d8c42` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1770/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079207692374642688)

### suspected (base_moved) at `0099d125f5c3`
- **FAIL** 2026-07-18T22:49:32+00:00 · build `2078581108336758784` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078581108336758784)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'Ready', 'WorkloadsReady', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-18T21:54:01Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-20T21:21:02+00:00 · build `2079290817322684416` · branch `master` · base `71dd0b64b348` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079290817322684416)

### suspected (base_moved) at `c8e2a2d72abf`
- **FAIL** 2026-07-15T08:17:00+00:00 · build `2077248409634344960` · branch `master` · base `687fc3439bce` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1732/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2077248409634344960)
  - `AssertionError: Service returned 502:`
- **PASS** 2026-07-22T07:04:23+00:00 · build `2079802182638505984` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1732/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079802182638505984)

### suspected (base_moved) at `7056d674e121`
- **FAIL** 2026-07-18T13:57:09+00:00 · build `2078441177786355712` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078441177786355712)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'Ready', 'RouterReady', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-18T13:01:27Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-22T09:31:44+00:00 · build `2079837164643815424` · branch `master` · base `5daeea6f120a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079837164643815424)
