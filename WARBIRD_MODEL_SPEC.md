# Warbird Model Spec — Local-First v7

**Date:** 2026-05-05 (updated 2026-05-28 for local-first pivot)
**Status:** Active, subordinate to `docs/MASTER_PLAN.md`

## Contract

**Local-first pivot (2026-05-28):** Warbird has shifted from pure PineScript
indicator modeling to a local-first platform. The local dashboard (TV
Lightweight Charts on localhost) is the primary platform for charting,
triggers, and trade recording. The Pine indicator remains the reference
implementation but is not the live trigger platform.

Model selection (AutoGluon families, hyperparameters) is TBD pending deep
research — the prior full-zoo locked config is no longer assumed active.

## Iteration Policy

Tuning and training are ongoing. Current trigger families, settings, thresholds,
search spaces, labels, and recommended build choices are mutable evidence
snapshots. They may be revised after new Pine/TradingView exports, Strategy
Tester evidence, and DuckDB/Core training evidence.

Any accepted model-contract change must update this spec, the Master Plan, the
active contract docs, and the relevant runbooks before the result is considered
ready for reuse by another agent.

## Training Truth

Allowed training inputs are manifest-backed sources:

- TradingView indicator CSV exports for non-Nexus lanes
- Databento ES market-data training rows (15m and 5m) when declared as Databento
  source data in the manifest
- TradingView/Pine `request.footprint()` `nexus_fp_*` snapshots for Nexus ML RSI
- deterministic features derived from those approved sources
- FRED, macro, news, options, and cross-asset data (approved under local-first
  data policy, 2026-05-28)

## Data Layer (locked 2026-05-11)

V9/Core ETL and training is **file-based** (parquet + CSV). The active stack:

- **DuckDB 1.5.2** for sort/filter/join/build over the source parquet and intermediate exports
- **Pandera 0.31.1** for schema/contract validation of every export CSV and manifest (knob set, ml_* features, label policy, dtypes)
- **fg-data-profiling 4.19.1** (`data_profiling` module) for profiling/report output

Local PG17 `warbird` and the `ag_training` / `ag_fib_*` warehouse tables remain
on disk for legacy lineage only — they back `scripts/ag/train_ag_baseline.py`,
not the active V9/Core trainer. The V9 path
(`scripts/ag/train_v9_locked.py`,
`scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`,
`scripts/ag/monte_carlo_v9.py`, `scripts/ag/shap_v9.py`) does not import
psycopg2 and has no Postgres dependency.

## Training Sequence (locked 2026-05-11)

- Build and train ES **15m first**.
- Build and train ES **5m only after** 15m success (fit + SHAP + Monte Carlo) is documented.

Rationale: per the 2026-04-27 operator checkpoint, 15m had +6.74% PnL / PF 1.143
vs. 5m −2.55% / PF 0.91. The 15m surface is the cleaner baseline; tune mechanics
there first before moving to the noisier 5m lane.

Disallowed active training inputs:

- Supabase daily/hourly runtime ingestion as a training feature source
- local `ag_training` warehouse rows
- Python OHLCV reconstruction as the canonical label source
- Databento rows mislabeled as TradingView/Pine indicator exports
- any non-manifest-backed or mislabeled data source

**Approved under local-first data policy (2026-05-28):** FRED, macro, news,
options, and cross-asset data are now allowed for the local modeling dataset.
All sources must be manifest-backed with honest labeling.

Historical warehouse tables may remain on disk for lineage. They are not active
model truth unless Kirk explicitly reopens that architecture.

## Model Objective

The model evaluates Pine settings and build choices.

Primary outputs:

- champion Pine input settings
- rejected Pine input settings
- module keep/remove recommendations
- stop/target policy recommendations
- signal-frequency and trade-quality diagnostics
- failure-mode notes

Primary metrics:

