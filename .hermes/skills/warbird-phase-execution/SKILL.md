---
name: warbird-phase-execution
description: >
  Execute Warbird work against the current authority stack. Use when Hermes must absorb
  plan changes, execute one active phase at a time, or align Pine, data, runtime,
  and contract work to the current Warbird Pro V9 indicator-only architecture.
---

# Warbird Phase Execution

Use this skill when work must align to the active Warbird plan instead of stale project memory.

## Required Reads

1. `AGENTS.md`
2. `docs/INDEX.md`
3. `CLAUDE.md`
4. `docs/MASTER_PLAN.md`
5. `docs/contracts/README.md`
6. `docs/cloud_scope.md`
7. `WARBIRD_MODEL_SPEC.md`
8. The live files for the touched subsystem

## Lock These Truths First

- The active architecture is Warbird Indicator-Only DuckDB Local Modeling Plan v6.
- The active main-chart indicator is `indicators/warbird-pro-v9.pine` / **Warbird Pro V9**.
- Nexus is a retained support/research lane only; do not route current V9 Core work through Nexus.
- V9 has no active strategy harness; use indicator-only preflight.
- V9 Core training is file-based DuckDB/Pandera/AutoGluon under `scripts/duckdb_local/` and `scripts/ag/train_v9_locked.py`.
- Cloud Supabase is runtime/support only, not training truth.
- V9 lane is ES-only, with ES 15m before ES 5m.
- `ml_trade_tp1..5` are label-construction inputs; `ml_trade_tp` is retired.
- Pine edits require explicit current-session approval; pushing to TradingView Pine Editor requires separate explicit approval.
- Training/modeling requires a second explicit approval after the user reviews the current indicator on chart. A prior “get ready to train” or “waiting on export” request is not enough if Pine was edited or TradingView/CDP preflight failed.
- Pine version authority must be resolved from the active Warbird docs, active Pine file, and current-session user instruction. If stale validator text says v5 but the active V9 file uses Pine V6-only syntax and the user confirms V6, preserve V6 and do not downgrade; otherwise stop before editing.

## Phase Sequencing for V9 Indicator Work

1. **Scope (no edits)** — inspect active docs/Pine/tests, run baseline validators, and identify exact deltas. Use the repo `.venv` for V9 Python contract tests before calling a missing dependency a blocker.
2. **Repair** — only after explicit current-session Pine-edit approval. Make the smallest non-destructive changes to the active V9 indicator and directly coupled docs/tests/scripts. If a Pine hidden export is added for training, wire it through the locked trainer feature list, Core ETL/builder, feature-count tests, and active docs in the same repair pass.
3. **Validate** — run Pine compile/lint, guardrails, V9 contract tests, and `npm run build`; report exact pass/fail status.
4. **Train** — only after indicator gates are clean, the user has reviewed the current indicator build on-chart, and the user gives explicit post-review approval for training/modeling. Respect ES 15m-first sequencing. If Pine changed after the last chart review, training is blocked until the user reviews that exact changed build on chart again.

## Work Modes

### 1. Plan Delta

Use when the user says the plan changed or corrects execution order.

- Extract the exact delta
- Recompute what phase is actually active
- Update execution order before touching ordinary implementation

### 2. Phase Kickoff

Use when starting or resuming a phase.

- Inventory the touched files, tables, routes, scripts, and indicators
- Separate canonical-local truth from cloud-serving truth
- Identify blockers before editing

### 3. Phase Execution

Use once scope is clear.

- Make a bounded change set
- Run the real gates for that surface
- Update active docs only if contract or operational truth changed
- End with the next blocking item

## Execution Workflow

1. Run `git status --short`
2. Scope the surface with `rg --files` and `rg -n`
3. Read the governing docs for the touched phase
4. Inventory the write-set and required verification gates
5. Execute only the active phase scope
6. Verify with repo gates
7. Report what changed, what was validated, and what blocks next

## Guardrails

- Do not reduce Warbird to TP1 or TP2 label language only. Entry-state fidelity is mandatory.
- Do not blur Tier 1 Pine transport with Tier 2 AG decisions.
- Do not collapse local canonical truth and cloud runtime subsets into one database story.
- Do not reintroduce stale v6 assumptions into v7 Pine work.
- Do not create new architecture docs unless explicitly asked. Update the active docs instead.
