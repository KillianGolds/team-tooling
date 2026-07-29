`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_decommission`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 0 · **Suspected:** 1 · **Runs seen:** 370
**First seen:** 2026-07-23T21:10:26+00:00 · **Last seen:** 2026-07-23T21:10:26+00:00

### suspected (base_moved) at `b2d6323b6248`
- **FAIL** 2026-07-23T21:10:26+00:00 · build `2080366412781588480` · branch `master` · base `ff189f41ff17` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080366412781588480)
  - `AssertionError: decommission: zero errors including transition: error rate 19.0% exceeds 0.0%`
- **PASS** 2026-07-23T18:18:14+00:00 · build `2080322438645682176` · branch `master` · base `b8bba71fe280` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1730/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080322438645682176)
