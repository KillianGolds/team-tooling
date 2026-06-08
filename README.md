# team-tooling

A small bot I built to keep our team's open upstream KServe PRs in one
place, so reviewers and approvers don't have to chase scattered threads to
see what's waiting on them.

## What it does

It surfaces our open PRs in two places, grouped by squad:

- **A pinned GitHub issue** that refreshes every few hours. The
  always-current "what needs review right now" board, on one stable URL
  anyone can bookmark or link to.
- **A scheduled Slack message** that links to the issue. Lower-cadence so
  it doesn't drown the team in posts.

Inside each squad, PRs land in three buckets, oldest first:

- **Ready for approver stamp**: LGTM'd (the `lgtm` label *or* a team
  member's `/lgtm` comment) but not yet `/approve`'d, *any size*. The
  bottleneck I most want visible.
- **Fast lane**: small (≤ `fast_lane_max_size` lines / `fast_lane_max_files`
  files), still awaiting LGTM.
- **Deep review**: larger PRs, still awaiting LGTM.

WIP-titled PRs are filtered out. A separate stale-alert @-mentions our
approvers on PRs with no activity (not just age) for `stale_days`, also
grouped by squad.

Schedules live in the workflow crons (see Architecture). The cron is the
source of truth, not this README.

The whole point is to fight out-of-sight-out-of-mind and make the LGTM →
/approve handoff visible to all of us.

### Community LGTM

Most of us aren't OWNERS reviewers upstream, so our `/lgtm` comments don't
trip Prow's `lgtm` label. The bot still counts a team member's `/lgtm`
comment as review signal (shown as `LGTM (comment)`) and promotes the PR to
*Ready for approver stamp*. Cancel handling is per-author latest-wins, so
`/lgtm cancel` undoes it.

## Why this repo is public

The pinned issue only works if anyone on the team and the upstream
approvers can open it from the URL or click through a cross-reference
notification on their PR. With a private repo, only collaborators can see
the issue and the whole "single shared URL" idea falls apart, so I made it
public.

Nothing in here is sensitive:

- Secrets (`GH_TOKEN`, `SLACK_WEBHOOK`) live in repo Secrets, never
  committed.
- `.env` is gitignored.
- `config.yml` lists public GitHub handles.
- The issue body just shows PRs that are already public upstream in
  `kserve/kserve`.

## How it's set up

### GitHub token

I use a fine-grained PAT scoped to **public-repo read**. The Action's
built-in `GITHUB_TOKEN` handles the issue-write side independently (the
workflow grants it `issues: write`), so my PAT never needs more scope than
that. Expiration is one year, with a calendar reminder for the day before.

### The pinned issue

Issue #1 in this repo is the live digest. The bot rewrites the body on
every cron run, so the URL is permanent. Pinned from the Issues tab.

### Slack incoming webhook (optional)

Only needed for `pr-digest.yml` and `stale-alert.yml`. Created at
api.slack.com/apps as a new app → Incoming Webhooks → install to one
channel. If you're only here for the GitHub issue, skip this.

### Repo secrets

In Settings → Secrets and variables → Actions:

- `GH_TOKEN`: my PAT, pasted cleanly with no leading or trailing
  whitespace.
- `SLACK_WEBHOOK`: the webhook URL (only needed if you're running the
  Slack workflows).

### `config.yml`

Single source of truth:

- `squads`: GitHub handles grouped by squad.
- `approvers`: maps a GitHub handle to a Slack member ID for the
  stale-alert mention (Slack profile → ⋯ → "Copy member ID").
- `issue.repo` and `issue.number`: which issue gets rewritten.
- `repos`: which upstream repos to watch.

## Bus factor

- **PAT owner:** _TODO: fill in name + GitHub handle_
- **PAT expires:** _TODO: fill in date_
- **Slack webhook owner:** _TODO: fill in_

If the PAT owner leaves or the token expires, the bot goes silent (no
Slack post, no issue update). Whoever notices first can regenerate the PAT
and update the `GH_TOKEN` secret. Longer-term I'd like a shared bot
GitHub account so this doesn't ride on any one person.

## Running it locally

```bash
pip install -r requirements.txt
export GH_TOKEN=github_pat_...

# Preview the pinned-issue Markdown without writing to GitHub:
python -m pr_digest.issue --dry-run

# Slack:
export SLACK_WEBHOOK=https://hooks.slack.com/services/...
python -m pr_digest.digest          # posts the digest to Slack
python -m pr_digest.stale           # stale alert (@-mentions approvers)
```

Preview the buckets and grouping without posting anywhere, dumped to a
text file:

```bash
export GH_TOKEN=github_pat_...
python -m pr_digest.dump
python -m pr_digest.dump --all-authors --limit 20  # quick sample
```

Tests:

```bash
pip install pytest
pytest tests/
```

## Architecture

```
config.yml                       ← single source of truth
.github/workflows/
├── pr-issue.yml                 ← refreshes the pinned GitHub issue
├── pr-digest.yml                ← Slack digest (cron is source of truth)
└── stale-alert.yml              ← stale-alert schedule
pr_digest/
├── config.py                    ← loads config.yml (squads → flat team_members union)
├── github_client.py             ← API wrapper + rate-limit handling
├── slack_formatter.py           ← Block Kit rendering, grouped by squad
├── markdown_formatter.py        ← GitHub Markdown rendering for the issue body
├── digest.py                    ← shared pipeline: search → enrich → bucket → partition
├── dump.py                      ← text-file preview, no posting
├── issue.py                     ← rewrites the pinned GitHub issue
└── stale.py                     ← stale alert (idle PRs, @-mentions approvers)
tests/
└── test_bucketing.py            ← bucketing, community-LGTM, squad partitioning, rendering
```

The issue workflow uses the Action's built-in `GITHUB_TOKEN` (with
`issues: write` set in the workflow's `permissions` block) to rewrite the
issue body. The read-only PAT (`GH_TOKEN`) handles upstream KServe
queries. So no Slack-app admin approval to fight, and no PAT scope beyond
public-repo read.

## Common changes

**Add a team member:** add their GitHub handle under the right squad in
`squads` in `config.yml`.

**Add a squad:** add a new key under `squads` with its members. The digest
grows a new grouped section automatically.

**Move someone between squads:** move their handle between squad lists.
Handle matching is case-insensitive.

**Change the pinned issue:** edit `issue.repo` and `issue.number` in
`config.yml`. The bot rewrites whatever issue you point it at.

**Add a repo to watch:** add it to `repos`. Works fine for multiple
upstream repos and any midstream or downstream you also care about.

**Tune the fast-lane threshold:** `thresholds.fast_lane_max_size`. 500 is
a starting guess; after a couple weeks of data it's worth checking
whether fast-lane PRs actually got faster reviews.

**Exclude noisy file types:** add globs to `exclude_paths`. Generated
files, vendored deps, lockfiles inflate PR size without adding review
burden.

**Change the schedule:** edit cron in the relevant workflow under
`.github/workflows/`. The Slack timing leans toward when *approvers*
start their day. The pinned issue can refresh more often since it doesn't
notify on every update.
