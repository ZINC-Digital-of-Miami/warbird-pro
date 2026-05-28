# Warbird Local-First DuckDB Platform Plan v7

**Date:** 2026-05-05 (V9 Core data layer locked to DuckDB local stack 2026-05-12; local-first pivot 2026-05-28)
**Status:** Active architecture plan

## Summary

**Local-first pivot (2026-05-28):** Warbird has shifted from pure PineScript
indicator modeling to a local-first platform. The local dashboard (TV
Lightweight Charts on localhost) is the primary platform for charting,
triggers, and trade recording. The Pine indicator remains the reference
implementation but is NOT the live trigger platform.

The local DuckDB / Pandera stack at `scripts/duckdb_local/` is used for
offline modeling, data recording, and analysis. Model selection (AutoGluon
families, hyperparameters) is TBD pending deep research — the prior full-zoo
locked config is no longer assumed active.

Single-surface update (2026-05-02): the only active main chart indicator is
**Warbird Pro V9** at `indicators/warbird-pro-v9.pine`. Nexus remains as the only retained
support/research Pine lane:

- `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`

All other Pine indicator, strategy, backtest, and fib-only variants are retired
from the active `indicators/` surface.

V9 lane update (2026-05-02, refined 2026-05-12): `warbird_pro_v9` is the
active modeling lane over the live Warbird Pro V9 indicator. It models ATR/risk
exits from manifest-backed ES training rows (15m and 5m) from TradingView
exports or Databento market data, ignores MES/NQ/MNQ rows, excludes `-.236` and
other negative fib extensions as stop candidates, keeps `-.236` only as
optional context/export data, and freezes fib anchors, fib visuals, and EMA/MA
setup until a champion is approved for Pine promotion. The production trainer
is `scripts/ag/train_v9_locked.py` (model config TBD — prior AutoGluon
full-zoo is reference only; calibrated log_loss, chronological IS/VAL/OOS
with embargo).

Data-layer + sequencing update (locked 2026-05-11):

- V9/Core ETL and training is file-based: **DuckDB 1.5.2** (sort/filter/build),
  **Pandera 0.31.1** (schema/contract validation), **fg-data-profiling 4.19.1**
  (`data_profiling` module — profiling reports). Local PG17 `warbird` warehouse
  is legacy-reference only; the V9/Core path does not import psycopg2.
- Build and train ES **15m first**; build and train ES 5m only after 15m
  success (fit + SHAP + Monte Carlo) is documented.

## Current Contract

- The canonical modeling object is the `Warbird Pro` Pine indicator behavior on
  TradingView.
- Training truth comes from manifest-backed active-lane sources: Pine/TradingView
  outputs emitted by `indicators/warbird-pro-v9.pine`, Databento ES
  market-data training rows (5m/15m) when declared as Databento source data, and, for
  Nexus work only, `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`.
- Allowed evidence includes TradingView indicator exports, hidden `ml_*` /
  `nexus_fp_*` plots, Nexus TradingView/Pine `request.footprint()` evidence for
  `NEXUS_FOOTPRINT_DELTA`, and deterministic columns derived from approved
  source rows.
- The optimization target is indicator quality: settings, thresholds, module
  toggles, stop/target policy, signal frequency, profit factor, drawdown,
  stability, direction balance, and operator usability.
- **Local-first data policy (2026-05-28 pivot):** FRED, macro, news, options,
  and cross-asset data are approved for the local modeling dataset. The prior
  TradingView-era restriction is revoked — local-first removes all TV data
  constraints. All sources must be manifest-backed with honest labeling.
  Mislabeled Databento/TradingView artifacts remain prohibited.
- Cloud Supabase is runtime/support only. It is not a model-training mirror and
  does not receive raw trials, raw labels, or full research datasets.

## Active Surfaces

**Canonical paths (2026-05-12):**

