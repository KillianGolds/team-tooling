`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_late_join`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 3 · **Suspected:** 2
**First seen:** 2026-07-23T10:45:30+00:00 · **Last seen:** 2026-08-23T12:14:39+00:00

### suspected (base_moved) at `8c8d651344da`
- **FAIL** 2026-07-21T23:44:50+00:00 · build `2079685052370784256` · branch `master` · base `ce59139e454f` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1757/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2079685052370784256)
  - `AssertionError: late-join: error rate 0.8% exceeds 0.0%`
- **PASS** 2026-07-23T10:45:30+00:00 · build `2080218582658060288` · branch `master` · base `8397970c6400` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1791/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2080218582658060288)

### suspected (base_moved) at `c78d978f49c3`
- **FAIL** 2026-07-30T02:21:37+00:00 · build `2082624433679241216` · branch `master` · base `dd8f478dbbf4` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1803/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082624433679241216)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-07-28T16:21:31+00:00 · build `2082106778211848192` · branch `master` · base `b62b4c92b12e` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1803/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2082106778211848192)

### confirmed (same_base) at `3f67f660b9c6`
- **FAIL** 2026-08-13T17:09:12+00:00 · build `2087921808643723264` · branch `master` · base `11e8b1666c1a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1873/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2087921808643723264)
  - `AssertionError: late-join: error rate 0.8% exceeds 0.0%`
- **PASS** 2026-08-13T18:42:02+00:00 · build `2087950233714561024` · branch `master` · base `11e8b1666c1a` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1873/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2087950233714561024)

### confirmed (same_base) at `a44277a09bee`
- **FAIL** 2026-08-20T15:01:21+00:00 · build `2090424567238496256` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090424567238496256)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-08-20T18:23:04+00:00 · build `2090483028374589440` · branch `release-v0.17` · base `147768f4c932` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2090483028374589440)

### confirmed (same_base) at `8665cd94c538`
- **FAIL** 2026-08-23T08:58:02+00:00 · build `2091424294914494464` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091424294914494464)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-08-23T12:14:39+00:00 · build `2091475409479667712` · branch `master` · base `3cf0a0416662` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1910/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2091475409479667712)
