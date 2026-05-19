---
name: tradingview-indicator-lifecycle
description: >
  Router for the full Warbird Pine lifecycle. Use when a request spans contract review,
  repair, build, optimization, transport checks, and release closeout and Hermes must
  choose the right next Pine operation.
---

# TradingView Indicator Lifecycle

Use this skill when the request spans more than one Pine phase or when you need to decide what kind of Pine work comes first.

## Canonical references

- `references/warbird-v9-rebuild-scope-notes.md` — session-derived notes for resuming half-finished V9 rebuild cleanup, including `.venv` pytest routing, lean-cut enforcement probe, and the Pine v5/v6 policy conflict.
- `references/warbird-chart-review-training-gate.md` — workflow correction: any Pine edit requires user chart review of that exact build before V9 training/modeling can start; CDP/preflight failures stop training rather than falling through to local-only training.

## Lifecycle Order

1. Lock authority and contract truth
2. Validate candidate and entry-state semantics
3. Choose the primary operation mode
4. Execute the Pine change
5. Run repo gates
6. Update active docs only if truth changed

## Authority Lock

Read the active Warbird authority stack before touching Pine:

1. `AGENTS.md`
2. `docs/INDEX.md`
3. `docs/MASTER_PLAN.md`
4. `docs/contracts/README.md`
5. `docs/contracts/pine_indicator_ag_contract.md`
6. `docs/runbooks/README.md`
7. `WARBIRD_MODEL_SPEC.md`
8. `CLAUDE.md`
9. `docs/agent-safety-gates.md`

Lock these current V9 truths before touching Pine:

- active main-chart indicator = `indicators/warbird-pro-v9.pine`, named **Warbird Pro V9** in TradingView
- Nexus remains a retained support/research lane only; do not route V9 Core work through Nexus
- V9 is indicator-only; use `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`, not the strategy-harness preflight
- production V9 trainer = `scripts/ag/train_v9_locked.py`
- V9 Core pipeline is file-based DuckDB/Pandera/AutoGluon under `scripts/duckdb_local/`; Postgres/cloud Supabase are not active training truth
- V9 lane is ES-only, 15m first; do not train/model unless indicator gates are clean, the user has reviewed the current indicator build on-chart, and the user gives explicit post-review training approval
- Pine/TradingView outputs and approved Databento ES rows are active data truth; no mock/demo/fake data
- `ml_trade_tp` is retired; `ml_trade_tp1..5` are label-construction inputs, not `ML_FEATURES`
- Pine edits require explicit current-session approval, and pushing to TradingView Pine Editor requires separate explicit approval
- Pine version authority can conflict during V9 rebuild work. If a pasted validator contract says v5 while the active file uses v6-only syntax (`//@version=6`, `input.*(..., active=...)`, `request.footprint()`), stop and resolve the conflict explicitly. If the user confirms in-session that Warbird is Pine V6, preserve V6 and do not downgrade to v5 to satisfy stale validator text.

## Choose the Mode

- Review: findings, risks, release readiness
- Repair: compile defect, runtime bug, behavior regression, naming issue
- Build: approved feature or contract extension
- Optimize: budget, stability, or signal-quality improvement without changing contract semantics

If multiple modes are needed, use this order:

1. Review
2. Repair
3. Build
4. Optimize

## Before Code

First do a no-edit scope pass when repo state or rebuild status is unknown:

1. `git status --short`
2. inspect the active authority docs and active Pine file
3. run/read existing Pine validators before proposing edits
4. run V9 Core contract tests through the repo venv: `.venv/bin/python -m pytest ...` (do not install packages just because system `pytest` misses repo deps)
5. if lean-cut status is uncertain, probe the gated contract with `WARBIRD_ENFORCE_PINE_LEAN_CUT=1 .venv/bin/python -m pytest tests/ag/test_v9_pine_lean_cut_contract.py -q`
6. summarize exact pass/fail deltas and ask for Pine-edit approval before modifying `indicators/warbird-pro-v9.pine`

Confirm before implementation:

1. no-repaint and confirmed-bar logic
2. entry event and entry activation timing
3. captured entry price or spot semantics
4. V9 Core training feature/label contract alignment
5. indicator-only preflight boundary compliance
6. `ml_*` feature vs label-input distinction (`ml_trade_tp1..5` are label inputs)
7. Pine budget safety and output-slot pricing
8. Pine v5/v6 policy is resolved explicitly if current code and validator contract disagree
9. New hidden Pine export columns intended for training are also wired into the locked trainer, Core ETL/builder, feature-count tests, and active docs; otherwise the indicator can emit data that AG silently ignores

If any of these are unresolved, the task is not ready for implementation.

## Closeout

For `.pine` changes, run and report exact status for:

- Pine compile check (`scripts/guards/compile-pine.sh <file>` when available)
- `scripts/guards/pine-lint.sh <file>`
- `scripts/guards/check-fib-scanner-guardrails.sh`
- `scripts/guards/check-contamination.sh`
- `scripts/guards/check-no-tv-force.sh`
- required V9 Core contract tests via `.venv/bin/python -m pytest ...`
- `npm run build`

Do not run training/modeling in closeout unless the user explicitly requested training and indicator gates are clean. Update active docs only if contract or operational truth changed.

## Guardrails

- TP1 and TP2 labels are not a substitute for entry-state validation
- Do not widen the task into an architecture rewrite unless explicitly asked
- Do not carry stale v7/MES/strategy-harness assumptions into current V9 Core indicator-only work
- Do not treat a system Python dependency miss as a repo contract failure; first retry with the repo `.venv`
- Do not edit Pine to satisfy skipped lean-cut tests until the user approves the lean-cut direction and Pine edits in the current session
- On TradingView CDP failure, stop immediately and wait for human instruction