| Role                                             | Path                                                                                                   |
| ------------------------------------------------ | ------------------------------------------------------------------------------------------------------ |
| Main chart Pine indicator                        | `indicators/warbird-pro-v9.pine`                                                                       |
| Retained Nexus research/support Pine             | `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`                                  |
| Locked 1y 15m Core export (CSV)                  | `scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv`                             |
| Manifest for that export                         | `scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.manifest.json`                   |
| Pandera profiling report                         | `scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.profile.html`                    |
| Core ETL builder                                 | `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`                               |
| **Production V9 trainer**                        | `scripts/ag/train_v9_locked.py`                                                                        |
| SHAP gate runner                                 | `scripts/ag/shap_v9.py`                                                                                |
| Monte Carlo gate runner                          | `scripts/ag/monte_carlo_v9.py`                                                                         |
| Smoke-validation card (no AG)                    | `scripts/duckdb_local/cards/core_training/2026_05_09_warbird_pro_autogluon_core.py`                    |
| Trade-dataset semantics (single source of truth) | `scripts/ag/train_v9_locked.py::build_trade_dataset`                                                   |
| Trained model output root                        | `models/warbird_pro_v9/locked_<tag>/`                                                                  |
| SHAP artifacts root                              | `artifacts/shap_v9/shap_<tag>/`                                                                        |
| Monte Carlo artifacts root                       | `artifacts/mc_v9/<tag>/`                                                                               |
| TV settings/tuning helpers (non-V9)              | `scripts/ag/tv_auto_tune.py`, `scripts/ag/tune_strategy_params.py`                                     |
| TradingView readiness doctor                     | `scripts/ag/tv_connection_doctor.py`                                                                   |
| Indicator-only AG contract                       | `docs/contracts/pine_indicator_ag_contract.md`                                                         |
| Startup review runbook                           | `docs/runbooks/startup_repo_review.md`                                                                 |
| V9 ML/trading research operating system          | `docs/runbooks/v9_ml_trading_research_operating_system.md`                                             |
| Legacy (do not use without architecture reopen)  | `scripts/ag/train_hard_gate.py`, `scripts/ag/train_ag_baseline.py`, local Postgres `warbird` warehouse |

## Global Agents Quality Surface (2026-05-22)

The quality-playbook runtime is retired for active Warbird execution. The
active quality lane is repo-native validators plus `agents/` automation.

Canonical active surfaces:

- `agents/README.md` (agent umbrella authority)
- `agents/skills/README.md` (skill curation and overlap policy)
- `agents/roles/README.md` (role curation and hardening plan)
- `agents/scripts/process_reaper.py` (no-manual process cleanup lane)
- `tests/ag/**` and existing guard scripts for code-path validation

Operational requirement for V9 Core changes (trainer/ETL/provenance/MC/SHAP):

- run impacted `tests/ag/**` before claiming completion
- always include the minimum contract lane:
  - `pytest tests/ag/test_v9_core_indicator_input_contract.py -q`
  - `pytest tests/ag/test_v9_core_training_targets.py -q`
- fail closed on provenance/hash/split ambiguity
- keep cloud/training boundary checks explicit (no raw trial/label dumps to
  cloud Supabase)

Quality workbook runtime/artifact surfaces are removed and are no longer an
active protocol surface.

## Git Push Protocol (Operational)

All agent instruction surfaces and planning docs use this canonical Git push protocol:

- push only after explicit user approval in the current session
- commit and push on `main` only
- use explicit remote/branch command: `git push origin main`
- if upstream is missing, set once with `git push -u origin main`
- never use `git push --force`, `git push -f`, or `git push --no-verify`
- rely on `.githooks/pre-commit` + `.githooks/pre-push` and verify audit logs in
  `.git/warbird-prechecks/`

This protocol supersedes any older push wording in historical docs under
`docs/plans/`.

**Workspace layout:**

```
scripts/duckdb_local/                          # V9 DuckDB/Pandera/Core workspace
├── cards/core_training/                       # local validation cards (smoke only)
├── cards/side_models/                         # MAE side-model scaffolds (post-Core)
├── workspaces/<indicator_key>/                # per-indicator workspace
│   ├── exports/                               # canonical export CSVs + manifests
│   ├── experiments/<symbol>_<tf>/             # local training artifacts
│   └── champion.json                          # promoted settings snapshot
├── cpcv.py, cpcv_helpers.py                   # embargoed chronological / CPCV splits
├── paths.py                                   # canonical path helpers
└── runner.py + warbird_optuna_hub.py          # legacy Optuna runner/hub (Nexus + v7 lanes)
```

## Research Reference Surface

