"""Parse pytest-json-report output (e2e_results.json) into TestResults.

Both CI lines produce these files with the same stack (pytest 7.4.4,
pytest-json-report 1.5.0, xdist 3.6.1), run with --maxfail and -m
selection. Every rule below traces back to a quirk found in real
artifacts, so don't simplify them away without re-checking:

Skips have no `call` key at all. Fixture errors put their crash under
`setup`, also with no `call`. Key on `call` and you silently drop both,
and fixture errors turned out to be a big share of the flakes. That's
why classification reads only the top-level `outcome`.

longrepr tells you nothing about pass/fail. Under xdist every phase of a
passing test carries a "[gwN]" worker banner there; sequential (-n 0)
runs leave it out entirely.

If collected - deselected > total, the run hit --maxfail and stopped
early. Tests missing from such a file never ran, and their absence is
unknown, not a pass, so the whole run gets marked truncated.

`environment` comes back {} (pytest-metadata version mismatch) and
`created` is a wall clock with no timezone. Run identity and timing have
to come from the fetcher's RunMeta, never from inside the file.
"""
import json

from flake_digest.model import RunMeta, TestResult


def parse_e2e_results(raw: bytes | str, run: RunMeta) -> list[TestResult]:
    """Parse one e2e_results.json into TestResults tagged with `run`.

    Malformed JSON raises json.JSONDecodeError: a corrupt artifact is an
    infra signal the caller should classify, not an empty run.
    """
    report = json.loads(raw)
    truncated = is_truncated(report.get("summary", {}))
    return [
        _parse_test(entry, run, truncated)
        for entry in report.get("tests", [])
    ]


def is_truncated(summary: dict) -> bool:
    """True when the run stopped early (--maxfail): fewer results reported
    than tests selected to run."""
    collected = summary.get("collected", 0)
    deselected = summary.get("deselected", 0)
    total = summary.get("total", 0)
    return collected - deselected > total


def _parse_test(entry: dict, run: RunMeta, truncated: bool) -> TestResult:
    call = entry.get("call")
    setup = entry.get("setup")
    return TestResult(
        run=run,
        nodeid=entry["nodeid"],
        outcome=entry["outcome"],
        duration=_duration(call, setup),
        failure_message=_failure_message(call, setup),
        truncated=truncated,
    )


def _duration(call: dict | None, setup: dict | None) -> float | None:
    # skips and fixture errors have no call phase; setup is what ran
    if call is not None and "duration" in call:
        return call["duration"]
    if setup is not None:
        return setup.get("duration")
    return None


def _failure_message(call: dict | None, setup: dict | None) -> str | None:
    # test failures crash under call, fixture errors under setup
    for phase in (call, setup):
        if phase and "crash" in phase:
            return phase["crash"].get("message")
    return None
