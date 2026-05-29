# V9 ML Trading Research Operating System

**Date:** 2026-05-21
**Status:** Active reusable research workflow

This runbook turns the current Warbird Pro V9 audit, reasoning structure, and
modeling workflow into a repeatable operating system for future indicator,
strategy, feature-engineering, and retraining cycles.

It is intentionally phase-gated. A later phase is invalid if an earlier gate
has not passed with evidence. The current stale V9 model artifacts may inform
hypotheses, but they are not a trustworthy benchmark and must not anchor future
decisions.

## A. System Objectives

The long-term purpose is to make Warbird research repeatable without letting
agents skip the work that actually protects edge:

- preserve Pine/TradingView indicator behavior as the modeling object
- validate indicator behavior on chart before any modeling
- use short-window modeling for fast discovery and feature triage
- reserve full-year AutoGluon training for surviving indicator/configuration
  candidates only
- keep 1m, 3m, 5m, 15m, and hybrid timeframe decisions evidence-driven
- create audit trails for every dataset, feature set, split, model, SHAP run,
  Monte Carlo run, and promotion recommendation
- prevent stale baselines, generic timeframe claims, dirty-worktree artifacts,
  or unvalidated Pine changes from entering the research chain

This system applies to:

- Warbird Pro V9 indicator research cycles
- AutoGluon retraining cycles
- DuckDB/Pandera Core export changes
- SHAP and Monte Carlo evaluation cycles
- TP/SL policy research
- timeframe research across ES 1m, 3m, 5m, 15m, and hybrid structures
- future strategy revisions that remain under the local-first contract

## B. Full Phase Architecture

The required sequence is:

1. Startup authority and working-tree preflight
2. Research question and hypothesis registration
3. Indicator design or modification
4. Pine/static validation
5. TradingView on-chart validation
6. Data contract and export design
7. Short-window exploratory dataset build
8. Short-window exploratory AutoGluon baseline
9. SHAP and Monte Carlo discovery analysis
10. Feature triage and indicator pruning
11. Timeframe validation and architecture decision
12. Full-year dataset build
13. Full AutoGluon model-suite training
14. Robustness, calibration, and policy testing
15. Promotion readiness packet
16. Supabase/runtime boundary review
17. Monitoring preparation
18. Iteration closeout and audit archive

No phase may be skipped silently. If a phase is intentionally removed for a
cycle, the run record must state why, who approved it, and what risk is
accepted.

## C. Phase-By-Phase Operational Design

### Phase 1: Startup Authority And Working-Tree Preflight

**Objective:** Establish repo truth before research, edits, or modeling.

**Inputs:**

- `AGENTS.md`
- `docs/INDEX.md`
- `docs/MASTER_PLAN.md`
- `docs/contracts/pine_indicator_ag_contract.md`
- `docs/runbooks/startup_repo_review.md`
- `docs/agent-safety-gates.md`
- current `git status --short`
- current branch/upstream/worktree inventory

**Outputs:**

- read-only startup review when required
- dirty-worktree inventory
- touched-surface map
- authority-doc list for the cycle

**Dependencies:** None.

**Validation logic:**

- local clone at `/Volumes/Satechi Hub/warbird-pro` is source of truth
- branch and upstream are known
- unstaged files are classified as user work, prior agent work, generated
  artifacts, or task-owned changes
- current baseline artifacts are explicitly labeled as stale, exploratory, or
  promotion-grade

**Audit gates:**

- `git status --short` recorded
- relevant docs read
- current model/export artifacts not trusted without manifest and settings
  proof

**Rollback conditions:**

- if working tree contains unexplained changes in the target surface, stop and
  classify them before editing
- if repo authority docs conflict, apply governance precedence from
  `docs/INDEX.md`

**Tooling:**

- `rg`, `git status`, `git log`, `git diff`
- `docs/runbooks/startup_repo_review.md`

**Failure modes:**

- treating stale memory as current truth
- overwriting user edits
- launching modeling from a dirty, unexplained tree
- relying on GitHub remote instead of the local clone

### Phase 2: Research Question And Hypothesis Registration

**Objective:** Convert the operator request into a testable research question.

**Inputs:**

- user objective
- current indicator contract
- latest chart settings
- known stale and current artifacts
- timeframe question

**Outputs:**

- research question
- null hypothesis
- success criteria
- stop criteria
- proposed touched surfaces
- expected outputs

**Dependencies:** Phase 1.

**Validation logic:**

- the question separates indicator behavior, model behavior, execution policy,
  and operator usability
- the plan states what evidence would disprove the idea
- the plan does not assume stale baseline metrics are valid

**Audit gates:**

- `HOOK_ASSUMPTIONS_SURFACED`
- `HOOK_BASELINE_STATUS_CLASSIFIED`
- `HOOK_TIMEFRAME_CLAIM_NON_GENERIC`

**Rollback conditions:**

- if the question is only "train again," return to indicator/timeframe
  framing
- if success criteria are only net profit, add calibration, drawdown,
  trade-count, direction, and regime criteria

**Tooling:**

- Markdown run record
- issue/checkpoint document when the cycle is large