- profit factor
- net profit
- expectancy per trade
- win rate
- max drawdown
- return over drawdown
- trade count and trade density
- long/short balance
- yearly and walk-forward stability
- footprint-rich versus footprint-poor cohort stability where available

## Active Pine Surfaces

  - `indicators/warbird-pro-v9.pine`
  - only active main chart indicator
  - TradingView indicator name: **Warbird Pro V9**
  - TradingView short title: **Warbird V9**
  - live entry trigger: `entryLongTrigger` / `entryShortTrigger` from the
    selected fib execution-anchor reclaim plus structure context, EMA/MA
    crossover alignment, optional liquidity influence, and the active NQ + 6E
    cross-asset influence when enabled; NQ is same-direction, and 6E is the
    USD-pressure proxy. Risk Mode and candlestick logic are removed from the
    active Pine execution contract: no Risk Mode input/table block, no
    candlestick input/gate, no candlestick detector block, and no `ml_pat_*`
    Pine exports
  - MA gate is price above/below BOTH the primary EMA21 and smoothing EMA9;
    the old `useMaGate`, `lengthMA=50`, and `lengthEMA=21` EMA/SMA HPO
    surface is retired for active V9/Core work
  - HTF confluence is direction-aware and corresponding-level only:
    chart `.382/.500/.618` compare to 1H `.382/.500/.618` projected in the
    resolved chart-fib direction, with live `htf1hLookback=8` mirrored by
    Core ETL as `knob_htf_1h_lookback`
  - footprint/order-flow hidden exports now include Pine-native delta
    imbalance, delta acceleration, aggressor pulse, volume-spike ratio, POC
    shift, absorption candidate, and flush candidate fields for Core parity and
    live visual checks
