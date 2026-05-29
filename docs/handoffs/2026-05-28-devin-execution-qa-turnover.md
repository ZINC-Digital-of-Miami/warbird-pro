# Warbird Pro Devin Execution And QA Turnover

**Date:** 2026-05-28
**Status:** Historical handoff; superseded for the next run by `docs/handoffs/2026-05-29-devin-chart-parity-launch-packet.md`
**Repo:** `/Volumes/Satechi Hub/warbird-pro`
**Primary authority:** `AGENTS.md`, `docs/INDEX.md`, `docs/MASTER_PLAN.md`, `docs/DEVIN_PLATFORM_PLAN.md`, `.devin/`

## Purpose

Devin is expected to run the next execution work. Codex should act as the
independent QA gatekeeper for Devin outputs before Kirk treats any claim as
accepted project state.

This document records the preceding planning/audit lane for the local chart
platform switch. The next active Devin run is plan-build only from
`docs/handoffs/2026-05-29-devin-chart-parity-launch-packet.md`. It does not
approve a PR #11 merge, Pine edit, model training, Supabase migration, Vercel
shutdown, or dashboard implementation.

The immediate Devin lane is to lock the exact local chart authority before
implementation: the current live Vercel dashboard chart is the pixel authority,
TradingView Lightweight Charts is mandatory, and the repo Warbird Pro V9 Pine
indicator is the indicator/visual logic authority.

## Operating Split

| Role | Responsibility | Not Allowed |
| --- | --- | --- |
| Devin | Implement approved phase work, produce small commits on `main`, return evidence packets | Self-certify completion, skip local gates, push without approval, touch Pine without current approval |
| Codex QA | Independently verify Devin claims against local repo, GitHub, SonarCloud, runtime outputs, and docs | Accept transcript-only proof, redesign Devin's scope during QA, silently fix Devin's work unless Kirk asks |
| Kirk | Approve phase starts, resolve architecture conflicts, approve pushes and Pine/TradingView operations | N/A |

## Current Repo-Verified State

Checked from local `main` on 2026-05-28:

- `main` tracks `origin/main`.
- `.devin/settings.toml`, 7 `.devin/rules/`, and 7 `.devin/playbooks/` exist on `main`.
- `docs/DEVIN_PLATFORM_PLAN.md` exists and is marked `Draft for refinement - NOT a build plan yet`.
- SonarQube workflow exists at `.github/workflows/sonarqube.yml`.
- `sonar-project.properties` exists.
- Codacy config residue has been removed from the working tree.
- `docs/MASTER_PLAN.md`, `AGENTS.md`, `CLAUDE.md`, and `.devin/rules/` include the 2026-05-28 local-first pivot.

User-provided platform status, not repo-verifiable from local files:

- Devin environment blueprint is active.
- 9 Devin knowledge notes are pending approval.
- 4 Devin platform playbooks do not exist on the Devin platform.
- No scheduled Devin sessions, triage rules, or smart rules are configured.
- PR #11 contains dashboard/engine work but is not merged to `main`.

Codex QA must re-check platform state if a Devin task depends on those platform
settings.

## Decision Update: Local Chart Platform Switch

Kirk has explicitly approved switching the dashboard direction to a local
machine charting platform now.

Locked direction:

- The chart renderer is **TradingView Lightweight Charts**. Do not evaluate or
  propose alternate chart libraries.
- Use the exact Lightweight Charts version from the current live Vercel
  dashboard if it is pinned. If it is not pinned or must be updated, use the
  current stable Lightweight Charts major line, **v5.2.0**, and document the
  parity impact.
- The current live Vercel dashboard chart is the pixel authority.
- `indicators/warbird-pro-v9.pine` is the indicator and visual-logic authority.
- No Pine edits are approved.
- No chart redesign is approved.
- No approximate chart rebuild is acceptable. The target is pixel-level parity.
- Preserve all four available timeframes.
- Make **5m** the canonical/default timeframe for training, primary settings,
  Nexus oscillator work, and operator focus.
- PR #11 is a prototype/source inventory. It is not approved to merge as-is.
- TradingView/Pine-only or footprint-only features that cannot run locally must
  be documented as honest adapter gaps. Do not substitute fake, mock, or proxy
  values as if they are equivalent.

Current Codex QA finding on PR #11:

