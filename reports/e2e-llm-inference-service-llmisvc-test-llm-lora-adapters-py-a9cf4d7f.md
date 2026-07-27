`llmisvc/test_llm_lora_adapters.py::test_llm_with_lora_adapters[cluster_cpu-single-lora-adapter-hf]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 2 · **Runs seen:** 356
**First seen:** 2026-06-30T16:50:48+00:00 · **Last seen:** 2026-07-24T00:58:13+00:00

### suspected (base_moved) at `55f8e9ae881c`
- **FAIL** 2026-06-30T16:50:48+00:00 · build `2071953501960802304` · branch `master` · base `7431f5f35afb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1682/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2071953501960802304)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='aa6ecaeb065034d2081d99096a22e274-1792588047.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /kserve-ci-e2e-test/lor`
- **PASS** 2026-06-30T05:41:25+00:00 · build `2071791222376108032` · branch `master` · base `82c255b05e92` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1682/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2071791222376108032)

### suspected (base_moved) at `800f29c3088b`
- **FAIL** 2026-07-01T19:35:35+00:00 · build `2072357802289926144` · branch `master` · base `7431f5f35afb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1692/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072357802289926144)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a92841c1281524e468ca1fc9c738baf1-1852884369.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /kserve-ci-e2e-test/lor`
- **PASS** 2026-07-01T23:46:23+00:00 · build `2072430800640413696` · branch `master` · base `d672737a5d55` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1692/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2072430800640413696)

### confirmed (same_base) at `b2d6323b6248`
- **FAIL** 2026-07-24T00:58:13+00:00 · build `2080431257170219008` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080431257170219008)
  - `kubernetes.client.exceptions.ApiException: (500)`
- **PASS** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
