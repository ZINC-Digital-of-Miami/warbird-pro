# Plan — Entry / Exit / Exhaustion Optuna Campaign (Phased, Multi-Leg)

> **Push Protocol Override (2026-05-16):** Use `main` and push with `git push origin main` only after explicit user approval in-session and passing hooks. If this historical plan contains older push wording, this override controls. Never use `git push --force`, `git push -f`, or `git push --no-verify`.

**Date:** 2026-04-29
**Status:** PROPOSED — awaiting Architect approval. Replaces the standalone confirmation-gate plan as the canonical campaign doc; the standalone plan is now Phase 2 of this campaign.
**Mission:** Nail entries and exits, with reliable heads-up exhaustion warning so the operator knows when to manage out.
**Cross-references:**
- `docs/plans/2026-04-29-confirmation-gate-optuna-phase.md` — Phase 2 detailed spec (patterns + MA)
- `docs/research/2026-04-29-candlestick-tf-priority-data.md` — Phase 2 data backbone
- `docs/research/2026-04-29-fib-anchor-tf-failure-modes.md` — anchor-side gap (out of this campaign — fib core locked)
- `docs/research/2026-04-29-fib-anchor-labeling-sheet.md` — deferred until campaign completes
- `docs/research/2026-04-29-15m-orderflow-reference-coverage.md` — reference parking lot
- `docs/runbooks/wbv7_institutional_optuna.md` — Optuna workspace contract
- AGENTS.md L150-153 — fib core lock (respected throughout)

---

## 1. Locked Surfaces

**Reversed earlier recommendation 2026-04-29:** Architect corrected my main-vs-paste choice. Visual stability + weeks of iteration on the paste branch outweigh theoretical execution-quality differences. Paste branch is the work surface; main's missing execution guards get ported into paste as Phase 0.5.

| Role | File | Branch | Permission |
|---|---|---|---|
| **Work surface** (the strategy being tuned) | `indicators/v7-warbird-institutional-backtest-strategy.pine` | `codex/wb-opt-bt-first-structural-fibs` (paste) | Pine edits with explicit per-session approval. Fib core (`fibHtfSnapshot`, `fibZzSource`, anchor ownership transitions, fib ladder math, trade fib freeze internals) remains LOCKED per AGENTS.md L150-153. **Visual contract enforced by `scripts/guards/check-visual-contract.sh`** — see Phase 0.5. |
| **New daily indicator** (to be created in Phase 0.7) | `indicators/v7-warbird-backtest-indicator.pine` (proposed name) | TBD | Derived from paste-branch strategy by stripping `strategy()` wrapper and entry/exit calls. Becomes daily live-chart surface and AG-export ground truth. |
| **On ice** (frozen reference, never touched) | `indicators/v7-warbird-institutional.pine` | main | NO edits during this campaign. Stays as legacy reference. |
| Out of campaign | `v7-warbird-strategy.pine`, `warbird-nexus-machine-learning-rsi*.pine`, `fibs-only.pine` | any | Untouched. Separate lanes. |

Main is the chaotic-fib-incident-revert lane (commits like `kirk-revert-strat-2026-04-28-fib-incident`, `revert: restore wb opt bt fib anchors`). The paste branch is the stable iteration surface where Architect built the visual contract over weeks. Main remains valuable as the source for the four execution-guard features being ported in Phase 0.5.

---

## 2. Diamond Detectability Crisis (Phase 1 trigger)

**As of 2026-04-29: zero exhaustion diamonds firing on the work surface across any chart.**

Diagnosis (static analysis, both paste and main share identical logic at line 979):

```pine
bullishExhaustion = mlExhSessionValid AND confirmed AND isSwingLowBar AND bullCooldownOk AND bullFpTriple AND bullCandleProven
```

**Architect confirmed TradingView Premium subscription 2026-04-29 → footprint subscription tier is NOT the cause.** The remaining possible causes, ranked:

