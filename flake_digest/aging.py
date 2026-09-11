"""Window aging: prune state to a rolling window and recompute what the
pruning touched. Nothing here is lost for good; every prior snapshot of
the state file lives in git history, which has been the durable record
since day one.

Two floors, and the distinction is the one real trap in this module.
The DATA floor (window_days) decides what the tracker displays. The
IDEMPOTENCY floor sits further back, past the listing window and its
pad: processed_builds is the guard against refolding whatever the
directory listing can still see, so pruning it to the data floor would
let boundary builds refold and double-count. Everything else prunes at
the data floor; build_timings gets its own longer retention because
runtime trends want more history than flake counts.
"""
from flake_digest.gcs_source import build_id_unix_ms, min_build_id_for
from flake_digest.model import FlakeRecord
from flake_digest.runner import WINDOW_PAD_DAYS

# extra margin behind the listing window before an idempotency entry may
# be forgotten; over-remembering is free, under-remembering double-counts
IDEMPOTENCY_MARGIN_DAYS = 2

_DAY_MS = 86_400_000


def _key_unix_ms(build_key: str) -> int | None:
    tail = build_key.rsplit(":", 1)[-1]
    return build_id_unix_ms(int(tail)) if tail.isdigit() else None


def _occurrence_ts(occ: dict) -> str:
    return max(filter(None, (occ["fail"]["timestamp"],
                             occ["pass"]["timestamp"])), default="")


def _floor_iso(now_ms: int, window_days: int) -> str:
    from datetime import datetime, timezone
    return datetime.fromtimestamp(
        (now_ms - window_days * _DAY_MS) / 1000, tz=timezone.utc).isoformat()


def prune(state: dict, now_ms: int, window_days: int,
          timings_retention_days: int) -> dict:
    """Prune in place; returns a summary of what aged out. Safe to run
    twice: the second pass finds nothing."""
    data_floor_iso = _floor_iso(now_ms, window_days)
    idem_floor_ms = now_ms - (window_days + WINDOW_PAD_DAYS
                              + IDEMPOTENCY_MARGIN_DAYS) * _DAY_MS
    timings_floor_ms = now_ms - timings_retention_days * _DAY_MS
    summary = {"builds": 0, "timings": 0, "sha_entries": 0,
               "occurrences": 0, "records": 0}

    for key in list(state["processed_builds"]):
        ms = _key_unix_ms(key)
        if ms is not None and ms < idem_floor_ms:
            del state["processed_builds"][key]
            summary["builds"] += 1

    for key in list(state["build_timings"]):
        ms = _key_unix_ms(key)
        if ms is not None and ms < timings_floor_ms:
            del state["build_timings"][key]
            summary["timings"] += 1

    for key, entry in list(state["sha_index"].items()):
        newest = max((obs["timestamp"] for obs in
                      (entry.get("pass"), entry.get("fail"))
                      if obs and obs.get("timestamp")), default="")
        if newest and newest < data_floor_iso:
            del state["sha_index"][key]
            summary["sha_entries"] += 1

    for key, rec in list(state["flakes"].items()):
        keep = [o for o in rec["occurrences"]
                if _occurrence_ts(o) >= data_floor_iso]
        aged = len(rec["occurrences"]) - len(keep)
        if not aged:
            continue
        summary["occurrences"] += aged
        if not keep:
            del state["flakes"][key]
            summary["records"] += 1
            continue
        state["flakes"][key] = _recompute(rec, keep)
    return summary


def _recompute(rec: dict, occurrences: list[dict]) -> dict:
    """Rebuild a record's aggregates purely from its remaining
    occurrences; first_seen_ever alone is exempt from the window."""
    times = sorted(_occurrence_ts(o) for o in occurrences)
    fresh = FlakeRecord(origin=rec["origin"], repo=rec["repo"],
                        job=rec["job"], nodeid=rec["nodeid"]).to_dict()
    fresh["confirmed_count"] = sum(
        o["classification"] == "confirmed" for o in occurrences)
    fresh["suspected_count"] = sum(
        o["classification"] == "suspected" for o in occurrences)
    fresh["shas_flaked"] = [o["sha"] for o in occurrences]
    fresh["first_seen"] = times[0]
    fresh["last_seen"] = times[-1]
    fresh["first_seen_ever"] = (rec.get("first_seen_ever")
                                or rec.get("first_seen"))
    fresh["last_failure_url"] = occurrences[-1]["fail"]["url"]
    fresh["occurrences"] = occurrences
    return fresh


def window_runs(state: dict, now_ms: int, window_days: int) -> tuple[dict, dict, bool]:
    """(runs per job_key, discarded per job_key, derived) for the window.

    Derived from the ledger when every in-window entry carries the v4
    shape; if any pre-v4 bare-true entry is still inside the window the
    ledger can't answer and the caller falls back to the legacy
    since-bootstrap counters. That fallback retires itself: the old
    entries age past the floor within one window of the v4 ship."""
    floor_ms = now_ms - window_days * _DAY_MS
    runs: dict[str, int] = {}
    discarded: dict[str, int] = {}
    for key, value in state["processed_builds"].items():
        ms = _key_unix_ms(key)
        if ms is None or ms < floor_ms:
            continue
        if not isinstance(value, dict):
            return state["job_runs"], state["discarded"], False
        # key shape: origin:repo:job:build_id, repo carries a "/"
        origin_repo, job, _ = key.rsplit(":", 2)
        origin, repo = origin_repo.split(":", 1)
        job_key = f"{origin}|{repo}|{job}"
        if value.get("run"):
            runs[job_key] = runs.get(job_key, 0) + 1
        if value.get("discarded"):
            discarded[job_key] = discarded.get(job_key, 0) + 1
    return runs, discarded, True
