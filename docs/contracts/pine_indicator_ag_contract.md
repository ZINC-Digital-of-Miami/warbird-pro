# Pine Indicator Modeling Contract

**Date:** 2026-05-05
**Status:** Active modeling contract

## Purpose

This contract defines the active Warbird training/modeling surface.

**Local-first pivot (2026-05-28):** The architecture has shifted to a
local-first platform. The Pine indicator remains the reference implementation
but is not the live trigger platform. FRED, macro, news, options, and
cross-asset data are now approved under the local-first data policy (all
sources must be manifest-backed with honest labeling).

## Iteration Policy

The active contract is allowed to evolve as tuning and training continue.
Trigger families, settings, thresholds, search spaces, and labels are current
evidence snapshots. They must be versioned through Markdown updates whenever a
new TradingView export, DuckDB/Core training result, or approved tuning batch
changes the accepted understanding.

Do not reuse an old export or trial without checking that its trigger family and
settings still match the current contract.

V9 lane contract (2026-05-02): `warbird_pro_v9` is a separate DuckDB local lane over
the active **Warbird Pro V9** indicator at `indicators/warbird-pro-v9.pine`. It does not create a new Pine source,
does not authorize Pine edits, and does not mutate the canonical fib anchor,
fib visual, or EMA/MA setup. It admits manifest-backed ES training rows
(15m and 5m) from TradingView exports or Databento market data and ignores
MES/NQ/MNQ rows.

Data-layer + sequencing contract (locked 2026-05-11):

- The V9/Core ETL stack is **DuckDB 1.5.2** (sort/filter/build over parquet+CSV),
  **Pandera 0.31.1** (schema/contract validation), and **fg-data-profiling 4.19.1**
  (`data_profiling` module — profiling/report output). No Postgres dependency on
  the V9 path.
- Training sequence: build and train ES **15m first**, ES 5m only after 15m
  success.

Operational preflight contract (2026-05-05): V9 has no active strategy
harness. Use `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`
for V9 indicator-only chart validation. Reserve regular `preflight` for
explicitly reopened strategy-harness sessions.

## Source Of Truth

Training rows may come only from manifest-backed active-lane sources:

- TradingView indicator CSV exports for non-Nexus lanes
- Databento ES market-data training rows (5m/15m) when the manifest declares a
  Databento capture/source kind
- TradingView/Pine `request.footprint()` `nexus_fp_*` snapshots for
  `NEXUS_FOOTPRINT_DELTA`
- deterministic columns derived from approved source rows

**Local-first data policy (2026-05-28):** FRED, macro, news, options, and
cross-asset data are now approved for the local modeling dataset. All sources
must be manifest-backed with honest labeling.

`warbird_pro_v9` may load ES exports across 5m/15m from the same active Warbird
Pro V9 training lane. MES/NQ/MNQ rows are ignored. No undeclared external
cross-symbol join, cloud table, or external feature stack is admitted into this
lane. Pine-native NQ + 6E values emitted by the active indicator are part of the
indicator behavior. Approved local Databento model-context side features must be
manifest-declared and must not be represented as Pine gates, Pine exports, or
TradingView indicator CSV data. Databento may supply ES market-data training
rows, but it is not the Pine indicator, not a trigger family, and not a
TradingView indicator CSV export.