**Failure modes:**

- optimizing a vague target
- conflating more entries with better opportunities
- optimizing full-year data before indicator behavior is validated

### Phase 3: Indicator Design Or Modification

**Objective:** Make all approved indicator, parameter, smoothing, signal,
filter, export, and derived-feature changes before modeling.

**Inputs:**

- approved scope
- Pine source
- matching Python ETL/reconstruction code
- current Pine output/request budget
- previous chart-validation notes

**Outputs:**

- scoped Pine changes, if approved
- matching DuckDB/Python ETL changes, if needed
- updated tests/contracts/docs
- explicit note of unchanged protected surfaces

**Dependencies:** Phases 1-2.

**Validation logic:**

- Pine and Python compute the same concept when both surfaces exist
- protected fib anchor ownership and ladder math are unchanged unless explicitly
  approved
- output and request budgets are repriced before new Pine plots or requests
- no visual-only setting is mistaken for a model feature

**Audit gates:**

- `HOOK_PINE_APPROVAL_PRESENT`
- `HOOK_PINE_PYTHON_PARITY_DEFINED`
- `HOOK_OUTPUT_BUDGET_PRICED`
- `HOOK_NO_UNAPPROVED_FIB_CORE_CHANGE`

**Rollback conditions:**

- revert only task-owned edits if Pine compile/lint or chart validation fails
  and the operator approves rollback
- otherwise checkpoint the failed state and stop

**Tooling:**

- TradingView Pine Script
- `./scripts/guards/pine-lint.sh`
- `./scripts/guards/check-fib-scanner-guardrails.sh`
- `./scripts/guards/check-contamination.sh`
- `./scripts/guards/check-no-tv-force.sh`
- targeted `tests/ag/**`

**Failure modes:**

- Pine and Python feature semantics diverge
- output budget exceeds TradingView cap
- same feature name changes meaning across exports
- agent edits Pine without current-session approval

### Phase 4: Pine And Static Validation

**Objective:** Prove changed files satisfy repo-local static guards before chart
validation.

**Inputs:**

- touched Pine files
- touched ETL/training/test files
- repo guard scripts

**Outputs:**

- guard outputs
- targeted pytest outputs
- diff summary

**Dependencies:** Phase 3.

**Validation logic:**

- Pine compile/lint passes
- contamination and forced-TV checks pass
- Python tests cover changed contract behavior
- no unrelated refactor or formatting churn is present

**Audit gates:**

- `HOOK_STATIC_GUARDS_PASS`
- `HOOK_TARGETED_TESTS_PASS`

**Rollback conditions:**

- if static guards fail, stop before chart validation
- if tests reveal contract drift, either update the contract with approval or
  undo the task-owned drift

**Tooling:**

- repo guard scripts
- `pytest tests/ag/...`
- `npm run build` when required

**Failure modes:**

- treating tests as optional because the change "looks obvious"
- using test edits to hide a contract mismatch
- leaving docs inconsistent with code

### Phase 5: TradingView On-Chart Validation

**Objective:** Validate indicator behavior in the chart before any modeling
work.

**Inputs:**

- statically validated indicator
- current live TradingView settings
- target symbols/timeframes
- chart-validation checklist

**Outputs:**

- chart proof notes
- symbol/timeframe/study state
- screenshots or manual validation notes when available
- confirmed signal/fib/TP/SL/feature-export alignment

**Dependencies:** Phases 3-4.

**Validation logic:**

- indicator renders without hidden sync errors
- fib levels, HTF confluence, entry triggers, TP/SL ladder, footprint features,
  and hidden `ml_*` outputs behave as expected
- bullish, bearish, range, high-volatility, and low-volatility regimes are
  inspected
- signal timing matches bar-close expectations

**Audit gates:**

- `HOOK_CHART_VALIDATION_REQUIRED`
- `HOOK_SIGNAL_ALIGNMENT_CONFIRMED`
- `HOOK_MARKET_INTERACTION_CONFIRMED`

**Rollback conditions:**

- if chart behavior is wrong, return to Phase 3
- if TradingView CDP is unresponsive, apply the hard stop protocol in
  `AGENTS.md`

**Tooling:**

- TradingView
- `python3 scripts/ag/tv_connection_doctor.py --json` before any CDP/MCP
  operation
- `python3 scripts/ag/tv_auto_tune.py --storage jsonl preflight --indicator-only`
  when appropriate

**Failure modes:**

- training on an indicator that has never been visually verified
- trusting hidden plots without checking visible market behavior
- retry-looping TradingView automation after CDP failure

### Phase 6: Data Contract And Export Design

**Objective:** Define the exact dataset that will be built.

**Inputs:**

- validated indicator settings
- source type: TradingView export or Databento
- target symbol/timeframe/session
- label horizon and embargo requirements
- feature list

**Outputs:**

- dataset contract
- manifest requirements
- expected row/trade counts
- expected feature columns
- split strategy
- friction assumptions

**Dependencies:** Phase 5.

**Validation logic:**

