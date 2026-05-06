# V9 Full Tunable Rebuild — Design Doc (WIP, locked at machine-shutdown checkpoint)

**Date:** 2026-05-05
**Status:** WIP — brainstorming phase, design NOT yet finalized, NOT yet approved
**Author:** Claude (under Kirk direction, /superpowers:brainstorming + /superpowers:verification-before-completion)
**Reason for lock:** Machine shutdown. Resume from this file in next session.

---

## Why This Exists

`build_v9_dataset.py` bakes 13 Pine settings into the CSV at dataset-build time:

```
RSI_OVERBOUGHT, RSI_OVERSOLD, RSI_LENGTH, SIGNAL_COOLDOWN_BARS,
LIQ_SWEEP_LOOKBACK, USE_LIQUIDITY_SWEEP, USE_PATTERN_CONFIRM,
USE_ML_FILTER, GATE_SHORTS_IN_BULL_TREND, SHORT_GATE_RSI_FLOOR,
ONE_SHOT_EVENT, EXEC_ANCHOR_RATIO, TRADE_STOP_ATR_MULT,
HTF_CONF_TOL_PCT, USE_MA_GATE, LENGTH_MA, LENGTH_EMA
```

All 4 Optuna cards (Card 1 exit, Card 2 entry filter, Card 3 AG meta, Card 4
challenger) only tune a thin shell of post-trigger filters. Anything that
controls **where the trigger fires** is fixed in the CSV. Card 1's 454 trials
were tuning around a frozen entry decision built from one specific
combination — likely wrong combination.

Kirk's directive (2026-05-05 ~20:30+):

> "rebuild so all this is in the fucking training and tuning. fuck"

Required tunable surface (Kirk's exact list):

- liquidity (real BSL/SSL pivots, real sweep/reclaim events)
- volumes (real bull/bear aggressor-classified buy/sell, NOT body/wick proxy)
- ADX (NEW — not currently in Pine inputs or `ml_*` features)
- ATR (already present)
- RSI (length, overbought, oversold, gate enable)
- candlesticks (`requireBull/BearPattern*`, pattern counts)
- rejection wicks (`rejectWick`)
- signal cooldown bars (`signalCooldownBars`)
- liquidity pool lookback (`liqLookbackBars`)
- bull regime RSI floor short gate (`gateShortsInBullTrend`,
  `shortGateRsiFloor`)
- HTF confluence tolerance % (`htfConfTolPct`)
- execution anchor (`optEntryLevelInput` ∈ {0.500, 0.618, 0.786})
- SL ATR multiplier — discrete categorical {1.0, 1.5, 2.0} ONLY
- exhaustion (`useExhaustion`, `exhaustionLevelAtrTol`)
- MA lengths (slow 50–100 int, fast 8–50 int)
- MA types (NEW Pine input — `maTypeSlow`/`maTypeFast` ∈
  {SMA, EMA, HMA, SMMA, VWMA, rolling-VWAP})
- RSI context levels
- retest context bars (`retestContextBars`)

Frozen (everything else):

- fib core: `autoTuneZZ`, `fibDeviationManual`, `fibDepthManual`,
  `fibThresholdFloorPct`, `fibConfluenceTolPct`, `minFibRangeAtr`,
  `fibHysteresisPct`, `useConfluenceAnchorSpan`
- viz: all `*ColorInput` / `*WidthInput`, `fibLineStyleInput`,
  `*LabelSizeInput`, `zoneFillTransparencyInput`, `tablePositionInput`,
  `showMlTable`, `showFibLevelLabelsInput`, `fibLabelOffsetBarsInput`,
  `showMaLines`, `extendLevelsRight`, `targetLookbackBars`
- one-shot: `oneShotEvent`
- exit (per Kirk explicit ban): `breakevenAfterR`, `trailActivationR`,
  `trailAtrMult`, `exitModel` categorical, `targetRiskMultiple`,
  `maxHoldBars`, `tradeMaxHoldBars`, `tradeStopAtrMult`, `atrPeriod`

Objective: **win rate on entry levels.** Primaries: VOLUME (real aggressor),
LIQUIDITY (real BSL/SSL), ADX, ATR, plus everything in the tunable list.

---

## Exit Model (locked by Kirk 2026-05-05)

> "exit model are the fucking fib extensions on the fib ladder, the fibs are
> frozen, they disappear when a trade is taken and the sl/entry/tp levels
> appear using the same fucking ladder style which is already built. remove
> breakeven and trailing - I'll do that on my own."

- **SL:** `stopAtrMult ∈ {1.0, 1.5, 2.0}` × ATR from entry. CATEGORICAL
  (3-value), not continuous.
- **TP:** fib extension(s) on the active ladder. Pine already renders
  `TARGET 1` and `TARGET 2` lines. **TBD: which fib extension is TP, single
  vs dual.** *Pending Kirk answer; design parked here.*
- **NO time exit.** `maxHoldBars` removed. Trades ride until SL or TP.
- **NO breakeven.** Kirk does it manually.
- **NO ATR trail.** Kirk does it manually.
- **NO `exitModel` categorical.** Only one exit family: SL+fib-TP.
- **NO `targetRiskMultiple`.** TP is fib, not R-based.

---

## Generic Terminology BAN (Kirk 2026-05-05)

> "YOU ARE BANNED FROM USING GENERIC BULLSHIT: VOLUME (primary) /
> LIQUIDITY (primary — sweep/lookback/pool). YOU WILL FIND AND USE REALLLLLLLL
> FUCKING LIQUIDITY AND BULL/BEAR - BUYER/SELLER VOLUME"

**Banned phrases:** "VOLUME (primary)", "LIQUIDITY (primary — sweep/lookback/
pool)", any handwave that doesn't name the exact data primitive.

