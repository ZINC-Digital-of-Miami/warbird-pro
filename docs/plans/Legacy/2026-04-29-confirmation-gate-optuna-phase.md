# Plan — Confirmation-Gate Optuna Phase (Patterns + MA Lengths)

> **Push Protocol Override (2026-05-16):** Use `main` and push with `git push origin main` only after explicit user approval in-session and passing hooks. If this historical plan contains older push wording, this override controls. Never use `git push --force`, `git push -f`, or `git push --no-verify`.

**Date:** 2026-04-29
**Status:** PROPOSED — awaiting Architect approval. **This plan is now Phase 2 of the broader campaign in `docs/plans/2026-04-29-entry-exit-exhaustion-optuna-campaign.md`.** Read the campaign doc first; this doc provides Phase 2 detail.
**Working file:** `indicators/v7-warbird-institutional-backtest-strategy.pine` on **main** (per campaign Section 1 — work-surface lock decision)
**Companion data:** `docs/research/2026-04-29-candlestick-tf-priority-data.md`
**Companion research:** `docs/research/2026-04-29-fib-anchor-tf-failure-modes.md`
**Parent campaign:** `docs/plans/2026-04-29-entry-exit-exhaustion-optuna-campaign.md`
**Cross-references:**
- `docs/plans/2026-04-10-fib-engine-fix-design.md` — anchor-side approved fixes (separate phase)
- `docs/runbooks/wbv7_institutional_optuna.md` — Optuna workspace contract for v7 institutional
- `docs/contracts/pine_indicator_ag_contract.md` — modeling truth contract
- AGENTS.md L150-153 — fib core lock; this plan stays out of that scope
- `feedback_no_bollinger_bands.md` — Bollinger Bands explicitly excluded; no future-candidate listing

---

## 1. Problem and Scope

The paste's confirmation gate (paste lines ~768-810) green-lights entries on a **hardcoded six-pattern set with a sign-error interpretation** of the MUQWISHI dashboard. On 4h MES with 7 years of data, three of the four "proven bearish" patterns are losers and the strongest claimed bullish pattern also loses. See `docs/research/2026-04-29-candlestick-tf-priority-data.md` for evidence.

**This phase replaces hardcoded confirmation logic with Optuna-tuned pattern selection and trend-bias MA lengths.** It does NOT touch fib core, anchor logic, trade state machine fib snapshot internals, or any other locked surface.