- `docs/research/2026-05-02-optuna-unified-platform.md` is a long-form Optuna
  ecosystem research report retained for Nexus/legacy work only. The V9 Core
  path is DuckDB/Pandera/AutoGluon and does not use that surface.
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
  and [continuous contracts](https://databento.com/docs/examples/symbology/continuous?historical=python&live=python&reference=python)
  for the Databento ingest side. The downstream V9 Core modeling stack is
  AutoGluon Tabular + DuckDB.

## Non-Goals

The following are explicitly retired from the active plan:

- building a daily-ingestion training warehouse
- using local legacy warehouse training tables (`ag_training`) as the model source
- training on mislabeled or non-manifest-backed data sources
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
- Databento ES market-data training rows (5m/15m) with a Databento capture/source
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

Run local DuckDB-backed AutoGluon modeling only against approved
manifest-backed trial data.

Permitted modeling questions:

- Which input settings improve profit factor, win rate, expectancy, drawdown,
  trade density, and yearly consistency?
- Which filter/module toggles improve or damage the signal?
- Which stop/target policy works best inside the current Pine state machine?
- In the `warbird_pro_v9` lane only, which ATR/risk exit policy works best for
  existing Warbird Pro V9 entry triggers across ES 5m/15m exports?
- Which Pine states or `ml_*` / `nexus_fp_*` exports explain winners versus
  failures?
- Which settings are robust across IS/OOS windows?

Prohibited modeling questions:

- Which non-manifest-backed external feature should gate trades?
- Which server-side model should score live alerts?
- Which warehouse feature should be joined into the indicator decision?
- Which external/server-side cross-asset feature should override V9 entries?

### Phase 4 - Explainability And Recommendation

Use feature-importance analysis (SHAP, AG leaderboard, Monte Carlo) to convert
model outputs into actionable Pine settings/build recommendations.

The output is a settings/build brief:

- champion settings
- rejected settings
- feature/module importance
- stability notes
- expected row/trade-state count
- known failure modes
- recommended Pine edits, if any

### Phase 4.5 - Validation Gating Before Live Trade Routing

**Mental model:** a trained classifier that posts strong log_loss / AUC / WR is
**not yet trustworthy**. Those metrics rank predictions but say nothing about
_why_ the model is good or whether the apparent edge translates to live P&L.
Two independent gates run between a clean fit and any live TradingView alert
that depends on the model's output:

**Gate 1 — SHAP**
(`scripts/ag/shap_v9.py --predictor-dir <model> --csv <15m-export>`).

Catches feature-level pathology that aggregate metrics hide:

- **Top-feature audit** — is the model leaning on plausibly causal features
  (entry triggers, fib reaction, liquidity, ATR-normalized distances) or on
  proxies that smell like leakage (raw timestamps, label-adjacent fields,
  bar-of-day in a way that codes regime)?
- **Per-class importance** — winners and losers should be driven by an
  overlapping but not identical feature set; total drift between classes
  implies the model is mostly fitting label noise.
- **Temporal stability** (early-half vs. late-half SHAP) — if importances
  shift dramatically, the model is regime-fitting and OOS performance will
  collapse the moment the regime ends.
- **Calibration check** (predicted vs. realized in probability bins) — is the
  `proba > 0.75` gate actually delivering ~75% real WR, or is the isotonic
  calibration miscalibrated for the high-confidence tail?
- **Redundancy + drop candidates** — high-|r| feature pairs and
  DEAD / REDUNDANT / UNSTABLE features inform the next Core feature trim.

**Gate 2 — Monte Carlo**
(`scripts/ag/monte_carlo_v9.py --predictor-path <model> --csv <15m-export> --split oos`).

Catches P&L-level pathology that SHAP can't see:

- **Overall P&L distribution + drawdown + WR + profit factor** under
  realistic resampling — does the OOS distribution have a tail that's
  fundable, or do drawdowns wipe accounts before the edge realizes?
- **Per-direction breakdown** — does the model work both long and short, or
  is it riding one regime?
- **Threshold sweep** (`P(winner_tp_before_sl) >= τ` for τ ∈ [0.50, 0.95]) —
  where is the EV maximum? Is `0.75` (the locked inference threshold)
  near it or far from it?
- **Calibration cohort check** — predicted vs. realized broken out by time
  of day, session, regime quartile. A miscalibrated cohort can dominate
  losses even if global calibration looks fine.
- **Regime stability** (early-half vs. late-half) — does the model survive
  the same period split that SHAP audits structurally?
- **Win/loss streak profile** — serial correlation of outcomes drives
  drawdown depth far more than headline WR.

**Promotion rule:** only after Gate 1 _and_ Gate 2 both clear do you
_enable_ (toggle from disabled → active) any TradingView alert that depends
on this model's output — i.e., an alert whose firing condition is
"V9 entry trigger AND model_proba >= 0.75" (whether wired via webhook,
TV alert action, or any downstream notification). The phrase "flip an
alert" in operator shorthand means exactly this toggle.

A model that passes log_loss but fails either gate will push high-confidence
"entries" that lose real money. The OOS WR being _higher_ than IS WR (the
2026-05-12 baseline showed IS 41.67% / VAL 43.60% / OOS 46.90%) is exactly
the pattern where gating is non-optional: it could mean genuine headroom or
it could mean the OOS window is a friendly regime that won't repeat. The
gates tell you which.

Failure of either gate routes back to Phase 3 or Phase 1 (settings change,
feature change, Pine change) — NOT to "tune the threshold" or "lower the
bar." The threshold is locked at 0.75 per the inference contract.

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

Verified 2026-05-21 by `scripts/guards/pine-lint.sh` after the V9
settings-surface cleanup:

- `warbird-pro-v9.pine`: 54 output-consuming calls
  (52 `plot()` + 2 `alertcondition()`), 11 `request.security()` calls after
  comment-line normalization, 1 `request.footprint()` call, 19 `line.new()`
  calls, 1 `box.new()`, and 1 `table.new()`. Session VWAP is intentionally
  modeling/export-only through `ml_liq_vwap_dist_atr`; it is not a visible
  chart overlay and not an operator-facing setting. The current build leaves
  10 output slots before the 64-call hard cap.

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
- `warbird_pro_v9` is isolated from `warbird_pro`: it admits ES 5m/15m
  TradingView/Databento exports only, ignores MES/NQ/MNQ, and optimizes ATR/risk exits without touching
  Pine.
- `-.236` is removed as a V9 stop candidate. It may remain only as an optional
  exported context feature.
- No forced TradingView launch/restart/process-kill automation.
- Banned methods: `tv_launch`, `launch_tv_debug_mac.sh`,
  `pkill -f TradingView`, `killall TradingView`.
- Live TradingView operations are one explicit command at a time; no retry loops.
- No champion is accepted without IS/OOS or walk-forward-style review.

## Current State (2026-05-12)

**V9 Core has one completed full `--model-suite` artifact.** It is not
promotion-ready until validation/provenance gates are tied to that exact run.

Recent local state (through commit `1747194`):

- V9 Core file pipeline is under `scripts/duckdb_local/` and
  `tests/duckdb_local/`. Nexus footprint research and legacy v7 profile
  adapters remain separate retained Optuna-owned surfaces.
- `scripts/ag/train_v9_locked.py` is the production V9 trainer. Default CSV
  fixed (5m → 15m, pointing at the locked 1y Core export). `--model-suite`
  flag adds the optional TP/SL touch + MFE/MAE side models. Docstring no
  longer points at the smoke card or `train_hard_gate.py`.
- `build_trade_dataset` semantics canonicalized in the docstring: 4×5
  TP/SL grid, touch-event labels for `tp_hit`/`stop_hit`, pessimistic
  same-bar collision for `winner_tp_before_sl`. `monte_carlo_v9.py` and
  `shap_v9.py` both import this function — single source of truth.
- Core ETL/Pandera/fg-data-profiling stack wired. DXY was removed from active
  V9 Core features on the 2026-05-11 gate-as-feature pivot; Databento
  trade-side CVD/order-flow features, May 2026
  order-flow threshold review (20% absorption/flush delta, 1.5x volume
  spike, 0.75 ATR range split) are in code. Smoke verification recorded
  in `docs/audits/2026-05-10-v9-core-smoke-verification.md`.
- The locked 15m export exists and validates: 23,513 bars (2025-05-11
  22:00 UTC → 2026-05-10 23:45 UTC), 1,414 long triggers, 1,284 short
  triggers. Latest full model-suite run
  `models/warbird_pro_v9/locked_20260512_083803/` used chronological
  IS/VAL/OOS splits of 22,654 / 4,830 / 4,830 model rows under the historical
  3-TP grid and 25-bar embargo (WR 33.07% / 34.02% / 35.13%). That run
  predates the current 5-TP / 10-bar chart-mirrored contract.
- Auxiliary smoke-validation card defaults updated to point at the same
  15m export — passes end-to-end against the new schema.

**Open work, in order:**

1. Verify the completed full-suite artifact provenance against the exact
   manifest, repo commit, and run command.
2. Run the SHAP gate (Phase 4.5, Gate 1) against the same 15m export/run. See the
   _Validation Gating Before Live Trade Routing_ section for what
   counts as a pass.
3. Run the Monte Carlo gate (Phase 4.5, Gate 2) against the same OOS split.
4. Only after both gates clear, enable any TradingView alert that filters
   on `model_proba >= 0.75`.
5. Use the already-trained `--model-suite` side models only after the same
   validation/provenance gates clear.

Owner/next trigger: validation/provenance pass for `locked_20260512_083803`.

The previous "Hybrid+ 4-card" tuning chain
(`warbird_pro_v9_exit_cpcv`, `warbird_pro_v9_entry_filter_cpcv`,
`warbird_pro_v9_ag_meta_cpcv`, `warbird_pro_v9_joint_challenger`) is
formally deprecated and superseded by the single `train_v9_locked.py`
trainer. Those profile modules remain on disk for archival reference
only; do not invoke them as a chain.

---

## V9 Core AutoGluon — Active Plan (2026-05-12)

The earlier Hybrid+ 4-card system (`warbird_pro_v9_exit_cpcv`,
`warbird_pro_v9_entry_filter_cpcv`, `warbird_pro_v9_ag_meta_cpcv`,
`warbird_pro_v9_joint_challenger`) is **deprecated**. Path went 4 → 2 → single
Core card. The Core card supersedes all four.

### Live Pine Settings (authoritative — must match dataset builder exactly)

| Parameter                  | Value     | Pine input name        |
| -------------------------- | --------- | ---------------------- |
| ZigZag Deviation           | **3.0**   | `fibDeviationManual`   |
| ZigZag Depth               | **10**    | `fibDepthManual`       |
| ZigZag Threshold Floor %   | **0.25**  | `fibThresholdFloorPct` |
| HTF Confluence Tolerance % | **1.5**   | `htfConfTolPct`        |
| HTF 1H Lookback (bars)     | **8**     | `htf1hLookback`        |
| Min Fib Range (ATR)        | **0.5**   | `minFibRangeAtr`       |
| Midpoint Hysteresis %      | **2.0**   | `fibHysteresisPct`     |
| Primary EMA Length         | **21**    | `len`                  |
| Primary EMA Source         | **close** | `src`                  |
| Primary EMA Offset         | **1**     | `offset`               |
| Smoothing Type             | **EMA**   | `maTypeInput`          |
| Smoothing Length           | **9**     | `maLengthInput`        |

**Rule:** Before every dataset build, read the live TradingView indicator
inputs panel and verify the dataset-builder constants match exactly. Pine code
`input.float(default, ...)` defaults are NOT authoritative — the user's saved
TV settings are. Contamination incident (2026-05-05) used dev=4.0, depth=20,
floor=0.50 — all wrong; do not repeat.

**MA rule:** the current Pine gate is price above/below BOTH the primary EMA21
and the smoothing EMA9. The old `useMaGate`, `lengthMA=50`, and
`lengthEMA=21` EMA/SMA HPO surface is retired for V9/Core.

### Candlestick Status (removed from active V9)

Candlestick logic is not part of the current V9 live Pine lane. The active
indicator no longer has a candlestick operator input, candlestick hard gate,
candlestick detector block, or `ml_pat_*` export plots. Historical pattern
work, including `patRisingWindow`, `patBearEngulf`, `patMarubozuBlack`,
`patTweezerTop`, the older dropped patterns, and the unverified Three Line
Strike idea, is lineage only. Do not use those names as active V9 features or
training requirements unless Kirk explicitly opens a new candlestick research
lane with its own audit, export budget, and AG contract.

### Core Training Dataset Contract

- **Source:** Databento ES — Trades 365d (footprint reconstruction) + OHLCV
  bars 15m (training resolution; ES 5m only after 15m success per locked
  sequence) + OHLCV 1m (microstructure features only). Active Pine cross-asset
  context is NQ + 6E only. DXY/VIX/ZN Pine requests, inputs, and exports are
  retired; 6E momentum/z-score and trend code are the CME-native USD-pressure
  proxy. Any manifest-declared Databento side context must stay within the
  active NQ + 6E feature contract and must not be described as a Pine gate or
  Pine export. ZN/HG/VIX/DXY are historical or dropped diagnostics unless Kirk
  explicitly opens a new research lane.
- **Window:** 2025-05-11 → 2026-05-10 (1y, dense feature coverage; the actual
  built export covers that range). The newer Databento OHLCV-1s 2315d
  download is reserved for a future v10 long-horizon ensemble card, NOT
  Core (would NaN 2/3 of feature surface).
- **Feature surface:** the trainer, Core ETL export schema, tests, and manifest
  are aligned to the current active families: non-fib/non-color settings plus
  MA/RSI/liquidity/NQ+6E/footprint/HTF signal evidence. `ML_FEATURES = 75`;
  the six trade-discoverable combo fields added by
  `build_trade_dataset` remain `sl_atr_mult`, `tp_ratio`, `tp_family_code`,
  `target_distance_points`, `stop_distance_points`, and `rr_ratio`, making
  `MODEL_FEATURES = 81`. Protected fib-engine logic/settings and color/visual
  inputs are excluded from AG features. Risk Mode and candlestick fields are
  excluded from the active V9 feature contract. NQ + 6E and `ml_htf_conf_total`
  are admitted as Pine-emitted model evidence; any non-Pine Databento side
  context must be explicitly declared by manifest.
- HTF confluence parity is included in this recovery scope: Pine and Core ETL
  must both use direction-aware, corresponding-level `.382/.500/.618` hits with
  `htf1hLookback=8` mirrored as `knob_htf_1h_lookback`.
- **Label (triple barrier):** `winner_tp_before_sl` = 1 if **this combo's**
  TP price touched before its SL price within `FORWARD_SCAN_BARS = 10`
  (2.5h on 15m, 50m on 5m); 0 if SL touched first OR if TP and SL touched on
  the same bar (pessimistic same-bar policy — intrabar sequencing is
  unobservable) OR neither barrier touches within the 10-bar window
  (sideways → avoid). Entries closer than `MIN_FUTURE_BARS = 10` bars to
  end-of-data are DROPPED. TP price is read directly from Pine's per-row
  fib-ladder plots `ml_trade_tp1` (fib 1.000), `ml_trade_tp2` (fib 1.236),
  `ml_trade_tp3` (fib 1.618), `ml_trade_tp4` (fib 2.000), and
  `ml_trade_tp5` (fib 2.236) — label-construction inputs only, NOT
  `ML_FEATURES`. SL price is `entry ± ml_atr14 × sl_mult`. The split
  embargo is `EMBARGO_BARS = 11`.
- **Discoverable trade grid:** Each admitted entry expands into 20 rows —
  4 SL ATR multiples {0.75, 1.0, 1.5, 2.0} × 5 TP ratios
  {1.000, 1.236, 1.618, 2.000, 2.236}.
  Each row carries its own (`sl_atr_mult`, `tp_ratio`, `tp_family_code`,
  `target_distance_points`, `stop_distance_points`, `rr_ratio`) plus
  the resolution label. The classifier learns from the entire grid so
  inference can rank trade-shape variants, not just entry direction.
- **Auxiliary touch-event labels** (`tp_hit`, `stop_hit`) record physical
  barrier touches at the resolution bar, NOT resolution outcomes — see
  the canonical docstring at
  `scripts/ag/train_v9_locked.py::build_trade_dataset`. On same-bar
  collisions both auxiliary flags are 1 even though `winner_tp_before_sl=0`.
  Trained separately under `--model-suite` for the downstream EV layer.

### Kirk's Trade Preferences (operator targets — not in training objective)

- **Target move:** 10 ES points (40 ticks, $500/contract).
- **Target SL:** 1.0 ATR. **Max SL:** 2.0 ATR. The discoverable SL grid
  `DISCOVERABLE_SL_ATR_MULTS = (0.75, 1.0, 1.5, 2.0)` brackets this range.
- **Target breakeven range:** 1–3R. The trainer uses fib-extension TPs
  `DISCOVERABLE_TP_RATIOS = (1.000, 1.236, 1.618, 2.000, 2.236)` rather than fixed
  R-multiples; per-row `rr_ratio` is a model feature so AG can condition
  on the realized R per combo. No composite objective — the legacy
  Optuna-era `target_hit_rate` 0.14-weight metric is retired.
- **Inference threshold:** `proba > 0.75` for Grade A+ entries.
  `eval_metric='log_loss'` + `calibrate=True` ensures the threshold = real WR.
- **Session filter:** feature only (`ml_session_ny/london/asia`,
  `ml_minutes_from_open`), NOT a pre-filter — let AG learn the regime.

### V9 Core Training Surface

| File                                                                                | Role                                                                                               | Status                  |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------- |
| `scripts/ag/train_v9_locked.py`                                                     | Production V9 AutoGluon trainer (entry classifier; `--model-suite` adds TP/SL/MFE/MAE side models) | Ready for live training |
| `scripts/duckdb_local/cards/core_training/2026_05_09_warbird_pro_autogluon_core.py` | Auxiliary smoke-validation card (records local validation evidence; does NOT invoke AG)            | Live                    |

**AG config (2026-05-28 — UNLOCKED, TBD):**

The prior full-zoo locked config is retained below as reference only — model
selection is TBD pending deep research. Do not assume this is the active config.

- `preset='best_quality'`
- Full zoo (7 families) via explicit `hyperparameters` dict:
  GBM (×2: standard + extra_trees), CAT, XGB, RF (×2: gini + entropy),
  XT (×2: gini + entropy), NN_TORCH, FASTAI
- `num_bag_folds=0`, `num_stack_levels=0` — no bagging, time-series safe
- `dynamic_stacking=False` — override preset default for reproducibility
- `eval_metric='log_loss'`, `calibrate=True`
- `time_limit=7200s` (2h, full zoo lets NN_TORCH + FASTAI converge)
- `ag_args_ensemble={'fold_fitting_strategy': 'sequential_local'}`
- All OpenMP families single-threaded; `OMP_NUM_THREADS=1` env guard at top

**Side card (post-Core):** `scripts/duckdb_local/cards/side_models/` will hold a MAE
regression model that predicts maximum adverse excursion per trade. Used for
SL sizing AFTER the Core binary classifier ranks setups. Trained separately;
NOT grafted into Core.

### Production Launch Sequence (2026-05-12)

The V9 Core path is invoked directly. `scripts/ag/train_hard_gate.py`
(Postgres `ag_training_runs` table, `baseline.DEFAULT_DSN`) is the legacy
gate and is NOT on the V9 path; the training-hard-gate skill describes that
legacy flow and does not apply here.

```bash
# 1. Train the entry classifier (default 15m export, 2h time budget)
python3 scripts/ag/train_v9_locked.py
#    → models/warbird_pro_v9/locked_<tag>/entry/predictor.pkl
#    → models/warbird_pro_v9/locked_<tag>/entry/leaderboard.csv
#    → models/warbird_pro_v9/locked_<tag>/entry/feature_importance.csv
#    → models/warbird_pro_v9/locked_<tag>/v9_winner_clf_summary.json

# 2. SHAP gate (Phase 4.5, Gate 1)
python3 scripts/ag/shap_v9.py \
    --predictor-dir models/warbird_pro_v9/locked_<tag> \
    --csv scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv
#    → artifacts/shap_v9/shap_<ts>/shap_feature_summary.csv (+ per_class,
#      temporal_stability, calibration, redundancy, drop_candidates, summary.md)

# 3. Monte Carlo gate (Phase 4.5, Gate 2)
python3 scripts/ag/monte_carlo_v9.py \
    --predictor-path models/warbird_pro_v9/locked_<tag> \
    --csv scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.csv \
    --split oos
#    → artifacts/mc_v9/<tag>/ (overall + per-direction P&L, threshold sweep,
#      calibration, regime stability, streak profile)

# 4. Only after both gates pass — enable the TV alert that filters on
#    model_proba >= 0.75. Until then, the alert stays disabled.
```

The `--model-suite` flag on `train_v9_locked.py` additionally fits TP-touch,
SL-touch, MFE-regression, and MAE-regression predictors (~10h total).
Entry-only first; suite later, once the entry classifier passes both gates.
