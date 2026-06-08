# team-tooling

Internal tooling for tracking upstream PRs across the team.

## What this does

Posts a digest of the team's open upstream PRs to Slack on a schedule,
**grouped by squad** within one channel. Inside each squad, PRs fall into three
buckets, oldest-first:

- **Ready for approver stamp** — LGTM'd (the `lgtm` label *or* a team member's
  `/lgtm` comment) but not yet `/approve`'d, *any size*. This is the bottleneck
  we most want visible.
- **Fast lane** — small (≤ `fast_lane_max_size` lines / `fast_lane_max_files`
  files), still awaiting LGTM.
- **Deep review** — larger PRs, still awaiting LGTM.

WIP-titled PRs are filtered out. A separate stale-alert @-mentions approvers on
PRs with no activity (not just age) for `stale_days`, also grouped by squad.

Schedule lives in the workflow cron (see Architecture) — cadence is still being
tuned, so treat the cron as the source of truth, not this README.

The goal is to fight out-of-sight-out-of-mind and make the LGTM → /approve
handoff visible.

### Community LGTM

Most team members aren't OWNERS reviewers, so their `/lgtm` comments don't apply
Prow's `lgtm` label. The digest still counts a team member's `/lgtm` comment as
review signal (`LGTM (comment)` badge) and promotes the PR to *Ready for
approver stamp*. Cancel handling is per-author latest-wins (`/lgtm cancel`
un-does it).

## Setup

### 1. Generate a GitHub token

Settings → Developer settings → Personal access tokens → **Fine-grained tokens**.
- Resource owner: your user account (or a shared bot account, see Bus Factor)
- Repository access: **Public repositories (read-only)** is enough
- Expiration: max 1 year. Set a calendar reminder for the day before.

### 2. Create a Slack incoming webhook

In Slack: app directory → Incoming Webhooks → add to the team channel.
Copy the webhook URL.

### 3. Add secrets

In this repo's Settings → Secrets and variables → Actions → New repository secret:

- `GH_TOKEN` — the PAT from step 1
- `SLACK_WEBHOOK` — the URL from step 2

### 4. Edit `config.yml`

Fill in `squads` (GitHub handles grouped by squad), `approvers` (handle → Slack
member ID), and any repos you want to watch. Push to main and the schedule
kicks in automatically.

### 5. Test it manually

Actions tab → **Upstream PR Digest** → Run workflow. Should post within ~30s.

## Bus factor

- **PAT owner:** _TODO: fill in name + GitHub handle_
- **PAT expires:** _TODO: fill in date_
- **Slack webhook owner:** _TODO: fill in_

When the PAT owner leaves or the token expires, the bot dies silently
(no Slack post). Whoever notices first regenerates the PAT and updates the
`GH_TOKEN` secret.

Long-term, consider a shared bot GitHub account so the PAT doesn't ride on
any individual.

## Local testing

```bash
pip install -r requirements.txt
export GH_TOKEN=github_pat_...
export SLACK_WEBHOOK=https://hooks.slack.com/services/...
python -m pr_digest.digest          # posts the digest to Slack
python -m pr_digest.stale           # posts the stale alert (@-mentions approvers)
```

Preview the buckets/grouping **without posting to Slack** — writes a text file:

```bash
export GH_TOKEN=github_pat_...
python -m pr_digest.dump                          # writes digest_output.txt
python -m pr_digest.dump --all-authors --limit 20 # quick sample, any author
```

Run the tests:

```bash
pip install pytest
pytest tests/
```

## Architecture

```
config.yml                  ← single source of truth (squads, approvers, thresholds)
.github/workflows/
├── pr-digest.yml           ← digest schedule (cron is source of truth)
└── stale-alert.yml         ← stale-alert schedule (cron is source of truth)
pr_digest/
├── config.py               ← loads config.yml (squads → flat team_members union)
├── github_client.py        ← API wrapper + rate-limit handling
├── slack_formatter.py      ← Block Kit rendering, grouped by squad
├── digest.py               ← daily digest: search → enrich → bucket → partition
├── dump.py                 ← text-file preview, no Slack
└── stale.py                ← stale alert (idle PRs, @-mentions approvers)
tests/
└── test_bucketing.py       ← bucketing, community-LGTM, squad partitioning
```

## Common changes

**Add a team member:** add their GitHub handle under the right squad in
`squads` in `config.yml`.

**Add a squad:** add a new key under `squads` with its members — the digest
grows a new grouped section automatically.

**Move someone between squads:** move their handle between squad lists. Handle
matching is case-insensitive.

**Add a repo to watch:** add it to `repos`. Works fine for multiple upstream
repos and any midstream/downstream you also care about.

**Tune the fast-lane threshold:** edit `thresholds.fast_lane_max_size`. 500 is
a starting guess. After a couple weeks of data, check whether PRs in the fast
lane actually got faster reviews — if not, the threshold may be wrong.

**Exclude noisy file types:** add globs to `exclude_paths`. Generated files,
vendored deps, lockfiles inflate PR size without adding review burden.

**Change the schedule:** edit cron in `.github/workflows/pr-digest.yml`. Bias
the timing toward when *approvers* start their day, not the whole team — they're
the bottleneck.

## Roadmap (not built yet)

- **Multi-channel routing (maybe)** — today all squads post to one channel,
  grouped by squad. *If* a squad wants its own channel, that's possible (one
  webhook per channel, or a real Slack app with a bot token) — but it's an
  option, not a commitment.
- Track time-in-state ("LGTM'd but unapproved for N days") to quantify the
  bottleneck.
- Per-approver workload view — how many PRs each approver is gating.
- Cross-repo dashboard if midstream/downstream get added.
- Snooze / claim buttons via a real Slack app (requires bot token, not just
  webhook).

Resist the temptation to build any of this until the basic version has been
running long enough to prove what actually helps.
