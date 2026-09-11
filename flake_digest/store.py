"""Committed state file for flake tracking; git history is the audit trail.

State shape (the `_schema` block inside the file restates this for
outside readers, since the committed JSON is a public interface):

    {
      "_schema": {version, keys, classes},
      "processed_builds": {"<idempotency key>": true, ...},
      "job_runs": {"<origin>|<repo>|<job>": <int>, ...},
      "discarded": {"<origin>|<repo>|<job>": <int>, ...},
      "sha_index": {"<origin>|<repo>|<job>|<nodeid>|<sha>":
                        {pass: <obs|null>, fail: <obs|null>, counted}, ...},
      "flakes": {"<origin>|<repo>|<job>|<nodeid>": <FlakeRecord dict>, ...},
      "build_timings": {"<processed_builds key>": <timing dict>, ...}
    }

`job` in every key is the normalized target (e2e-predictor), not the
branch-embedding Prow job name. Bump SCHEMA_VERSION whenever the shape
changes.

sha_index is what makes pairing work across incremental cron runs: the
failing build may have been processed weeks before the passing one shows
up. Each side keeps its latest observation (build id, url, timestamp,
base sha, evidence flags) so the completed pair carries full evidence;
`counted` stops a sha from being counted as more than one occurrence.
`discarded` counts builds whose two head-SHA sources disagreed.

The `runs` field inside stored FlakeRecords stays 0; the per-job
denominator lives in job_runs and gets joined in at render time.
"""
import json
from pathlib import Path

DEFAULT_STATE_PATH = Path(__file__).resolve().parent / "state" / "flakes_state.json"

SCHEMA_VERSION = 4


def _schema() -> dict:
    return {
        "version": SCHEMA_VERSION,
        "window": "state is a rolling window since v4: occurrences,"
                  " sha_index entries and processed builds older than the"
                  " window are pruned each run (git history of this file"
                  " keeps every prior snapshot). FlakeRecord counts cover"
                  " the window; first_seen_ever survives pruning.",
        "keys": {
            "flakes": "origin|repo|job|nodeid; job is the normalized target"
                      " (e.g. e2e-predictor), stable across branch renames",
            "sha_index": "origin|repo|job|nodeid|sha",
            "processed_builds": "idempotency ledger; values since v4 are"
                                " {run, discarded, result} so windowed"
                                " per-job denominators derive from it"
                                " (pre-v4 values are bare true: unknown)",
            "job_runs": "origin|repo|job; legacy since-bootstrap counters,"
                        " read only while pre-v4 ledger entries remain in"
                        " the window, then removable",
            "discarded": "origin|repo|job (unclassifiable builds; same"
                         " legacy status as job_runs)",
            "build_timings": "same key as processed_builds; one entry per"
                             " completed build that had parsed results or"
                             " a measured test phase (results-bearing only"
                             " before schema v3): tests_total_s (summed"
                             " test durations across invocation files),"
                             " test_count, wall_clock_s (finished minus"
                             " started), result, truncated (pytest stopped"
                             " early; total not comparable to complete"
                             " runs), files_parsed/files_expected (partial"
                             " fetch detection), test_phase_s (ci-operator"
                             " test-phase elapsed from junit_operator.xml,"
                             " the number the 2h step timeout applies to;"
                             " since v3). Phase-only entries exist for"
                             " builds without result files (kserve-module,"
                             " timeout-killed builds); their pytest fields"
                             " are null, meaning no data, not zero."
                             " Filters like successes-only are the"
                             " reader's job; nothing is filtered at write.",
        },
        "classes": "confirmed = both sides of the same-head-SHA rerun pair"
                   " carry full evidence under the origin's rule (results"
                   " files present, head SHA verified by two sources, no"
                   " environment drift such as a moved base); suspected ="
                   " same head SHA but weaker evidence. Never summed.",
    }


def empty_state() -> dict:
    return {"_schema": _schema(), "processed_builds": {}, "job_runs": {},
            "discarded": {}, "sha_index": {}, "flakes": {},
            "build_timings": {}}


def load_state(path: Path | None = None) -> dict:
    path = path or DEFAULT_STATE_PATH
    if not Path(path).exists():
        return empty_state()
    state = json.loads(Path(path).read_text())
    for key, default in empty_state().items():
        state.setdefault(key, default)
    state["_schema"] = _schema()  # always current writer's description
    return state


def save_state(state: dict, path: Path | None = None) -> None:
    path = Path(path or DEFAULT_STATE_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    # sorted keys so the committed file diffs stably run-to-run
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def is_processed(state: dict, build_key: str) -> bool:
    return build_key in state["processed_builds"]


def mark_processed(state: dict, build_key: str, *, run: bool = False,
                   discarded: bool = False, result: str | None = None) -> None:
    """Since schema v4 the ledger value records what each build was, so
    per-job denominators can be recomputed for any window instead of
    living in irreversible counters. Pre-v4 entries are a bare `true`:
    membership still answers idempotency, but their run-ness is unknown,
    which is why the windowed denominators fall back to the legacy
    counters until every in-window entry carries the new shape."""
    state["processed_builds"][build_key] = {
        "run": run, "discarded": discarded, "result": result}
