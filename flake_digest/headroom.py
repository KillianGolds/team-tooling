"""Runtime headroom: how close each job's test phase runs to the step
ceiling, computed from the build_timings retained since schema v3.

The number that matters is test_phase_s against the 2h per-step timeout,
because that timeout kills a job mid-run and shows up here as a timeout
failure rather than a slow success. Healthy-runtime stats come from
successful builds only: a failed build's phase is either cut short or
the ceiling itself, and neither says what a normal run needs. Builds
whose phase reached the ceiling are counted separately, whatever their
result, since a multi-step phase can legitimately pass 2h without any
single step hitting its limit.

One honest caveat baked into the rendering too: the phase spans every
step in the test block, not just the pytest container, so these numbers
read slightly high. The error is in the safe direction for a headroom
check.
"""
import math

# the aging module owns build-key time decoding; reusing its private
# helper beats a second copy drifting out of sync
from flake_digest.aging import _key_unix_ms, job_key_of

# openshift/release default per-step timeout, verified 2026-09 for the
# kserve e2e steps (the job-level timeout is 4h and never the binding
# constraint here)
STEP_CEILING_S = 7200

# p90 within 25 percent of the ceiling is where the warning line starts
WARN_FRACTION = 0.75

# medians from fewer builds than this on either side say nothing about
# creep, so the trend cell stays empty instead of jittering
MIN_TREND_SAMPLES = 5

_DAY_MS = 86_400_000


def _percentile(sorted_vals: list[float], q: int) -> float | None:
    """Nearest-rank percentile; exact enough for dozens of samples and
    has no interpolation surprises at small n."""
    if not sorted_vals:
        return None
    k = max(0, math.ceil(q / 100 * len(sorted_vals)) - 1)
    return sorted_vals[k]


def compute_headroom(state: dict, now_ms: int,
                     recent_days: int = 14) -> dict[str, dict]:
    """Per job key: phase stats for the recent window plus a median
    trend against the window before it.

    {"successes", "median_s", "p90_s", "max_s", "at_ceiling", "trend_s"}
    per job; at_ceiling counts completed builds of any result whose
    phase reached STEP_CEILING_S inside the recent window. Jobs appear
    when they have any phase-bearing timing in either window, so a job
    that stopped succeeding entirely still shows a row (with empty
    stats) rather than vanishing from the one table about risk.
    """
    recent_floor = now_ms - recent_days * _DAY_MS
    prior_floor = now_ms - 2 * recent_days * _DAY_MS
    jobs: dict[str, dict] = {}
    for key, timing in state["build_timings"].items():
        phase = timing.get("test_phase_s")
        ms = _key_unix_ms(key)
        if phase is None or ms is None or ms < prior_floor:
            continue
        j = jobs.setdefault(job_key_of(key),
                            {"recent": [], "prior": [], "at_ceiling": 0})
        recent = ms >= recent_floor
        if timing.get("result") == "SUCCESS":
            (j["recent"] if recent else j["prior"]).append(phase)
        if recent and phase >= STEP_CEILING_S:
            j["at_ceiling"] += 1

    out: dict[str, dict] = {}
    for job_key, j in jobs.items():
        rec = sorted(j["recent"])
        pri = sorted(j["prior"])
        row = {
            "successes": len(rec),
            "median_s": _percentile(rec, 50),
            "p90_s": _percentile(rec, 90),
            "max_s": rec[-1] if rec else None,
            "at_ceiling": j["at_ceiling"],
            "trend_s": None,
        }
        if len(rec) >= MIN_TREND_SAMPLES and len(pri) >= MIN_TREND_SAMPLES:
            row["trend_s"] = _percentile(rec, 50) - _percentile(pri, 50)
        out[job_key] = row
    return out


def thin_headroom(stats: dict[str, dict]) -> list[str]:
    """Job keys whose p90 crossed the warning line or that already
    reached the ceiling this window, worst first."""
    flagged = [
        (job_key, row) for job_key, row in stats.items()
        if (row["p90_s"] or 0) >= STEP_CEILING_S * WARN_FRACTION
        or row["at_ceiling"]
    ]
    flagged.sort(key=lambda kv: -(kv[1]["p90_s"] or 0))
    return [job_key for job_key, _ in flagged]
