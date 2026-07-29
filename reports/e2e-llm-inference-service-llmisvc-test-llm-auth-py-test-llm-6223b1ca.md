`llmisvc/test_llm_auth.py::test_llm_auth_enabled_requires_token[cluster_cpu-cluster_single_node-auth-enabled-default]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 3 · **Runs seen:** 369
**First seen:** 2026-07-18T09:30:01+00:00 · **Last seen:** 2026-07-22T09:31:44+00:00

### suspected (base_moved) at `3f6dcd734dc6`
- **FAIL** 2026-07-18T09:30:01+00:00 · build `2078380559326777344` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078380559326777344)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'Ready', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-18T08:38:13Z', 'message': 'AuthPolicy CRD i`
- **PASS** 2026-07-10T11:32:51+00:00 · build `2075510059160309760` · branch `master` · base `b939e7006ceb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2075510059160309760)

### suspected (base_moved) at `0099d125f5c3`
- **FAIL** 2026-07-18T22:49:32+00:00 · build `2078581108336758784` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078581108336758784)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-18T21:57:56Z', 'message': 'AuthPolicy CRD i`
- **PASS** 2026-07-20T21:21:02+00:00 · build `2079290817322684416` · branch `master` · base `71dd0b64b348` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079290817322684416)

### suspected (base_moved) at `7056d674e121`
- **FAIL** 2026-07-18T13:57:09+00:00 · build `2078441177786355712` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078441177786355712)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'WorkloadsReady', 'Ready'}, got [{'lastTransitionTime': '2026-07-18T13:05:29Z', 'message': 'AuthPolicy CRD i`
- **PASS** 2026-07-22T09:31:44+00:00 · build `2079837164643815424` · branch `master` · base `5daeea6f120a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079837164643815424)