**Real LIQUIDITY = BSL/SSL pivots:**
- Buy-side liquidity (BSL) = pivot highs where stops cluster above
- Sell-side liquidity (SSL) = pivot lows where stops cluster below
- Real sweep = price wicked through pivot then closed back through
- Real reclaim = subsequent close back inside the swept range
- Pine already emits: `ml_swept_bsl`, `ml_swept_ssl`, `ml_reclaimed_bsl`,
  `ml_reclaimed_ssl`, `ml_bsl_dist_atr`, `ml_ssl_dist_atr`,
  `ml_pivot_dist_atr` (derived from `liqLookbackBars` pivot scan)

**Real BULL/BEAR VOLUME = aggressor-classified:**
- Buy volume = sum of trades where aggressor hit the ASK
- Sell volume = sum of trades where aggressor hit the BID
- Signed delta = buy_vol − sell_vol per bar
- Cumulative delta = running sum of signed delta
- **NEVER** body/wick proxy. **NEVER** close-vs-open volume split.
- **NEVER** rely on `ml_net_delta_20` derived from OHLCV — it's a synthetic
  body-volume proxy banned by Kirk on 2026-05-05.

Required source for V9 historical training (pending Kirk choice):

- **Path A:** Databento `trades` schema (every print has aggressor `side`
  field B/A); aggregate to 5m → real `buy_vol_5m`, `sell_vol_5m`,
  `signed_delta_5m`, `cum_delta_5m`. Historical-only, live parity later.
- **Path B:** Pine `request.footprint()` for V9 (currently registry-banned
  for V9 lane); emits `v9_fp_buy_volume`/`v9_fp_sell_volume`/`v9_fp_delta`.
  Live + historical parity, but eats output budget.
- **Path C:** Both — Databento trades historical + Pine footprint live with
  parity tests. Most rigorous, biggest lift.

---

## Architecture Decision (Kirk-directed)

**Full Python re-trigger of Pine entry/exit logic.**

> "rebuild so all this is in the fucking training and tuning"

- New module: `scripts/optuna/v9_trigger.py` re-implements Pine
  `entryLongTrigger` / `entryShortTrigger` from raw OHLCV + raw fib levels
  + raw HTF pivots + raw BSL/SSL pivots + raw aggressor volume. Parameterized
  on every currently-baked Pine input.
