`llmisvc/test_llm_tls.py::test_llm_tls_resources[cluster_cpu-cluster_single_node-router-managed-workload-single-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 0
**First seen:** 2026-08-26T20:48:41+00:00 · **Last seen:** 2026-08-26T20:48:41+00:00

### confirmed (same_base) at `30c2946f5be3`
- **FAIL** 2026-08-26T17:13:58+00:00 · build `2092634091923968000` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092634091923968000)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-08-26T20:48:41+00:00 · build `2092680786200236032` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092680786200236032)