Databento note: Databento historical
[`get_range`](https://databento.com/docs/api-reference-historical/timeseries/timeseries-get-range?historical=python&live=python&reference=python),
[programmatic batch downloads](https://databento.com/docs/examples/basics-historical/programmatic-batch-download),
[OHLCV resampling](https://databento.com/docs/examples/basics-historical/ohlcv-resampling?historical=python&live=python&reference=python),
and [continuous contracts](https://databento.com/docs/examples/symbology/continuous?historical=python&live=python&reference=python)
are valid references for Databento-sourced training rows. Manifests must use
honest capture/source language such as `DATABENTO_OHLCV_CSV`; Databento rows
must not be labeled `TRADINGVIEW_INDICATOR_CSV` or represented as the Pine
indicator source.

## Entry Trigger Authority

Every modeling run must declare which Pine trigger family produced its rows.
Do not mix trigger families inside one run.

- `LIVE_ANCHOR_FOOTPRINT`: live Warbird Pro trigger from
  `indicators/warbird-pro-v9.pine`. Entries are
  `entryLongTrigger` / `entryShortTrigger`, built from the selected fib
  execution-anchor reclaim, structure context, EMA/MA crossover alignment,
  optional liquidity influence, one-shot gating, ladder validity, and the
  active NQ + 6E cross-asset influence when enabled. NQ is same-direction; 6E
  up is USD-weak/long-favorable and 6E down is USD-strong/short-favorable. Risk
  Mode and candlestick logic are removed from the active Pine contract: no Risk
  Mode input/table block, no candlestick input/gate, no candlestick detector
  block, and no `ml_pat_*` Pine exports. (The trigger-family name is legacy and
  retained for continuity.)
- `NEXUS_FOOTPRINT_DELTA`: Nexus lower-pane footprint-delta trigger from
  `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`. Rows
  must come from TradingView/Pine `request.footprint()` evidence containing
  `nexus_fp_*` fields. CSV exports, local OHLCV parquet, Databento bars, and
  synthetic body/wick delta are not valid tuning evidence for this trigger
  family.

`acceptEvent` alone is not the live Warbird Pro entry trigger. It is a
diagnostic/setup-archetype event unless a future explicitly reopened strategy
surface defines it as part of its own execution path.

Retired trigger families are historical only unless Kirk explicitly reopens
them with a new active strategy/backtest harness:

- `STRATEGY_ACCEPT_SCALP`
- `BACKTEST_DIRECT_ANCHOR`

## Locked Fib Baseline (2026-04-30)

Warbird Pro fib core in `indicators/warbird-pro-v9.pine` is the
protected baseline. It must remain stable while 5m/15m tuning iterates.

Protected scope:

- `fibZzUpdate()` and ZigZag settings semantics
- anchor ownership/state transition logic for fib legs
- fib ladder construction via `fibPrice` and canonical fib ratios
- active fib draw span and chart-level construction

Allowed tuning scope while lock is active:

- non-fib thresholds and safety gates
- lookback/cooldown controls outside fib anchor math
- EMA-MA/RSI/liquidity/XA/footprint thresholds and execution toggles
- footprint/order-flow feature exports and diagnostic table rows, as long as
  the single `request.footprint()` path is reused and the Pine output budget is
  explicitly repriced

Any proposed fib-core change requires explicit approval plus before/after
TradingView evidence with manifest coverage.

## Warbird Pro V9 Exit Modeling

The `warbird_pro_v9` lane models ATR/risk exits from existing Warbird Pro V9
entry triggers. It must not treat `-.236` or any negative fib extension as a stop
family/candidate. If `-.236` is exported, it is context only and may be carried
as `fib_neg_0236_context`.

Frozen during V9:

- fib anchor ownership and ZigZag settings
- fib ladder/visual construction
- EMA/MA visual display semantics
- Pine source code until promotion approval

The V9 MA gate is price above/below BOTH the primary EMA and its smoothing MA:
primary `len=21`, `src=close`, `offset=1`, smoothing `maTypeInput=EMA`, and
`maLengthInput=9`. The old `useMaGate`, `lengthMA=50`, and `lengthEMA=21`
EMA/SMA HPO surface is retired for active V9/Core work.

HTF confluence is a hidden model/export feature, not a visible fib-ladder
change. It must project the 1H `.382/.500/.618` levels in the resolved
chart-fib direction and count only corresponding-level hits:
chart `.382` to HTF `.382`, chart `.500` to HTF `.500`, and chart `.618` to
HTF `.618`. The active 1H lookback knob is `htf1hLookback=8` and must be
mirrored by Core ETL as `knob_htf_1h_lookback`.

## Explicit Exclusions

The active modeling dataset must not join:

- Supabase cloud tables
- Databento rows mislabeled as TradingView indicator exports or Pine indicator
  sources
- local `ag_training` rows
- Python reconstructed fib interactions
- Risk Mode fields or candlestick pattern columns; those are not active V9 Pine
  execution/export surfaces
- any non-manifest-backed or mislabeled data source

**Approved under local-first data policy (2026-05-28):** FRED, macro, news,
options, economic calendar, and cross-asset data are now allowed for the local
modeling dataset. All sources must be manifest-backed with honest labeling.

## Required Export Manifest

Every modeling run must record:

- indicator file path
- repo commit
- TradingView symbol
- timeframe
- export date range
- export method (`CSV` for Warbird Pro indicator exports, `TV_FOOTPRINT_PARQUET`
  for Nexus request.footprint snapshots)
- source kind / capture method; Databento rows must use a Databento source
  kind instead of the TradingView CSV label
- trigger family
- Pine input settings
- row count and trade count
- export hash
- notes on missing or platform-limited fields

## Modeling Target

The target is a Pine settings/build recommendation.

Valid recommendations:

- input default changes
- search-space narrowing
- module keep/remove decisions
- threshold changes
- stop/target policy changes
- Pine code-change proposals for explicit approval
- V9 ATR/risk exit policy recommendations from ES 5m/15m export evidence

Invalid recommendations:

- server-side feature gates
- cloud scoring packets
- macro/FRED gates used as Pine live gates (approved for local modeling only)
- daily-ingestion dependencies
- invisible data joins not present in Pine output
- V9 promotion based on NQ/MNQ, negative-fib stop candidates, or Pine edits made
  before explicit promotion approval

## Validation

A champion setting/build requires:

- real TradingView evidence
- no mock rows
- exact manifest
- IS/OOS or walk-forward-style review
- commission and slippage assumptions recorded
- failure modes documented

## Promotion

Promotion is manual. A promoted result updates Pine settings/build docs and, only
after approval, Pine defaults or code. It does not imply server-side live model
deployment.
