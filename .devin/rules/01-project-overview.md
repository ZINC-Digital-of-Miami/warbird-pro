# Project Overview

Warbird Pro is a PineScript trading indicator modeling project for ES/MES futures.

## Active Surfaces

- **Main chart indicator:** `indicators/warbird-pro-v9.pine` (TradingView name: "Warbird Pro V9")
- **Offline analysis stack:** DuckDB 1.5.2 / Pandera 0.31.1 / AutoGluon 1.5 at `scripts/duckdb_local/`
- **Production trainer:** `scripts/ag/train_v9_locked.py`
- **Runtime/dashboard:** Next.js + Supabase (support only — NOT training)
- **Nexus:** retained research lane only (`indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`)

## Architecture

The active plan is **Warbird Indicator-Only DuckDB Local Modeling Plan v6**: perfect the TradingView indicator settings, train offline with AutoGluon over approved Pine + Databento source rows, promote results back into Pine after approval.

V9 Core uses a file-based pipeline (DuckDB/Pandera/AutoGluon) — no Postgres dependency. Cloud Supabase is runtime/support only. The local PG17 `warbird` warehouse is legacy/reference.

## Live Pine Settings (Authoritative)

See `AGENTS.md` lines 181–204 for the canonical live Pine settings table. These values are authoritative and must match any dataset builder constants before every build.

## Current State & Blockers (as of 2026-05-12)

One completed full `--model-suite` artifact at `models/warbird_pro_v9/locked_20260512_083803/`. Not promotion-ready until:
1. Provenance review against exact manifest/commit/run-command
2. SHAP gate (Gate 1) — `scripts/ag/shap_v9.py`
3. Monte Carlo gate (Gate 2) — `scripts/ag/monte_carlo_v9.py`

Both gates must pass before enabling any TradingView alert.

## Baseline Checkpoint (2026-04-27 operator snapshots)

- 15m: +6.74% PnL, PF 1.143, 434 trades, 3.47% max DD
- 5m: -2.55% PnL, PF 0.91, 295 trades, 3.44% max DD
- 1h: -9.26% PnL, PF 0.929, 801 trades, 14.33% max DD

## Deeper Context

- Full architecture: `docs/MASTER_PLAN.md`
- Agent rules and hard constraints: `AGENTS.md`
- Indicator contract: `docs/contracts/pine_indicator_ag_contract.md`
- Model spec: `WARBIRD_MODEL_SPEC.md`
- V9 ML research operating system: `docs/runbooks/v9_ml_trading_research_operating_system.md`

Note: `AGENTS.md` and `CLAUDE.md` were written for Claude Code and Copilot. Project knowledge in them is accurate. Behavioral enforcement sections (completion schemas, read-order mandates, rogue-proof contracts) are legacy agent-policing and do not apply to Devin.