1. **Primary suspect — joint probability of the AND-chain is structurally near-zero.** Independent gate estimates: `isSwingLowBar` (~10%) × `bullFpTriple` (~30% with footprint live) × `bullCandleProven` (~3% — strict wick ratios `lowerWickRatio >= 0.55 AND upperWickRatio <= 0.25` for `longLowerShadow`) ≈ 0.1% of bars ≈ 1 diamond every ~12 trading days on 5m. Even with Premium, the gate is a near-zero-probability conjunction.
2. **Compounding suspect — the hardcoded pattern set is sign-mis-grounded.** Per `docs/research/2026-04-29-candlestick-tf-priority-data.md`, the patterns gating `bullCandleProven` and `bearCandleProven` are not just rare — they're the wrong patterns. Long Lower Shadow loses on 5m/10m. Long Upper Shadow catastrophically loses on 4h. So even on the rare bar where the AND-chain aligns, the signal quality is poor or inverted.
3. **Tertiary edge case — footprint backfill on Strategy Tester historicals.** Even with Premium, `request.footprint()` may return `na` on bars beyond the chart's footprint backfill window. This is a quick visual check (open a footprint pane in TV, confirm numbers populate on the test bars) — not a primary hypothesis given the joint-probability finding above.

This is Phase 1's first deliverable. Optuna tuning of the diamond gates is meaningless until the gate fires at all.

---

## 3. Campaign Phases — Sequential, Hyper-Clean

Each phase has a closed parameter set. **No parameter is tuned in more than one phase.** After each phase completes:

1. The winning parameter set is **frozen** — it becomes a fixed input to all downstream phases.
2. The strategy_tuning_space.json (or successor config) is updated to drop the just-frozen knobs and add the next phase's knobs.
3. A walk-forward validation gate is passed before the phase is marked complete.
4. The Optuna study DB for that phase is archived under `scripts/duckdb_local/workspaces/<phase_name>/`.

**Phase order (each builds on the previous):**

| Phase | Owns | Frozen by start of phase | Touch Pine? |
|---|---|---|---|
| **0. Baseline** | None — measure only | None | No |
| **0.5. Visual safeguards + four-guard port** | Visual contract manifest + frozen snapshot + guard script (built); port `strategy.cancel` paths, `lastConsumedLong/ShortEntryIdx`, `entryPrice := strategy.position_avg_price`, `prevClose` wick rejection from main into paste | None | YES — additive only, fib core untouched, visual contract enforced |
| **0.7. Indicator extraction** | New `v7-warbird-backtest-indicator.pine` derived from paste strategy (strip `strategy()` wrapper, drop entry/exit calls, retain everything else) | Phase 0.5 | YES — new file creation, visual contract preserved verbatim |
| **1. Diamond Detectability Fix** | AND-chain → weighted score gate restructure; placeholder candle-proven set using existing `wickRejectBull/Bear` | Phases 0.5, 0.7 | YES — code restructure |
| **2. Entry Gate (Patterns + MA)** | Top-6 pattern toggles, MA fast/slow/trend periods | Phase 1 winners | Yes — pre-Optuna prep per `2026-04-29-confirmation-gate-optuna-phase.md` |
| **3. Diamond Tuning** | `optImbalanceRows`, `zeroPrintVolRatio`, `exhaustionLevelAtrTol`, swing lookback, `exhCooldown`, Phase 1 weights/threshold | Phases 1-2 | Possibly — only if `exhCooldown` becomes an input (currently hardcoded 8) |
| **4. Stop / Target Structure** | `optStopAtrMult`, `optMaxRiskAtr`, `optEntryLevelInput`, `backtestExitTargetInput` | Phases 1-3 | No (knobs already exist) |
| **5. Setup Lifecycle** | `setupExpiryMinutesInput`, `cooldownBarsInput` | Phases 1-4 | No |
| **6. Regime Gates** | ADX trending floor, ADX exhaustion ceiling (NEW), `gateShortsInBullTrend`, `shortTrendGateAdx` | Phases 1-5 | Yes — adding ADX exhaustion ceiling input |
| **7. Full Integrated Validation** | Multi-year walk-forward across regimes; compare to Phase 0 baseline; fakeout-rejection check (per `docs/research/2026-04-29-fakeouts-to-avoid.md`) | All previous | No |

