`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-custom-route-timeout-scheduler-managed-workload-single-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1 · **Runs seen:** 356
**First seen:** 2026-06-26T23:29:32+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### suspected (base_moved) at `8d0f4fa336d1`
- **FAIL** 2026-06-26T23:29:32+00:00 · build `2070609724344111104` · branch `master` · base `171919f9ea1b` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2070609724344111104)
  - `AssertionError: ❌ Failed to call model: HTTPConnectionPool(host='abad617a8cab14ca8b6e631ecd62093c-336011534.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /kserve-ci-e2e-test/c`
- **PASS** 2026-06-25T19:46:03+00:00 · build `2070194846089351168` · branch `master` · base `63cadcaf267e` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2070194846089351168)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
