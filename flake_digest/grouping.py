"""Incident grouping: a render-time view over occurrences, never a mutation.

Stage 1 is structural only. Two rules:

- Parametrization collapse: occurrences from the same test function
  (nodeid minus the [param] suffix), same job, sharing the same fail/pass
  build pair, are one incident. Same-function-different-params on one
  build pair is structurally near-certain to be one event.
- Wave collapse, job-level only: fail sides from the same PR, triggered
  within a tight window (their snowflake build ids decode to trigger
  times; the real five-job wave this was tuned on sat ~30ms apart), and
  sharing a no_results_reason. Cross-function or cross-PR merging is
  deliberately NOT done here: without message evidence, two functions
  failing in one build might be one cause or two flakes co-occurring,
  and a false merge hides a real distinct problem while a false split is
  only cosmetic. Stage 2's fingerprints earn those merges with evidence.

Near-miss declines get logged: same PR and reason but outside the
window, or same window and reason but different PRs. Those logs are the
corpus for judging the window tuning and for what stage 2 has waiting.

Nothing here reads or writes state beyond occurrences; a grouping bug is
fixed by re-rendering.
"""
from flake_digest.gcs_source import build_id_unix_ms
from flake_digest.model import JOB_LEVEL_NODEID

WAVE_WINDOW_SECONDS = 120


def base_function(nodeid: str) -> str:
    return nodeid.split("[", 1)[0]


def pr_from_url(url: str) -> int | None:
    # .../pr-logs/pull/<repo_slug>/<pr>/... — internal grouping key only,
    # never rendered anywhere
    parts = url.split("/")
    try:
        return int(parts[parts.index("pull") + 2])
    except (ValueError, IndexError):
        return None


def _occurrence_time_s(occ: dict) -> float | None:
    bid = occ["fail"]["build_id"]
    return build_id_unix_ms(int(bid)) / 1000 if bid.isdigit() else None


def compute_incidents(state: dict, log=lambda msg: None):
    """(incidents, singleton_items). Each item is {key, rec, occ}; each
    incident carries separate confirmed/suspected counts, member record
    keys and pages, and a content-derived label so identity is stable
    across renders."""
    test_items, job_items = [], []
    for key, rec in state["flakes"].items():
        for occ in rec["occurrences"]:
            item = {"key": key, "rec": rec, "occ": occ}
            (job_items if rec["nodeid"] == JOB_LEVEL_NODEID
             else test_items).append(item)

    incidents, used = [], set()

    # rule 1: parametrization collapse
    groups = {}
    for it in test_items:
        rec, occ = it["rec"], it["occ"]
        gk = (rec["origin"], rec["repo"], rec["job"],
              base_function(rec["nodeid"]),
              occ["fail"]["build_id"], occ["pass"]["build_id"])
        groups.setdefault(gk, []).append(it)
    for (origin, repo, job, func, *_), members in sorted(groups.items()):
        if len(members) < 2:
            continue
        incidents.append(_incident(
            kind="params",
            label=f"{func.rsplit('/', 1)[-1]} ({len(members)} parametrizations)",
            jobs=[job], members=members,
            sha=members[0]["occ"]["sha"]))
        used.update(id(m) for m in members)

    # rule 2: job-level waves, with near-miss decline logging
    by_pr_reason = {}
    for it in job_items:
        pr = pr_from_url(it["occ"]["fail"]["url"])
        reason = it["occ"]["fail"].get("no_results_reason")
        t = _occurrence_time_s(it["occ"])
        if pr is None or reason is None or t is None:
            continue
        by_pr_reason.setdefault((pr, reason), []).append((t, it))

    clustered = []  # (pr, reason, start_t, members) for the cross-PR check
    for (pr, reason), timed in sorted(by_pr_reason.items()):
        timed.sort(key=lambda x: x[0])
        cluster = [timed[0]]
        for entry in timed[1:]:
            if entry[0] - cluster[0][0] <= WAVE_WINDOW_SECONDS:
                cluster.append(entry)
            else:
                gap = entry[0] - cluster[0][0]
                log(f"wave near-miss: two fail groups share a PR and "
                    f"reason ({reason}) but sit {gap:.0f}s apart, outside "
                    f"the {WAVE_WINDOW_SECONDS}s window; not merged")
                clustered.append((pr, reason, cluster))
                cluster = [entry]
        clustered.append((pr, reason, cluster))

    for pr, reason, cluster in clustered:
        members = [it for _, it in cluster]
        if len(members) < 2:
            continue
        jobs = sorted({m["rec"]["job"] for m in members})
        incidents.append(_incident(
            kind="wave",
            label=f"{len(jobs)}-job wave, {reason}",
            jobs=jobs, members=members, reason=reason))
        used.update(id(m) for m in members)

    # cross-PR near-miss: same reason, overlapping window, different PRs
    for i, (pr_a, reason_a, ca) in enumerate(clustered):
        for pr_b, reason_b, cb in clustered[i + 1:]:
            if (pr_a != pr_b and reason_a == reason_b
                    and abs(ca[0][0] - cb[0][0]) <= WAVE_WINDOW_SECONDS):
                log(f"wave near-miss: fail groups from two different PRs "
                    f"share reason ({reason_a}) inside one window; not "
                    f"merged (cross-PR needs stage-2 evidence)")

    singletons = [it for it in test_items + job_items if id(it) not in used]
    return incidents, singletons


def _incident(*, kind, label, jobs, members, sha=None, reason=None):
    occs = [m["occ"] for m in members]
    times = sorted(t for o in occs
                   for t in (o["fail"]["timestamp"], o["pass"]["timestamp"])
                   if t)
    return {
        "kind": kind,
        "label": label,
        "jobs": jobs,
        "record_keys": sorted({m["key"] for m in members}),
        "confirmed": sum(o["classification"] == "confirmed" for o in occs),
        "suspected": sum(o["classification"] == "suspected" for o in occs),
        "first_seen": times[0] if times else None,
        "last_seen": times[-1] if times else None,
        "sha": sha,
        "reason": reason,
    }
