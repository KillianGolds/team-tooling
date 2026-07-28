`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-custom-route-timeout-pd-scheduler-managed-workload-pd-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1 · **Runs seen:** 367
**First seen:** 2026-07-21T18:44:27+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### suspected (base_moved) at `c869a5ec8292`
- **FAIL** 2026-07-21T15:10:07+00:00 · build `2079554406809866240` · branch `master` · base `f43e170bf716` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1729/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079554406809866240)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-07-21T18:44:27+00:00 · build `2079616271057424384` · branch `master` · base `9d7eb2569501` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1729/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079616271057424384)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `kubernetes.client.exceptions.ApiException: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