- source kind is honest
- ES-only requirement is maintained for V9 Core
- no cloud Supabase tables, mislabeled data, or non-manifest-backed joins enter
  the dataset (FRED, macro, news, options approved under local-first policy
  when manifest-backed)
- features use information available at or before the bar
- labels use future windows only

**Audit gates:**

- `HOOK_DATA_SOURCE_HONEST`
- `HOOK_NO_EXTERNAL_STACK`
- `HOOK_TEMPORAL_ALIGNMENT_DEFINED`
- `HOOK_LABEL_HORIZON_DEFINED`

**Rollback conditions:**

- if the export cannot prove settings, source, or hash, rebuild the export
- if required columns are missing, return to indicator/export design

**Tooling:**

- DuckDB
- Pandera
- `fg-data-profiling` / `data_profiling`
- Databento historical APIs when source kind is Databento
- manifest JSON

**Failure modes:**

- mislabeled Databento rows as TradingView exports
- stale settings embedded in a fresh-looking CSV
- Python reconstructed features that do not match Pine behavior

### Phase 7: Short-Window Exploratory Dataset Build

**Objective:** Build a lightweight 1-2 month dataset for fast discovery and
elimination.

**Inputs:**

- Phase 6 dataset contract
- validated indicator/export source
- selected candidate timeframes

**Outputs:**

- short-window CSV/parquet exports
- manifests
- profiling reports
- row/trade/label distributions
- feature nonzero/null statistics

**Dependencies:** Phase 6.

**Validation logic:**

- this is explicitly exploratory, not promotion-grade
- date range is short enough for rapid iteration
- no final optimization claims are made from this phase
- row counts and label counts are sufficient for discovery

**Audit gates:**

- `HOOK_SHORT_BASELINE_ONLY`
- `HOOK_PROFILE_REPORT_PRESENT`
- `HOOK_FEATURE_COLUMNS_MATCH_CONTRACT`

**Rollback conditions:**

- if discovery window has too few entries, adjust timeframe/window only after
  documenting why
- if profiling reveals broken fields, return to Phase 3 or 6

**Tooling:**

- `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`
- DuckDB
- Pandera
- profiling reports
- `scripts/ag/report_v9_core_smoke.py` for smoke-style reporting patterns

**Failure modes:**

- treating short-window results as final proof
- using a window that is too favorable or too sparse
- ignoring null/zero feature diagnostics

### Phase 8: Short-Window Exploratory AutoGluon Baseline

**Objective:** Fit a lightweight model only to discover signal structure.

**Inputs:**

- short-window dataset
- feature list
- temporal split/embargo
- label definition

**Outputs:**

- exploratory AutoGluon run
- baseline metrics
- probability outputs
- feature importance artifacts

**Dependencies:** Phase 7.

**Validation logic:**

- temporal order is preserved
- no random shuffle
- no test-set tuning
- run metadata records feature list, split boundaries, label distribution, git
  hash, library versions, CSV hash, and manifest hash
- output is labeled exploratory

**Audit gates:**

- `HOOK_TEMPORAL_SPLIT_VALID`
- `HOOK_EXPLORATORY_LABEL_APPLIED`
- `HOOK_NAIVE_BASELINE_REPORTED`

**Rollback conditions:**

- if label distribution is broken or one-class, return to data/label design
- if model only beats naive baseline in one tiny cohort, do not advance

**Tooling:**

- AutoGluon Tabular
- `scripts/ag/train_v9_locked.py` patterns
- append-only `models/warbird_pro_v9/<tag>/`

**Failure modes:**

- using exploratory results as champion proof
- allowing AutoGluon to hide a broken feature contract
- ranking geometry leakage as "edge"

### Phase 9: SHAP And Monte Carlo Discovery Analysis

**Objective:** Identify clear winners, losers, unstable signals, and fragile
behavior before expensive training.

**Inputs:**

- exploratory model artifacts
- short-window dataset
- exact split truth
- friction assumptions

**Outputs:**

- SHAP summaries
- permutation importance
- calibration bins
- Monte Carlo robustness report
- feature stability report
- per-direction/per-session diagnostics

**Dependencies:** Phase 8.

**Validation logic:**

- SHAP is evaluated on held-out data
- feature ranking is checked by side, session, volatility regime, and timeframe
  where feasible
- Monte Carlo includes friction costs and drawdown tails
- active execution bins are calibrated

**Audit gates:**

- `HOOK_SHAP_STABILITY_REQUIRED`
- `HOOK_MC_ROBUSTNESS_REQUIRED`
- `HOOK_DIRECTION_SPLIT_REQUIRED`
- `HOOK_CALIBRATION_ACTIVE_BINS_REQUIRED`

**Rollback conditions:**

- if SHAP ranking is unstable or non-interpretable, triage features before
  retraining
- if Monte Carlo deteriorates versus naive or prior candidate, return to
  feature/indicator design

**Tooling:**

- `scripts/ag/shap_v9.py`
- `scripts/ag/monte_carlo_v9.py`
- SHAP
- NumPy/Pandas vectorized simulation
- optional mature experiment tracking such as MLflow if adopted later

**Failure modes:**

