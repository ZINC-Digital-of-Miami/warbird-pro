# Project Overview

Warbird Pro is a local-first trading indicator modeling project for ES/MES futures.

## Active Surfaces

- **Pine indicator:** `indicators/warbird-pro-v9.pine` (TradingView name: "Warbird Pro V9") — reference implementation, NOT the live trigger platform
- **Local dashboard:** TradingView Lightweight Charts v5 on localhost (hosting platform TBD). Engine at `engine/` (PR #11, branch `devin/1779988864-warbird-command-center`)
- **Data layer:** DuckDB for local data/trade recording; Databento live MES streaming; FRED, news, macro data all available (local removes TV restrictions)
- **ML stack:** DuckDB 1.5.2 / Pandera 0.31.1 at `scripts/duckdb_local/`; model selection TBD — NOT using full AutoGluon zoo
- **Nexus:** retained research lane only

## Architecture

**Local-first.** The system is NOT hinged on the TradingView live indicator. The local dashboard (TV Lightweight Charts on localhost) is the primary platform for charting, triggers, and trade recording. The hosting platform is not fully chosen yet. Crons run on local machine, dashboard pushes from Devin.

**Key shifts (2026-05-28):**
- **NOT indicator-driven** — the local engine is the trigger platform, not TradingView
- **FRED, news, macro, options data NOW ALLOWED** — local-first removes all TradingView data restrictions
- AutoGluon full-zoo is **no longer locked** — specific model set TBD after deep research
- Past testing results (15m baseline included) are **skewed and unreliable** — do not use as baseline
- Vercel/Next.js dashboard is **decommissioned**
- Code quality checks: SonarQube (Sonic)

## Live Pine Settings (Reference)

See `AGENTS.md` lines 181–204 for the canonical Pine settings table. These values describe the TradingView indicator state but the local engine may diverge as it evolves independently.

## Deeper Context

- Full architecture: `docs/MASTER_PLAN.md`
- Platform plan: `docs/DEVIN_PLATFORM_PLAN.md`
- Agent rules and hard constraints: `AGENTS.md`
- Indicator contract: `docs/contracts/pine_indicator_ag_contract.md`
- Model spec: `WARBIRD_MODEL_SPEC.md`

Note: `AGENTS.md` and `CLAUDE.md` were written for Claude Code and Copilot. Project knowledge in them is accurate and has been updated for the local-first pivot. Behavioral enforcement sections (completion schemas, read-order mandates, rogue-proof contracts) are Claude/Copilot-specific agent-policing and do not apply to Devin.
