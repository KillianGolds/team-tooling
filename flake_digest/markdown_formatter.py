"""Render flake state as the pinned issue body and per-test report pages.

Suspected is the primary ranked table on midstream, not confirmed. Nearly
every rerun pair sits hours apart, master moves in between, and the pair
gets tagged base_moved; demanding confirmed would hide almost everything,
including hand-verified real flakes. So the issue leads with suspected
under a clear caveat and shows confirmed as the gold-standard subset.

Cross-reference silence is enforced here at the rendering boundary:
ensure_render_safe runs on the issue body and every report page before
anything is written. PR numbers live in internal state only.
"""
import hashlib
import re

from flake_digest.model import JOB_LEVEL_NODEID

TOP_TEST_ROWS = 20

# GitHub fires an unretractable cross-ref notification onto a PR the
# moment "#123" or a .../pull/123 link renders anywhere. Prow links are
# safe even though their path contains "pull/": the repo slug sits
# between "pull/" and the number (pr-logs/pull/opendatahub-io_kserve/1613),
# so `pull/` followed directly by a digit only ever matches GitHub-style
# PR URLs.
_CROSS_REF_PATTERNS = (re.compile(r"#\d"), re.compile(r"pull/\d"))
MAX_BODY_CHARS = 50_000  # GitHub caps at 65,536; fail loudly well before


def ensure_render_safe(text: str, where: str, max_chars: int = MAX_BODY_CHARS) -> None:
    for pattern in _CROSS_REF_PATTERNS:
        m = pattern.search(text)
        if m:
            start = max(0, m.start() - 60)
            raise ValueError(
                f"{where}: cross-reference risk {m.group()!r} near: "
                f"...{text[start:m.end() + 20]!r}")
    if len(text) > max_chars:
        raise ValueError(f"{where}: {len(text)} chars exceeds {max_chars}")


def report_filename(rec: dict) -> str:
    """Collision-free page name for one record.

    Nodeids differ in ways a slug flattens (brackets, ::, parametrization
    punctuation), and a collision would mean one test's evidence silently
    overwrites another's every run. The short hash of the full record key
    is what actually guarantees uniqueness; the slug is just for humans.
    """
    key = f"{rec['origin']}|{rec['repo']}|{rec['job']}|{rec['nodeid']}"
    slug = re.sub(r"[^a-z0-9]+", "-",
                  f"{rec['job']}-{rec['nodeid']}".lower()).strip("-")[:60].rstrip("-")
    return f"{slug}-{hashlib.sha1(key.encode()).hexdigest()[:8]}.md"


def render_report_page(rec: dict, runs: int, discarded: int) -> str:
    """Full evidence for one flaky test (or one job-level row)."""
    lines = [f"`{rec['nodeid']}`", ""]
    lines += [
        f"**Job:** {rec['job']} · **Repo:** {rec['repo']} ({rec['origin']})",
        f"**Confirmed:** {rec['confirmed_count']} · "
        f"**Suspected:** {rec['suspected_count']} · "
        f"**Runs seen:** {runs}"
        + (f" · **Discarded builds:** {discarded}" if discarded else ""),
        f"**First seen:** {rec['first_seen']} · **Last seen:** {rec['last_seen']}",
        "",
    ]
    for occ in rec["occurrences"]:
        lines.append(f"### {occ['classification']} ({occ['tag']}) at `{occ['sha'][:12]}`")
        for side in ("fail", "pass"):
            s = occ[side]
            base = f" · base `{s['base_sha'][:12]}`" if s.get("base_sha") else ""
            lines.append(f"- **{side.upper()}** {s['timestamp']} · "
                         f"build `{s['build_id']}` · branch `{s['branch']}`"
                         f"{base} · [prow]({s['url']})")
            if side == "fail":
                if s.get("no_results_reason"):
                    lines.append(f"  - no results file: {s['no_results_reason']}")
                if s.get("failure_message"):
                    first = s["failure_message"].splitlines()[0]
                    lines.append(f"  - `{first[:200]}`")
        lines.append("")
    return "\n".join(lines)


