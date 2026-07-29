`llmisvc/test_llm_inference_service.py::test_llm_inference_service[cluster_cpu-cluster_single_node-router-with-refs-pd-scheduler-managed-workload-pd-cpu-model-fb-opt-125m]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 6 · **Runs seen:** 374
**First seen:** 2026-07-01T23:46:23+00:00 · **Last seen:** 2026-07-08T08:45:24+00:00

### suspected (base_moved) at `800f29c3088b`
- **FAIL** 2026-07-01T23:46:23+00:00 · build `2072430800640413696` · branch `master` · base `d672737a5d55` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1692/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072430800640413696)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-01T22:40:43Z', 'severity': 'Info', 'status'`
- **PASS** 2026-07-01T19:35:35+00:00 · build `2072357802289926144` · branch `master` · base `7431f5f35afb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1692/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072357802289926144)

### suspected (base_moved) at `a7f604c6b6fa`
- **FAIL** 2026-07-02T17:28:23+00:00 · build `2072697199526940672` · branch `master` · base `fe3584f59ace` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1688/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072697199526940672)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-02T16:22:43Z', 'severity': 'Info', 'status'`
- **PASS** 2026-07-01T15:14:26+00:00 · build `2072297248502321152` · branch `master` · base `7431f5f35afb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1688/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072297248502321152)

### suspected (base_moved) at `8d0f4fa336d1`
- **FAIL** 2026-07-06T12:19:50+00:00 · build `2074061417408892928` · branch `master` · base `caebcfbeb438` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074061417408892928)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'Ready', 'RouterReady', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-06T11:29:44Z', 'severity': 'Info', 'status'`
- **PASS** 2026-06-26T23:29:32+00:00 · build `2070609724344111104` · branch `master` · base `171919f9ea1b` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2070609724344111104)

### suspected (base_moved) at `9bb346f45313`
- **FAIL** 2026-07-02T20:08:04+00:00 · build `2072733249930530816` · branch `master` · base `830d45fb8b0c` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1697/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072733249930530816)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'Ready', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-02T19:05:29Z', 'severity': 'Info', 'status'`
- **PASS** 2026-07-08T00:05:47+00:00 · build `2074604231733547008` · branch `master` · base `a193f40bcafe` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1697/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074604231733547008)

### suspected (base_moved) at `88af9dcf7b24`
- **FAIL** 2026-07-02T20:17:17+00:00 · build `2072733273179557888` · branch `master` · base `830d45fb8b0c` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1695/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072733273179557888)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'WorkloadsReady', 'Ready'}, got [{'lastTransitionTime': '2026-07-02T19:12:24Z', 'severity': 'Info', 'status'`
- **PASS** 2026-07-07T23:37:48+00:00 · build `2074604416744296448` · branch `master` · base `a193f40bcafe` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1695/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074604416744296448)

### suspected (base_moved) at `818bb3bc6aa2`
- **FAIL** 2026-07-06T13:59:27+00:00 · build `2074083352842866688` · branch `master` · base `caebcfbeb438` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074083352842866688)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'Ready', 'RouterReady', 'WorkloadsReady'}, got [{'lastTransitionTime': '2026-07-06T12:47:45Z', 'severity': 'Info', 'status'`
- **PASS** 2026-07-08T08:45:24+00:00 · build `2074742584659415040` · branch `master` · base `8365299e74df` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1684/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2074742584659415040)
