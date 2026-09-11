`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-managed-workload-llmd-simulator1]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1
**First seen:** 2026-08-31T19:55:31+00:00 · **Last seen:** 2026-08-31T19:55:31+00:00 · **Tracking since:** 2026-07-20T15:54:50+00:00

### suspected (base_moved) at `419a52e4ab43`
- **FAIL** 2026-08-31T19:55:31+00:00 · build `2094484519200493568` · branch `master` · base `606d130e70ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1923/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2094484519200493568)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-08-31T16:32:52+00:00 · build `2094435511706849280` · branch `master` · base `843270d4005f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1923/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2094435511706849280)