---

## 4. Phase Detail

### Phase 0 — Baseline

Measure-only. No tuning. Establishes the score-to-beat.

**Deliverables:**
- Strategy Tester runs at default settings on MES 5m, 15m, 30m, 1h. Document PnL, PF, Max DD, win rate, trades/day, avg time-in-trade, **diamond fires/day per TF**, and number of WB_LONG/WB_SHORT entries.
- Walk-forward split definition: training/validation periods that all subsequent phases use identically.
- Regime tagging: which baseline metrics come from trending vs ranging segments.

**Success criterion:** documented numbers exist; campaign has its yardstick. No code changes.

### Phase 0.5 — Visual safeguards + four-guard port

**Goal:** Lock the visual layer mechanically AND port the four execution-quality features main has but paste lacks. Both must complete before Phase 1 touches code.

**Visual safeguards (already built 2026-04-29):**
- `docs/contracts/visual_contract_line_ranges.md` — 14-region marker-based manifest
- `.references/visual_contract_frozen_2026-04-29.txt` — verbatim snapshot of all 14 regions
- `scripts/guards/check-visual-contract.sh` — mechanical diff guard, tested with 5 scenarios (unmodified PASS, color/width/rename/structural FAIL, signal-edit PASS)

**Four-guard port from main into paste (additive only):**
1. `strategy.cancel("Long")` / `strategy.cancel("Short")` paths — main has 8+ explicit cancels at SETUP→ACTIVE transition, EXPIRED state, and exit boundaries; paste has 0. Cancels prevent phantom pending orders inflating/deflating trade counts.
2. `lastConsumedLongEntryIdx` / `lastConsumedShortEntryIdx` (and `lastConsumedAnchorHighTime/LowTime`) — main has anti-re-fire guards; paste lacks them. Prevents same fib level from re-firing within the same anchor window.
3. `entryPrice := strategy.position_avg_price` reconciliation — main reads back the actual broker fill on TRADE_ACTIVE transition; paste uses the theoretical `entryLevel`. Affects Optuna metric accuracy under slippage.
4. `prevClose` confirmation on wick rejection — main has `prevClose >= level` / `prevClose <= level` in `wickRejectBull/Bear`; paste has the looser version. Tightens the rejection trigger.

**All four touch the trade state machine block (paste lines ~1140-1280) but NOT the fib snapshot internals (lines ~1280-1320, the `snap*` variables and `tradeFibFrozen` block) which are in locked fib core. Pre-edit verification: the visual-contract guard must pass after each port; the trade state machine is outside all 14 protected visual regions.**

**Success criterion:** all four features merged into paste; visual-contract guard returns green; pine-lint, check-fib-scanner-guardrails, check-contamination, npm run build, indicator/strategy parity all pass; Strategy Tester run on MES 5m/15m produces identical-or-better trade count and PnL vs paste before port (no regression).

**Pine prep (requires explicit per-session approval):** ~30 lines across 4 features in trade state machine block. Each feature is independently reviewable.

### Phase 0.7 — Indicator extraction

**Goal:** Create the daily live-chart indicator that mirrors the paste strategy.

**File:** `indicators/v7-warbird-backtest-indicator.pine` (or alternate name per Architect preference).

**Method (mostly mechanical):**
1. Copy paste strategy file verbatim.
2. Replace `strategy(...)` declaration with `indicator(...)` declaration. Same shorttitle base, e.g. `"Warbird Pro Optuna Live"`.
3. Remove `strategy.entry`, `strategy.exit`, `strategy.cancel`, `strategy.close_all`, `strategy.position_size`, `strategy.position_avg_price` references — these don't exist outside `strategy()`.
4. Trade state machine logic stays — it's just signal computation. The `tradeState` enum, `entryPrice`, `slPrice`, `tp1-5Price` etc. all remain so labels still draw.
5. Remove `default_qty_*`, `commission_*`, `margin_*`, `slippage`, `pyramiding` parameters — strategy-only.
6. Update header comment block to reflect indicator role.

