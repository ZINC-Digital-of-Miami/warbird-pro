# Warbird Pro — Devin Platform Plan

**Created:** 2026-05-28  
**Status:** Draft for refinement — NOT a build plan yet  
**Purpose:** Captures everything discussed, decided, and half-planned so Kirk can review and refine before execution begins.

> **2026-05-29 Supersession Note:** For local dashboard implementation decisions
> (chart stack, fibs, MAs, layout, cards, pressure bar, correlations, AI analysis),
> the authority is `agents/skills/chart-parity-authority/SKILL.md` (v2.4.1).
> Where this plan conflicts with that skill, the skill wins. Key updates:
> - Fib engine (`engine/fib_engine.py`) is used EXACTLY as-is — no modifications, no "evolve independently" language applies to fib computation.
> - Chart source is the EXACT `LiveMesChart.tsx` from main, ported to the local dashboard.

---

## 1. Architecture Direction (Decided 2026-05-28)

### What Changed
- **Vercel/Next.js dashboard** → DECOMMISSIONED. Replaced by local Python engine + TradingView Lightweight Charts v5
- **System is NOT hinged on TradingView live indicator** — the local engine is the primary platform. TV indicator is reference, not the trigger
- **Data restrictions LIFTED** — FRED, macro, news, options data are now allowed. Local-first removes all TradingView constraints
- **AutoGluon full-zoo "locked" config** → UNLOCKED. Specific model set TBD after deep research
- **Past testing results are SKEWED** — 15m/5m/1h baselines from 2026-04-27 should not be relied upon
- **Codacy** → REMOVED. Replaced by SonarQube (Sonic) for code quality checks
- **Cloud Supabase for training** → PROHIBITED. DuckDB for all local data/trade recording
- **Dashboard hosting platform** → TBD. Using TV Lightweight Charts but the hosting/serving platform is not fully chosen

### What Stays
- DuckDB 1.5.2 / Pandera 0.31.1 for data pipeline
- SHAP and Monte Carlo gates as validation concepts (approach, not specific configs)
- Manifest-backed data with honest labeling
- Databento for live MES streaming (free tier, OHLCV-1m included in subscription)
- All Pine protection rules (no edits without approval, budget tracking, no fibHtfSnapshot)

---

## 2. Local Dashboard — Command Center (PR #11)

### What Exists (Branch: `devin/1779988864-warbird-command-center`)

**Python Engine (`engine/`):**
- FastAPI server on port 3100 serving static HTML dashboard
- Databento Live feed → 1m bars aggregated to 1/3/5/15m/1h/4h
- Fib engine: multi-period confluence (8/13/21/34/55 bar lookbacks) — ported from Pine V9
- Trigger engine: zone proximity, rejection wick, volume spike, engulfing, squeeze
- Pressure bar: volume delta (30%), RSI (25%), momentum (20%), TTM squeeze (25%)
- Nexus ML RSI: AMF oscillator ported from Pine v1.2.6
- AI analysis card: OpenRouter → `mistralai/ministral-3b-2512` (~$0.02/day)
- WebSocket push for all updates