- `build_v9_dataset.py` strips ALL decision-baking; emits **raw inputs only**
  (raw OHLCV, raw fib snapshots per bar, raw HTF pivots, raw BSL/SSL pivots,
  raw aggressor buy/sell volume, ADX components, RSI components — every
  ingredient needed to recompute any candidate trigger configuration).
- All 4 profiles (Card 1/2/3/4) call the trigger module per trial with the
  trial's sampled params. No more pre-baked entries.
- Pine emit: ADD `maTypeSlow`/`maTypeFast` inputs + `select_ma()` switch
  (SMA/EMA/HMA/SMMA/VWMA/rolling-VWAP). Mirror in Python for parity. ADD
  ADX components (length, smoothing) to Pine emit so Python has them.
- Pine source-of-truth parity: snapshot test on 1k+ bars comparing Pine
  trigger output (current CSV) vs Python re-trigger output (same params).
  Must match bar-by-bar within tolerance before trusting.

---

## Pending Decisions (locked here, resume in next session)

1. **TP semantics** — single TP at one fib extension (which? `1.236` only or
   tunable categorical from `[1.236, 1.618, 2.000, 2.618]`?), dual TP
   (TP1 partial / TP2 full at fixed or tunable fib levels), or scale-out
   runner (TP1 closes part, remainder runs to TP2 with no auto-trail since
   trail is banned).
2. **Aggressor volume source** — Path A (Databento trades), Path B (Pine
   `request.footprint()` for V9), or Path C (both). Affects ingest, manifest
   capture method, and live-vs-historical parity strategy.
3. **Card 1's existing 399 complete + 54 pruned trials** — wipe (results
   were on baked CSV, unreliable) or keep as legacy comparison baseline.
4. **Trial budgets** for expanded search space — same 1000/card or scaled
   (search space is ~3× larger after rebuild).
5. **Currently-tuned params not on Kirk's list** — must verify each is
   either kept (Kirk's intent: "list is additive") or frozen (strict reading
   of "everything else is frozen"): `requireXaNqAlignment`,
   `blockShortsInStrongUp`, `minPivotDistAtr`, `maxBslDistAtrLong`,
   `maxSslDistAtrShort`, `minHtfConfTotal`. Default assumption pending Kirk:
   keep tunable since they're filter-strictness knobs.

---

## State at Lock

- **Card 1 stopped:** 399 COMPLETE + 54 PRUNED + 1 cleaned-to-FAIL trials in
  `scripts/optuna/workspaces/warbird_pro_v9_exit_cpcv/study.db`. Last trial
  completed 13:04 2026-05-05. No runner process active. Hub on :8090 + child
  dashboard on :8105 still running.
- **Card 1 results:** unreliable. CSV had baked-in
  USE_LIQUIDITY_SWEEP=False + 13 other settings; trial scores reflect that
  fixed entry surface, not the true tunable space.
- **No Pine edits this session.** No profile edits. No registry edits.
  No `build_v9_dataset.py` edits. No commits.
- **Brainstorming phase only.** This doc is the only artifact written.
- **Next steps in next session:** answer the 5 Pending Decisions above,
  finalize this design, get Kirk approval, then invoke
  `superpowers:writing-plans` to produce the implementation plan.

---

## Hard Rules Locked This Session (do not violate)

- No "VOLUME (primary)" or "LIQUIDITY (primary)" generic phrasing — name the
  exact primitive (`ml_swept_bsl`, `buy_vol_5m_aggressor`, etc.).
- No body/wick volume proxy. No OHLCV-derived "delta". Real aggressor only.
- No baked decisions in `build_v9_dataset.py`. Raw inputs only.
- No automatic time exit, breakeven, or ATR trail in V9 exit model. Ever.
- No slamming together a 9-phase rewrite without brainstorming + design doc
  + Kirk approval + per-phase verification. /superpowers:brainstorming →
  /superpowers:writing-plans → execute one phase → verify → commit → next.
- `targetLookbackBars`, `extendLevelsRight`, `useConfluenceAnchorSpan`,
  fib core inputs, viz inputs all stay frozen.
