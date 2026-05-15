# Nexus Indicator Quality Lane

## NEXUS_SCOPE_LOCK

This protocol governs the entire Nexus indicator lane and only the Nexus indicator lane:

- Active Pine file: `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
- Active indicator title: `Warbird Nexus Machine Learning RSI - Optuna Fast Test`
- Active evidence family: `NEXUS_FOOTPRINT_DELTA`
- Approved live/evidence source: TradingView/Pine `request.footprint()` and the emitted `nexus_fp_*` plots from this indicator
- Out of scope unless explicitly requested in the current session: V9 Core, V9 Pine, model training, Optuna launches, Supabase, dashboard/runtime, Databento OHLCV replacements, and alert promotion

Do not route Nexus work through V9 contracts. Alerts are not signal authority. Do not use alerts as signal authority. Alerts may exist as UI conveniences, but quality decisions are based on the plotted/evidence state and footprint-derived calculations.

## What The Indicator Must Do

The Nexus indicator is a research/support oscillator focused on footprint-aware exhaustion and divergence. Its quality contract is:

1. Pull real footprint data once per bar with `request.footprint()`.
2. Derive bar delta from `footprint.delta()`.
3. Derive footprint liquidity/volume from `footprint.rows()` and `volume_row.total_volume()`.
4. Normalize cumulative delta and delta slope without OHLCV/candle-body proxy substitution.
5. Use footprint gas-out/deceleration as the exhaustion authority.
6. Use structural price/oscillator divergence only when its filters and footprint/volume confirmation semantics are explicit.
7. Export hidden diagnostic plots that allow TradingView CSV/manual inspection of footprint availability, delta, total volume, normalized delta, slope, direction, gas-out, mode, and signal tier.
8. Keep alerts separate from signal truth; alert toggles must never redefine the plotted/evidence contract.

## Indicator Surface Map

| Surface | Code Area | Quality Requirement |
| ------- | --------- | ------------------- |
| Inputs/settings | Main, visual, zones, volume flow, footprint delta, regime, divergence, exhaustion, alerts | Each setting must either change visible/evidence behavior or be documented as UI-only. Defaults must reflect the current Nexus lane, not V9. |
| Footprint request | `request.footprint(footprintTicksPerRowInput, footprintVaPercentInput, footprintImbalancePercentInput)` | One cached request path per bar. No fake footprint reconstruction from candles, volume, or Databento bars. |
| Footprint rows/liquidity | `footprint.rows()` + row total volume aggregation | `fpTotalVolume` must come from footprint rows and remain positive before `fpFlowAvailable` is true. |
| Delta state | `fpBarDelta`, `fpCumDelta`, `normCumDelta`, `deltaSlope`, `deltaDir` | Direction and gas-out logic must fail closed when footprint is unavailable. |
| AMF oscillator | `roc`, `er`, `ewi`, `smp`, `oscVal`, `sigVal` | Oscillator can frame context, but it is not a substitute for footprint evidence. |
| Volume flow | VNVF block | Signed flow must be driven by footprint delta and footprint total volume. No candle body/wick delta proxy. |
| Regime | `regimeScore` and fills | Regime may summarize state; it must not hide unavailable footprint. |
| Exhaustion | gas-out + fatigue markers | Real exhaustion requires footprint delta deceleration in the relevant signed direction. |
| Divergence | pivot tracking + structural filter | Divergence must cite its structural and footprint/volume confirmation rules. If footprint confirmation is required, unavailable footprint must not silently pass. |
| Plots/evidence | visible plots + hidden `nexus_*` plots | Every hidden plot name is part of the CSV/evidence contract and must be reviewed before rename/removal. |
| Alerts | alertcondition/alert block | Alerts are non-authoritative. They can be disabled, renamed, or removed only after confirming no workflow depends on them. |
| Watermark/table | last-bar UI | Cosmetic only. Must not affect signals/evidence. |

## Work Types Covered

Use this lane for every task touching Nexus indicator behavior or proof:

- setting audit or preset/default changes
- Pine edits to the Nexus file
- plot/output additions, removals, or renames
- footprint request, footprint row, delta, liquidity, VNVF, exhaustion, divergence, regime, or oscillator changes
- TradingView compile/visual validation of Nexus
- CSV/export evidence review of `nexus_fp_*` plots
- documentation updates describing Nexus behavior
- quality review after assistant failures or scope drift

## Pre-Edit Protocol

1. Run `git status --short`.
2. Read `AGENTS.md` and this file.
3. Read the full Nexus Pine file, not only the changed block.
4. State the expected touched files before editing.
5. Price Pine budget before editing: count output-consuming calls, `request.security()`, and `request.footprint()` paths with `./scripts/guards/pine-lint.sh` where possible.
6. Confirm the task is Nexus-scoped. If the reasoning mentions V9, stop and re-scope unless the user explicitly requested a cross-lane comparison.

## Edit Rules

- Never edit the Nexus Pine file without explicit approval in the current session.
- Keep `request.footprint()` cached and singular unless the user explicitly approves a request-budget change.
- Do not introduce OHLCV, candle-body, wick, local CSV, Databento bar, or synthetic volume proxies as replacements for footprint evidence.
- Do not treat `ta.crossover()` or alert toggles as exhaustion authority.
- Do not claim divergence is footprint-confirmed unless the code requires footprint/volume confirmation for that divergence path.
- Hidden `nexus_*` plots are evidence contracts; renames require documentation and downstream export review.
- If footprint is unavailable, footprint-backed exhaustion/divergence must fail closed or visibly declare unavailable state.

## Required Verification Gates

Run these after any Nexus Pine edit before claiming completion:

```bash
curl -s -X POST "https://pine-facade.tradingview.com/pine-facade/translate_light?user_name=admin&v=3" \
  -H 'Referer: https://www.tradingview.com/' \
  -F "source=<indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine"
