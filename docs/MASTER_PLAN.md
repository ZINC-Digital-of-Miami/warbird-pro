# Warbird Indicator-Only Optuna Plan v6

**Date:** 2026-05-05
**Status:** Active architecture plan

## Summary

Warbird training is a pure PineScript indicator modeling program.

The active goal is to perfect the TradingView indicator itself: settings, state
machine, entries, exits, filters, hidden exports, and visual/operator build.
Optuna and supporting scripts may be used offline, but only to model and rank
PineScript indicator behavior. They do not create a separate data-stack
decision engine.

Single-surface update (2026-05-02): the only active main chart indicator is
**Warbird Pro V9** at `indicators/warbird-pro-v9.pine`. Nexus remains as the only retained
support/research Pine lane:

- `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`

All other Pine indicator, strategy, backtest, and fib-only variants are retired
from the active `indicators/` surface.

V9 lane update (2026-05-02): `warbird_pro_v9` is a separate Optuna lane over the
same active Warbird Pro V9 indicator. It models ATR/risk exits from
manifest-backed ES/MES training rows from TradingView exports or Databento
market data, ignores NQ/MNQ rows,
excludes `-.236` and other negative fib extensions as stop candidates, keeps
`-.236` only as optional context/export data, and freezes fib anchors, fib
visuals, and EMA/MA setup until a champion is approved for Pine promotion.

## Current Contract

- The canonical modeling object is the `Warbird Pro` Pine indicator behavior on
  TradingView.
- Training truth comes from manifest-backed active-lane sources: Pine/TradingView
  outputs emitted by `indicators/warbird-pro-v9.pine`, Databento ES/MES
  market-data training rows when declared as Databento source data, and, for
  Nexus work only, `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`.
- Allowed evidence includes TradingView indicator exports, hidden `ml_*` /
  `nexus_fp_*` plots, Nexus TradingView/Pine `request.footprint()` evidence for
  `NEXUS_FOOTPRINT_DELTA`, and deterministic columns derived from approved
  source rows.
- The optimization target is indicator quality: settings, thresholds, module
  toggles, stop/target policy, signal frequency, profit factor, drawdown,
  stability, direction balance, and operator usability.
- External feature stacking is out of scope. No FRED, macro, news, options,
  cross-asset, Supabase, or mislabeled Databento/TradingView artifacts are
  admitted into the active modeling dataset.
- Cloud Supabase is runtime/support only. It is not a model-training mirror and
  does not receive raw trials, raw labels, or full research datasets.

## Active Surfaces

- Main chart indicator:
  - `indicators/warbird-pro-v9.pine`
