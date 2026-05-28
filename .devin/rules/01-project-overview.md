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

## Deeper Context

- Full architecture: `docs/MASTER_PLAN.md`
- Agent rules and hard constraints: `AGENTS.md`
- Indicator contract: `docs/contracts/pine_indicator_ag_contract.md`
- Model spec: `WARBIRD_MODEL_SPEC.md`

Note: `AGENTS.md` and `CLAUDE.md` were written for Claude Code and Copilot. Project knowledge in them is accurate. Behavioral enforcement sections (completion schemas, read-order mandates, rogue-proof contracts) are legacy agent-policing and do not apply to Devin.