- `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
  - retained Nexus lower-pane footprint-delta research/tuning surface
  - active trigger family: `NEXUS_FOOTPRINT_DELTA`
  - footprint delta must come from TradingView/Pine `request.footprint()`
    `nexus_fp_*` fields; CSV exports, local OHLCV parquet, and synthetic
    body/wick delta are invalid tuning evidence for this surface

Retired/removed Pine variants are historical lineage only:

- `indicators/warbird-pro-indicator.pine`
- `indicators/Warbird_Pro_v7.pine`
- `indicators/v7-warbird-institutional.pine`
- `indicators/v7-warbird-strategy.pine`
- `indicators/v7-warbird-institutional-backtest-strategy.pine`
- `indicators/fibs-only.pine`
- `v8-warbird-live.pine`
- `v8-warbird-prescreen.pine`

## Locked Baseline Checkpoint (2026-04-27)

Operator checkpoint summary from TradingView strategy snapshots:

- 15m: +6.74% PnL, PF 1.143, 434 trades, 3.47% max drawdown
- 5m: -2.55% PnL, PF 0.91, 295 trades, 3.44% max drawdown
- 1h: -9.26% PnL, PF 0.929, 801 trades, 14.33% max drawdown

Policy from this checkpoint:

- 15m behavior remains a historical reference baseline for fib and structure
  semantics.
- 5m remains the active tuning lane.
- The protected fib core now lives in
  `indicators/warbird-pro-v9.pine`. No strategy/backtest Pine harness is
  active unless Kirk explicitly reopens one.

Protected fib-core scope in `indicators/warbird-pro-v9.pine`:

- ZigZag/fib anchor ownership transitions (`fibAnchorHigh/Low`, anchor bars,
  `fibZzUpdate()`, `fibBull`)
- fib ladder math (`fibPrice`, canonical retracement/extension level construction)
- active fib draw span and level construction

Allowed tuning scope while locked:

- non-fib risk gates, trigger thresholds, reclaim/sweep lookbacks, and cooldowns
- EMA-MA/RSI/liquidity/XA/footprint thresholds and execution-safety parameters
- module on/off decisions that do not alter fib math or anchor state ownership

## Feature Scope

Feature scope includes indicator-emitted and manifest-backed local data sources.

Current V9 Core AG feature policy: train on non-fib/non-color indicator
settings and MA/RSI/liquidity/NQ+6E/footprint/HTF signal evidence emitted by
the approved source surface. Do **not** train on protected fib-engine settings,
fib internals, visual/color inputs, Risk Mode, or candlestick pattern fields.
Pine fib ladder prices remain required label-construction inputs only.

Admitted feature families:

- Pine input settings
- Pine state-machine fields
- Pine `ml_*` hidden exports
- Databento ES market-data training rows (5m/15m) when the run manifest declares a
  Databento source/capture kind
- Nexus `nexus_fp_*` footprint fields from TradingView/Pine
  `request.footprint()`
- OHLCV columns included in the TradingView export
- deterministic columns computed only from approved source rows

Approved under local-first data policy (2026-05-28):

- FRED, macro, news, options, and cross-asset data when manifest-backed
- Databento model-context side features when manifest-declared and limited to
  the active contract set (never represented as Pine gates or Pine exports).
  Pine-native NQ + 6E values emitted by the active indicator are part of the
  indicator behavior

Not admitted:
- candlestick pattern columns unless a future research lane explicitly reopens
  them; they are not in the current active Pine export contract
- Supabase/cloud serving tables
- local warehouse reconstructed fib rows
- Databento rows recorded as `TRADINGVIEW_INDICATOR_CSV` or as a Pine indicator
  source

## Label Scope

Labels resolve from approved manifest-backed source rows only.

Allowed labels:

- trade profit/loss
- Pine state outcomes such as `ml_last_exit_outcome`
- TP/SL-style state outcomes emitted by the active Pine indicator
- derived binary or multiclass labels computed from exported Pine trade/state
  fields

Current V9 Core TP/SL label grid: each admitted entry expands to 20 combos
(4 SL ATR multiples × 5 TP fib-extension prices). TP prices are read from
`ml_trade_tp1` through `ml_trade_tp5` for fib 1.000 / 1.236 / 1.618 / 2.000 /
2.236 and are not ML features.

Any label must be tied to the export manifest and cannot use future columns not
available in the Pine/TradingView output.

## Explainability

Feature-importance analysis from V9 Core AutoGluon/SHAP outputs is used to
explain settings and build choices, not to publish a live server model.

Required explanation outputs:

- setting importance
- module/toggle importance
- cohort stability
- long/short asymmetry
- yearly or walk-forward drift
- failure modes that require Pine review

## Packet Rule

There is no active server-side scoring packet requirement.

The promotion artifact is a Pine settings/build brief containing:

- indicator file and commit
- symbol/timeframe
- source/export manifest
- trigger family used for evidence
- champion settings
- validation metrics
- rejected settings
- recommended Pine code/default changes

## Runtime Boundary

Supabase ingestion may remain for live chart/runtime support, but it is not an
active training source. Databento is an approved training data supplier for
manifest-backed ES 5m/15m market-data rows; it is not the Pine indicator and must
not be labeled as a TradingView indicator CSV. Cloud must not receive raw trial
data, raw labels, or full research datasets.

## Verification

Before any Pine build or settings promotion:

- run `python3 scripts/ag/tv_connection_doctor.py --json` before live
  TradingView CDP/MCP operations
- for V9 indicator-only sessions, run
  `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`
- reserve regular `tv_auto_tune.py preflight` for explicitly reopened
  strategy-harness sessions
- verify the Pine source compiles through pine-facade
- run `pine-lint.sh`
- run contamination guard
- run `npm run build`
- save the source export, Databento manifest, or CDP evidence
- document the exact settings and date range

## Legacy

The following are legacy for active modeling:

- `ag_fib_snapshots`
- `ag_fib_interactions`
- `ag_fib_stop_variants`
- `ag_fib_outcomes`
- `ag_training`
- local warehouse lineage tables
- FRED/macro feature scope
- Python reconstruction as canonical training generator
- server-side model packet promotion