- accepting high EV with tiny trade count
- hiding a broken long side behind profitable shorts
- interpreting correlated duplicates as independent edge

### Phase 10: Feature Triage And Indicator Pruning

**Objective:** Remove weak inputs and preserve only feature families that earn
their complexity.

**Inputs:**

- SHAP outputs
- Monte Carlo outputs
- feature family map
- indicator/export cost
- Pine output budget

**Outputs:**

- keep/drop/watchlist decision table
- retrain candidate feature list
- indicator simplification recommendations
- required Pine/ETL changes for next cycle

**Dependencies:** Phase 9.

**Validation logic:**

- every dropped feature has evidence
- protected operator-visible indicator components are not removed by automation
  without approval
- feature redundancy is handled within families
- low-information features do not enter full-year training

**Audit gates:**

- `HOOK_WEAK_FEATURES_REMOVED_OR_JUSTIFIED`
- `HOOK_REDUNDANCY_REVIEW_COMPLETE`
- `HOOK_OPERATOR_FEATURE_APPROVAL_REQUIRED`

**Rollback conditions:**

- if a feature is operationally important but low SHAP, mark it operator-only
  rather than deleting it
- if a feature is predictive but brittle, move it to watchlist and require
  full-year confirmation

**Tooling:**

- SHAP summaries
- correlation matrices
- feature-family metadata
- Pine output budget report

**Failure modes:**

- feature hoarding
- deleting operator-critical context because it is not predictive
- keeping noisy features because they sound institutionally plausible

### Phase 11: Timeframe Validation And Architecture Decision

**Objective:** Decide whether the next cycle should use 1m, 3m, 5m, 15m, or a
hybrid structure.

**Inputs:**

- short-window results by timeframe
- chart-validation observations
- trigger frequency
- collision rates
- slippage assumptions
- SHAP/MC robustness

**Outputs:**

- timeframe decision record
- primary entry timeframe
- context timeframe
- parked timeframes with reopen criteria

**Dependencies:** Phases 5, 7-10.

**Validation logic:**

- justification covers discretionary and ML perspectives
- trade frequency, entry precision, label quality, microstructure noise,
  regime clarity, feature stability, stationarity, data density, learnability,
  overfitting risk, execution practicality, latency sensitivity, volatility
  responsiveness, and SHAP/MC interpretability are addressed
- generic claims like "15m has less noise" are rejected

**Audit gates:**

- `HOOK_TIMEFRAME_JUSTIFICATION_NON_GENERIC`
- `HOOK_SHORT_TF_LABEL_NOISE_REVIEWED`
- `HOOK_HYBRID_STRUCTURE_EVALUATED`

**Rollback conditions:**

- if timeframe evidence is inconclusive, run another short-window discovery
  pass instead of full-year training
- if shorter timeframes only win before friction, reject or reframe as
  execution timing research

**Tooling:**

- per-timeframe DuckDB exports
- SHAP/MC comparison reports
- chart screenshots/notes
- optional Databento resampling references

**Failure modes:**

- selecting 1m/3m because it creates more labels
- selecting 15m because it looks cleaner but cannot meet operator needs
- ignoring 5m entries with 15m context as the likely first hybrid candidate

### Phase 12: Full-Year Dataset Build

**Objective:** Build the larger dataset only after indicator, feature, and
timeframe triage pass.

**Inputs:**

- surviving indicator configuration
- surviving feature list
- selected timeframe architecture
- source contract
- split/embargo policy

**Outputs:**

- full-year CSV/parquet export
- manifest
- profiling report
- row/trade/label distribution
- split plan

**Dependencies:** Phase 11.

**Validation logic:**

- only surviving features/configurations enter
- source and settings are current
- manifest hashes match exported data
- temporal coverage is sufficient
- label horizon and embargo match trainer contract

**Audit gates:**

- `HOOK_FULL_YEAR_ALLOWED`
- `HOOK_MANIFEST_HASH_MATCH`
- `HOOK_SPLIT_EMBARGO_VALID`

**Rollback conditions:**

- if data coverage is insufficient, return to timeframe/source design
- if feature columns drift, return to Phase 6

**Tooling:**

- DuckDB
- Pandera
- profiling report
- `build_core_dataset.py`

**Failure modes:**

- launching full-year training from stale settings
- importing eliminated features
- building a dataset the trainer cannot validate

### Phase 13: Full AutoGluon Model-Suite Training

**Objective:** Train the production-grade candidate suite.

**Inputs:**

- full-year validated dataset
- locked feature list
- split contract
- time limit
- AutoGluon config

**Outputs:**

- entry classifier
- TP touch head
- stop touch head
- MFE regressor
- MAE regressor
- leaderboard and feature importance
- run summary

**Dependencies:** Phase 12.

**Validation logic:**

- full zoo is used when compute budget allows
- chronological split and embargo are enforced
- `eval_metric='log_loss'` for probability heads
- calibration is enabled where supported
- model artifacts are append-only

**Audit gates:**

- `HOOK_AG_RUN_METADATA_COMPLETE`
- `HOOK_MODEL_SUITE_COMPLETE`
- `HOOK_NO_RANDOM_TIME_SPLIT`

