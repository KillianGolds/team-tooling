`llmisvc/test_llm_inference_service_stop.py::test_llm_stop_feature[cluster_cpu-cluster_single_node-router-managed-workload-single-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0
**First seen:** 2026-09-11T21:39:25+00:00 · **Last seen:** 2026-09-11T21:39:25+00:00

### confirmed (same_base) at `9447f454698d`
- **FAIL** 2026-09-11T19:32:49+00:00 · build `2098467276784144384` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098467276784144384)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-09-11T21:39:25+00:00 · build `2098495862442299392` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098495862442299392)
