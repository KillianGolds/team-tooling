`llmisvc/test_llm_model_routing_only.py::test_model_based_routing_only[cluster_single_node-cluster_cpu-service]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 3 · **Suspected:** 3
**First seen:** 2026-10-15T23:35:03+00:00 · **Last seen:** 2026-10-31T17:06:26+00:00 · **Tracking since:** 2026-10-14T22:24:20+00:00

### suspected (base_moved) at `73c770939284`
- **FAIL** 2026-10-15T21:03:07+00:00 · build `2110806564330803200` · branch `master` · base `0e1ec92502fe` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2106/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2110806564330803200)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a188d00ca856b4864976d2e46249f627-756681200.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-15T23:35:03+00:00 · build `2110840716161716224` · branch `master` · base `a85489b653c6` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2106/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2110840716161716224)

### confirmed (same_base) at `c5fd7514b2f6`
- **FAIL** 2026-10-19T18:11:00+00:00 · build `2112215703552528384` · branch `master` · base `6de44e751514` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2099/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2112215703552528384)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a33b9250660e248959785ad9abca9a3d-137526384.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-19T15:40:44+00:00 · build `2112171426965360640` · branch `master` · base `6de44e751514` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2099/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2112171426965360640)

### confirmed (same_base) at `96de6b5059af`
- **FAIL** 2026-10-23T23:13:39+00:00 · build `2113735665974775808` · branch `master` · base `5aabec9b8c19` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2129/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2113735665974775808)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a09366349b2eb496b91c73c01c019c9d-285760914.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-25T01:01:33+00:00 · build `2114127885999542272` · branch `master` · base `5aabec9b8c19` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2129/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2114127885999542272)

### suspected (base_moved) at `61c6bb0aa2a1`
- **FAIL** 2026-10-28T23:00:56+00:00 · build `2115548408201613312` · branch `master` · base `6302141aa9dc` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2088/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115548408201613312)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='ac824220d78054117ad49c36440b8579-918133191.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-28T13:41:09+00:00 · build `2115407713155420160` · branch `master` · base `958de5310307` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2088/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115407713155420160)

### suspected (base_moved) at `6f309394888a`
- **FAIL** 2026-10-30T01:42:17+00:00 · build `2115953395868110848` · branch `master` · base `b8a7dcc6e5f9` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2109/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2115953395868110848)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a996d1f8bf9324233bf3e6362206c6ea-694271250.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-30T14:40:23+00:00 · build `2116152769000771584` · branch `master` · base `ad57c8e98703` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2109/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2116152769000771584)

### confirmed (same_base) at `076a091bea8e`
- **FAIL** 2026-10-31T17:06:26+00:00 · build `2116551593359839232` · branch `release-v0.17` · base `aaefcec9cd60` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2155/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2116551593359839232)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='ad4140dc133254a548bf7b311b021dbd-524742149.us-west-2.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-model-based-ro`
- **PASS** 2026-10-31T15:22:52+00:00 · build `2116515437112987648` · branch `release-v0.17` · base `aaefcec9cd60` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/2155/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2116515437112987648)
