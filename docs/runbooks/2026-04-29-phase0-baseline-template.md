# Phase 0 — Baseline Measurement Template

**Date:** 2026-04-29
**Status:** Template — to be filled by Architect
**Campaign:** `docs/plans/2026-04-29-entry-exit-exhaustion-optuna-campaign.md`
**Work surface:** `indicators/v7-warbird-institutional-backtest-strategy.pine` on `codex/wb-opt-bt-first-structural-fibs` branch (paste, pre-Phase-0.5)

## Purpose

Establish the score-to-beat. Every later phase compares its winning configuration against THIS baseline. Without it, "improvement" is undefined.

## How To Run

1. **Branch:** Switch your TradingView Pine Editor to the paste-branch source (the version visually validated, NOT main, NOT the post-Phase-0.5 ported version). This baseline measures the strategy AS IT IS BEFORE the four-guard port.

2. **Defaults:** Use the strategy's input defaults exactly as committed. Do NOT tune any inputs for this run. The campaign needs the un-tuned baseline.

3. **Symbol:** MES1!

4. **Bar Magnifier:** ON (already enabled in `strategy()` declaration).

5. **Slippage:** 1 tick (already pinned).

6. **Commission:** $1.00/side (already pinned).

7. **Per-timeframe runs:** 5m, 15m, 30m, 1h. Run each timeframe SEPARATELY. Do NOT blend results.

8. **Date range per TF:** Use the TradingView default historical window for each TF (the platform's max-bars-back). Document the actual start/end date the run captured.

## Walk-Forward Split (Define Once, Apply To All Phases)

Architect: pick a split rule and stick with it for the entire campaign. Recommendation:

- **Training window:** rolling 6 months (most recent 6mo for each fold).
- **Validation window:** the immediately-following 1 month.
- **Number of folds:** 4 (covers ~10 months of out-of-sample data).
- **Step:** advance by 1 month between folds.

Example with today as 2026-04-29:
- Fold 1: Train 2025-09 → 2026-02, Validate 2026-03
- Fold 2: Train 2025-10 → 2026-03, Validate 2026-04
- Fold 3: Train 2025-08 → 2026-01, Validate 2026-02
- Fold 4: Train 2025-07 → 2025-12, Validate 2026-01

Adjust per available history per TF (5m has shorter window than 4h).

**Approve / modify the split here and the value sticks across all phases.**

## Per-TF Baseline Metrics

### 5m

| Metric | Value | Notes |
|---|---|---|
| Backtest start date | | TV window-bounded |
| Backtest end date | | |
| Total trades | | |
| WB_LONG entries | | |
| WB_SHORT entries | | |
| Trades / day (RTH only) | | |
| Net P&L ($) | | |
| Profit Factor | | |
| Win rate (%) | | |
| Avg win ($) | | |
| Avg loss ($) | | |
| Max Drawdown ($) | | |
| Max Drawdown (%) | | |
| Avg time in trade (bars) | | |
| **Diamond fires / session (bull)** | | Critical — should be near zero per crisis memo |
| **Diamond fires / session (bear)** | | Same |
| Long TP / Short TP hits | | |
| Stop-out count | | |

### 15m

(same table)

### 30m

(same table)

### 1h

(same table)

## Regime Tagging

For each TF, segment the backtest into regime windows. Document baseline metrics within each regime so later phases know whether they're improving the WHOLE strategy or just one regime.

**Regime definitions:**
- **Trending up:** ADX > 25 AND `close > ema100` AND `ema100 > ema100[20]`
- **Trending down:** ADX > 25 AND `close < ema100` AND `ema100 < ema100[20]`
- **Ranging:** ADX < 20
- **Transition:** 20 ≤ ADX ≤ 25

Architect: tag each fold's bars with regime, sum trades per regime, compute per-regime PnL/PF/DD. Doesn't have to be precise — visual estimation from chart is acceptable for baseline.

| Regime | 5m PF | 15m PF | 30m PF | 1h PF | Notes |
|---|---|---|---|---|---|
| Trending up | | | | | |
| Trending down | | | | | |
| Ranging | | | | | |
| Transition | | | | | |

## Sanity Checks Before Considering Baseline "Locked"

- [ ] Each TF's run completed without TV errors.
- [ ] Bar Magnifier flag is ON (visible in Strategy Tester properties).
- [ ] Slippage = 1 tick, Commission = $1.00 (TV defaults match `strategy()` declaration).
- [ ] Diamond-fires-per-session counts confirm the dead-diamond crisis (likely 0).
- [ ] Trade counts non-zero on at least 2 of 4 TFs (otherwise the strategy is too restrictive at defaults to even baseline).

## When This Phase Completes

Architect signs off on this filled-in template. The numbers become the immutable baseline reference for Phase 1-7 success/regression evaluation. Do not retro-edit baseline metrics later — if you discover something off, document it in a follow-up note rather than overwriting.