**Rollback conditions:**

- if validation fails, stop and fix dataset or trainer contract
- if only one head trains cleanly, do not promote suite behavior

**Tooling:**

- AutoGluon Tabular
- `scripts/ag/train_v9_locked.py`
- append-only `models/warbird_pro_v9/locked_<tag>/`

**Failure modes:**

- interpreting entry-head success as full policy success
- missing side-model failures
- omitting library/version/provenance metadata

### Phase 14: Robustness, Calibration, And Policy Testing

**Objective:** Decide whether the trained suite is useful under trading
friction and regime stress.

**Inputs:**

- full model suite
- full-year dataset
- SHAP outputs
- Monte Carlo outputs
- threshold sweep
- TP/SL grids

**Outputs:**

- robustness report
- calibrated threshold recommendation
- TP family policy
- SL policy
- long/short/session/regime breakdown
- no-trade regime notes

**Dependencies:** Phase 13.

**Validation logic:**

- active threshold bins are calibrated
- after-cost EV is positive with acceptable drawdown
- trade count is sufficient
- long and short sides are reviewed separately
- Monte Carlo drawdown tails are tolerable
- policy is stable across subperiods

**Audit gates:**

- `HOOK_ACTIVE_BIN_CALIBRATION_PASS`
- `HOOK_MC_DRAWDOWN_PASS`
- `HOOK_TRADE_COUNT_FLOOR_PASS`
- `HOOK_DIRECTIONAL_ASYMMETRY_EXPLAINED`
- `HOOK_POLICY_NOT_ENTRY_ONLY`

**Rollback conditions:**

- if robustness fails, return to feature triage or timeframe decision
- if model only works in one regime, mark it as regime-specific and do not
  promote as general

**Tooling:**

- `scripts/ag/shap_v9.py`
- `scripts/ag/monte_carlo_v9.py`
- policy sweep helpers
- mature calibration plots and reliability diagrams if added later

**Failure modes:**

- approving a model because one threshold has high win rate with too few trades
- relying on entry probability while stop/TP heads disagree
- ignoring drawdown tails

### Phase 15: Promotion Readiness Packet

**Objective:** Convert validated research into an operator-safe recommendation.

**Inputs:**

- robustness report
- chart-validation notes
- model artifacts
- feature triage record
- timeframe decision

**Outputs:**

- recommended timeframe structure
- Pine settings/build recommendation
- confidence thresholds
- TP/SL policy
- no-trade filters
- expected frequency
- risk limits
- required manual TradingView steps
- non-promotion caveats

**Dependencies:** Phase 14.

**Validation logic:**

- recommendation is tied to exact artifacts
- Pine edits/default changes are separated from model policy
- Supabase/cloud deployment is not implied
- operator can reproduce the chart setup

**Audit gates:**

- `HOOK_PROMOTION_PACKET_COMPLETE`
- `HOOK_PINE_PROMOTION_APPROVAL_REQUIRED`
- `HOOK_OPERATOR_REPRODUCIBILITY_PRESENT`

**Rollback conditions:**

- if packet cannot identify exact settings/artifacts, do not promote
- if Pine source change is required, open a new approved Pine cycle

**Tooling:**

- Markdown promotion record
- manifests
- SHAP/MC artifacts
- TradingView chart notes

**Failure modes:**

- silent live-routing assumption
- changing Pine defaults without approval
- treating model artifact existence as promotion proof

### Phase 16: Supabase And Runtime Boundary Review

**Objective:** Ensure runtime/support surfaces do not become hidden training
truth.

**Inputs:**

- promotion packet
- any runtime dashboard/API changes
- Supabase migration intent

**Outputs:**

- cloud boundary confirmation
- allowed runtime artifacts
- forbidden raw research data list
- migration notes if needed

**Dependencies:** Phase 15.

**Validation logic:**

- Supabase remains runtime/support only
- no raw trials, labels, full research datasets, or hidden scoring packets are
  pushed to cloud
- local DuckDB remains the training/data authority

**Audit gates:**

- `HOOK_SUPABASE_RUNTIME_ONLY`
- `HOOK_NO_CLOUD_TRAINING_MIRROR`

**Rollback conditions:**

- if cloud change would store raw labels/trials, reject or redesign
- if API implies live execution, require separate architecture approval

**Tooling:**

- `supabase/migrations/` only for approved runtime DDL
- Next.js build checks when runtime code changes
- `docs/cloud_scope.md`

**Failure modes:**

- cloud data drift
- accidental raw research upload
- runtime UI overstating model readiness

### Phase 17: Monitoring Preparation

**Objective:** Define how promoted behavior will be watched after adoption.

**Inputs:**

- promotion packet
- expected trade frequency
- calibration thresholds
- feature list
- data-source update cadence

**Outputs:**

- monitoring checklist
- drift metrics
- retraining triggers
- failure alerts
- manual review cadence

**Dependencies:** Phase 15 and Phase 16 when runtime surfaces are touched.

**Validation logic:**

