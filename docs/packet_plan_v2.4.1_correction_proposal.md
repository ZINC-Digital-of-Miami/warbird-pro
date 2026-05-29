# Warbird Pro — Packet Plan v2.4.1 (Corrected Proposal)

**Status:** CORRECTED — aligned with Kirk's locked rulings from planning session
**Supersedes:** Original v2.4.1 proposal (rejected per audit)
**Scope:** Surgical correction of project-plan/implementation drift surfaced by the Audit of Packet 2.4
**Date:** 2026-05-29
**Authority:** Chart Parity Authority Packet v2.4.1 + `agents/skills/chart-parity-authority/SKILL.md`

> This document corrects the original v2.4.1 proposal against Kirk's locked rulings.
> Decisions that were posed as open questions in the original are answered here —
> they were already resolved by Kirk during the v2.4 → v2.4.1 planning session.

---

## 0. Critical findings (resolved)

**A. Target branch:** Work on `main` per AGENTS.md:409. PR #11 branch
(`devin/1779988864-warbird-command-center`) contains `dashboard/` and `engine/`
files — cherry-pick `engine/` only. Dashboard frontend from PR #11 is DISCARDED
(was LWC-based before the LiveMesChart directive).

**B. Line number drift:** The original audit's line numbers no longer match the
live files. Corrected locations from the original proposal are accurate and
retained in the change-set table below.

**C. Canonical packet:** The v2.4.1 packet exists at the planning session level
and is governed by `agents/skills/chart-parity-authority/SKILL.md` (imported
locally from PR #14). No external doc handoff needed.

---

## 1. TradingView — chart stack (RESOLVED)

**Locked ruling:** We use TradingView Lightweight Charts. The repo is public.
Licensing is NOT a blocker — repo goes private if needed. Do not raise
licensing concerns.

**Chart source:** Pull the EXACT chart from `components/charts/LiveMesChart.tsx`
on main. It already uses TradingView Lightweight Charts with the exact theme,
bar spacing, rightOffset, watermark, crosshair, SMA200 (white, w2). Port the
exact settings/code. Strip the chart's own fib rendering (V16FibLinesPrimitive +
autofib-v16). Fibs come from the indicator instead.

No changes needed to the charting dependency. No BLOCKED status.

---

## 2. UI / label drift — unify correlations cadence to 1h

**Locked ruling:** Correlations = 1h update cycle, isolated. Do not mix with
anything else.