**Visual contract:** copied verbatim, then visual-contract guard re-run against new file with adapted manifest.

**Success criterion:** new indicator file compiles; runs on chart; produces same fib levels, labels, colors as the strategy; AG export columns intact; visual-contract guard passes against an indicator-side snapshot.

**Pine prep (requires explicit per-session approval):** new file creation, mostly copy + targeted deletions. ~50 lines of strategy-specific code removed, no new logic added.

### Phase 1 — Diamond Detectability Fix

**Liquidity-sweep filtering acceptance criterion:** post-Phase-1 logic must filter the liquidity sweeps annotated in `docs/research/2026-04-29-fakeouts-to-avoid.md`. Currently the paste fires `longConfirmed` / `shortConfirmed` on `liqSweepBull` / `liqSweepBear` alone (paste lines 821-828), without requiring diamond co-confirmation. The Phase 1 restructure must:

1. Accept `liqSweepBull` / `liqSweepBear` as a SCORE INPUT to the new weighted exhaustion gate, not as a standalone entry confirmation.
2. Modify the entry chain so `longConfirmed` requires either a pattern OR a wick rejection OR (sweep AND diamond co-occurrence). Same for short side.

Acceptance: each annotated bar in the fakeouts/sweeps research doc must classify as "no entry fired" or "entry invalidated by exhaustion".

**Goal:** Make diamonds fire at a non-zero, operator-meaningful rate before they get tuned.

**Premium confirmed 2026-04-29 — subscription is not the cause. Phase 1 is a code-restructure phase, not an environmental investigation.**

**Investigation + fix steps (in order):**
1. Static code review (DONE in this plan — see Section 2).
2. **One-bar visual check** (no Pine edits): open the footprint pane in TV alongside the strategy on the test chart and confirm numbers populate on the test bars. This is a 30-second sanity check that rules out the tertiary edge case (footprint backfill window). If footprint visibly populates → proceed to step 3. If it doesn't → step 4 covers the fallback path.
3. **AND-chain restructure (primary fix path).** The gate from AND-of-6 to a weighted score-based trigger is the structural fix:
   - Convert the 6 gates into 6 boolean signals each contributing a configurable weight to a confidence score.
   - Diamond fires when score crosses a tunable threshold instead of all 6 simultaneously aligning.
   - Pattern set on `bullCandleProven`/`bearCandleProven` swaps to a placeholder using the safer `wickRejectBull`/`wickRejectBear` already in code (paste lines 833-834) until Phase 2 lands the MUQWISHI-validated patterns.
   - Pine prep: ~15 lines + 2-3 new inputs (weights, threshold).
4. **Footprint-fallback path (only if step 2 reveals no footprint backfill).** Add a non-footprint exhaustion detector using delta sign approximation + wick rejection at swing extreme + cooldown. Out-of-scope unless step 2 says we need it.
5. Pine prep (whichever path of 3 or 4) requires explicit per-session approval before edits.
6. Re-baseline after fix to confirm diamonds now fire at a sane rate (target: 1-3 per session per direction on 5m, 1-2 per day on 15m).

**Success criterion:** diamonds fire at ≥1/session/direction on 5m AND ≥1/day/direction on 15m. No false-positive flood (cap at <10/session/direction). Diamond fires correlate with subsequent adverse price moves vs. trade direction (operator-actionable signal).

**Tuning surface (Optuna):** none in Phase 1 itself — the 2-3 new weight/threshold inputs added in step 3 are tuned in Phase 3 (Diamond Tuning) once Phase 2's patterns are also in place.

**What NOT to touch in Phase 1:** patterns themselves beyond the placeholder swap (Phase 2 owns the real pattern logic), stop/target (Phase 4), entry direction logic (already handled by `dir`), fib core (LOCKED).

### Phase 2 — Entry Gate (Patterns + MA Lengths)

**Detailed in:** `docs/plans/2026-04-29-confirmation-gate-optuna-phase.md`

