`llmisvc/test_rolling_upgrade.py::test_rolling_upgrade_coordination[cluster_cpu-cluster_single_node-router-managed-workload-llmd-simulator-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1 · **Runs seen:** 367
**First seen:** 2026-07-21T18:44:27+00:00 · **Last seen:** 2026-07-21T18:44:27+00:00

### suspected (base_moved) at `c869a5ec8292`
- **FAIL** 2026-07-21T15:10:07+00:00 · build `2079554406809866240` · branch `master` · base `f43e170bf716` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1729/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079554406809866240)
  - `RuntimeError: ❌ Exception when calling CustomObjectsApi->get_namespaced_custom_object for LLMInferenceService: (500)`
- **PASS** 2026-07-21T18:44:27+00:00 · build `2079616271057424384` · branch `master` · base `9d7eb2569501` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1729/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079616271057424384)