- mechanically mergeable onto current `origin/main`
- `npm ci` and `npm run build` passed in a simulated merge worktree
- Python engine compile/import smoke passed
- runtime smoke served `/` and `/api/status` without keys
- `npm run lint` failed in `dashboard/app.js`
- `docs/DASHBOARD_PLAN.md` is stale against the PR itself
- higher-timeframe aggregation is count-based, not wall-clock/session aligned
- `engine/trade_log.py` does not match the planned normalized DuckDB trade log
  surface and computes short PnL incorrectly

Therefore, PR #11 should be treated as salvageable prototype work, not a clean
merge candidate.

## Critical Stop Condition: Authority Drift

The current documentation stack is not perfectly aligned.

Aligned with the 2026-05-28 pivot:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/MASTER_PLAN.md`
- `docs/DEVIN_PLATFORM_PLAN.md`
- `.devin/rules/`

Still carrying older restrictions or narrower language:

- `WARBIRD_MODEL_SPEC.md` still disallows FRED, macro, news/options, and most external feature joins.
- `docs/contracts/pine_indicator_ag_contract.md` still says no external feature stack is admitted.
- `docs/cloud_scope.md` still prohibits FRED/macro/cross-asset feature warehouses for active modeling.
- `docs/INDEX.md` still describes the active split as Pine/TradingView plus Databento/Nexus centered, without fully expressing the local-first pivot.

Until Kirk explicitly resolves this conflict in the authority docs, Devin must
not start data/modeling work that depends on FRED, macro, news, options, broad
cross-asset features, or Supabase migration into modeling.

This conflict does **not** block the local chart parity lane. Devin may inspect,
map, and plan the local Lightweight Charts dashboard using the live Vercel chart
and Warbird Pro V9 Pine indicator as authority. Devin may not present local
engine triggers, external features, model outputs, or Supabase-derived data as
training truth until the authority docs are reconciled.

Allowed before that conflict is resolved:

- documentation cleanup to align the authority stack, if Kirk approves that exact scope
- PR #11 review against current local-first chart requirements
- local chart parity authority packet
- Sonar/GitHub quality verification
- Devin platform configuration review
- non-Pine repo hygiene that does not change modeling truth

## Devin Preflight Requirement

Before every Devin work session, Devin must return a short preflight packet:

```text
DEVIN PREFLIGHT
Branch/upstream:
Working tree:
Last 5 commits:
Task scope:
Files expected to change:
Authority docs read:
Required verification gates:
Known blockers:
Push approval status:
```

Minimum local checks:

```bash
git status --short --branch --untracked-files=all
git log --oneline --decorate -5
```

For fresh/context-reset sessions, Devin must follow
`docs/runbooks/startup_repo_review.md` before implementation.

## Execution Phases And QA Gates

### Phase 0 - Lock The Plan

Goal: turn `docs/DEVIN_PLATFORM_PLAN.md` from draft context into an approved,
conflict-free execution plan.

Devin deliverable:

- one doc update that reconciles `AGENTS.md`, `docs/INDEX.md`, `docs/MASTER_PLAN.md`,
  `docs/cloud_scope.md`, `docs/contracts/pine_indicator_ag_contract.md`,
  `WARBIRD_MODEL_SPEC.md`, `CLAUDE.md`, and `.devin/`
- explicit statement of what the local-first pivot changes and what it does not change
- explicit Supabase boundary: runtime/support only vs. migrated local modeling data
- explicit model-selection status: research required, no training yet

Codex QA pass criteria:

- no conflicting data-source rules remain across authority docs
- plan still preserves Pine safety rules
- no implementation claims are introduced without evidence
- docs-only verification is sufficient unless operational state is claimed

### Phase 1 - Local Chart Parity Authority Packet

Goal: lock the exact local chart contract before implementation or merge.

This is the currently opened Devin lane.

Devin must not merge PR #11 or implement new chart code until Kirk approves this
packet.

Devin deliverable:

- source-of-truth map comparing:
  - current live Vercel dashboard chart implementation
  - PR #11 branch `devin/1779988864-warbird-command-center`
  - `indicators/warbird-pro-v9.pine`
  - existing chart primitives/components used by the Vercel dashboard
- exact Lightweight Charts version decision:
  - current live Vercel pinned version, if pinned
  - otherwise current stable v5.2.0
  - any API or rendering differences that affect pixel parity
- full visual/behavior inventory:
  - candles, wick colors, borders, background, grid, spacing, right offset,
    price scale, time scale, crosshair, labels, markers, panes, fib lines,
    fib colors, golden zone, EMA21, EMA9, Nexus oscillator, volume/pressure
    panels, timeframe controls, and right-side cards
- four-timeframe preservation plan with 5m as canonical/default
- Vercel-code reuse/port map
- PR #11 keep/fix/discard map
- Pine/TradingView-only and footprint-only adapter-gap register
- exact implementation phases after approval
- merge/rebuild recommendation for PR #11

Codex QA pass criteria:

- packet proves the target chart is the live Vercel chart, not a redesign
- Lightweight Charts is the only renderer considered
- any version move to v5.2.0 is justified against live Vercel parity
- every claimed visual source is mapped to actual code or Pine lines
- PR #11 known blockers are acknowledged instead of hidden
- no mock data is presented as live, production, or footprint-equivalent data
- no Pine files are changed
- no Vercel/Next.js shutdown is claimed as done or approved

After Kirk approves the packet and implementation begins, required verification
depends on touched files. For dashboard/runtime code, expect at minimum:

```bash
npm run lint
npm run build
```

plus the narrowest available Python/runtime checks for the local engine, and
visual proof against the live Vercel chart.

### Phase 2 - Supabase To DuckDB Audit

Goal: inventory useful Supabase historical/runtime data and define what moves
local, what stays runtime-only, and what is dropped.

Devin deliverable:

- table inventory with owner, purpose, row counts, date ranges, and data sensitivity
- classification: migrate to DuckDB, keep runtime-only, drop/archive
- DuckDB schema proposal before migration
- manifest format for migrated sources

Codex QA pass criteria:

- no cloud table is used as training truth unless authority docs explicitly allow it
- every migrated source has row counts, date ranges, hashes or reproducible export proof
- DuckDB schema has explicit keys, constraints, naming, and source lineage
- no raw trials, labels, or AG/SHAP artifacts are written to cloud

### Phase 3 - Vercel / Next.js Shutdown

Goal: shut down Vercel/Next.js only after the local dashboard/runtime replacement
is proven.

Devin deliverable:

- dependency map showing which routes/components/libs are still used
- removal/archive plan
- proof the local replacement covers required runtime functions
- rollback plan

Codex QA pass criteria:

- Vercel is not disabled before replacement is operational
- DNS/routing implications are documented
- no active runtime route is deleted without replacement proof

### Phase 4 - Model And Data Research

Goal: select model/data approach before training.

Devin deliverable:

- research brief with candidate models, label schemes, timeframe strategy, data sources, and evaluation plan
- leakage and manifest controls
- proposed SHAP/Monte Carlo criteria

Codex QA pass criteria:

- no training run is presented as accepted research
- old skewed baselines are not used as decision evidence
- every proposed data source has source/capture, lag/availability, and leakage notes
- output is a decision memo, not a model promotion

### Phase 5 - Training And Validation

Goal: train only after Phase 4 is approved.

Devin deliverable:

- exact command, commit, manifests, row counts, date ranges, split policy, metrics
- SHAP artifacts and findings
- Monte Carlo artifacts and findings
- promotion or rejection recommendation

Codex QA pass criteria:

- training uses approved sources only
- no future leakage or mislabeled source kind
- SHAP and Monte Carlo both pass before any alert/trade-routing claim
- old `locked_20260512_083803` artifact is historical unless revalidated under current contract

### Phase 6 - Pine Promotion

Goal: apply validated settings/build changes to Pine only after explicit Kirk approval.

Devin deliverable:

- exact proposed Pine diff
- output/request budget before and after
- before/after TradingView evidence if fib visuals or trigger semantics change
- all mandatory Pine gates

Codex QA pass criteria:

- current-session Pine approval exists
- no protected fib anchor/ladder semantics changed without explicit approval
- no banned `fibHtfSnapshot` pattern reappears
- all Pine verification gates pass

Mandatory gates for any `.pine` edit:

```bash
./scripts/guards/pine-lint.sh <file>
./scripts/guards/check-fib-scanner-guardrails.sh
./scripts/guards/check-contamination.sh
./scripts/guards/check-no-tv-force.sh
npm run build
```

## Devin Closeout Packet

Every Devin delivery must end with:

```text
DEVIN CLOSEOUT
Status: COMPLETE | INCOMPLETE | BLOCKED
Task scope:
Files changed:
Commits:
Claims made:
Verification run:
Verification not run:
Evidence links or local artifact paths:
Known gaps:
Push status:
Next requested decision:
```

If Devin claims a phase is complete, the closeout must include enough evidence
for Codex to reproduce or independently disprove the claim.

## Codex QA Protocol

Codex QA should not accept Devin's closeout as proof. For each Devin delivery:

1. Establish the governing scope and authority docs.
2. Inventory every factual claim.
3. Verify local files and Git state first.
4. Verify external systems only when relevant: GitHub PR/checks, SonarCloud,
   Devin platform, Supabase, Vercel, Databento, TradingView.
5. Run the required gates for touched surfaces.
6. Report blocking failures before summaries.
7. Use the verdict `PASSED`, `PASSED WITH REGISTERED AMBIGUITY`, or `BLOCKED`.

QA report format:

```text
DEVIN QA VERDICT: PASSED | PASSED WITH REGISTERED AMBIGUITY | BLOCKED