**Dashboard (`dashboard/`):**
- Plain HTML/JS/CSS — no React, no Next.js
- Lightweight Charts v5 candlestick chart
- Fib lines as LineSeries (bounded anchor → 8 bars right)
- EMA21 (white, width 2) + EMA9 (teal #26A69A, width 2) overlays
- Golden zone fill between .382–.618
- Pressure bar, Nexus sub-chart, 6 right-panel cards

**Trade Log (`engine/trade_log.py`):**
- DuckDB schema at `data/warbird_trades.duckdb` (gitignored, initialized on first use)
- Tables: `trades`, `trade_tags`, `indicator_state`
- Ready for recording entries, outcomes, pattern tags, and indicator state

### Key Requirement: Slick Dashboard with Fib Logic

The local dashboard is NOT hinged on the TradingView live indicator. The fib engine logic in `engine/fib_engine.py` is used exactly as-is from the repo — no modifications, no alternative engines (see `agents/skills/chart-parity-authority/SKILL.md`). The chart is ported exactly from `components/charts/LiveMesChart.tsx` using TradingView Lightweight Charts.

**Current chart styling (from PR #11):**
- Candle theme: up=#26C6DA, down=#FF0000, borderUp/borderDown=transparent
- Wicks: up=white #FFFFFF, down=rgba(178,181,190,0.83)
- Background: transparent with gradient underneath
- Font: Inter for chart, JetBrains Mono for data
- Bar spacing: 10px (min 8px), right offset: 16 bars
- Crosshair: solid with label backgrounds

**Fib colors (Kirk's live TradingView settings):**
- .382/.618 = RED `#cc0000` solid width 2
- Pivot (.500) = white dashed
- 1.000 = white dotted
- Targets (1.236, 1.618, 2.000, 2.236) = teal `#0097A7`
- Golden zone fill between .382–.618

**Full fib levels (13):**
0, .236, .382, Pivot, .618, .786, 1.000, TP1 (1.236), 1.382, 1.5, TP2 (1.618), TP3 (2.000), TP4 (2.236)

### What's Half-Planned (from `docs/DASHBOARD_PLAN.md` in PR #11)

**Phase B — Fib Rendering (match V9 Pine + Kirk's live screenshots):**
1. Port `V16FibLinesPrimitive` canvas renderer to dashboard (zone fill + proper line drawing)
2. Use Kirk's live color settings for fib colors
3. Add fib labels (ratio + price) positioned 8 bars right of last bar
4. Proper draw span: anchor start bar to `lastBar + 8 bars`
5. Add -.236 stop level, 1.382, 1.5 waypoints, and TP4/TP5 extension levels

**Phase C — DuckDB Setup:**
1. Create `data/` directory
2. Initialize DuckDB at `data/warbird_trades.duckdb` with trade log schema
3. Wire trade recording into the engine (manual or auto based on trigger signals)

**Phase D — Remaining Features:**
1. News feed + econ calendar (Finnhub free tier)
2. Trade log + pattern learning
3. Performance optimization

### Unresolved Dashboard Questions

1. **Hosting platform** — TV Lightweight Charts is the charting library, but what serves/hosts the dashboard? (FastAPI localhost? Electron app? Something else?)
2. **Should fibs drive actual trade entries?** (fib reclaim + MA gate → GO signal + Entry/SL/TP lines + DuckDB recording)
3. **Cron architecture** — Kirk wants "the machine to pull crons, local dashboard off Devin." What crons? Databento backfill? FRED data pulls? News feeds? DuckDB maintenance?
4. **Multiple timeframes on chart** — Currently supports switching between 1m/3m/5m/15m. Is that sufficient or does Kirk want multi-TF overlay?

---

## 3. Deep Research Needed (Before Building)

Kirk explicitly said: "we have to do deep research on the models/data used/fib indicator polishing up/architecture."

### Model Research
- AutoGluon full-zoo was the previous locked config. That's now open.
- Questions to answer:
  - Which specific model families perform best for this domain? (GBM, CatBoost, XGBoost, neural nets, or simpler?)
  - Is the triple-barrier labeling approach optimal, or should we explore other label schemes?
  - What's the right inference threshold? (0.75 was locked — should it be validated?)
  - Should we explore online learning / adaptive models for live trading?

### Data Research
- **Data restrictions are LIFTED** — local-first means FRED, macro, news, options, and any locally accessible data are now approved sources alongside Pine/TV exports + Databento
- Past testing on all models was skewed — cannot rely on prior feature importance rankings
- Questions to answer:
  - What timeframe granularity produces the best signal? (no reliable baseline exists — 15m PF 1.143 from 2026-04-27 is skewed)
  - Is the 1-year data window (2025-05 to 2026-05) sufficient?
  - Which FRED/macro indicators have predictive value for ES/MES entries?
  - What news/events data feeds are available and useful? (Finnhub, others?)
  - Should we add order flow / depth-of-book data from Databento?
  - What features from the 75 ML_FEATURES are actually predictive? (needs fresh SHAP, not skewed results)

### Fib Indicator Polishing
- V9 has 54 output-consuming calls, 10 slots remaining
- Questions to answer:
  - Which fib levels actually predict profitable entries?
  - Should the golden zone (.382-.618) weight be adjustable?
  - Is HTF confluence (1H) adding edge or just complexity?
  - EMA21+EMA9 gate: is this the right MA configuration?

### Architecture Research
- Current: Python FastAPI + WebSocket + Lightweight Charts
- Questions to answer:
  - Is FastAPI the right choice or should we use something lighter (Flask, raw asyncio)?
  - WebSocket vs SSE for real-time updates?
  - Should the fib engine run in a separate process for performance?
  - How should DuckDB handle concurrent reads/writes during live trading?

---

## 4. Devin Platform Setup (Completed)

### Knowledge Notes (Suggested — Awaiting Approval)
1. **Project Architecture & Active State** — V9 indicator, Nexus research, DuckDB stack, training sequence, blockers
2. **Live Pine Settings (Authoritative)** — table of settings from AGENTS.md 181–204
3. **Agent Governance History & Pain Points** — rogue agent incidents, settings contamination, tv_launch incidents
4. **V9 Core Training Pipeline Details** — trainer, labels, features, post-fit gates
5. **Git Protocol & Quality Gates** — main-only, push approval, precheck, lint/build
6. **Dashboard Command Center (PR #11)** — Python engine, LWC, DuckDB trade log, Databento
7. **Code Quality & CI Setup** — SonarQube replacing Codacy
8. **ML Modeling Direction (Pivot)** — AG unlocked, models TBD, data research first

### .devin/ Rules (In Repo)
1. `01-project-overview.md` — Architecture, active surfaces, key shifts
2. `02-hard-rules.md` — Data sources, Pine protection, CDP-down protocol, cloud/DB rules
3. `03-git-protocol.md` — Main-only, push approval, precheck
4. `04-pine-verification.md` — 6 mandatory gates for any .pine edit
5. `05-quality-gates.md` — Precheck, lint/build, SonarQube, contract tests
6. `06-reference-docs.md` — Pointer table to deeper context docs
7. `07-common-mistakes.md` — Domain-specific traps (settings contamination, scope creep, output budget)

### .devin/ Playbooks (In Repo)
1. `pine-edit-workflow.md` — 8-step Pine edit workflow
2. `commit-and-push.md` — 8-step commit/push workflow
3. `v9-training-workflow.md` — Training workflow with AG-unlocked note
4. `dataset-build-workflow.md` — 8-step dataset build with settings verification
5. `shap-monte-carlo-gates.md` — Post-training validation gates
6. `docs-update-workflow.md` — Change type → doc update mapping
7. `supabase-cloud-work.md` — Allowed/prohibited cloud usage

### Platform Playbooks (Submitted for Approval)
1. V9 Pine Edit — mirrors .devin/ playbook at platform level
2. Commit & Push Protocol — mirrors .devin/ playbook at platform level
3. V9 Core Training — with AG-unlocked note
4. Dashboard Engine Development — for Python engine + LWC + DuckDB work

### Environment Blueprint (Suggested — Awaiting Approval)
- npm install with native platform deps
- Git hooks path configuration
- Knowledge entries for lint, build, test, startup, pre_commit

### SonarQube (Sonic)
- `sonar-project.properties` created in repo with exclusion patterns (migrated from old `.codacy.yaml`)
- SonarQube is installed in GitHub as a GitHub App
- Devin MCP integration has placeholder URLs — Kirk can configure at org settings → MCP servers if desired
- All Codacy files, config, references removed from repo

### Wiki
- Generated at https://app.devin.ai/wiki/ZINC-Digital-of-Miami/warbird-pro
- Will auto-update as repo evolves

---

## 5. What Happens Next (Kirk's Call)

This plan captures the current state. Before executing, Kirk should decide:

1. **PR #11** — Merge as-is to get the engine/dashboard foundation on main? Or refine further on the branch?
2. **Dashboard scope** — How "slick as fuck" does the dashboard need to be before we start wiring trade logic? Is the current LWC implementation sufficient, or does Kirk want a complete visual overhaul first?
3. **Cron architecture** — What recurring jobs should run on the local machine? (e.g., Databento backfill, DuckDB maintenance, model retraining, alert monitoring)
4. **Research priority** — Start with model research, data research, fib polishing, or architecture? Or do them in parallel?
5. **Trade entry logic** — Should the engine auto-fire entries from fib reclaim + MA gate, or should it surface signals for manual execution?

---

## Appendix: Pine Settings (Authoritative — 2026-05-14)

| Input | Live Value |
|-------|-----------|
| ZigZag Deviation | 3.0 |
| ZigZag Depth | 10 |
| ZigZag Threshold Floor % | 0.25 |
| HTF Confluence Tolerance % | 1.5 |
| HTF 1H Lookback (bars) | 8 |
| Min Fib Range ATR | 0.5 |
| Midpoint Hysteresis % | 2.0 |
| Primary EMA Length | 21 |
| Primary EMA Source | close |
| Primary EMA Offset | 1 |
| Smoothing Type | EMA |
| Smoothing Length | 9 |

## Appendix: Historical Performance (2026-04-27 Operator Snapshots)

> **WARNING:** These results are SKEWED and should NOT be relied upon for decisions.
> Past testing on all models was compromised. Fresh testing with clean data is required.

| Timeframe | PnL | Profit Factor | Trades | Max DD |
|-----------|-----|---------------|--------|--------|
| 15m | +6.74% | 1.143 | 434 | 3.47% |
| 5m | -2.55% | 0.91 | 295 | 3.44% |
| 1h | -9.26% | 0.929 | 801 | 14.33% |
