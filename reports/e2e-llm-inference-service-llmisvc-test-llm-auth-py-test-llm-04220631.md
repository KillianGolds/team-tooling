`llmisvc/test_llm_auth.py::test_llm_auth_disabled_no_token_required[cluster_cpu-cluster_single_node-auth-disabled]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1 · **Runs seen:** 378
**First seen:** 2026-06-26T23:29:32+00:00 · **Last seen:** 2026-06-26T23:29:32+00:00

### suspected (base_moved) at `8d0f4fa336d1`
- **FAIL** 2026-06-25T19:46:03+00:00 · build `2070194846089351168` · branch `master` · base `63cadcaf267e` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2070194846089351168)
  - `requests.exceptions.ReadTimeout: HTTPConnectionPool(host='aa78981d6368c441c801bf51c49fd2af-640996353.us-east-1.elb.amazonaws.com', port=80): Read timed out. (read timeout=60)`
- **PASS** 2026-06-26T23:29:32+00:00 · build `2070609724344111104` · branch `master` · base `171919f9ea1b` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1671/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2070609724344111104)
