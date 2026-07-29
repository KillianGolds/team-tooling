`llmisvc/test_flow_control.py::test_flow_control_smoke[cluster_cpu-cluster_single_node-flow-control-utilization-detector]`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 1 · **Suspected:** 4 · **Runs seen:** 371
**First seen:** 2026-07-18T12:41:26+00:00 · **Last seen:** 2026-07-22T09:31:44+00:00

### confirmed (same_base) at `35e70806618d`
- **FAIL** 2026-07-18T12:41:26+00:00 · build `2078434853891608576` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078434853891608576)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a8524b15418474e389d76d46178798eb-1515068777.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-flow-control-`
- **PASS** 2026-07-18T10:59:33+00:00 · build `2078406677463306240` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078406677463306240)

### suspected (base_moved) at `21b099ce0cf6`
- **FAIL** 2026-07-18T14:43:46+00:00 · build `2078467907251081216` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078467907251081216)
  - `requests.exceptions.ConnectionError: HTTPConnectionPool(host='a7e0a6a8185fa4a74888f81966502d31-1734149490.us-east-1.elb.amazonaws.com', port=80): Max retries exceeded with url: /e2e-test-flow-control-`
- **PASS** 2026-07-18T16:26:13+00:00 · build `2078493048152526848` · branch `master` · base `9a148cc23cd7` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1765/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078493048152526848)

### suspected (base_moved) at `54f1a2337f66`
- **FAIL** 2026-07-19T21:54:33+00:00 · build `2078924338689478656` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1770/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078924338689478656)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'WorkloadsReady', 'Ready'}, got [{'lastTransitionTime': '2026-07-19T20:29:58Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-20T15:54:50+00:00 · build `2079207692374642688` · branch `master` · base `dfa3f25d8c42` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1770/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079207692374642688)

### suspected (base_moved) at `0099d125f5c3`
- **FAIL** 2026-07-18T22:49:32+00:00 · build `2078581108336758784` · branch `master` · base `0e1cac589c72` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078581108336758784)
  - `AssertionError: Missing true conditions: {'Ready', 'RouterReady'}, expected {'WorkloadsReady', 'Ready', 'RouterReady'}, got [{'lastTransitionTime': '2026-07-18T21:24:02Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-20T21:21:02+00:00 · build `2079290817322684416` · branch `master` · base `71dd0b64b348` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1759/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079290817322684416)

### suspected (base_moved) at `7056d674e121`
- **FAIL** 2026-07-18T13:57:09+00:00 · build `2078441177786355712` · branch `master` · base `afbee690bd11` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2078441177786355712)
  - `AssertionError: Missing true conditions: {'RouterReady', 'Ready'}, expected {'RouterReady', 'WorkloadsReady', 'Ready'}, got [{'lastTransitionTime': '2026-07-18T12:31:35Z', 'message': 'Managed HTTPRout`
- **PASS** 2026-07-22T09:31:44+00:00 · build `2079837164643815424` · branch `master` · base `5daeea6f120a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1766/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079837164643815424)