Scope reviewed:
Claims verified:
Integrity checks:
Blocking failures:
Accepted ambiguities:
Scope-dodge register:
Required fixes before next phase:
```

## Current Open Blockers

- `docs/DEVIN_PLATFORM_PLAN.md` is still a draft, not an execution authority.
- Authority docs conflict on the local-first data/modeling pivot.
- 9 Devin knowledge notes reportedly await Kirk approval.
- 4 Devin platform playbooks reportedly do not exist on the platform.
- PR #11 dashboard/engine work is not merged to `main` and is not merge-ready as-is.
- Local chart parity authority packet has not been produced or approved.
- Supabase-to-DuckDB migration has not started.
- Vercel/Next.js shutdown has not started.
- Model-selection research has not started.
- No post-pivot training run exists.
- SHAP and Monte Carlo gates have not accepted any current artifact.
- Agent umbrella Phase 2 and Phase 3 remain incomplete.

## Immediate Recommended Next Request To Devin

Ask Devin for this next:

```text
Do not merge PR #11 and do not implement yet.

Next task: create a Chart Parity Authority Packet for the local Warbird dashboard.

Mandatory direction:
- TradingView Lightweight Charts is the required chart renderer. Do not evaluate or propose other chart libraries.
- Inspect the current live Vercel dashboard. If its Lightweight Charts version is pinned, use that exact version for local parity. If not pinned or if an update is required, use current stable Lightweight Charts v5.2.0 and document parity impact.
- The live Vercel dashboard chart is the pixel authority.
- The repo Warbird Pro indicator, indicators/warbird-pro-v9.pine, is the indicator/visual logic authority.
- No Pine edits.
- No chart redesign.
- No approximation. The target is pixel-for-pixel parity with the live Vercel chart.
- PR #11 is a prototype/source inventory, not approved for merge as-is.