def render_issue_body(state: dict, cfg: dict, now_iso: str) -> str:
    reports_base = f"https://github.com/{cfg['issue']['repo']}/blob/main/reports/"
    flakes = list(state["flakes"].values())
    test_rows = [r for r in flakes if r["nodeid"] != JOB_LEVEL_NODEID]
    # confirmed leads the ranking; sorting by the sum would let the
    # noisier suspected signal set the order over the gold standard
    test_rows.sort(key=lambda r: (-r["confirmed_count"], -r["suspected_count"]))
    confirmed_rows = sorted((r for r in flakes if r["confirmed_count"]),
                            key=lambda r: -r["confirmed_count"])

    out = [
        "## KServe e2e flake tracker (midstream)",
        "",
        f"_Last updated {now_iso}. All data is presubmit; there is no clean "
        "scheduled baseline._",
        "",
        "**How to read this.** A row counts occurrences where the same test "
        "both failed and passed at the same PR head commit across rerun "
        "pairs. These are flakes observed among same-commit reruns, not "
        "flake rates. Most pairs are **suspected**: reruns usually happen "
        "hours apart and the target branch moves in between (tagged "
        "`base_moved`), so a branch-side fix or break can't be ruled out. "
        "**Confirmed** means the branch base matched too and both builds "
        "carry full evidence; it's the gold standard, and rare on presubmit "
        "data. The two counts are never summed.",
        "",
        "### Flaky tests (ranked, suspected + confirmed shown separately)",
        "",
        "| Test | Job | Suspected | Confirmed | Runs seen | Last seen | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for rec in test_rows[:TOP_TEST_ROWS]:
        runs = state["job_runs"].get(
            f"{rec['origin']}|{rec['repo']}|{rec['job']}", 0)
        out.append(
            f"| `{_display_nodeid(rec['nodeid'])}` | {rec['job']} "
            f"| {rec['suspected_count']} | {rec['confirmed_count']} | {runs} "
            f"| {_short_ts(rec['last_seen'])} "
            f"| [evidence]({reports_base}{report_filename(rec)}) |")
    if not test_rows:
        out.append("| _none in the current window_ | | | | | | |")
    if len(test_rows) > TOP_TEST_ROWS:
        out.append("")
        out.append(f"_{len(test_rows) - TOP_TEST_ROWS} more test(s) below the "
                   f"cut; every one has a page under `reports/`._")

    out += ["", "### Confirmed (gold standard)", ""]
    if confirmed_rows:
        for rec in confirmed_rows:
            label = "whole job" if rec["nodeid"] == JOB_LEVEL_NODEID else \
                f"`{_display_nodeid(rec['nodeid'])}`"
            out.append(f"- {label} in {rec['job']}: {rec['confirmed_count']} "
                       f"confirmed ([evidence]({reports_base}{report_filename(rec)}))")
    else:
        out.append("_None yet. Expected: confirmed needs a rerun pair whose "
                   "base branch didn't move in between._")

    out += [
        "",
        "### Job-level (job-level) rows",
        "",
        "_Whole-job fail/pass at the same commit, from Prow's own result "
        "records. Catches infra flakes that never write test results._",
        "",
        "| Job | Suspected | Confirmed | Runs seen | Discarded builds |",
        "|---|---|---|---|---|",
    ]
    for job_key in sorted(state["job_runs"]):
        origin, repo, job = job_key.split("|", 2)
        rec = state["flakes"].get(f"{job_key}|{JOB_LEVEL_NODEID}")
        s = rec["suspected_count"] if rec else 0
        c = rec["confirmed_count"] if rec else 0
        link = (f" ([evidence]({reports_base}{report_filename(rec)}))"
                if rec else "")
        out.append(f"| {job}{link} | {s} | {c} "
                   f"| {state['job_runs'][job_key]} "
                   f"| {state['discarded'].get(job_key, 0)} |")

    return "\n".join(out) + "\n"


def _display_nodeid(nodeid: str, limit: int = 70) -> str:
    short = nodeid.rsplit("/", 1)[-1].replace("|", "\\|")
    return short if len(short) <= limit else short[:limit - 3] + "..."


def _short_ts(ts: str | None) -> str:
    return (ts or "")[:10]
