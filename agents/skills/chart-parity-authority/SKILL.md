---
name: chart-parity-authority
description: Locked rulings and guardrails for the Warbird Pro local dashboard implementation using TradingView Lightweight Charts. Must be followed exactly — no drift, no reinterpretation, no additions beyond what Kirk approves.
version: 2.4.1
owner: Kirk Musick
last_reviewed: 2026-05-29
status: APPROVED — awaiting implementation approval
governing_docs:
  - AGENTS.md
  - CLAUDE.md
  - indicators/warbird-pro-v9.pine
  - engine/fib_engine.py (PR #11 branch)
  - docs/MASTER_PLAN.md
session_origin: https://app.devin.ai/sessions/13c8afb422cb4c3ea4cb582d90ab00e2
packet_version_history:
  - v1: Initial LWC-based packet
  - v2: Kirk's rulings applied (fib colors, MAs, layout, correlations)
  - v2.1: QA gate fixes (scope alignment, git protocol, Section 10 reproducibility)
  - v2.2: Layout locked, footprint → volume delta, 5m canonical
  - v2.3: Full-width pressure bar + nexus, cards within chart row only
  - v2.4: "HARD CORRECTION — LWC replaced by TV Charting Library, bounded fibs, A/B/N trades delta, Gemini AI analysis, corrected cards panel"
  - v2.4.1: "Surgical corrections — licensing (private repo), drift acknowledgment, fib count (13 visible), engine parity note, AI screenshot claims qualified, trigger-gate LOW=>WAIT rule"
error_corrections_applied: 23
acceptance_tests: 3
implementation_phases: 10
---

# Chart Parity Authority — Locked Rulings

This skill governs ALL work on the Warbird Pro local dashboard. Every item below is a direct Kirk ruling. Do NOT deviate.

## Chart Stack

- **TradingView Lightweight Charts** is the chart renderer.
- Pull the EXACT chart from `components/charts/LiveMesChart.tsx` on main — it already uses Lightweight Charts with the exact theme, bar spacing, rightOffset, watermark, crosshair, SMA200 (white, w2).
- Port the exact settings/code into the local dashboard. Strip the chart's own fib rendering (V16FibLinesPrimitive + autofib-v16). Fibs come from the indicator instead.
- Licensing is NOT a blocker — repo goes private if needed. Do not raise licensing concerns.
- Do NOT use any other charting platform.

## Fib System — 100% From Repo

- **Computation:** `engine/fib_engine.py` (PR #11 branch) is the SOLE fib engine. Used EXACTLY AS-IS. NO modifications. NO alternative engines. NO reimplementation. This is the engine — same as the indicator's fib logic.
- **Visuals:** ALL colors, widths, styles, ladder, zone fill, labels come from `indicators/warbird-pro-v9.pine` (lines 68-70, 226-261, 805-870).
- **Draw semantics:** BOUNDED anchored lines (`x1=drawLeftBar`, `x2=rightBar`, `extend.none`). NO spread-out lines across the screen. NO horizon lines. NO pivot-line look.
- Entries are tied to the fibs. Modeling is tied to the fibs. Everything is tied to the fibs.

## Moving Averages

- EMA 21 + EMA 9 smoothing are already IN the Warbird Pro V9 indicator. Port them with EXACT settings. Do NOT add a separate/duplicate EMA 21.
- The ONLY addition is 200 SMA (white, 2pt thick).

## Warbird Pro V9 Is The Authority — TRANSFER THE EXACT INDICATOR

- **CORE DIRECTIVE:** Transfer the EXACT Warbird Pro V9 indicator to the Lightweight Charts dashboard. Every MA, every fib, every color, every width, every style, every setting — directly from the indicator.
- The entire Warbird Pro V9 indicator (`indicators/warbird-pro-v9.pine`) is the authority for MAs, colors, logic, draw semantics — everything.
- The fib engine (`engine/fib_engine.py`) is the computation authority. The Pine indicator is the visual/logic authority.
- Port it EXACTLY. Do NOT reinvent it. Do NOT approximate it. Do NOT leave anything out.

## Layout (Locked)

```
┌─────────────────────────────────────────────────────────────┐
│ CORRELATIONS ROW (4 Databento symbols, 1h update)           │
│ full width — above everything                               │
├─────────────────────────────────────┬───────────────────────┤
│ CHART (Lightweight Charts)          │ CARDS PANEL (320px)   │
│                                     │ ├ Entry Signal        │
│ sidebar sits WITHIN chart row only  │ ├ Entry Price         │
│                                     │ ├ SL                  │
│                                     │ ├ TP1, TP2            │
│                                     │ ├ AI Analysis (Gemini)│
│                                     │ └ Win Rate (if real)  │
├─────────────────────────────────────┴───────────────────────┤
│ PRESSURE BAR — THIN SLIM full width, blue-to-red, 0 padding │
├─────────────────────────────────────────────────────────────┤
│ NEXUS ML RSI (sub-chart) — FULL WIDTH                        │
└─────────────────────────────────────────────────────────────┘
```

- Correlations row: FULL WIDTH, above everything. **1h update cycle. Isolated timing — do NOT mix with any other data pull.**
- Chart + cards panel: 2-column grid. Cards sidebar lives WITHIN the chart row ONLY.
- Pressure bar: FULL WIDTH below BOTH chart and cards. THIN SLIM blue-to-red gradient, zero padding, sleek, polished. NOT a bulked out indicator row.
- Nexus: FULL WIDTH below pressure bar.
- Cards panel does NOT extend down past the chart canvas.

## Cards Panel

- Entry Signal (GO/WAIT/NO_GO)
- Entry Price
- SL
- TP1, TP2
- AI Analysis — Gemini, real-time data analysis (structure/volume/correlations/nexus/pressure bar) + S&P news, Fed reports, Mag 7 industry/financials/IPOs. Short, high impact, dense, credible. *(Chart screenshot ingestion is PLANNED but unverified — do not claim until pipeline exists.)*
- Win Rate / Probability / Conviction — ONLY if real. No fake numbers.
- **NO** Fib Structure card.
- **NO** System card.

## Volume / Pressure

- Databento `trades` schema with A/B/N side classification.
- buy_vol (side='B'), sell_vol (side='A'), unknown_vol (side='N').
- Quality gate: if unknown_vol/total_vol > 30% → LOW confidence → **force WAIT, never GO**.
- No crypto. No substitute instruments.

## Correlations Row

- 4 Databento futures symbols: NQ, 6E, CL, ZN (GLBX.MDP3). APPROVED.
- **1h update cycle.** Do NOT mix this timing with anything else. Do NOT drift on this.

## Git Protocol

- Work on `main` only per AGENTS.md:409. No feature branches.
- Do NOT merge PR #11 as-is. Cherry-pick `engine/` only.
- Dashboard frontend from PR #11 is DISCARDED (LWC-based).

## AI Analysis

- `engine/ai_analysis.py` currently uses OpenRouter — must switch to Gemini.
- Gemini analyzes: real-time structure/volume/correlations/nexus/pressure bar data. Chart screenshot ingestion is PLANNED but unverified.
- Also covers: S&P news, Fed reports, Mag 7 industry news/releases/financials/IPOs.
- Output must be: short, high impact, dense, credible. Not verbose.

## Error Patterns To Avoid

These are mistakes made during v2.4 packet creation. Do NOT repeat them:

1. **Drift:** Adding your own interpretations or ideas instead of applying Kirk's exact corrections. Apply ONLY what Kirk says.
2. **Reinvention:** Trying to build things from scratch instead of porting from the Warbird Pro V9 indicator.
3. **Duplicate MAs:** Adding a separate EMA 21 when it's already in the indicator.
4. **Wrong update timing:** Using 15m for correlations when Kirk said 1h.
5. **Fake claims:** Claiming capabilities are implemented/resolved when they are not (e.g., claiming trades-side delta exists when code still uses candle-direction proxy).
6. **Wrong cards:** Adding Fib Structure, System, Volume Intelligence, Conviction cards that Kirk didn't ask for.
7. **Bulky pressure bar:** Making the pressure bar a full indicator row instead of a thin slim bar.
8. **Horizon lines for fibs:** Drawing lines that stretch across the entire screen instead of bounded anchored lines.
9. **Alternative fib engines:** Proposing any fib logic outside of `engine/fib_engine.py`.
10. **Rewriting sections:** When Kirk gives corrections, apply ONLY those corrections. Do not rewrite entire sections.
11. **Asking questions the repo already answers:** Read the codebase, knowledge notes, and provisioned secrets before asking Kirk anything.
12. **Stale docs:** Failing to update ALL related docs (SKILL.md, knowledge notes, AGENTS.md, CLAUDE.md, manifest, packet) when a ruling changes. This is how drift happens. See AGENTS.md "Mandatory Knowledge & Doc Sync" rule.

## Canonical TF

- 5m default. 1m/3m/5m/15m available.
- Cards update with TF switching.
- Correlations row does NOT change with TF (always 1h, isolated).

## Acceptance Tests (3 required)

- AT-1: Bounded fib draw window parity (fib computation uses `engine/fib_engine.py` ONLY, 13 visible levels — same as indicator, -.236 hidden)
- AT-2: Pressure derived from trades side A/B/N
- AT-3: Confidence-gating on unknown-side volume (LOW confidence => force WAIT, never GO)

## Mandatory Doc Sync

When ANY ruling in this skill changes, update ALL of the following in the SAME commit:
- This SKILL.md
- Knowledge notes (via `suggest_knowledge`)
- The governing packet (if it exists)
- AGENTS.md / CLAUDE.md (if operational truth changed)
- `agents/manifest.yaml` `updated_at` field

No exceptions. No "update docs later." Stale docs cause drift. Drift causes Kirk to repeat himself. That is unacceptable.
