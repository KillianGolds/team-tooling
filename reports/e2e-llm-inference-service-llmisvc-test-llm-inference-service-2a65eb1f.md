`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_multi_node-router-managed-workload-simulated-dp-ep-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1 · **Runs seen:** 361
**First seen:** 2026-07-09T15:11:05+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### suspected (base_moved) at `a7f604c6b6fa`
- **FAIL** 2026-07-09T15:11:05+00:00 · build `2075199676763607040` · branch `master` · base `2fdc97517179` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1688/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2075199676763607040)
  - `AssertionError: Missing true conditions: {'Ready', 'WorkloadsReady'}, expected {'RouterReady', 'Ready', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-09T14:15:23Z', 'severity': 'Info', 'stat`
- **PASS** 2026-07-07T23:56:51+00:00 · build `2074604342177959936` · branch `master` · base `a193f40bcafe` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1688/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074604342177959936)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `kubernetes.client.exceptions.ApiException: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