**Findings (from original proposal, verified):**
- Correlations already refresh hourly (`DashboardLiveClient.tsx:66`). Good.
- Remaining 15m label drift in `dashboard/` (PR #11 branch):
  - `app.js:580` — conviction card hardcoded "15m" layer
  - `index.html:26` — 15m TF button in chart switcher

**Action:** Remove the "15m" conviction label. Keep 15m as a chart TF viewing
option (1m/3m/5m/15m per locked canonical TF). Do NOT rip 15m out of
`config.py`/`bar_store`/`server` aggregation — those are infrastructure.

---

## 3. Code cleanup — remove volume histogram + wrong cards

**Locked ruling:** Cards panel contains ONLY: Entry Signal (GO/WAIT/NO_GO),
Entry Price, SL, TP1, TP2, AI Analysis (Gemini), Win Rate/Conviction (only if
real). No Fib Structure card. No System card.

**Action (PR #11 branch files):**

`dashboard/app.js`:
- Remove `let volumeSeries = null;` (`:38`)
- Remove `HistogramSeries` creation + `priceScale("volume")` block (`:119-126`)
- Remove `volumeSeries.setData(...)` block (`:270-276`)
- Remove `volumeSeries.update(...)` block in live-bar handler (`:761-765`)

`dashboard/index.html`:
- Remove "Fib Structure" card (`:124-131`)
- Remove "System" card (`:133-150`)
- Remove dead JS refs (`updateSystemCard()`, its `setInterval`, and all
  `fib-card`/`fib-levels` render paths)

System health readout: removed entirely. Not in Kirk's card spec.

---

## 4. Data feed — Databento `trades` schema + A/B/N side aggregation

**Locked ruling:** We have Databento. API key is already provisioned. Use
`trades` schema with A/B/N side classification. No crypto. No substitute
instruments.

**Current:** `engine/databento_feed.py` subscribes `schema="ohlcv-1m"` only.

**Action:**
- Add `trades`-schema path in `databento_feed.py` (Databento `TradeMsg`)
- Aggregate each trade by `side` field into per-bar buckets:
  - `'A'` = ask-side (sell aggressor) → **sell volume**
  - `'B'` = bid-side (buy aggressor) → **buy volume**
  - `'N'` = none/unknown → tracked separately
- Extend `Bar` (`engine/bar_store.py`) with `buy_vol` / `sell_vol` /
  `unknown_vol`
- Keep `ohlcv-1m` as labeled fallback when trades unavailable

No decision needed. Databento entitlement and API key are available.

---

## 5. Trades-side delta + confidence gate

**Locked ruling:** LOW confidence => force WAIT, never GO. This is a hard
trigger-gate rule.

**Action:**
- Compute real trades-side delta from Section 4 buckets:
  `delta = buy_vol - sell_vol`, `delta_ratio = delta / (buy_vol + sell_vol)`
- Replace candle-body proxy at `indicators.py:438-447` with real delta when
  trades data is present
- In `engine/trigger_engine.py` (`:211-217`): if `confidence == "LOW" and
  decision == "GO"` → force `decision = "WAIT"`
- Quality gate: if `unknown_vol / total_vol > 30%` → LOW confidence
- Add unit test: LOW-confidence + high-score => WAIT (never GO)
- Mirror gate wording in code contract doc

---

## 6. Fibonacci — use the EXACT indicator

**Locked ruling:** `engine/fib_engine.py` is the SOLE fib computation engine.
Used EXACTLY as-is from the repo. No modifications. No alternative engines. No
reimplementation. No approximation language. This IS the engine — same as the
indicator's fib logic.

**The original proposal's option 6A ("relabel as approximation") is REJECTED.**
Kirk ruled explicitly and repeatedly: the fib engine is the fib engine, same as
indicator, no approximation disclaimers.

**The original proposal's option 6B ("port ZigZag parity") is NOT NEEDED.**
The engine is used as-is. It is the authority.

**Action:** No changes to `engine/fib_engine.py`. Remove unused imports if they
exist, but do NOT add approximation language, disclaimers, or banners.

### 6c. Visible ladder = 13 (RESOLVED)

**Locked ruling:** 13 visible levels. `-.236` hidden — same as the indicator.
No decision needed.

Pine `warbird-pro-v9.pine:837` has `lineNeg236` `visible=false`, `:874` label
also hidden. The engine's 13 `FIB_LABELS` match. Document `-.236` as hidden SL
reference. No Pine edit.

---

## 7. Accuracy audit — claims vs. reality

- **"No remaining drift found":** Replaced by Section 13 of v2.4.1 packet:
  Current-Code Drift Acknowledgment table with 5 items and exact file:line refs.
- **"AI screenshot-analysis is active":** NOT true in code.
  `engine/ai_analysis.py` is text-only OpenRouter. Chart screenshot ingestion is
  PLANNED but unverified — do not claim until pipeline exists. AI model must
  switch from OpenRouter to Gemini per Kirk's ruling.
- **"TV Charting Library is public":** Corrected — we use Lightweight Charts.
  Licensing is not a blocker.

---

## 8. Corrected change-set summary

| # | File | Change | Risk |
|---|---|---|---|
| 1 | docs + SKILL.md | Chart source = LiveMesChart.tsx exact, licensing not a blocker | doc-only |
| 2 | `dashboard/app.js` | Remove "15m" conviction label, unify to 1h cadence | low |
| 3 | `dashboard/index.html`, `dashboard/app.js` | Remove volume histogram + Fib Structure + System cards + dead JS | low |
| 4 | `engine/databento_feed.py`, `engine/bar_store.py` | Add `trades` schema + A/B/N side aggregation (ohlcv-1m fallback) | med |
| 5 | `engine/indicators.py`, `engine/trigger_engine.py`, contract doc, tests | Trades-side delta + confidence; LOW=>WAIT gate | med |
| 6 | `engine/fib_engine.py` | Clean unused imports ONLY. No logic changes. No approximation language. | minimal |
| 6c | docs only | Document 13-level ladder + hidden `-.236`. No Pine edit. | doc-only |
| 7 | docs + `engine/ai_analysis.py` | Remove false claims; switch OpenRouter to Gemini | low-med |

---

## 9. Testing plan

- `npm run lint` + `npm run build` (Next.js side must stay green)
- `pytest` for engine: (a) A/B/N aggregation, (b) trades-side delta,
  (c) LOW-confidence => WAIT gate. Run existing contract tests.
- Manual dashboard smoke (browser recording): confirm volume histogram gone,
  wrong cards gone, conviction shows no "15m", chart renders + EMAs + fibs
- Databento: validate `trades` ingestion against historical data using the
  provisioned API key; verify ohlcv-1m fallback path

---

## 10. Decisions (ALL RESOLVED — no questions for Kirk)

All decisions from the original proposal have been answered by Kirk's locked
rulings during the v2.4 → v2.4.1 planning session:

| Original Question | Resolution |
|---|---|
| Target branch? | `main` per AGENTS.md:409. Cherry-pick engine/ from PR #11. |
| Packet doc location? | Governed by `agents/skills/chart-parity-authority/SKILL.md` |
| Remove 15m chart TF button? | Keep 15m as chart viewing option. Remove 15m cadence label only. |
| Databento trades entitlement + API key? | Available. Already provisioned. Do not ask Kirk for it. |
| Fib parity: relabel or port? | Neither. Use engine as-is. No approximation language. Same as indicator. |
| Ladder: 13 or re-enable -.236? | 13 visible. -.236 hidden. Same as indicator. |
