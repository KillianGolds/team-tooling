`llmisvc/test_llm_canary_lifecycle.py::TestCanaryLifecycle::test_late_join`

**Job:** e2e-llm-inference-service · **Repo:** opendatahub-io/kserve (midstream)
**Confirmed:** 6 · **Suspected:** 0
**First seen:** 2026-08-13T18:42:02+00:00 · **Last seen:** 2026-09-11T21:39:25+00:00 · **Tracking since:** 2026-07-23T10:45:30+00:00

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

### confirmed (same_base) at `dfb3fd0aa3e5`
- **FAIL** 2026-08-25T13:09:35+00:00 · build `2092210654617276416` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092210654617276416)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-08-25T16:47:09+00:00 · build `2092261395939725312` · branch `release-v0.17` · base `97dac48d95ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1905/pull-ci-opendatahub-io-kserve-release-v0.17-e2e-llm-inference-service/2092261395939725312)

### confirmed (same_base) at `5ef0c7095395`
- **FAIL** 2026-09-01T22:29:00+00:00 · build `2094885324776804352` · branch `master` · base `606d130e70ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2094885324776804352)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-09-02T00:45:32+00:00 · build `2094922054145937408` · branch `master` · base `606d130e70ad` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1904/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2094922054145937408)

### confirmed (same_base) at `9447f454698d`
- **FAIL** 2026-09-11T19:32:49+00:00 · build `2098467276784144384` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098467276784144384)
  - `AssertionError: v2 received no traffic after join (40 total)`
- **PASS** 2026-09-11T21:39:25+00:00 · build `2098495862442299392` · branch `master` · base `b2435fe1ae99` · [prow](https://prow.ci.openshift.org/view/gs/test-platform-results/pr-logs/pull/opendatahub-io_kserve/1869/pull-ci-opendatahub-io-kserve-master-e2e-llm-inference-service/2098495862442299392)