./scripts/guards/pine-lint.sh indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine
./scripts/guards/check-contamination.sh
./scripts/guards/check-no-tv-force.sh
npm run build
```

If only quality docs/tests changed and Pine did not change, run:

```bash
./.venv/bin/python -m pytest quality/test_functional.py -k nexus -q
npm run build
```

## Footprint Proof Standard

A Nexus claim is not proven by compile success alone. The report must include a footprint proof table:

| Proof Item | Required Evidence |
| ---------- | ----------------- |
| Real footprint request | `request.footprint()` call site with line number |
| Real bar delta | `footprint.delta()` call site with line number |
| Real row liquidity | `footprint.rows()` and `volume_row.total_volume()` call sites with line numbers |
| Availability gate | `fpFlowAvailable` definition and its positive-volume requirements |
| Delta normalization | `normCumDelta`, `deltaSlope`, `deltaDir` definitions |
| Exhaustion authority | `gasOutBull` / `gasOutBear` definitions and downstream marker use |
| Divergence confirmation | `sfVolPassBull` / `sfVolPassBear` or successor definitions |
| Evidence exports | hidden `nexus_fp_*` / `nexus_*` plot names |
| Non-authoritative alerts | alert block gated or documented as not signal truth |

## Static Review Checklist

Before approving any Nexus change, check:

- [ ] The file still starts with `//@version=6`.
- [ ] The indicator title still identifies the Nexus study lane.
- [ ] Input groups match the behavior they control.
- [ ] Footprint request parameters come from the Footprint Delta inputs.
- [ ] `fpFlowAvailable` cannot be true with missing delta or non-positive total volume.
- [ ] Volume flow uses footprint delta/row volume, not candle body/wick proxy.
- [ ] Exhaustion markers are footprint-gas-out based when described as real exhaustion.
- [ ] Divergence labels are structurally filtered and volume/footprint semantics are explicit.
- [ ] Hidden plot exports cover footprint availability, delta, total volume, normalized delta, slope, ratio, direction, gas-out, mode, and signal tier.
- [ ] Alert settings do not alter the evidence contract.
- [ ] No V9 file, setting, trainer, or model artifact is touched.

## Reporting Template

Every completed Nexus task must report:

1. Files changed.
2. Whether the Nexus Pine file changed.
3. Footprint proof table with file:line citations.
4. Verification commands run and pass/fail outputs.
5. Any unavailable proof, clearly labeled as not verified.
6. Explicit statement that V9 was not touched, or a line-cited explanation if the user explicitly requested a cross-lane change.