**Owns:**
- 6 pattern toggles (Engulfing Bull/Bear, Tweezer Bottom Bull, Long Lower Shadow Bull, Hammer Bull, Falling Window Bear) — replaces the sign-error-grounded hardcoded set.
- MA fast (5-25), slow (15-60), trend (30-200) periods — replaces hardcoded EMA9/21/50.

**Frozen at start:** Phase 1 diamond fix (so the strategy is in a valid execution state).

**Pine prep required:** expose pattern toggles as `input.bool`, MA periods as `input.int` with constraint fast<slow<trend.

**Success criterion:** out-of-sample PF improves vs Phase 0 baseline; trade count does not collapse below baseline × 0.5; at least 2 patterns and one MA configuration are non-trivial winners; **fakeout-rejection** — entries on bars annotated in `docs/research/2026-04-29-fakeouts-to-avoid.md` must either not fire OR be immediately invalidated by Phase 1 exhaustion signal.

### Phase 3 — Diamond Tuning

**Goal:** Now that diamonds fire (Phase 1) and entries use the right patterns (Phase 2), tune the diamond's quality.

**Search space:**
| Knob | Current | Range |
|---|---|---|
| `optImbalanceRows` | 2 | 1-3 |
| `zeroPrintVolRatio` | 0.10 | 0.02-0.30 |
| `exhaustionLevelAtrTol` | 0.10 | 0.05-0.30 |
| Swing lookback (currently 10 hardcoded) | 10 | 5-25 (NEW input — Pine prep) |
| `exhCooldown` (currently 8 hardcoded) | 8 | 3-30 (NEW input — Pine prep) |

**Frozen at start:** Phases 1-2.

**Pine prep required:** swing lookback + cooldown bars become inputs (~2 lines each).

**Success criterion:** diamonds correlate with mid-trade adverse moves (e.g., diamond firing within trade lifetime predicts the trade closing at TP1-TP2 instead of TP3-TP5 with statistical significance). The signal must be operator-actionable for "punch out" decisions.

### Phase 4 — Stop / Target Structure

**Search space:**
| Knob | Current | Range |
|---|---|---|
| `optStopAtrMult` | 1.5 | 1.0-3.5 |
| `optMaxRiskAtr` | 3.0 | 2.5-4.5 |
| `optEntryLevelInput` | "0.618" | {"0.500","0.618","0.786"} categorical |
| `backtestExitTargetInput` | "TP1" | {"TP1","TP2","TP3","TP4","TP5"} categorical |

**Frozen at start:** Phases 1-3.

**Pine prep required:** none — all knobs already exist as inputs.

**Success criterion:** PF improves AND average loss size shrinks vs Phase 2 frozen baseline. Walk-forward confirms.

### Phase 5 — Setup Lifecycle

**Search space:**
| Knob | Current | Range |
|---|---|---|
| `setupExpiryMinutesInput` | 180 | 15-720, step 15 |
| `cooldownBarsInput` | 0 (disabled) | 0-50 |

**Frozen at start:** Phases 1-4.

**Pine prep required:** none.

**Success criterion:** stale-setup fills decrease (measured: % of fills more than N bars after setup arming); trade frequency does not collapse.

### Phase 6 — Regime Gates

**Search space:**
| Knob | Current | Range |
|---|---|---|
| ADX trending floor (currently `adxVal > 25`) | 25 | 20-35 |
| ADX exhaustion ceiling (NEW) | n/a | 35-55 (counter-trade rejection gate) |
| `gateShortsInBullTrend` | true | {true, false} |
| `shortTrendGateAdx` | 10.0 | 5-25 |

**Frozen at start:** Phases 1-5.

**Pine prep required:** add ADX exhaustion ceiling as `input.float` and a gate that rejects setups when `adxVal >= ceiling`.

**Success criterion:** chop-period PF improves; trend-period PF stable or improves.

### Phase 7 — Full Integrated Validation

**Goal:** confirm the full campaign produced a strategy that beats Phase 0 baseline by a meaningful margin out-of-sample.

