`llmisvc/test_llm_model_routing_only.py::test_model_based_routing_only[cluster_single_node-cluster_cpu-gateway]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 5 · **Suspected:** 1
**First seen:** 2026-10-27T23:41:32+00:00 · **Last seen:** 2026-11-06T22:27:58+00:00 · **Tracking since:** 2026-10-13T14:19:46+00:00

### confirmed (same_base) at `6488274b8c5d`
- **FAIL** 2026-10-27T19:48:16+00:00 · build `2115140882217832448` · branch `master` · base `fd466456c6e2` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115140882217832448)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='ab819ed7c8ba347b4bdbb171b3b4e03a-1002325950.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-r`
- **PASS** 2026-10-27T23:41:32+00:00 · build `2115199975683002368` · branch `master` · base `fd466456c6e2` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115199975683002368)

### confirmed (same_base) at `33a0df575200`
- **FAIL** 2026-10-28T12:31:33+00:00 · build `2115384979851579392` · branch `master` · base `958de5310307` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115384979851579392)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a70b22b39a874440eb98986bfd381f38-2126068800.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-r`
- **PASS** 2026-10-28T14:20:11+00:00 · build `2115422882333986816` · branch `master` · base `958de5310307` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2125/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115422882333986816)

### confirmed (same_base) at `d1751b2516ca`
- **FAIL** 2026-10-30T09:57:40+00:00 · build `2116072593621520384` · branch `master` · base `c6f8caad6b3d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2113/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2116072593621520384)
  - `AssertionError: ❌ Failed to call model: HTTPConnectionPool(host='acbb30aca2e744d0db4b5bdf2cea2fbd-946807991.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /v1/completions (Caus`
- **PASS** 2026-10-30T12:04:48+00:00 · build `2116114472652247040` · branch `master` · base `c6f8caad6b3d` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2113/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2116114472652247040)

### suspected (base_moved) at `642956109907`
- **FAIL** 2026-10-30T21:30:15+00:00 · build `2116252517988831232` · branch `master` · base `dbd2476df3bb` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2116252517988831232)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a68fcfc00ecb44631a8524ad08e960e6-2022215001.us-west-2.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-r`
- **PASS** 2026-10-30T16:34:05+00:00 · build `2116180222909878272` · branch `master` · base `277d961b85da` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2144/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2116180222909878272)

### confirmed (same_base) at `dce5f750e540`
- **FAIL** 2026-11-06T18:48:58+00:00 · build `2118747700441649152` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2172/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2118747700441649152)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a804f57d353ee400b9a0b167e17b5b8a-1313856041.us-west-2.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-r`
- **PASS** 2026-11-06T22:27:58+00:00 · build `2118803598295961600` · branch `master` · base `a16b6ca93e10` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2172/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2118803598295961600)

### confirmed (same_base) at `076a091bea8e`
- **FAIL** 2026-10-31T15:22:52+00:00 · build `2116515437112987648` · branch `release-v0.17` · base `aaefcec9cd60` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2155/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2116515437112987648)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='adc79961c48ab408d9e7571074c8613e-799004705.us-west-2.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-31T17:06:26+00:00 · build `2116551593359839232` · branch `release-v0.17` · base `aaefcec9cd60` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2155/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2116551593359839232)
