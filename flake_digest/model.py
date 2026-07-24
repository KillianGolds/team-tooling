"""Core data types for flake tracking.

Run identity (origin, repo, job, sha, build) always comes from the
fetcher that downloaded the artifact, never from inside the results
file. The file can't be trusted for it: `environment` is empty on both
lines and `created` has no timezone.

origin is the CI substrate (midstream Prow vs upstream GHA); repo is the
source repository. Kept separate because odh-model-controller is coming,
and it shares the substrate but not the repo.
"""
from dataclasses import dataclass, field


# skipped/xfailed/xpassed are neutral: they sit on neither side of a
# fail/pass pair
PASS_OUTCOMES = frozenset({"passed"})
NON_PASS_OUTCOMES = frozenset({"failed", "error"})
NEUTRAL_OUTCOMES = frozenset({"skipped", "xfailed", "xpassed"})

# nodeid used for job-level rows, which come from finished.json and have
# no per-test data
JOB_LEVEL_NODEID = "<job-level>"


@dataclass(frozen=True)
class RunMeta:
    """Identity of one CI build/artifact, supplied by the fetcher.

    origin: "midstream" | "upstream"
    repo: source repository, e.g. "opendatahub-io/kserve"
    job: the normalized job key (e2e-predictor), stable across branch
         renames. The full CI job name travels on the evidence instead.
    build_id: idempotency component; Prow build id, GHA "{run_id}:{attempt}".
    url: safe-to-render link (Prow /view/gs/... or an actions run URL);
         never a PR URL.
    timestamp: ISO 8601 from the CI system, never from file contents.
    """
    origin: str
    repo: str
    job: str
    sha: str
    build_id: str
    url: str
    timestamp: str


@dataclass(frozen=True)
class TestResult:
    """One test's outcome in one build.

    truncated is run-level: the producing run aborted early (--maxfail), so
    nodeids absent from that run are UNKNOWN, and absence-based logic must
    never read them as passes.
    """
    run: RunMeta
    nodeid: str
    outcome: str
    duration: float | None = None
    failure_message: str | None = None
    truncated: bool = False

    @property
    def is_pass(self) -> bool:
        return self.outcome in PASS_OUTCOMES

    @property
    def is_non_pass(self) -> bool:
        return self.outcome in NON_PASS_OUTCOMES

    @property
    def is_neutral(self) -> bool:
        return not self.is_pass and not self.is_non_pass


@dataclass
class FlakeRecord:
    """Accumulated flake history for one (origin, repo, job, nodeid).

    confirmed and suspected counts never get summed together. What earns
    confirmed is the origin classifier's call (for Prow: results files on
    both sides, head SHA verified two ways, base didn't move); anything
    weaker lands in suspected with a tag saying why.

    occurrences keeps one evidence bundle per counted sha: both build ids
    and urls, both outcomes, timestamps, branch and full job name per
    side, the failure message, and the classification tag.
    """
    origin: str
    repo: str
    job: str
    nodeid: str
    confirmed_count: int = 0
    suspected_count: int = 0
    runs: int = 0
    shas_flaked: list[str] = field(default_factory=list)
    first_seen: str | None = None
    last_seen: str | None = None
    last_failure_url: str | None = None
    occurrences: list[dict] = field(default_factory=list)

    @property
    def key(self) -> str:
        return f"{self.origin}|{self.repo}|{self.job}|{self.nodeid}"

    @property
    def is_job_level(self) -> bool:
        return self.nodeid == JOB_LEVEL_NODEID

    def to_dict(self) -> dict:
        return {
            "origin": self.origin,
            "repo": self.repo,
            "job": self.job,
            "nodeid": self.nodeid,
            "confirmed_count": self.confirmed_count,
            "suspected_count": self.suspected_count,
            "runs": self.runs,
            "shas_flaked": self.shas_flaked,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "last_failure_url": self.last_failure_url,
            "occurrences": self.occurrences,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "FlakeRecord":
        return cls(
            origin=d["origin"],
            repo=d["repo"],
            job=d["job"],
            nodeid=d["nodeid"],
            confirmed_count=d.get("confirmed_count", 0),
            suspected_count=d.get("suspected_count", 0),
            runs=d.get("runs", 0),
            shas_flaked=list(d.get("shas_flaked", [])),
            first_seen=d.get("first_seen"),
            last_seen=d.get("last_seen"),
            last_failure_url=d.get("last_failure_url"),
            occurrences=list(d.get("occurrences", [])),
        )
