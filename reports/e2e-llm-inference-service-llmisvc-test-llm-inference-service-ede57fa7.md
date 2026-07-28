`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-no-scheduler-workload-single-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 1 · **Runs seen:** 362
**First seen:** 2026-07-21T08:33:50+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### suspected (base_moved) at `d71d8d162079`
- **FAIL** 2026-07-21T06:33:12+00:00 · build `2079427127505063936` · branch `master` · base `330fb196192d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079427127505063936)
  - `AssertionError: Missing true conditions: {'WorkloadsReady', 'Ready'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-21T06:03:04Z', 'severity': 'Info', 'stat`
- **PASS** 2026-07-21T08:33:50+00:00 · build `2079458353657942016` · branch `master` · base `e9669aae71d5` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079458353657942016)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
