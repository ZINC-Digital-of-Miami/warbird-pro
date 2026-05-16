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
7. Export data-window/export-only diagnostic plots that allow TradingView CSV/manual inspection of footprint availability, footprint quality, delta, total volume, normalized delta, slope, direction, gas-out, mode, signal tier, pivot-confirmation lag, regime score, oscillator momentum, volume-flow state, and raw/confirmed divergence flags.
8. Keep alerts separate from signal truth; alert toggles must never redefine the plotted/evidence contract.

## Indicator Surface Map

| Surface | Code Area | Quality Requirement |
| ------- | --------- | ------------------- |
| Inputs/settings | Main, visual, zones, volume flow, footprint delta, regime, divergence, exhaustion, alerts | Each setting must either change visible/evidence behavior or be documented as UI-only. Defaults must reflect the current Nexus lane, not V9. |
| Footprint request | `request.footprint(footprintTicksPerRowInput, footprintVaPercentInput, footprintImbalancePercentInput)` | One cached request path per bar. No fake footprint reconstruction from candles, volume, or Databento bars. |
| Footprint rows/liquidity | `footprint.rows()` + row total volume aggregation | `fpTotalVolume` must come from footprint rows and remain positive before `fpFlowAvailable` is true. |
| Delta state | `fpBarDelta`, `fpCumDelta`, `normCumDelta`, `deltaSlope`, `barDeltaRatio`, `fpQualityOk`, `deltaDir` | Direction, gas-out, fatigue, and signal-tier logic must fail closed until footprint evidence has usable volume and enough continuous history. |
| AMF oscillator | `roc`, `er`, `ewi`, `smp`, `oscVal`, `sigVal` | Oscillator can frame context, but it is not a substitute for footprint evidence. |
| Volume flow | VNVF block | Signed flow must be driven by footprint delta and footprint total volume. No candle body/wick delta proxy. |
| Regime | `regimeScore` and fills | Regime may summarize state; it must not hide unavailable footprint. |
| Exhaustion | gas-out + fatigue markers | Real exhaustion requires footprint delta deceleration in the relevant signed direction. |
| Divergence | pivot tracking + structural filter + `nexus_div_*` exports | Divergence must cite its structural and footprint/volume confirmation rules. If footprint confirmation is required, unavailable footprint must not silently pass. Raw and confirmed divergence flags must export separately so lag and false-positive rates can be measured. |
| Plots/evidence | visible plots + data-window/export-only `nexus_*` plots | Every data-window/export-only plot name is part of the CSV/evidence contract and must be reviewed before rename/removal. |
| Alerts | alertcondition/alert block | Alerts are non-authoritative. Current Nexus checkpoint removes the alert block entirely because the operator does not use alerts; reintroducing alerts requires explicit approval and budget pricing. |
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
- Current checkpoint: generic cross dots are UI-only context, default OFF, and excluded from the data-window/export-only `nexus_signal_tier` authority.
- Do not claim divergence is footprint-confirmed unless the code requires footprint/volume confirmation for that divergence path.
- Data-window/export-only `nexus_*` plots are evidence contracts; renames require documentation and downstream export review.
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
| Availability gate | `fpFlowAvailable` and `fpQualityOk` definitions and their positive-volume/history requirements |
| Delta normalization | `normCumDelta`, `deltaSlope`, `deltaDir` definitions |
| Exhaustion authority | `gasOutBull` / `gasOutBear` definitions and downstream marker use |
| Divergence confirmation | `sfVolPassBull` / `sfVolPassBear` or successor definitions |
| Evidence exports | data-window/export-only `nexus_fp_*` / `nexus_*` plot names, including `nexus_fp_quality_ok`, `nexus_pivot_span`, `nexus_regime_score`, `nexus_osc_momentum`, `nexus_vf_calc`, and raw/confirmed `nexus_div_*` flags |
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
- [ ] Data-window/export-only plot exports cover footprint availability, footprint quality, delta, total volume, normalized delta, slope, ratio, direction, gas-out, mode, signal tier, pivot span, regime score, oscillator momentum, volume-flow state, and raw/confirmed divergence flags.
- [ ] Alert settings do not alter the evidence contract, and no `alertcondition()` / `alert()` calls exist unless explicitly re-approved.
- [ ] No V9 file, setting, trainer, or model artifact is touched.

## Reporting Template

Every completed Nexus task must report:

1. Files changed.
2. Whether the Nexus Pine file changed.
3. Footprint proof table with file:line citations.
4. Verification commands run and pass/fail outputs.
5. Any unavailable proof, clearly labeled as not verified.
6. Explicit statement that V9 was not touched, or a line-cited explanation if the user explicitly requested a cross-lane change.


## Nexus 15m Heavy-Training Prep Gate

Before any heavier Nexus 15m model training run:

1. Re-export TradingView chart data after any Pine export-surface change.
2. Build the isolated dataset with:

   ```bash
   python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/build_nexus_15m_dataset.py      --source-csv "/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv"
   ```

3. Confirm `exports/nexus_15m_dataset.manifest.json` declares `trigger_family: NEXUS_FOOTPRINT_DELTA` and does not reference V9.
4. Confirm `reports/pretrain_label_audit.md` reports chronological splits over the footprint-quality subset, with embargo.
5. Confirm incomplete future labels are `<NA>` rather than silently labeled flat/false.
6. Only then prepare the heavy model config; do not start training from this gate without explicit operator approval.

