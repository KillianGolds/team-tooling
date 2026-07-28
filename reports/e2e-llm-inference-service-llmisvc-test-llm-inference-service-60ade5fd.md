`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-managed-workload-pd-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 2 · **Suspected:** 0 · **Runs seen:** 362
**First seen:** 2026-07-19T09:42:38+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### confirmed (same_base) at `bf5784c504ee`
- **FAIL** 2026-07-19T06:34:51+00:00 · build `2078700793065639936` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078700793065639936)
  - `AssertionError: Missing true conditions: {'WorkloadsReady', 'Ready'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-19T06:03:00Z', 'severity': 'Info', 'stat`
- **PASS** 2026-07-19T09:42:38+00:00 · build `2078748847613415424` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078748847613415424)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `kubernetes.client.exceptions.ApiException: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