**In scope:**
- Pattern enable/disable toggles (per pattern, per direction).
- MA period inputs (replacing hardcoded EMA9 / EMA21 / EMA50 used in `microTrendLong` / `microTrendShort` and trend-bias logic).
- ADX exhaustion threshold (currently fixed at 25/20 trending/ranging; let Optuna search higher exhaustion gates per Architect's reference reading on 15m exhaustion).

**Explicitly out of scope:**
- Fib anchor logic, ZigZag, structural pivot, fib ladder math, trade fib freeze internals (locked).
- Stop/target/exit knobs (existing Optuna phase).
- Bollinger Bands (excluded per Architect preference).
- Footprint logic (already covers absorption / delta divergence / zero-print — no changes proposed).

## 2. Top-6 Pattern Slate (from data, see companion research)

| # | Pattern | Direction | Empirical evidence |
|---|---|---|---|
| 1 | Engulfing (Bull) | LONG | 4h +14% to +17%, 30m +22% to +30% |
| 2 | Engulfing (Bear) | SHORT | 4h +9% to +15%, 5m +4% to +6% |
| 3 | Tweezer Bottom (Bull) | LONG | 4h +19% to +25%, 30m +10% to +14% |
| 4 | Long Lower Shadow (Bull) | LONG | 30m +15% to +32%, 15m +8% at 1:6 |
| 5 | Hammer (Bull) | LONG | 30m +6% to +12% |
| 6 | Falling Window (Bear) | SHORT | 1h +9% to +15% |

Optuna search space: each pattern has a per-direction `input.bool` toggle. Optuna may enable any subset 0..6. The hardcoded MES-15m set in the paste is removed in the same edit.

**Pattern definitions:** the paste must use Warbird-native detectors that match MUQWISHI's library outputs within tolerance on the same chart. Pre-Optuna sanity check fires both detectors side-by-side and confirms agreement before any tuning trial runs.

## 3. MA Length Search Space

Replace hardcoded periods in `microTrendLong` / `microTrendShort` (paste lines ~1163, ~1170) with `input.int`-driven values:

| Knob | Current | Proposed search range | Step |
|---|---|---|---|
| Fast EMA period | 9 | 5–25 | 1 |
| Slow EMA period | 21 | 15–60 | 1 |
| Trend EMA period | 50 | 30–200 | 5 |

Optuna constraint: fast < slow < trend. Otherwise reject the trial.

## 4. ADX Threshold (optional sub-knob)

Currently `regimeTrending = adxVal > 25` and `regimeRanging = adxVal < 20`. Architect's 15m reversal/exhaustion reference highlights ADX > 40-50 as an exhaustion indicator. Make these tunable:

| Knob | Current | Proposed search range |
|---|---|---|
| Trending floor | 25 | 20–35 |
| Exhaustion ceiling | (not gated) | 35–55 (NEW, becomes a counter-trade gate) |

Setups firing while `adxVal >= exhaustionCeiling` get rejected (or weighted lower in confidence). Optional: Optuna may set this very high to disable the gate.

## 5. Pre-Optuna Pine Prep (DRAFT — requires explicit approval before any edit)

Pine prep steps before the search space is reachable:

1. Add `input.bool` for each of the 6 candidate patterns × 2 directions where applicable.
2. Add `input.int` for the three MA periods.
3. Add `input.float` (or `input.int`) for ADX exhaustion ceiling.
4. Replace the hardcoded `provenBullishPattern` / `provenBearishPattern` expressions with toggle-gated versions.
5. Replace hardcoded `ema9`, `ema21`, `ema50` literals with the input-driven periods.
6. Run the Pine verification pipeline (pine-lint, check-fib-scanner-guardrails, check-contamination, npm run build, indicator/strategy parity check).
7. Update `scripts/duckdb_local/strategy_tuning_space.json` (or equivalent) to expose the new knobs.
8. Re-export TV CSV per `docs/runbooks/wbv7_institutional_optuna.md` Section 1 with the new inputs at default values.

These are doc-described, not implemented. **Pine implementation requires per-session explicit approval.**

## 6. Phase Order — How This Fits The Broader Tuning Campaign

Architect's stated workflow (per memory): "lock the fibs on a 5m, we tune everything around it… capture trends, update indicator, backtest, feed Optuna for next run."

This phase fits as one of these placements (Architect chooses):

**Option A — Standalone first phase:**
1. Confirmation Gate (this plan) → freeze winning patterns + MA lengths.
2. Stop/Target/Exit (existing knobs).
3. ADX/regime fine-tune (refine sweet spots).
4. Fib anchor (separate plan, separate locked-rule unlock).
5. Final integrated tuning.

**Option B — Interleaved:**
1. Stop/Target with current confirmation set.
2. Confirmation Gate (this plan).
3. Re-tune Stop/Target with corrected confirmation set.
4. Fib anchor (separate).
5. Final integrated tuning.

Recommendation: **Option A**. Confirmation gate has provable defects right now (sign error). Tuning anything else on top of it will optimize around the defect. Fix it first, then tune downstream.

## 7. Success Criteria

- Confirmation gate uses Optuna-selected pattern subset and MA lengths instead of hardcoded values.
- Out-of-sample (walk-forward) profit factor strictly improves vs. the hardcoded baseline on MES 5m / 15m / 30m / 1h / 4h.
- Trade frequency does NOT collapse — pattern subset must keep enough triggers to be statistically meaningful.
- No regression in fib anchor behavior (anchor is locked; this phase doesn't touch it).
- Pine verification pipeline passes per AGENTS.md Pine Verification section.

## 8. 15m Reversal/Exhaustion Reference Mapping (for future phases, NOT this one)

Architect shared a 15m reversal/exhaustion checklist 2026-04-29. Coverage map for any FUTURE phase that extends the gate:

| Reference signal | Status in current Warbird code | Phase placement |
|---|---|---|
| CHoCH | Exists in `v7-warbird-institutional.pine` lines 307-308 (alerts only). Not used as anchor source or confirmation gate. | Future — fib anchor phase candidate |
| HTF S/R 4H zones | Implemented (`htf4hHigh/Low` + `htfConfluenceCheck`) | Already in code |
| Quasimodo pattern | Not in code | Future — separate plan |
| RSI divergence | RSI computed (`rsi14`, `f_rsi_knn`); divergence logic not present | Future — separate plan |
| **Bollinger Band rejection** | **EXCLUDED per Architect preference** | **Never** |
| ADX > 40-50 exhaustion | ADX computed; exhaustion threshold not gated | This phase (Section 4) |
| Volume exhaustion / climax | Footprint delta, POC, imbalance present; "climax then reversal candle" detection not present | Future — separate plan |
| Footprint absorption | Implemented (`mlExhAbsorption`, `mlExhDeltaDiv`, `mlExhZeroPrint`) | Already in code |
| VWAP reversal | Implemented (`vwapCode` ±2 reclaim/reject) | Already in code |

This phase only consumes ADX threshold tunability. Quasimodo, RSI divergence, climax volume are explicit follow-up phases (separate plans).

## 9. Locked Rules Respected

- Fib core (`fibHtfSnapshot`, `fibZzSource`, anchor ownership transitions, fib ladder math, trade fib freeze internals) — UNTOUCHED.
- Repo-wide fib scanner guardrail (banned `ta.barssince(...)` + `pivotHighInWindow/pivotLowInWindow` pattern) — not relevant to this phase, will not be reintroduced.
- No Pine edits this turn. Plan-only.
- No TradingView Pine Editor push.
- Bollinger Bands not in scope.
- Doc-first discipline — this plan exists before any code change, and any subsequent code change requires explicit per-session approval.
- Pine verification pipeline will run on any touch.
- Walk-forward validation required before champion settings are accepted.

## 10. Open Questions for Architect

1. Approve Option A (standalone first phase) vs Option B (interleaved)?
2. Approve Top-6 candidate slate from Section 2, or expand/contract?
3. Approve MA search ranges in Section 3, or different ranges?
4. Approve adding ADX exhaustion ceiling as a tunable, or hold for a separate phase?
5. Approve the pre-Optuna Pine prep checklist as the next implementation work, pending separate per-session sign-off when ready to edit?

This plan does NOT begin Pine implementation. Implementation requires explicit "Act Mode" sign-off and adherence to AGENTS.md Pine Verification.