When explicitly approved, run the first sequential heavy target only:

```bash
python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/train_nexus_15m_heavy.py \
  --manifest scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/exports/nexus_15m_dataset.manifest.json \
  --target label_volume_expansion_next_12b \
  --time-limit 14400 \
  --hpo-trials 80 \
  --num-bag-folds 5 \
  --num-bag-sets 2 \
  --num-stack-levels 1 \
  --dynamic-stacking auto \
  --model-profile neural_scout
```

Record the latest report from
`scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/reports/heavy_training_latest.md`
and keep the run Nexus-only.


Heavy-train leakage rule: AutoGluon k-fold bagging/stacking may be used only as
variance reduction inside the historical train segment. The chronological
validation split must remain `tuning_data`/bag-holdout, the future test split
must remain untouched until final scoring, and internal AutoGluon k-fold scores
are not OOS proof.


Section-by-section heavy training rule: do not blend all Nexus indicator areas
in the first pass. Train `footprint_delta_flow` first, then `volume_flow`,
`oscillator_regime`, `divergence_exhaustion`, and finally
`signal_tier_composite`. A section can proceed only when its chronological test
metrics clear the saved gate; otherwise rerun or revise that section before
continuing.


After Sections 01-02, use `neural_scout` for upcoming sections: full HPO on FastAI/Torch neural models, fixed tiny GBM/CAT/XGB scouts for grounding, and no RF/XT unless a later section proves the tree families deserve reopening.


## Deferred Hold: Nexus Live Meter + Tuning Path Governance (2026-05-15)

Status: deferred during active heavy training by operator instruction.

This section preserves implementation intent without changing active training or Pine behavior.

### Freeze Boundary While Training Is Active

Do not modify these surfaces during the current active run:

- `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
- `scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/build_nexus_15m_dataset.py`
- `scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/train_nexus_15m_heavy.py`
- in-flight manifests, report JSON/MD, and model artifacts for the active run

### Three Tuning Paths (Decision Lock)

Use this routing before any post-training tuning work:

1. If a knob is reconstructible from bar data + derived TA, tune with Python Optuna (`scripts/optuna/runner.py`).
2. If a knob requires Pine-only APIs (`request.footprint`, exhaustion internals, TradingView-only replay behavior), tune with CDP TradingView auto-tune (`scripts/ag/tv_auto_tune.py`, `scripts/ag/tune_strategy_params.py`).
3. If candidate space is under ~10 configs and promotion is the goal, use Manual Deep Backtest in TradingView for final OOS confirmation.

Never tune Pine-only footprint/exhaustion internals using the Python reconstruction path.

### Deferred Post-Training Implementation Backlog

When the active run finishes and a new edit window is approved:

- add live pressure meter from footprint bar-delta ratio (0-100, center 50)
- add buyer/seller gas-remaining intrabar telemetry with `varip` peak tracking
- add long/short confidence outputs and confidence state code
- add export-only diagnostics:
  - `nexus_live_pressure_meter`
  - `nexus_pressure_side`
  - `nexus_buyer_gas_remaining`
  - `nexus_seller_gas_remaining`
  - `nexus_gas_remaining_active`
  - `nexus_pressure_slowdown`
  - `nexus_long_confidence`
  - `nexus_short_confidence`
  - `nexus_confidence_state`

### TC Skill Enforcement Matrix (Required Before Pine Edit)

Map each implementation surface to the matching TradingCode skill reference:

- inputs and user-configurable surface: `.claude/skills/tc-indicators-basics/SKILL.md`
- math/normalization/clamping/rounding: `.claude/skills/tc-math/SKILL.md`
- operator precedence and boolean logic: `.claude/skills/tc-operators/SKILL.md`
- TA primitives and smoothing choices: `.claude/skills/tc-technical-analysis/SKILL.md`
- advanced flow/intrabar state (`varip`, arrays, staged conditions): `.claude/skills/tc-advanced-pine/SKILL.md`
- plot/output budgeting and display contract: `.claude/skills/tc-plots/SKILL.md`
- drawing object alternatives (`line.new`, `label.new`, `box.new`): `.claude/skills/tc-visual-output/SKILL.md`
- bar/background visual diagnostics: `.claude/skills/tc-bar-coloring/SKILL.md`
- non-authoritative alert plumbing (if reintroduced): `.claude/skills/tc-alerts/SKILL.md`

### Pine Budget And Request Discipline (Applied At Resume)

- budget all output-consuming calls before and after each change
- use `hline()` and drawing primitives where possible to conserve the 64-cap output budget
- keep `request.footprint()` cached once per bar and avoid request path multiplication
- no dynamic request expansions without explicit budget pricing in the report

### Resume Gates (After Training Ends)

Before claiming any post-hold implementation complete:

1. Pine facade compile check
2. `./scripts/guards/pine-lint.sh indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
3. `./scripts/guards/check-contamination.sh`
4. `./scripts/guards/check-no-tv-force.sh`
5. `npm run build`
6. `./.venv/bin/python -m pytest quality/test_functional.py -k nexus -q`

Save a dated result note under `quality/results/` that includes tuning-path choice, TC skill mapping used, budget counts, and explicit statement that V9 surfaces were not touched.
