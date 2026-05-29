# Warbird Pro Devin Knowledge Blueprint

This is the exact Knowledge set to create or approve in Devin Settings & Library > Knowledge for `ZINC-Digital-of-Miami/warbird-pro`.

Official Devin guidance this blueprint follows:

- Knowledge should hold repeated codebase/workflow context, not one-off task details.
- Trigger descriptions must be specific because Devin retrieves Knowledge based on the trigger.
- Keep each item focused and relevant; Devin reads the whole item when retrieved.
- Pin repo-critical Knowledge to this repo so it is always active for Warbird work.
- Deduplicate first, resolve conflicts second, then fill gaps.

## Folder Layout

Create this folder tree:

```text
Warbird Pro
  00 Always Active
  10 Chart Parity
  20 Devin Execution
  30 Review Insights QA
  40 Supabase DuckDB
  50 Vercel Demotion
```

All notes below should be pinned to `ZINC-Digital-of-Miami/warbird-pro` unless explicitly stated otherwise.

## Knowledge Items

### 00 Always Active / Repo Authority And Source Of Truth

**Trigger Description:** `warbird-pro repo, AGENTS.md, source of truth, local clone, startup, any Warbird task`

**Macro:** `!warbird-authority`

**Content:**

```text
For Warbird Pro, the local clone at /Volumes/Satechi Hub/warbird-pro is the source of truth. Start with AGENTS.md and repo-local files before relying on GitHub, Devin summaries, screenshots, or prior chat. Hard safety rules and current user instructions outrank older summary docs. Report blockers instead of substituting remote web state when local state is required.
```

### 00 Always Active / No Premature Completion Claims

**Trigger Description:** `Warbird completion claim, done, ready, green checks, mergeable, QA, closeout`

**Macro:** `!warbird-proof`

**Content:**

```text
Do not claim Warbird work is complete from Devin Review, Sonar/Sonic, or CI alone. Return evidence: files changed, exact authority read, commands run, command outcomes, adapter gaps, unverified claims, and remaining blockers. Codex QA remains an independent acceptance gate and may block even when Devin Review and Sonar pass.
```

### 10 Chart Parity / Packet v2.4.1 Authority

**Trigger Description:** `chart parity, Packet v2.4, Packet v2.4.1, PR #14, local dashboard, LiveMesChart, chart implementation`

**Macro:** `!warbird-chart-packet`

**Content:**

```text
For Warbird chart parity work, use the locally imported PR #14 / Packet v2.4.1 authority. Read agents/skills/chart-parity-authority/SKILL.md top-to-bottom and docs/packet_plan_v2.4.1_correction_proposal.md before writing plans or code. PR #14 is closed as partial-import archive evidence, not a merge target. Older v2.1 packet diffs are superseded. Do not merge PR #11 as-is.
```

### 10 Chart Parity / Live Chart Source

**Trigger Description:** `LiveMesChart, Lightweight Charts, local dashboard chart source, dashboard baseline`

**Macro:** `!warbird-live-chart`

**Content:**

```text
Use components/charts/LiveMesChart.tsx as the source for retained Lightweight Charts behavior: theme, bar spacing, right offset, watermark, crosshair, and SMA200. PR #11 dashboard frontend is source inventory only unless a packet step explicitly retains a surface. Do not redesign the chart or introduce another charting platform.
```

### 10 Chart Parity / Exact Rulings No Interpretation

**Trigger Description:** `Kirk ruling, exact instruction, packet correction, chart packet revision, drift, do not reinterpret`

**Macro:** `!warbird-exact-ruling`

**Content:**

```text
When Kirk gives an exact Warbird ruling, apply it literally. Do not add hedging, alternative options, approximation language, or "needs approval" language that changes the ruling. If the ruling conflicts with existing docs, surface the conflict and update the governing docs/Knowledge in the same change after approval.
```

### 10 Chart Parity / Layout Contract

**Trigger Description:** `dashboard layout, correlations row, cards panel, pressure bar, Nexus placement, sidebar scope`

**Macro:** `!warbird-layout-contract`

**Content:**

```text
Warbird chart layout is locked: correlations row full width above everything; chart plus 320px cards panel in one row; cards stay within chart row only; thin full-width pressure bar below chart/cards; full-width Nexus sub-chart below pressure bar. Do not extend the sidebar over pressure/Nexus and do not move correlations off the 1h isolated update cycle.
```

### 10 Chart Parity / Nexus And Standard Volume Adapter Gap

**Trigger Description:** `Nexus, ML RSI, standard volume, footprint, request.footprint, volume delta, adapter gap`

**Macro:** `!warbird-nexus-volume`

**Content:**

```text
For the local dashboard, drop in the approved Nexus logic as-is minus TradingView-centric items. Use standard volume for now. Do not present standard volume, candle-body delta, or unavailable footprint data as equivalent to TradingView request.footprint or Databento trades-side evidence. Label missing evidence as an adapter gap and apply the configured confidence gate when quality is LOW.
```

### 20 Devin Execution / Manual First, Automations Later

**Trigger Description:** `Devin automation, schedule, trigger, auto-fix, auto-push, managed Devin, parallel session`

