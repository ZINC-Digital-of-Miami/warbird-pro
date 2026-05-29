# Project Overview

Warbird Pro is a local-first trading indicator and dashboard project for ES/MES futures.

## Active Surfaces

- **Pine indicator:** `indicators/warbird-pro-v9.pine` (TradingView name: "Warbird Pro V9") — visual/logic authority for the local dashboard port; never edit without current-session approval
- **Chart parity authority:** `agents/skills/chart-parity-authority/SKILL.md` (PR #14 / v2.4.1) governs local dashboard implementation decisions when present
- **Local dashboard:** TradingView Lightweight Charts on localhost (hosting platform TBD). Use the exact `components/charts/LiveMesChart.tsx` chart surface as the visual source and approved `engine/` surfaces from PR #11 only where the packet allows them
- **Data layer:** DuckDB for local data/trade recording; Databento live MES streaming; FRED, news, macro data all available (local removes TV restrictions)
- **ML stack:** DuckDB 1.5.2 / Pandera 0.31.1 at `scripts/duckdb_local/`; model selection TBD — NOT using full AutoGluon zoo
- **Nexus:** retained support/research lane; for the local dashboard, drop in the approved Nexus logic as-is minus TradingView-centric items and use standard volume until real footprint/trades-side evidence is implemented

## Architecture

**Local-first, packet-first.** The system is moving toward a local dashboard/runtime, but the Vercel dashboard is not demoted until the chart packet and implementation are complete and verified. The local dashboard uses TradingView Lightweight Charts on localhost. The hosting platform is not fully chosen yet. Crons run on the local machine, dashboard work can be executed by Devin, and Codex QA remains the independent verification gate.

**Key shifts (2026-05-28):**
- **Packet-first chart lane** — complete and verify chart parity/local dashboard work before Vercel demotion
- **FRED, news, macro, options data NOW ALLOWED** — local-first removes all TradingView data restrictions
- AutoGluon full-zoo is **no longer locked** — specific model set TBD after deep research
- Past testing results (15m baseline included) are **skewed and unreliable** — do not use as baseline
- Vercel/Next.js dashboard is **pending demotion only after local proof**; do not claim it is decommissioned before replacement proof exists
- Code quality checks: SonarQube (Sonic)

## Live Pine Settings (Reference)

See `AGENTS.md` for the canonical Pine settings table. These values describe the TradingView indicator state. For chart parity work, do not diverge from the active chart-packet authority unless Kirk gives a newer explicit ruling.

## Deeper Context

- Full architecture: `docs/MASTER_PLAN.md`
- Platform plan: `docs/DEVIN_PLATFORM_PLAN.md`
- Agent rules and hard constraints: `AGENTS.md`
- Indicator contract: `docs/contracts/pine_indicator_ag_contract.md`
- Model spec: `WARBIRD_MODEL_SPEC.md`
- Devin control plane: `.devin/wiki.json`, `.devin/environment-blueprint.yaml`, `.devin/playbooks/`

Note: `AGENTS.md` is still the repo instruction surface. Devin-specific repo rules live in `.devin/`, but they do not override `AGENTS.md`, hard safety rules, or explicit current-session user instructions.