- monitor trade count drought/flood
- monitor long/short imbalance
- monitor active-bin calibration
- monitor feature staleness and missing columns
- monitor slippage and friction drift
- monitor market regime changes

**Audit gates:**

- `HOOK_MONITORING_PLAN_PRESENT`
- `HOOK_RETRAINING_TRIGGERS_DEFINED`

**Rollback conditions:**

- if live/paper behavior diverges from expected calibration, pause promotion
  and reopen research cycle
- if data/source drift appears, disable new training/promotion claims

**Tooling:**

- local monitoring artifacts
- dashboard/runtime support if approved
- Supabase only for runtime summaries, not raw research truth

**Failure modes:**

- model decay goes unnoticed
- frequency target overwhelms quality target
- retraining happens reactively without full gate sequence

### Phase 18: Iteration Closeout And Audit Archive

**Objective:** Make the cycle reproducible and safe for the next run.

**Inputs:**

- all artifacts from Phases 1-17
- final repo diff
- test/guard outputs

**Outputs:**

- closeout record
- artifact index
- changed-file summary
- unresolved risks
- next-cycle recommendations
- updated docs when operational truth changed

**Dependencies:** all previous phases reached or explicitly stopped.

**Validation logic:**

- every artifact has a path
- every skipped phase has a reason
- every failed gate has a disposition
- docs reflect accepted new truth

**Audit gates:**

- `HOOK_CLOSEOUT_COMPLETE`
- `HOOK_DOCS_SYNCED`
- `HOOK_NO_UNVERIFIED_COMPLETION_CLAIM`

**Rollback conditions:**

- if docs and code disagree, update docs or mark implementation incomplete
- if verification is missing, final status is incomplete

**Tooling:**

- Markdown checkpoint
- `git diff --stat`
- `git diff --check`
- repo guard scripts when committing/pushing

**Failure modes:**

- leaving chat-only decisions
- forgetting which artifact was authoritative
- future agents reusing stale outputs

## D. Reusable Checkpoint Hooks

Hooks are reusable gate names. They can be implemented as manual checklist
items, guard-script checks, CI validations, or future workflow-orchestration
nodes. A hook failure is a hard stop unless the operator explicitly records an
exception.

### Authority And Assumption Hooks

`HOOK_BASELINE_STATUS_CLASSIFIED`

- Requires every referenced model/export to be labeled `stale`,
  `exploratory`, `candidate`, or `promotion-grade`.
- Fails if stale baselines are used as benchmark truth.

`HOOK_ASSUMPTIONS_SURFACED`

- Requires explicit assumptions for source data, timeframe, chart settings,
  label horizon, friction, and model objective.
- Fails on unstated assumptions.

`HOOK_DEPENDENCIES_VERIFIED`

- Requires the phase to list upstream artifacts and docs.
- Fails if the plan references helper scripts or tools not found in the repo.

### Indicator Hooks

`HOOK_PINE_APPROVAL_PRESENT`

- Required before any `.pine` edit.
- Fails if approval is missing in the current session.

`HOOK_OUTPUT_BUDGET_PRICED`

- Requires plot, alertcondition, request.security, request.footprint, line, box,
  and table budget review for Pine edits.
- Fails if new outputs are added without budget accounting.

`HOOK_PINE_PYTHON_PARITY_DEFINED`

- Required when Pine logic has a Python/DuckDB reconstruction.
- Fails if one surface changes and the other remains semantically stale.

`HOOK_CHART_VALIDATION_REQUIRED`

- Required before modeling after indicator changes.
- Fails if the indicator has not been placed on chart and visually validated.

`HOOK_SIGNAL_ALIGNMENT_CONFIRMED`

- Requires manual or tool-backed validation that signals fire on expected bars,
  with no hidden plot/export mismatch.

`HOOK_MARKET_INTERACTION_CONFIRMED`

- Requires behavior review across trend, pullback, chop, high-volatility,
  low-volatility, long, and short regimes.

### Data Hooks

`HOOK_DATA_SOURCE_HONEST`

- Requires manifest source kind to match actual source.
- Fails on mislabeled Databento/TradingView artifacts.

`HOOK_NO_EXTERNAL_STACK`

- Blocks cloud joins, mislabeled data, or non-manifest-backed joins in active
  V9 Core training. FRED, macro, news, options, and cross-asset data are
  approved under local-first policy (2026-05-28) when manifest-backed.

`HOOK_TEMPORAL_ALIGNMENT_DEFINED`

- Requires every feature at time `t` to be available at or before `t`.
- Fails on backward-fill, future leakage, or release-time ambiguity.

`HOOK_LABEL_HORIZON_DEFINED`

- Requires deterministic label horizon, collision policy, and embargo.
- Fails if label horizon is implicit or inherited from stale runs.

`HOOK_MANIFEST_HASH_MATCH`

- Requires CSV/parquet hash and manifest-declared hash to match.

### Modeling Hooks

`HOOK_SHORT_BASELINE_ONLY`

- Marks 1-2 month runs as discovery-only.
- Fails if used for promotion or final model selection.

`HOOK_TEMPORAL_SPLIT_VALID`

- Requires chronological split and embargo.
- Fails on random split or shuffled time-series.

