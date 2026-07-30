`llmisvc/test_llm_inference_service_stop.py::test_llm_stop_feature[cluster_cpu-cluster_single_node-router-managed-workload-single-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0 · **Runs seen:** 379
**First seen:** 2026-07-24T00:58:13+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
