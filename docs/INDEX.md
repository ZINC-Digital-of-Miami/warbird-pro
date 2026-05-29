# Warbird Documentation Index

**Date:** 2026-05-22
**Status:** Active Documentation Authority
**Active Plan:** Warbird Indicator-Only DuckDB Local Modeling Plan v6

This file is the single entrypoint for Warbird architecture, contract, and operations documentation.

Ignore all other plans, decisions, scratch notes, and historical architecture docs unless they are linked from this index.

## Governance Precedence

If documentation conflicts, apply this precedence:

1. Hard safety rules are immutable top priority unless Kirk explicitly revokes them.
2. Dated decision records define current direction when summaries lag.
3. Summary docs (`AGENTS.md`, `CLAUDE.md`, `docs/MASTER_PLAN.md`, runbooks) are derived operational views and must not override (1) or (2).

## Iteration Rule

The indicator-only plan is active, but tuning and training are ongoing. Treat
current trigger families, settings, thresholds, and search spaces as the latest
documented evidence snapshot. They may change after new TradingView exports and
DuckDB/Core training evidence. Any accepted change must update this indexed
authority set in the same commit.

Current checkpoint lock (2026-05-02): **Warbird Pro V9**
(`indicators/warbird-pro-v9.pine`) is the only active main chart indicator,
Nexus is retained via
`indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`, and all
other Pine variants are historical unless explicitly reopened. 5m/15m tuning
must preserve the protected Warbird Pro fib anchor ownership and ladder math
unless explicitly reopened with evidence.

V9 lane lock: `warbird_pro_v9` is a separate DuckDB local workspace/profile for
ES-only (5m/15m) ATR/risk exit modeling over active Warbird Pro V9 training rows
from TradingView exports or Databento market data. It ignores MES/NQ/MNQ rows,
removes `-.236` as a stop candidate, keeps `-.236` only as optional
context/export data, and does not authorize Pine edits until a champion is
approved for promotion.

TradingView preflight lock (2026-05-05): V9 has no active strategy harness.
Use `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`
for V9 chart validation and reserve regular `preflight` for explicitly reopened
strategy-harness sessions.

## Canonical Git Push Protocol

Use one repository push path across all active and historical docs:

- push only after explicit user approval in the current session
- work on `main` only
- push explicitly with `git push origin main`
- set upstream once with `git push -u origin main` when required
- never use `git push --force`, `git push -f`, or `git push --no-verify`

This protocol is authoritative in `AGENTS.md` and `docs/MASTER_PLAN.md`, and
overrides stale push wording in older `docs/plans/` artifacts.

## Read Order

1. `docs/MASTER_PLAN.md` — Warbird Indicator-Only DuckDB Local Modeling Plan v6
2. `docs/contracts/README.md`
3. `docs/contracts/pine_indicator_ag_contract.md`
4. `docs/runbooks/README.md`
5. `docs/runbooks/startup_repo_review.md` - required fresh-chat/start-of-day read-only initialization
6. `docs/runbooks/v9_ml_trading_research_operating_system.md` - reusable indicator-first ML/trading research workflow
7. `docs/contracts/schema_migration_policy.md`
8. `docs/cloud_scope.md`
9. `WARBIRD_MODEL_SPEC.md`
10. `agents/README.md`
11. `CLAUDE.md`
12. `docs/agent-safety-gates.md`
13. `Powerdrill/reports/2026-04-06-powerdrill-findings.md`
14. `docs/research/2026-05-02-optuna-unified-platform.md` - Nexus/legacy research reference only (non-authority for V9 Core)

## Authority Split

- `docs/MASTER_PLAN.md`
  - the only planning authority — Warbird Indicator-Only DuckDB Local Modeling Plan v6
- `docs/contracts/`
  - the only interface and payload authority
- `docs/contracts/pine_indicator_ag_contract.md`
  - exact active indicator-only modeling contract
- `docs/cloud_scope.md`
  - the only cloud-whitelist authority
- `docs/runbooks/README.md`
  - the operational runbook index
- `docs/runbooks/startup_repo_review.md`
  - required fresh-chat/start-of-day read-only initialization report checklist
- `docs/runbooks/v9_ml_trading_research_operating_system.md`
  - reusable phase-gated workflow requiring indicator/chart validation before
    modeling, short-window exploratory baselines before full-year training, and
    SHAP/Monte Carlo feature triage before promotion claims
- `agents/README.md`
  - canonical multi-IDE agent umbrella (roles, skills, MCP registry, cleanup lane)
- `agents/manifest.yaml`
  - single canonical registry for active role/skill/MCP surfaces
- `agents/skills/phase-2-custom-skill-migration.md`
  - sequential phase-2 plan for migrating remaining custom-only legacy skills
- quality workbook runtime/artifact surfaces were removed from the active repo
  surface; canonical agent runtime policy now lives under `agents/`
- `docs/runbooks/v9_core_smoke_verification.md`
  - reproducible Core ETL smoke verification commands and exact metric reporting
- `CLAUDE.md`
  - current operational truth and runtime status
- `WARBIRD_MODEL_SPEC.md`
  - subordinate indicator-only model contract and settings artifact semantics

## Canonical Split

- **Pine/TradingView outputs** = active training/modeling truth
- **Databento ES 5m/15m market-data rows** = approved training data supplier when
  manifests identify Databento as source/capture kind; Databento is not the
  Pine indicator source
- **Active Pine files** = `warbird-pro-v9.pine` plus retained Nexus
  `warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
- **Local DuckDB workspaces** under `scripts/duckdb_local/workspaces/` = active V9/Core modeling state
- **Local `warbird` PG17 warehouse** = legacy/reference unless explicitly reopened. The active V9/Core data layer is file-based: **DuckDB 1.5.2** (sort/filter/build), **Pandera 0.31.1** (schema/contract validation), **fg-data-profiling 4.19.1** (`data_profiling` module — profiling reports). Locked 2026-05-11.
- **Training sequence (locked 2026-05-11)**: build and train ES **15m first**; ES 5m only after 15m success (fit + SHAP + Monte Carlo) is documented.
- **Cloud Supabase** = runtime/support only, not training truth
- Active artifacts: `artifacts/tuning/` and `scripts/duckdb_local/workspaces/<indicator_key>/`
- Active Warbird Pro V9 lane: `scripts/duckdb_local/workspaces/warbird_pro_v9/` and
  `scripts/duckdb_local/warbird_pro_v9_profile.py`

## Startup Review Records

- `docs/runbooks/2026-04-29-startup-repo-review-initialization.md`
  - initial startup repo review findings and permanence record

## Execution Handoffs

- `docs/handoffs/2026-05-28-devin-execution-qa-turnover.md`
  - active handoff for Devin-run execution with Codex as independent QA gatekeeper

## Research References

- `docs/research/2026-05-02-optuna-unified-platform.md`
  - comprehensive Optuna ecosystem research report retained for Nexus/legacy
    work only
  - this report is reference material and does not override active contract
    restrictions in `docs/MASTER_PLAN.md` and `docs/contracts/pine_indicator_ag_contract.md`

## Historical Material

- Everything outside this index is reference-only unless a document linked here explicitly reopens it.
- Legacy plan and decision docs remain useful for lineage, but they must not drive new implementation.