`HOOK_NAIVE_BASELINE_REPORTED`

- Requires majority-class or equivalent naive baseline comparison.

`HOOK_AG_RUN_METADATA_COMPLETE`

- Requires git commit, dirty status, feature list, split boundaries, label
  distribution, row counts, library versions, time limit, model config, and
  artifact paths.

`HOOK_MODEL_SUITE_COMPLETE`

- Requires entry, TP, stop, MFE, and MAE heads when model-suite behavior is
  claimed.

### SHAP And Monte Carlo Hooks

`HOOK_SHAP_STABILITY_REQUIRED`

- Requires feature importance review across folds/cohorts/timeframes where
  feasible.
- Fails if feature ranking is unstable and no triage decision is made.

`HOOK_WEAK_FEATURES_REMOVED_OR_JUSTIFIED`

- Requires low-information features to be dropped, parked, or explicitly
  justified.

`HOOK_MC_ROBUSTNESS_REQUIRED`

- Requires after-cost Monte Carlo with drawdown tails and path distributions.

`HOOK_ACTIVE_BIN_CALIBRATION_PASS`

- Requires calibration in the probability bins intended for execution.

`HOOK_DIRECTION_SPLIT_REQUIRED`

- Requires long and short metrics separately.
- Fails if combined EV hides a broken side.

`HOOK_MC_DRAWDOWN_PASS`

- Requires drawdown tails within operator-acceptable bounds.

### Timeframe Hooks

`HOOK_TIMEFRAME_JUSTIFICATION_NON_GENERIC`

- Requires specific discretionary and ML reasoning for selected timeframe.
- Fails on generic claims such as "15m is less noisy."

`HOOK_SHORT_TF_LABEL_NOISE_REVIEWED`

- Requires label collision, slippage, latency, and microstructure noise review
  for 1m/3m/5m.

`HOOK_HYBRID_STRUCTURE_EVALUATED`

- Requires explicit consideration of 5m entries with 15m context before
  selecting a single-timeframe path.

### Promotion And Monitoring Hooks

`HOOK_POLICY_NOT_ENTRY_ONLY`

- Requires TP/SL and regime policy review, not entry probability alone.

`HOOK_PROMOTION_PACKET_COMPLETE`

- Requires exact artifacts, settings, threshold, timeframe, TP/SL policy,
  risk notes, and manual validation steps.

`HOOK_SUPABASE_RUNTIME_ONLY`

- Confirms Supabase is runtime/support only, not raw training truth.

`HOOK_MONITORING_PLAN_PRESENT`

- Requires drift, calibration, trade-count, feature-staleness, and retraining
  triggers before promoted behavior is treated as operational.

`HOOK_CLOSEOUT_COMPLETE`

- Requires artifact index, failed/skipped gate disposition, changed-file list,
  verification outputs, and next steps.

## E. Sequential Dependency Graph

```text
Authority Preflight
  -> Research Question
  -> Indicator Design
  -> Static Validation
  -> Chart Validation
  -> Data Contract
  -> Short-Window Build
  -> Exploratory AutoGluon
  -> SHAP/MC Discovery
  -> Feature Triage
  -> Timeframe Decision
  -> Full-Year Build
  -> Full Model Suite
  -> Robustness/Policy Testing
  -> Promotion Packet
  -> Supabase/Runtime Boundary Review
  -> Monitoring Prep
  -> Closeout Archive
```

Dependency rules:

- indicator validation always precedes modeling
- short-window discovery always precedes full-year training
- feature triage always precedes full-year training
- timeframe decision always precedes full-year training
- full model suite must precede policy claims
- robustness testing must precede promotion
- monitoring prep must precede operational rollout

## F. Technical Stack Mapping

### TradingView Pine Script

Role:

- canonical indicator behavior
- visible operator surface
- hidden `ml_*` export fields
- entry, TP, SL, fib, footprint, and confluence behavior

Rules:

- no edits without explicit approval
- chart validation precedes modeling
- output/request budget is repriced before edits
- Pine and Python reconstruction must stay semantically aligned

### DuckDB

Role:

- local file-backed feature build and dataset assembly
- fast filtering/sorting/joining over parquet and CSV
- active V9/Core data path

Rules:

- local DuckDB is training data authority
- exports must be manifest-backed
- feature columns must match trainer contract

### Pandera And Data Profiling

Role:

- schema validation
- contract validation
- null/type/range checks
- profile reports for smoke and full exports

Rules:

- missing required fields block modeling
- profile reports are required for dataset acceptance

### AutoGluon

Role:

- calibrated entry classifier
- TP touch model
- stop touch model
- MFE/MAE regressors
- full-zoo comparison when compute budget allows

Rules:

- chronological splits only
- model-suite claims require all heads
- exploratory runs are labeled exploratory
- full-year runs require clean feature/timeframe triage first

### SHAP

Role:

- feature admission/removal evidence
- cohort and timeframe interpretability
- weak/redundant feature detection

Rules:

- SHAP must not be used alone for promotion
- unstable SHAP requires feature triage, not blind training

### Monte Carlo