**Method:**
- Multi-year walk-forward (rolling 6mo train / 2mo test, 5+ folds) on MES 5m, 15m, 30m, 1h.
- Regime-segmented analysis: trending up, trending down, chop, post-news, event-day windows (NFP/FOMC/CPI per existing paste detection).
- Compare to Phase 0 baseline: PF lift, DD reduction, diamond signal value, entry win rate, exit timing.

**Success criterion:** out-of-sample PF lift ≥ +X% (Architect chooses threshold); no regime-segment regression > Y% relative to baseline.

**No code changes in Phase 7.** Pure validation.

---

## 5. Hyper-Clean Optuna Hygiene

Each phase strictly observes:

1. **One Optuna study DB per phase**, archived under `scripts/duckdb_local/workspaces/<phase_name>/study.db`.
2. **Search space lock at phase start**: knobs not in this phase are FIXED (frozen winners from upstream phases or defaults for downstream phases). No exploratory tuning of unrelated parameters.
3. **Walk-forward only** — no static train/test splits per `MEMORY.md` and AGENTS.md backtest discipline.
4. **Backtest discipline preserved**: `slippage=1`, `commission_value=1.00`, `use_bar_magnifier=true`, `process_orders_on_close=false` — already in main, not tunable.
5. **Sample-size guards**: any phase that produces fewer than N trades on the validation window has its champion rejected (N = baseline trades/period × 0.5).
6. **Champion = top-1 by primary metric AND consistent across walk-forward folds**, not single-fold winner.
7. **Regression check**: champion must not degrade Phase 0 baseline metrics on any regime segment by more than tolerance T (Architect picks T per phase).
8. **TF-aware**: each phase's champion may be different per timeframe. Optuna runs per TF; results are not blended across TFs unless explicit regime-blend evidence supports it.

---

## 6. Locked Rules Respected

- Fib core (`fibHtfSnapshot`, `fibZzSource`, anchor ownership transitions, fib ladder math, trade fib freeze internals) — UNTOUCHED across all phases.
- Repo-wide fib scanner guardrail (banned `ta.barssince(...)` + `pivotHighInWindow/pivotLowInWindow` pattern) — not reintroduced.
- **Visual contract** — `scripts/guards/check-visual-contract.sh` enforces the 14-region manifest at every Pine touch. Same enforcement tier as fib-core lock.
- No Pine edits without explicit per-session approval. All Pine prep listed per phase.
- No TradingView Pine Editor push without explicit approval.
- Bollinger Bands not in scope (per `feedback_no_bollinger_bands.md`).
- Doc-first discipline — this plan + Phase 2 detail exist before any code change.
- Pine verification pipeline runs on every touch: pine-lint, fib-scanner-guardrails, contamination, **check-visual-contract**, build, indicator/strategy parity.
- Walk-forward required at every phase gate.
- Live indicator (`v7-warbird-institutional.pine`) on ice — no edits.
- Cloud Supabase is runtime/support only — does not receive raw trials, labels, SHAP, or full research datasets per AGENTS.md.

---

## 7. Open Questions for Architect

1. **Approve Phase 0 measure-only baseline as the first action?** No code, no risk — just measurement. Establishes yardstick.
2. **Phase 1 fpAvailable check approach** — is plotting `fpAvailable` for visual diagnosis in TV Strategy Tester acceptable, or would you prefer a different diagnostic?
3. **Per-TF phase parallelism** — run each phase per TF independently (5m, 15m, 30m, 1h all get their own Phase 2 study), or pick a primary TF (15m per memory) and validate others post-hoc?
4. **Phase 7 success threshold X** — what PF lift counts as a successful campaign? Default proposal: ≥ +20% PF improvement out-of-sample, max-DD not worse than baseline.
5. **Approval flow** — explicit per-phase sign-off before that phase's Pine prep / Optuna run, or batch approval per pair of phases?

This plan does NOT begin Pine implementation. Implementation requires explicit per-session approval. Phase 0 (baseline measurement) requires no Pine changes and can begin immediately on approval.
