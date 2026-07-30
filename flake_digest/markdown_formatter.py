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
WAVE_DISPLAY_CAP = 6

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


def render_report_page(rec: dict) -> str:
    """Full evidence for one flaky test (or one job-level row).

    No run denominators here on purpose: they tick on nearly every cron
    cycle and were rewriting ~46 pages per run. They stay exact in state
    and on the issue; a page's git diff should mean something happened to
    THIS test.
    """
    lines = [f"`{rec['nodeid']}`", ""]
    lines += [
        f"**Job:** {rec['job']} · **Repo:** {rec['repo']} ({rec['origin']})",
        f"**Confirmed:** {rec['confirmed_count']} · "
        f"**Suspected:** {rec['suspected_count']}",
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
    # imported here: grouping imports gcs_source, and this module is
    # imported early enough that a top-level import would be circular the
    # day grouping ever needs a formatter helper
    from flake_digest.grouping import compute_incidents

    reports_base = f"https://github.com/{cfg['issue']['repo']}/blob/main/reports/"
    flakes = list(state["flakes"].values())
    test_rows = [r for r in flakes if r["nodeid"] != JOB_LEVEL_NODEID]
    # confirmed leads the ranking; sorting by the sum would let the
    # noisier suspected signal set the order over the gold standard
    test_rows.sort(key=lambda r: (-r["confirmed_count"], -r["suspected_count"]))

    incidents, singletons = compute_incidents(state)
    conf_incidents = sorted((i for i in incidents if i["confirmed"]),
                            key=lambda i: -i["confirmed"])
    # confirmed occurrences that grouped with nothing, back at record grain
    singleton_confirmed: dict[str, int] = {}
    for it in singletons:
        if it["occ"]["classification"] == "confirmed":
            singleton_confirmed[it["key"]] = singleton_confirmed.get(it["key"], 0) + 1

    out = [
        "## KServe e2e flake tracker (midstream)",
        "",
        f"_Last updated {now_iso}. All data is presubmit; there is no clean "
        "scheduled baseline._",
        "",
        "**How to read this.** A row counts occurrences where the same test "
        "both failed and passed at the same PR head commit across rerun "
        "pairs. These are flakes observed among same-commit reruns, not "
        "flake rates. **Suspected** still means both outcomes happened on "
        "identical PR code, which is most likely a flake; the caveat is "
        "that reruns usually land hours apart and the branch the PR merges "
        "onto moves underneath (tagged `base_moved`), so a branch-side fix "
        "or break can't be fully ruled out. **Confirmed** means that branch "
        "base matched as well and both builds carry full evidence: the gold "
        "standard, and rarer on presubmit data. The two counts are never "
        "summed. One more wrinkle for anyone checking evidence by hand: a "
        "test can pass in a build whose job failed overall, so the green "
        "side of a pair sometimes comes from a red job.",
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
    if conf_incidents or singleton_confirmed:
        for inc in conf_incidents:
            pages = [report_filename(state["flakes"][k])
                     for k in inc["record_keys"]]
            tail = (f"([evidence]({reports_base}{pages[0]}))" if len(pages) == 1
                    else f"([evidence]({reports_base}{pages[0]}), "
                         f"{len(pages)} pages under reports/)")
            counts = f"{inc['confirmed']} confirmed"
            if inc["suspected"]:
                counts += f", {inc['suspected']} suspected"
            out.append(f"- **{inc['label']}** in {', '.join(inc['jobs'])}: "
                       f"{counts} {tail}")
        singles = sorted(singleton_confirmed.items(), key=lambda kv: -kv[1])
        for key, count in singles:
            rec = state["flakes"][key]
            label = "whole job" if rec["nodeid"] == JOB_LEVEL_NODEID else \
                f"`{_display_nodeid(rec['nodeid'])}`"
            out.append(f"- {label} in {rec['job']}: {count} "
                       f"confirmed ([evidence]({reports_base}{report_filename(rec)}))")
    else:
        out.append("_None yet. Expected: confirmed needs a rerun pair whose "
                   "base branch didn't move in between._")

    waves = sorted((i for i in incidents if i["kind"] == "wave"),
                   key=lambda i: i["last_seen"] or "", reverse=True)
    if waves:
        out += ["", "### Job-level incidents (waves)", "",
                "_Several jobs failing and passing together, grouped when "
                "their fail builds share one trigger wave and one failure "
                "reason. One row here is one infra event, not N flakes._",
                ""]
        for inc in waves[:WAVE_DISPLAY_CAP]:
            links = ", ".join(
                f"[{state['flakes'][k]['job']}]"
                f"({reports_base}{report_filename(state['flakes'][k])})"
                for k in inc["record_keys"])
            counts = f"suspected {inc['suspected']}"
            if inc["confirmed"]:
                counts = f"confirmed {inc['confirmed']} · " + counts
            out.append(f"- **{inc['label']}**: {links} · {counts} · "
                       f"{_short_ts(inc['first_seen'])} to "
                       f"{_short_ts(inc['last_seen'])}")
        if len(waves) > WAVE_DISPLAY_CAP:
            # waves have no pages of their own; the pointer has to name
            # where their evidence really lives or the line dangles
            out += ["", f"_{len(waves) - WAVE_DISPLAY_CAP} older wave(s) in "
                    "the window not listed; every member occurrence is on "
                    "its job-level page under `reports/`, and the full "
                    "history is in `flake_digest/state/flakes_state.json`._"]

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
    """Shorten with a middle ellipsis that keeps the parametrization
    tail. Tail-ellipsis collapsed distinct params into one visible
    string; the tail is exactly where siblings differ."""
    short = nodeid.rsplit("/", 1)[-1].replace("|", "\\|")
    if len(short) <= limit:
        return short
    if "[" in short and short.endswith("]"):
        func, param = short[:-1].split("[", 1)
        budget = limit - len(func) - 3  # brackets and the ellipsis
        if budget >= 8:
            head = param[:budget // 2]
            tail = param[len(param) - (budget - budget // 2):]
            return f"{func}[{head}…{tail}]"
    keep = limit - 1
    return short[:keep // 2] + "…" + short[len(short) - (keep - keep // 2):]


def _short_ts(ts: str | None) -> str:
    return (ts or "")[:10]