Role:

- path robustness
- drawdown tails
- threshold and policy stress testing
- TP/SL family robustness

Rules:

- include friction
- direction/session/regime splits are mandatory
- high win rate with tiny trade count is not enough

### Supabase

Role:

- runtime/support/dashboard only
- optional summary storage after promotion

Rules:

- no raw research datasets
- no raw labels/trials
- no hidden cloud training mirror
- no live scoring packet unless architecture is explicitly reopened

### Research Tooling

Preferred mature tooling and patterns:

- AutoGluon Tabular for model families and ensembling
- DuckDB for local analytical storage and reproducible file builds
- Pandera for schema contracts
- SHAP for model explanation
- NumPy/Pandas vectorized Monte Carlo and calibration analysis
- Databento official historical APIs for approved market-data rows
- MLflow or similar append-only experiment tracking may be adopted later, but
  only if it records local artifact truth without replacing repo manifests

Avoid:

- hand-rolled experiment tracking when a mature append-only tool is available
- ad hoc CSV string parsing where DuckDB/Pandas schemas are available
- cloud databases as hidden research truth
- custom orchestration before the phase gates are stable as docs/scripts

## G. Risk And Failure Framework

### Operational Risks

- dirty working tree contaminates research state
- future agents trust stale baselines
- Pine edit proceeds without approval
- chart validation is skipped
- docs and code drift after accepted changes

Mitigation:

- Phase 1 preflight
- baseline classification hook
- Pine approval hook
- closeout archive

### Data Risks

- source kind mislabeled
- settings embedded in export are stale
- missing feature columns
- malformed OHLCV bars
- timeframe/session gaps
- contract-roll effects

Mitigation:

- manifest hash gate
- Pandera validation
- profiling report
- timestamp/session checks

### Modeling Risks

- random splits or leakage
- full-year training before triage
- geometry variables dominate without true edge
- model-suite side heads fail silently
- calibration breaks in execution bins

Mitigation:

- temporal split hook
- short-window-only hook
- model-suite-complete hook
- active-bin calibration hook

### Quant Research Risks

- noisy labels on 1m/3m
- 15m too sparse for opportunity target
- 5m over-loosened into garbage candidates
- combined EV hides broken long or short side
- SHAP rankings unstable across regimes

Mitigation:

- timeframe justification hook
- label-noise review
- direction split hook
- SHAP stability hook

### Execution Risks

- slippage destroys short-timeframe edge
- latency matters more than model output
- same-bar collision policy distorts labels
- TP/SL recommendations are not actionable in Pine/operator workflow

Mitigation:

- friction-inclusive Monte Carlo
- collision-rate review
- policy-not-entry-only hook
- promotion packet with operator steps

### Infrastructure Risks

- Supabase becomes hidden research truth
- local artifacts overwritten
- helper scripts referenced but missing
- TradingView CDP failure triggers unsafe automation

Mitigation:

- runtime-only Supabase hook
- append-only artifact convention
- dependency verification hook
- TradingView hard-stop protocol

## H. Reusability And Scaling Strategy

Every cycle should create or update a run record with:

- research question
- phase checklist
- hook outcomes
- source artifacts
- feature list
- dataset manifest
- model tag
- SHAP tag
- Monte Carlo tag
- promotion decision
- monitoring plan

Recommended reusable directory pattern:

```text
artifacts/research_cycles/<cycle_id>/
  cycle_plan.md
  indicator_validation.md
  dataset_contract.md
  short_window/
    manifest.json
    profile.html
    metrics.json
  shap/
  monte_carlo/
  feature_triage.md
  timeframe_decision.md
  full_year/
  promotion_packet.md
  closeout.md
```

Recommended cycle ID format:

```text
YYYYMMDD_<surface>_<research_question_slug>
```

Scaling path:

1. Keep the workflow in Markdown until the gates are stable.
2. Convert high-value hooks into repo guard scripts.
3. Add structured run metadata JSON for each cycle.
4. Optionally adopt MLflow or another mature experiment tracker for model
   metadata, while keeping manifests and repo docs authoritative.
5. Add dashboard summaries only after the cloud boundary is explicitly defined.

The system is reusable because each cycle has the same skeleton:

```text
Validate indicator -> build small -> discover -> triage -> select timeframe
-> build full -> train suite -> stress policy -> promote or reject -> monitor
```

## I. Final Audit Completeness Check

This runbook includes:

- all critical phases from research through monitoring
- explicit indicator-before-modeling sequencing
- short-window exploratory baseline requirements
- MC/SHAP feature triage requirements
- full-year training entry conditions
- timeframe research gates
- AutoGluon, DuckDB, Supabase, Pine, SHAP, and Monte Carlo stack mapping
- phase-specific validation logic
- rollback and failure handling
- reusable checkpoint hooks
- dependency graph
- scaling strategy for repeated cycles

Nothing in this workflow authorizes:

- Pine edits without explicit approval
- modeling before chart validation
- full-year training from stale indicator settings
- treating the current stale baseline as benchmark truth
- storing raw research truth in Supabase
- skipping feature triage before expensive training
