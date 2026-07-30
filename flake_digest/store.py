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

SCHEMA_VERSION = 2


def _schema() -> dict:
    return {
        "version": SCHEMA_VERSION,
        "keys": {
            "flakes": "origin|repo|job|nodeid; job is the normalized target"
                      " (e.g. e2e-predictor), stable across branch renames",
            "sha_index": "origin|repo|job|nodeid|sha",
            "job_runs": "origin|repo|job (completed-build denominator)",
            "discarded": "origin|repo|job (unclassifiable builds)",
            "build_timings": "same key as processed_builds; one entry per"
                             " results-bearing build since schema v2:"
                             " tests_total_s (summed test durations across"
                             " invocation files), test_count, wall_clock_s"
                             " (finished minus started), result, truncated"
                             " (pytest stopped early; total not comparable"
                             " to complete runs), files_parsed/"
                             "files_expected (partial fetch detection)."
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


def mark_processed(state: dict, build_key: str) -> None:
    state["processed_builds"][build_key] = True