- Retained Nexus support/research lane:
  - `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
- Optimization and modeling tools:
  - `scripts/optuna/`
  - `scripts/optuna/warbird_pro_v9_profile.py`
  - `scripts/optuna/workspaces/warbird_pro_v9/`
  - `scripts/ag/tv_auto_tune.py`
  - `scripts/ag/tune_strategy_params.py`
  - `scripts/ag/tv_connection_doctor.py`
- Artifacts:
  - `artifacts/tuning/`
  - `scripts/optuna/workspaces/<indicator_key>/`

## Research Reference Surface

- `docs/research/2026-05-02-optuna-unified-platform.md` is the current
  long-form Optuna platform research report for ecosystem-level guidance
  (samplers, pruners, storage, orchestration, walk-forward design patterns).
- This file is reference-only and does not supersede active contract rules:
  Pine/TradingView-only modeling rows, explicit trigger-family declaration,
  and no out-of-scope feature stacking without an architecture reopen.
- Databento is an approved market-data supplier for training rows when the
  manifest declares a Databento capture/source kind. Databento is not the
  Pine indicator, not a TradingView indicator CSV, and not a substitute for
  trigger-family identity. Use Databento historical
  [`get_range`](https://databento.com/docs/api-reference-historical/timeseries/timeseries-get-range?historical=python&live=python&reference=python),
  [programmatic batch downloads](https://databento.com/docs/examples/basics-historical/programmatic-batch-download),
  [OHLCV resampling](https://databento.com/docs/examples/basics-historical/ohlcv-resampling?historical=python&live=python&reference=python),
  [continuous contracts](https://databento.com/docs/examples/symbology/continuous?historical=python&live=python&reference=python),
  Optuna [`create_study`](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.create_study.html),
  and Optuna [`TPESampler`](https://optuna.readthedocs.io/en/stable/reference/samplers/generated/optuna.samplers.TPESampler.html).

## Non-Goals

The following are explicitly retired from the active plan:

- building a daily-ingestion training warehouse
- using local legacy warehouse training tables (`ag_training`) as the model source
- training on FRED, macro, news, options, or cross-asset features
- reconstructing Pine behavior from Python OHLCV as the canonical label path
- recording Databento market-data rows as `TRADINGVIEW_INDICATOR_CSV` or as a
  Pine indicator source
- promoting a live model packet that scores separate server-side features
- using cloud Supabase as a training database
- reviving deleted Pine strategy, backtest, or fib-only variants without an
  explicit architecture reopen

## Trigger Families

Every modeling run must declare exactly one trigger family:

- `LIVE_ANCHOR_FOOTPRINT`: entries from `warbird-pro-v9.pine`
  `entryLongTrigger` / `entryShortTrigger` (legacy trigger-family identifier;
  rebuild lane does not require footprint inputs).
- `NEXUS_FOOTPRINT_DELTA`: Nexus lower-pane footprint-delta evidence from the
  retained Nexus Pine files. Rows must come from TradingView/Pine
  `request.footprint()` `nexus_fp_*` evidence.

Deleted strategy/backtest trigger families are inactive unless Kirk explicitly
reopens them in a new plan update.

## Plan Phases

### Phase 0 - Authority Reset

Keep the active authority docs aligned with the single main indicator plus
retained Nexus lane.

Required surfaces:

- `AGENTS.md`
- `docs/INDEX.md`
- `docs/MASTER_PLAN.md`
- `docs/contracts/`
- `docs/runbooks/`
- `docs/cloud_scope.md`
- `WARBIRD_MODEL_SPEC.md`
- `CLAUDE.md`
- `README.md`

### Phase 1 - Pine Baseline Lock

Before modeling any settings, lock the exact Pine build being optimized.

Required facts:

- source file path
- TradingView symbol and timeframe
- indicator version / commit
- exported columns
- Pine input defaults
- trigger family
- plot/request budget
- compile/lint status

No Pine code changes are allowed without explicit session approval.

### Phase 2 - Training Row Capture

Capture training rows from manifest-backed active-lane sources.

Allowed sources:

- TradingView indicator CSV export from `warbird-pro-v9.pine`
- Databento ES/MES market-data training rows with a Databento capture/source
  kind in the manifest
- hidden `ml_*` export fields emitted by that indicator
- retained Nexus `nexus_fp_*` footprint exports for `NEXUS_FOOTPRINT_DELTA`
- deterministic artifacts produced from approved source rows

Required manifest fields:

- indicator file when the source is Pine/TradingView
- repo commit
- symbol
- timeframe
- source/export date range
- Pine input settings when the source is Pine/TradingView
- trigger family and source Pine file when applicable
- source kind / capture method
- row count
- export hash
- notes on missing or platform-limited fields

### Phase 3 - Settings And Build Modeling

Run Optuna modeling only against approved manifest-backed trial data.

Permitted modeling questions:

- Which input settings improve profit factor, win rate, expectancy, drawdown,
  trade density, and yearly consistency?
- Which filter/module toggles improve or damage the signal?
- Which stop/target policy works best inside the current Pine state machine?
- In the `warbird_pro_v9` lane only, which ATR/risk exit policy works best for
  existing Warbird Pro V9 entry triggers across ES/MES exports?
- Which Pine states or `ml_*` / `nexus_fp_*` exports explain winners versus
  failures?
- Which settings are robust across IS/OOS windows?

Prohibited modeling questions:

- Which macro/FRED/cross-asset feature should gate trades?
- Which server-side model should score live alerts?
- Which warehouse feature should be joined into the indicator decision?
- Which NQ or cross-asset feature should gate V9 entries?

### Phase 4 - Explainability And Recommendation

Use feature-importance analysis from Optuna results to convert model outputs
into actionable Pine settings/build recommendations.

The output is a settings/build brief:

- champion settings
- rejected settings
- feature/module importance
- stability notes
- expected row/trade-state count
- known failure modes
- recommended Pine edits, if any

### Phase 5 - Pine Implementation

Only after Kirk approval, apply Pine changes or default-setting changes.

Required gates after any `.pine` edit:

1. pine-facade compile check
2. `./scripts/guards/pine-lint.sh <file>`
3. `./scripts/guards/check-fib-scanner-guardrails.sh`
4. `./scripts/guards/check-contamination.sh`
5. `./scripts/guards/check-no-tv-force.sh`
6. `npm run build`

Indicator/strategy parity is inactive because no active strategy Pine file
exists in `indicators/`.

TradingView preflight split:

- `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`
  for V9 indicator-only sessions
- `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight` only when a
  strategy harness is explicitly reopened and loaded on chart

### Phase 6 - Promotion

Promotion is manual. A champion means:

- the TradingView indicator settings/build are approved
- the evidence and artifacts are saved
- docs and runbooks are updated
- no separate server-side scoring engine is implied

## Pine Budget Baseline

Verified 2026-05-04:

- `warbird-pro-v9.pine`: 19 output-consuming calls
  (17 `plot()` + 2 `alertcondition()`), 4 `request.security()` calls,
  0 `request.footprint()` calls, 16 `line.new()` calls, 1 `box.new()`,
  and 1 `table.new()`.

Any Pine addition must be priced before code is written. Nexus request/output
budgets must be repriced before any Nexus edit.

## Verification Locks

- No mock data.
- No external feature stacking.
- No daily-ingestion training dependency.
- No Pine edits without explicit approval.
- Canonical fib and trade-state semantics are locked in
  `indicators/warbird-pro-v9.pine`: anchor ownership, fib ladder
  construction (`fibPrice` + canonical levels), entry/stop/target state, and
  `ml_last_exit_outcome` semantics are protected scope.
- Banned regression pattern (repo-wide): do not use the pivot-window
  `fibHtfSnapshot` variant with `ta.barssince(...)` and
  `pivotHighInWindow` / `pivotLowInWindow`; it has repeatedly produced wide-fib
  failures.
- No settings result is trusted without TradingView indicator export evidence.
- `warbird_pro_v9` is isolated from `warbird_pro`: it admits ES/MES TradingView
  exports only, ignores NQ/MNQ, and optimizes ATR/risk exits without touching
  Pine.
- `-.236` is removed as a V9 stop candidate. It may remain only as an optional
  exported context feature.
- No forced TradingView launch/restart/process-kill automation.
- Banned methods: `tv_launch`, `launch_tv_debug_mac.sh`,
  `pkill -f TradingView`, `killall TradingView`.
- Live TradingView operations are one explicit command at a time; no retry loops.
- No champion is accepted without IS/OOS or walk-forward-style review.

## Current Blocker

Hybrid+ 4-card authority run is deprecated. Active direction is the single
Core training card (`scripts/optuna/cards/core_training/2026_05_09_warbird_pro_autogluon_core.py`).
Treat legacy Hybrid+ runtime notes as historical only.

---

## V9 Core AutoGluon — Active Plan (2026-05-09)

### Live Pine Settings (authoritative — must match `build_v9_dataset.py` exactly)

| Parameter | Value | Pine input name |
|-----------|-------|-----------------|
| ZigZag Deviation | **3.0** | `fibDeviationManual` |
| ZigZag Depth | **10** | `fibDepthManual` |
| ZigZag Threshold Floor % | **0.15** | `fibThresholdFloorPct` |
| Confluence Tolerance % | **0.05** | `fibConfluenceTolPct` |
| Min Fib Range (ATR) | **0.5** | `minFibRangeAtr` |
| Midpoint Hysteresis % | **2.0** | `fibHysteresisPct` |
| MA Length (SMA) | **13** | `lengthMA` |
| EMA Length | **6** | `lengthEMA` |

**Critical rule:** Before every dataset build, read the live TradingView indicator
inputs panel and verify `build_v9_dataset.py` constants match exactly.
The Pine code `input.float(default, ...)` defaults are NOT authoritative —
the user's saved TV settings are.

### Training Dataset Contract

- Source: `data/mes_1m.parquet` (Databento 1m MES, 2020-01-01+)
- Build script: `scripts/optuna/workspaces/warbird_pro_v9/build_v9_dataset.py`
- Output: `exports/mes_5m.csv` — 441,852 5m bars, sha256 recorded in manifest
- IS window: `2020-01-01 → 2024-12-31` (runner `--start`/`--end` flags)
- OOS lock: `2025-01-01+` — untouched until champion promotion
- Clean build committed: `dd81ebf` (2026-05-05), after contamination purge

**Contamination incident (2026-05-05):** Prior CSV was built with stale params
`dev=4.0, depth=20, floor=0.50`. All study DBs were deleted and the dataset
rebuilt clean with `dev=3.0, depth=10, floor=0.15`. Runner label `MES_15m` was
also fixed to `MES_5m` (commit `c241214`).

### Kirk's Exit Trade Preferences (GOAL — Optuna rewards these)

- **Target SL:** 1.0 ATR (search range: 0.75–2.0; max SL = 2.0 ATR)
- **Target breakeven range:** 1–3R (`targetRiskMultiple` range: 1.0–3.0)
- Objective includes `target_hit_rate` reward (weight 0.14): fraction of trades
  exiting at TARGET, not stop/time. Configs where price reaches the 1–3R goal
  are actively scored higher.

### 4-Card Sequence

| Card | Profile | Trials | Status |
|------|---------|--------|--------|
| 1 | `warbird_pro_v9_exit_cpcv` | 1000 | **Running** (PID 71880) |
| 2 | `warbird_pro_v9_entry_filter_cpcv` | 1000 | Pending Card 1 |
| 3 | `warbird_pro_v9_ag_meta_cpcv` | 1000 | Pending Card 2 |
| 4 | `warbird_pro_v9_joint_challenger` | 500 | Pending Card 3 |

Cards run via `scripts/optuna/orchestrate_v9_run.py` in dependency order.
AG (Card 3) uses `best_quality` preset + `num_bag_folds=8`, `num_stack_levels=1`.

### Promotion Gate (champion.json)

```bash
python scripts/optuna/promote_v9_champion.py --run-id <run_id>
```

- WR drop IS→OOS ≤ 25%
- OOS PF ≥ 1.10
- Card 4 must strictly beat Cards 1+2+3 winner on OOS to promote