What to inspect:
1. Current live Vercel dashboard chart implementation.
2. PR #11 branch: devin/1779988864-warbird-command-center.
3. Repo Pine indicator: indicators/warbird-pro-v9.pine.
4. Existing chart primitives/components used by the Vercel dashboard.

Requirements:
- Inventory every chart visual and behavior: candles, wick colors, borders, background, grid, spacing, right offset, price scale, crosshair, labels, fib lines, fib colors, golden zone, EMA21, EMA9, Nexus oscillator, volume/pressure panels, timeframe controls, right-side cards.
- Preserve all four available timeframes.
- Make 5m the canonical/default timeframe for training, primary settings, Nexus oscillator work, and operator focus.
- Identify exactly which Vercel chart code should be reused or ported into the local Lightweight Charts dashboard.
- Identify exactly which PR #11 code should be kept, fixed, or discarded.
- Identify any Pine/TradingView-only or footprint-only features that cannot run locally yet. Document them as honest adapter gaps. Do not fake or mock them.
- Review docs/DEVIN_PLATFORM_PLAN.md, docs/MASTER_PLAN.md, AGENTS.md, and docs/handoffs/2026-05-28-devin-execution-qa-turnover.md before making recommendations.

Deliverable:
- A written Chart Parity Authority Packet with:
  - source-of-truth map
  - Lightweight Charts version decision
  - PR #11 gap list
  - exact implementation phases
  - merge/rebuild recommendation
  - explicit blockers
  - verification plan for pixel parity and local runtime

Do not implement until Kirk approves the packet.
```

Do not ask Devin to train, migrate Supabase, shut down Vercel, create more
rulebooks/playbooks, or touch Pine until the relevant gate above is explicitly
opened.