**Macro:** `!warbird-manual-first`

**Content:**

```text
Warbird Devin execution is manual-first. Before any write automation, run the playbook manually once and pass Codex QA. Allowed early automations are read-only PR drift review, read-only Sonic findings summary, and read-only packet consistency checks. Forbidden without explicit approval: auto-fix, auto-push, auto-merge, cloud migration execution, Pine edits, Vercel demotion.
```

### 20 Devin Execution / Main-Only And Push Approval

**Trigger Description:** `Warbird git, main branch, push, commit, PR, branch, merge`

**Macro:** `!warbird-git`

**Content:**

```text
Warbird work lands on main only unless Kirk explicitly says otherwise. Push only after explicit current-session approval. Use git push origin main. Never force push or use --no-verify. If Devin creates a PR/branch, treat it as review/input until Kirk approves how to integrate it.
```

### 30 Review Insights QA / Sonic Is Advisory

**Trigger Description:** `Sonic, SonarQube, SonarCloud, quality gate, code quality, suggested fix`

**Macro:** `!warbird-sonic`

**Content:**

```text
SonarQube/Sonic findings are advisory until mapped to a repo file, rule, severity, owning surface, root cause, and verification step. Do not auto-apply Sonic suggested fixes. Return a defect map first, get scope approval for broad fixes, then run local verification.
```

### 30 Review Insights QA / Self-Heal Loop

**Trigger Description:** `Devin Review feedback, repeated issue, failed gate, improve playbook, update knowledge, session analysis`

**Macro:** `!warbird-self-heal`

**Content:**

```text
After every Devin Review, Sonic issue, failed local gate, or Codex QA block, decide whether the failure is reusable process knowledge. If yes, update the relevant .devin/rules/ or .devin/playbooks/ file and propose a Knowledge update. Do not say Devin learned unless a rule, playbook, Knowledge note, or automation change is actually present or submitted.
```

### 30 Review Insights QA / Session Insights Retrospective

**Trigger Description:** `Session Insights, category mismatch, actionable feedback, session size, ACU usage, user messages`

**Macro:** `!warbird-session-insights`

**Content:**

```text
After meaningful Devin sessions, generate Session Insights and record category, ACU usage, user messages, session size, Issue Timeline, Actionable Feedback, and Knowledge Usage. Compare the shown category to Warbird intent. If the session is L/XL or category-mismatched, split or rewrite the next launch prompt before continuing.
```

### 30 Review Insights QA / Misleading Knowledge Cleanup

**Trigger Description:** `misleading knowledge, Knowledge Usage, stale knowledge, repeated issue, retry loop`

**Macro:** `!warbird-knowledge-cleanup`

**Content:**

```text
If Session Insights flags misleading Knowledge, do not ignore it. Identify whether the problem is stale content, broad trigger, conflict, wrong repo scope, or missing stop condition. Edit, narrow, disable, delete, or replace the item before the next similar Devin run. Repeated timeline issues should become an environment blueprint, playbook, rule, or Knowledge update.
```

### 30 Review Insights QA / Session 13c8 Failure Pattern

**Trigger Description:** `session 13c8, Devin environment configuration status update, PR #14, packet drift, false completion, knowledge neglect`

**Macro:** `!warbird-session-13c8`

**Content:**

```text
Session 13c8 produced PR #14 but exposed recurring failures: false completion claims, repeated instruction drift, delayed Knowledge updates, parallel-agent misalignment, layout misunderstanding, and charting/licensing confusion. Future Devin runs must be smaller, use exact packet authority, update Knowledge promptly, and include Session Insights Review before the next run.
```

### 40 Supabase DuckDB / Read-Only Migration Audit

**Trigger Description:** `Supabase to DuckDB, migration, cloud data, schema inventory, Supabase connector`

**Macro:** `!warbird-supabase-audit`

**Content:**

```text
Supabase-to-DuckDB starts as a read-only audit, not a migration. Prefer repo-local read-only tooling or a read-only Devin Supabase connector. Stop if only write-capable or service-role credentials are available unless Kirk explicitly approves. Inventory tables, row counts, date ranges, keys, sensitivity, and classification before proposing any DuckDB schema or data movement.
```

### 50 Vercel Demotion / Proof Before Demotion

**Trigger Description:** `Vercel demotion, Vercel shutdown, Next.js dashboard removal, local replacement, DNS`

**Macro:** `!warbird-vercel-demotion`

**Content:**

```text
Do not demote, disable, or delete Vercel/Next.js until the local dashboard/runtime replacement is proven and Kirk approves the demotion in the current session. Required proof includes lint/build passing, local dashboard runtime proof, chart packet coverage, dependency map, DNS/routing implications, and rollback plan.
```

## Knowledge Hygiene Rules

- Keep each note short and single-purpose.
- Prefer a trigger tied to a task type, file surface, or repeated failure.
- Do not duplicate AGENTS.md verbatim; summarize the triggerable decision.
- Review pending Knowledge suggestions after every major Devin session.
- Deduplicate before adding more notes.
- Disable stale notes rather than letting conflicting guidance accumulate.
- Promote only organization-wide guidance to broader scope; keep Warbird-specific notes pinned to Warbird.
