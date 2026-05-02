# Putting Optuna on Steroids: A Unified Optimization & Training Platform for Warbird

**Date:** 2026-05-02
**Author:** Claude (research agent) — at Architect's request
**Scope:** Deep research on Optuna as the central platform for all Warbird optimization and training, casting wide across the Python ML/DL ecosystem. Trading-context: MES/ZL futures, Warbird fib structure, Apple Silicon, no Docker.

---

## 0. Executive Summary — the One True Stack

For the Mac Mini M4 Pro 24 GB primary + MacBook Air M3 8 GB satellite, no Docker, allergy to paid services:

| Layer | Pick | Why |
|---|---|---|
| Optuna core | **`optuna >= 4.7`** (Jan 19 2026 release) | Latest stable; AutoSampler-ready; GPSampler now supports constrained multi-objective. |
| Integrations | **`optuna-integration`** (separate pip package) | The `optuna.integration.*` modules have been migrating out of core into this package since v3.2 (PyTorch Lightning, LightGBM, XGBoost, CatBoost, MLflow, W&B, BoTorch, Dask, fastai, sklearn, Trackio, etc.). The core import paths still work as shims for backward compatibility, but install `optuna-integration[lightgbm,xgboost,catboost,sklearn,mlflow,pytorch_lightning,botorch]` explicitly. |
| Sampler | **AutoSampler from OptunaHub** (`samplers/auto_sampler`) | As of Optuna 4.6 (Nov 2025), AutoSampler fully covers single-, multi-objective, and constrained problems by switching between TPE / GP / NSGA-II / NSGA-III based on the search space size and budget. |
| Pruner | **HyperbandPruner** for ML model training, **WilcoxonPruner** for walk-forward backtest folds | Hyperband dominates Median/Successive-Halving in Optuna's own benchmarks for iterative model training; Wilcoxon (added v3.6) was practically built for "score this strategy across N CV folds and stop early if it's stochastically worse than the incumbent." |
| Storage | **`JournalStorage` + `JournalFileBackend`** on the Mac Mini's local SSD, exported via SMB/AFP to the MacBook Air | Stable since Optuna 4.0. SQLite is officially "do not use over a network share" in the Optuna FAQ; PostgreSQL is overkill for two boxes. JournalStorage is NFS/SMB-safe by design. |
| Orchestration | **Hydra** (`hydra-optuna-sweeper`) | Config-driven, reproducible CLI runs across studies. |
| Tracking | **MLflow** (local file store) via `MLflowCallback` | Free, no service required, plays clean with Optuna; child-run grouping per Optuna trial. |
| Dashboard | **`optuna-dashboard`** + `optuna-fast-fanova` | Real-time visualisation; v0.20 added LLM-driven natural-language plot generation. |
| Backtest engine | **`vectorbt`** (open source) for parameter sweeps + custom event-driven engine for the Warbird fib logic | vectorbt for vectorised, Numba-accelerated grid/random sweeps; event-driven loop for the rules. |
| TA library | **`pandas-ta-classic`** (community fork, actively maintained 2024-2025) | Original `pandas-ta` is in maintenance limbo; `pandas-ta-classic` on PyPI is the live fork with TA-Lib bridge. |
| TradingView pull | **`tvdatafeed`** (rongardF fork) | 5,000-bar chunks per timeframe; non-Selenium since 2.0; combine with a local Parquet cache. |
| Data leakage protection | **Combinatorial Purged CV** (skfolio's `CombinatorialPurgedCV` or `timeseriescv`) + **Deflated Sharpe Ratio** as a post-study filter | López de Prado's CPCV is gold standard; pair with DSR (Bailey & Lopez de Prado 2014). |
| Hardware strategy | Single-process trials with internal threading on the Mac Mini, secondary worker on the Air pulling from the same Journal log | Don't run AutoGluon on the Air — use it for cheap models or as a TPE warmer. |

---

## 1. Core Optuna Integration Patterns (2025–2026)

### 1.1 `optuna.integration` → `optuna-integration` package split

Starting v3.2 (mid-2023) and continuing through 4.x, integration modules migrated out of core into `optuna-integration`. Today the package ships extras for `[botorch, catboost, comet, dask, fastai, fastaiv2, keras, lightgbm, mlflow, pytorch-distributed, pytorch-ignite, pytorch-lightning, shap, sklearn, skorch, tensorboard, tensorflow, tfkeras, wandb, xgboost, trackio]`.

**Modern import:** `from optuna_integration.lightgbm import LightGBMPruningCallback` (the old `from optuna.integration import ...` still works as a shim but warns).

Install for Warbird:

```bash
pip install \
  "optuna>=4.7" \
  "optuna-integration[lightgbm,xgboost,catboost,sklearn,mlflow,pytorch_lightning,botorch]" \
  "optunahub" \
  "optuna-dashboard[fast-fanova]" \
  "cmaes" "scipy" "torch" --extra-index-url https://download.pytorch.org/whl/cpu
```

### 1.2 The objective function pattern

```python
import optuna

def objective(trial: optuna.Trial) -> float | tuple[float, float]:
    rr_min      = trial.suggest_float("rr_min", 1.5, 3.5, step=0.1)
    fib_entry   = trial.suggest_categorical("fib_entry", [0.5, 0.618, 0.65])
    target_ext  = trial.suggest_categorical("target_ext", [1.0, 1.236, 1.382, 1.618])
    vix_thresh  = trial.suggest_float("vix_thresh", 14.0, 30.0)
    swing_lookback = trial.suggest_int("swing_lookback", 8, 80, log=True)

    trial.set_user_attr("git_sha", os.environ.get("GIT_SHA", "dev"))

    sharpe_per_fold = []
    for fold_idx, (train_idx, test_idx) in enumerate(walk_forward_splits):
        result = run_warbird_backtest(train_idx, test_idx, **trial.params)
        sharpe_per_fold.append(result.sharpe)
        trial.report(result.sharpe, step=fold_idx)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(sharpe_per_fold))
```

`study.optimize(objective, n_trials=500, timeout=3600*8, gc_after_trial=True)` is the production call. `gc_after_trial=True` matters on the 8 GB Air to release per-trial DataFrames.

### 1.3 `Trial.suggest_*` best practices for trading

| Method | Use for | Example |
|---|---|---|
| `suggest_categorical` | Discrete sets (Fib levels, on/off flags) | `fib_entry ∈ {0.5, 0.618, 0.65}` |
| `suggest_int(name, lo, hi, log=False)` | Bar lookbacks, ATR periods | `atr_period ∈ [5, 50]` |
| `suggest_float(name, lo, hi, log=True)` | Risk per trade, learning rates | `risk_pct = log [0.0025, 0.02]` |
| `suggest_float(..., step=0.1)` | Quantised continuous (R:R, ATR mults) | `rr_min ∈ [1.5, 3.5] step 0.1` |

**Three traps:**
1. Don't make the search space asymmetric to the prior — putting `rr_min` between 0.5 and 5.0 wastes 80% of trials in the unprofitable region.
2. Don't `suggest_categorical` for ordered numeric values — strips ordering from TPE/GP. Use `suggest_float` with `step=`.
3. `suggest_uniform` / `suggest_loguniform` are deprecated. Use `suggest_float(..., log=True)`.

### 1.4 Storage — the right backend for two-Mac setup

Optuna FAQ is unambiguous:
- **SQLite** is fine for single machine, single process. **Don't** put it on a network share.
- **PostgreSQL/MySQL** (RDBStorage) is recommended scale-out path; v4.1 added UPSERT acceleration.
- **JournalStorage** (stable in Optuna 4.0) uses an append-only operation log and **is** safe over NFS/SMB.

For Warbird:

```python
from optuna.storages import JournalStorage
from optuna.storages.journal import JournalFileBackend

storage = JournalStorage(
    JournalFileBackend("/Volumes/MacMiniShare/warbird/studies/zl_v17.log")
)
study = optuna.create_study(
    study_name="zl_v17",
    storage=storage,
    sampler=optunahub.load_module("samplers/auto_sampler").AutoSampler(seed=42),
    directions=["maximize", "minimize"],   # Sharpe ↑, max DD ↓
    load_if_exists=True,
)
```

### 1.5 Distributed / parallel patterns

- **Single-machine, multi-thread**: `study.optimize(objective, n_jobs=N)` — simplest, GIL-bound for pure Python, fine when objective spends time in C extensions (Numba/LightGBM).
- **Single-machine, multi-process**: launch N independent `python run_study.py` processes pointing at the same storage. Most reliable — each process has its own heap, OOM in one trial doesn't kill others.
- **Multi-machine**: same pattern, storage on shared volume (Journal) or network DB.
- **Heartbeat**: `RDBStorage(url=..., heartbeat_interval=60, grace_period=120, failed_trial_callback=RetryFailedTrialCallback(max_retry=3))`. If a worker dies, others mark trial FAILED after grace period and re-enqueue.
- **gRPC storage proxy** (Optuna 4.5+, `wait_server_ready` added 4.5/4.6) — recommended path beyond two boxes.

### 1.6 Samplers — pick by problem shape

| Sampler | Best for |
|---|---|
| **AutoSampler** (OptunaHub) | Default for everything. Picks TPE/GP/NSGA-II/NSGA-III based on dimensionality and objectives. Full multi-objective + constrained support since 4.6. |
| TPESampler | Mixed continuous + categorical, < 1k trials, ≤ ~20 dims. Will be replaced as default in v5. |
| GPSampler | Smooth continuous, expensive evaluations (< 200 trials). Constrained MO since v4.5. |
| CmaEsSampler | High-dim continuous, no categoricals. |
| NSGAIISampler / NSGAIIISampler | Multi-objective Pareto fronts. NSGA-III for 4+ objectives. |
| BoTorchSampler | Bayesian-optimal MO with constraints. Requires `optuna-integration[botorch]`. |
| RandomSampler | Sanity baseline. Always run a Random study alongside TPE. |
| GridSampler | Exhaustive sweeps in tiny spaces. |
| QMCSampler | Quasi-Monte-Carlo warm-up. Better space coverage than Random for first 50 trials. |

**Pragmatic rule for Warbird: AutoSampler everywhere by default.**

### 1.7 Pruners

- `MedianPruner` — friendly, conservative.
- `PercentilePruner` — like Median but configurable.
- `SuccessiveHalvingPruner` (ASHA) — async, aggressive, great for parallel workers.
- `HyperbandPruner` — runs multiple SHA brackets. **Best general-purpose** per Optuna's benchmarks.
- `ThresholdPruner(upper=, lower=)` — kills trials exceeding absolute bound (e.g., max-DD > 8% → prune).
- `PatientPruner(wrapped_pruner, patience=N)` — wraps another pruner, only prunes after N non-improving steps.
- `WilcoxonPruner(p_threshold=0.1)` (v3.6, March 2024) — paired statistical test across "problem instances". **Right pruner for walk-forward folds**: report Sharpe per fold, Wilcoxon prunes trials statistically unlikely to beat the incumbent.

**Recipe:** HyperbandPruner for hyperparameter search inside a model (LightGBM trees, NN epochs); WilcoxonPruner for backtest folds across CPCV/walk-forward.

### 1.8 Multi-objective optimisation

```python
def objective(trial):
    params = suggest_strategy(trial)
    res = run_backtest(params)
    return res.sharpe, res.max_drawdown_pct   # maximize, minimize

study = optuna.create_study(
    directions=["maximize", "minimize"],
    sampler=optunahub.load_module("samplers/auto_sampler").AutoSampler(),
)

# Pareto front
import optuna.visualization as vis
vis.plot_pareto_front(study, target_names=["Sharpe", "MaxDD"]).show()
for t in study.best_trials:
    print(t.number, t.values, t.params)
```

`study.best_trial` is single-objective only; multi-objective uses `study.best_trials` (plural).

### 1.9 Constrained optimisation

Optuna convention: constraint value `≤ 0` is *feasible*, `> 0` is *violated*.

```python
def objective(trial):
    params = suggest(trial)
    res = run_backtest(params)
    cons = (2.0 - res.average_rr,             # R:R ≥ 2.0
            res.max_drawdown_pct - 0.10)      # MaxDD ≤ 10%
    trial.set_user_attr("constraint", cons)
    return res.sharpe, -res.max_drawdown_pct

def constraints_func(trial):
    return trial.user_attrs["constraint"]

sampler = optunahub.load_module("samplers/auto_sampler").AutoSampler(
    constraints_func=constraints_func
)
```

### 1.10 Visualisation & dashboards

- `optuna-dashboard journal:///path/to/study.log` for live UI. v0.20 has LLM-powered natural-language filtering.
- `optuna-fast-fanova` accelerates fANOVA importance for >50 features.
- Built-in plots: `plot_optimization_history`, `plot_param_importances`, `plot_parallel_coordinate`, `plot_pareto_front`, `plot_slice`, `plot_contour`, `plot_terminator_improvement`, `plot_timeline` (v3.2).

---

## 2. Specific ML Library Integrations

### 2.1 AutoGluon Tabular inside Optuna

AutoGluon does its own model search and ensembling. Tune the **meta-knobs**, not per-model HP — let AutoGluon handle internal HPO:

- `presets` ∈ {`medium_quality`, `high_quality`, `best_quality`, `extreme_quality`}
- `time_limit`
- `eval_metric`
- `excluded_model_types`
- `num_bag_folds`, `num_stack_levels`, `holdout_frac`, `use_bag_holdout`

```python
from autogluon.tabular import TabularPredictor, TabularDataset
import optuna

def objective(trial):
    preset    = trial.suggest_categorical("preset", ["medium_quality", "high_quality", "best_quality"])
    time_lim  = trial.suggest_int("time_limit", 60, 900, log=True)
    n_bag     = trial.suggest_int("num_bag_folds", 0, 8)
    n_stack   = trial.suggest_int("num_stack_levels", 0, 2)
    excl      = trial.suggest_categorical("excluded_models",
        [(), ("KNN",), ("KNN","NN_TORCH"), ("FASTAI","NN_TORCH","KNN")])

    sharpes = []
    for fold, (train_df, val_df) in enumerate(walk_forward_splits):
        path = f"AG_models/trial_{trial.number}_fold_{fold}"
        predictor = TabularPredictor(
            label="y_label", eval_metric="roc_auc",
            problem_type="binary", path=path,
        ).fit(train_df, tuning_data=val_df, time_limit=time_lim,
              presets=preset, num_bag_folds=n_bag, num_stack_levels=n_stack,
              excluded_model_types=list(excl), use_bag_holdout=True, verbosity=0)
        proba = predictor.predict_proba(val_df)[1]
        sharpe = warbird_backtest_from_signals(proba, val_df).sharpe
        sharpes.append(sharpe)
        trial.report(sharpe, step=fold)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return float(np.mean(sharpes))
```

**Two key points:**
1. AutoGluon's internal HPO uses **Ray Tune**, not Optuna. AutoGluon 1.5 only exposes `auto`, `random`, `local_random`, `bayes` searchers. There is **no first-class Optuna searcher inside AutoGluon**. Either let AutoGluon do internal HPO as a black box, or set `hyperparameter_tune_kwargs=None` and let Optuna control everything from outside. **Latter is what Warbird should do** — keeps search history in one Optuna study.

2. AutoGluon eats memory. On the 8 GB Air, only run with `presets="medium_quality"`, `num_bag_folds=0`, minimal model dict. Run `best_quality`/`extreme_quality` only on the Mini.

### 2.2 LightGBM

Two integrations in `optuna-integration[lightgbm]`:

**(a) Pruning callback** — drops into normal LightGBM training:

```python
import lightgbm as lgb
from optuna_integration.lightgbm import LightGBMPruningCallback

def objective(trial):
    params = {
        "objective": "binary", "metric": "auc",
        "learning_rate": trial.suggest_float("lr", 1e-3, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 16, 256),
        "max_depth": trial.suggest_int("max_depth", 3, 12),
        "min_data_in_leaf": trial.suggest_int("min_data_in_leaf", 5, 200, log=True),
        "feature_fraction": trial.suggest_float("feature_fraction", 0.5, 1.0),
        "bagging_fraction": trial.suggest_float("bagging_fraction", 0.5, 1.0),
        "bagging_freq": trial.suggest_int("bagging_freq", 0, 7),
        "lambda_l1": trial.suggest_float("l1", 1e-8, 10.0, log=True),
        "lambda_l2": trial.suggest_float("l2", 1e-8, 10.0, log=True),
        "verbose": -1,
    }
    pruning = LightGBMPruningCallback(trial, "auc", valid_name="valid_0")
    booster = lgb.train(params, dtrain, num_boost_round=2000,
        valid_sets=[dvalid], valid_names=["valid_0"],
        callbacks=[lgb.early_stopping(100), pruning])
    return booster.best_score["valid_0"]["auc"]
```

**(b) `LightGBMTuner` / `LightGBMTunerCV`** — drop-in replacement for `lightgbm.train` doing *stepwise* tuning (regularisation → leaves → feature_fraction → bagging → min_child_samples). Use **(a)** for production search loops, **(b)** when sanity-checking a feature set.

### 2.3 XGBoost & CatBoost

```python
from optuna_integration.xgboost import XGBoostPruningCallback
from optuna_integration.catboost import CatBoostPruningCallback
```

Same shape as LightGBM. For XGBoost: add `booster ∈ {gbtree, dart, gblinear}` — DART helps with noisy labels (trading) at slower training. For CatBoost: leave categorical handling to CatBoost's `cat_features`.

### 2.4 scikit-learn

- **`OptunaSearchCV`** (in `optuna-integration[sklearn]`) — drop-in for `GridSearchCV`/`RandomizedSearchCV`.
- **Custom objective** — write trial → preprocessing → fit → CV yourself. **What Warbird should do** because trading needs time-series-aware CV.

**Tip:** tune preprocessing as part of the same trial (scaler choice, PCA components, rolling-window length, winsorisation thresholds). It's the whole reason to use Optuna over hand grid-search.

### 2.5 PyTorch Lightning

```python
from optuna_integration.pytorch_lightning import PyTorchLightningPruningCallback

def objective(trial):
    model = MyLitModel(
        lr=trial.suggest_float("lr", 1e-5, 1e-2, log=True),
        hidden=trial.suggest_int("hidden", 32, 512, log=True),
        dropout=trial.suggest_float("dropout", 0.0, 0.5),
    )
    trainer = pl.Trainer(
        accelerator="mps",   # Apple Silicon
        max_epochs=50,
        callbacks=[PyTorchLightningPruningCallback(trial, monitor="val_loss")],
        enable_progress_bar=False,
    )
    trainer.fit(model, datamodule=dm)
    return trainer.callback_metrics["val_loss"].item()
```

For M4 Pro: `accelerator="mps"`. Don't DDP across the two Macs.

### 2.6 TensorFlow / Keras

`TFKerasPruningCallback` is the modern one. Wire into `model.fit(callbacks=[...])`.

### 2.7 Classical time-series

- **`statsmodels`** (ARIMA/SARIMAX/VAR) — wrap `.fit()` in objective; `suggest_int` for `p, d, q`.
- **Prophet** — tune `changepoint_prior_scale` (`log [0.001, 0.5]`), `seasonality_prior_scale`.
- **`sktime` / `darts`** — both have native Optuna examples.
- **`tsfresh`** — feature extraction params (`fc_parameters`, `default_fc_parameters="comprehensive"` vs `"efficient"`) are themselves hyperparameters. Cache aggressively.

---

## 3. SHAP and Feature Selection

Three patterns ranked by usefulness:

### 3.1 SHAP as post-hoc prune (preprocessing)

Run a single high-quality LightGBM/AutoGluon on the full ~60-feature set, compute SHAP, drop below threshold, then start Optuna on reduced set. **Warbird's current approach** — right starting point.

### 3.2 SHAP-as-feature-selector inside Optuna trial

Tune the feature set:

```python
def objective(trial):
    n_keep = trial.suggest_int("n_features_keep", 5, 40)
    selected = SHAP_RANKED_FEATURES[:n_keep]
    X_sub = X[selected]
    # ... train + backtest
```

SHAP is one-time cached oracle. Pay once; Optuna decides cut.

### 3.3 Iterative wrapped feature selection

- **Boruta** (`BorutaPy`) — adds shadow features, accepts those statistically beating shadows.
- **mlxtend** `SequentialFeatureSelector` — forward/backward, expensive.
- **`scikit-feature`** rank-based selectors.

For Warbird: SHAP-once + `n_features_keep` trick = 90% value at 5% runtime.

### 3.4 Engineering parameters as Optuna parameters

**Highest leverage thing probably under-used.** Lookback windows, ATR multipliers, RSI periods, swing-detection thresholds, VIX filter level — all hyperparameters. Stop hard-coding them in the indicator module; `trial.suggest_*` them inside the same study tuning the model. AutoSampler jointly explores feature-engineering × model-HP joint space.

---

## 4. Trading-Specific Objectives & Backtest Integration

### 4.1 Backtest engine choice

| Engine | Verdict |
|---|---|
| **vectorbt** (open source) | ✅ Best for vectorised parameter sweeps; Numba-fast; integrates with pandas-ta. **Bulk of the search.** |
| vectorbt PRO | Paid. CV/WFA classes great, but multi-TF + path-dependent fib logic awkward without pro features. Skip. |
| **Backtrader** | Mature event-driven; verbose API; slower but honest about path dependence. |
| backtesting.py | Has its own optimiser — duplicative with Optuna. Quick checks only. |
| bt | Portfolio-allocation oriented. Wrong tool for futures intraday. |
| zipline-reloaded | Daily-bar focused. Skip. |
| pybroker | Decent middle ground; supports walk-forward + ML signals natively. |
| **Custom event-driven** | What you'll end up with for the fib measured-move logic specifically. Hand-roll on pandas + Numba. |

**Recommended split for Warbird:**
- **vectorbt** for feature/indicator parameter sweeps.
- **Custom event-driven mini-engine** wrapped in `run_warbird_backtest(params) → BacktestResult` returning `(sharpe, sortino, calmar, max_dd, profit_factor, expectancy, turnover, hit_rate, mean_rr, n_trades, equity_curve)`.

The Optuna objective calls `run_warbird_backtest`, returns the metric, stashes the rest in `trial.set_user_attr` for dashboard plots.

### 4.2 Objective metrics

For futures with R:R targeting, **Sharpe alone is wrong**. Use:

- `Sharpe` (annualised, daily returns)
- `Sortino` (downside-only)
- `Calmar = AnnReturn / |MaxDD|`
- `MAR` (rolling Calmar)
- `Profit Factor = gross_profit / gross_loss`
- `Expectancy = win_rate * avg_win − loss_rate * avg_loss`
- `SQN = sqrt(N) * mean_R / std_R`
- **GT-Score** (2024–2025 paper) — composite with trade-count gate.

For "Sharpe AND not-MaxDD", run **multi-objective with `directions=["maximize", "minimize"]`**: maximise Sortino + Calmar, minimise MaxDD + Turnover. Look at Pareto front, pick a region (e.g., MaxDD ≤ 8%), rank within by Calmar.

### 4.3 Walk-forward optimisation inside Optuna

Most important pattern for trading:

```
For trial in Optuna study:
    For each WF split (train, test):
        train indicator on train slice
        score on test slice → fold_metric
        trial.report(fold_metric, step=fold_idx)
        if trial.should_prune(): raise TrialPruned
    return aggregate(fold_metrics)
```

Knobs:
- **Fold size:** 6–12 months train / 2–3 months test for MES/ZL on 5m.
- **Embargo:** 1–5 days between train/test to prevent label leakage.
- **Aggregator:** not `mean` — use `median` or `mean − k * std` (penalises high variance).
- **Pruner:** `WilcoxonPruner(p_threshold=0.1)`.

```python
sampler = optunahub.load_module("samplers/auto_sampler").AutoSampler(seed=42)
pruner  = optuna.pruners.WilcoxonPruner(p_threshold=0.1)
study   = optuna.create_study(direction="maximize", sampler=sampler, pruner=pruner,
                              storage=storage, study_name="warbird_wfo_v17",
                              load_if_exists=True)

def objective(trial):
    p = suggest_params(trial)
    fold_sharpes = []
    for fold_idx, (train, test) in enumerate(np.random.permutation(WF_SPLITS)):
        res = run_warbird_backtest(train, test, **p)
        fold_sharpes.append(res.sharpe)
        trial.report(res.sharpe, step=fold_idx)
        if trial.should_prune():
            return float(np.mean(fold_sharpes))   # workaround
    return float(np.median(fold_sharpes) - 0.5 * np.std(fold_sharpes))
```

**Two notes:**
1. **Shuffle fold order each trial** — Wilcoxon explicitly warns fixed order causes overfitting to first folds.
2. **"Return mean instead of raise TrialPruned"** is documented workaround for samplers that can't use intermediate values from pruned trials.

### 4.4 Combinatorial Purged Cross-Validation (López de Prado)

`skfolio.model_selection.CombinatorialPurgedCV` or `timeseriescv`. CPCV produces multiple backtest paths from a single historical path by combinatorially picking k-of-N test groups, embargoing around them. This:

- gives you a **distribution** of Sharpes per param set, not a point estimate;
- enables PBO and DSR computation;
- pairs naturally with `WilcoxonPruner` (each path is one "problem instance").

**Walk-forward stays the industry standard for live deployment simulation; CPCV is what you use for parameter selection.** Combine: select with CPCV, validate chosen params with one final WFO pass.

### 4.5 Deflated Sharpe Ratio and Probability of Backtest Overfitting

After Optuna finishes, you've run N statistical tests. Naive "pick best" inflates Sharpe massively. Deflate it:

- **`pypbo`** (Bailey & López de Prado's PBO + DSR in Python).
- Roll your own — closed-form (Bailey 2014) is ~40 lines.
- `compute_deflated_sharpe_ratio(estimated_sharpe, sharpe_variance, nb_trials, backtest_horizon, skew, kurtosis)` from gmarti.gitlab.io.

If DSR p-value > ~0.05, you don't have a strategy — you have a backtest artefact.

### 4.6 Monte Carlo & robustness

Cheapest, most useful trick: per trial, do N Monte Carlo perturbations (resample trade returns 1000×, compute Sharpe distribution) and return the **5th-percentile Sharpe**, not the mean. Pushes Optuna toward parameters robust to the realised path.

Bootstrap equity curve and use `expected_max_drawdown_at_95_percentile` as one MO dimension.

---

## 5. TradingView-Specific Patterns

### 5.1 Pulling data: `tvdatafeed`

`pip install --upgrade --no-cache-dir git+https://github.com/rongardF/tvdatafeed.git` (PyPI lags GitHub). 5,000 bars per request.

```python
from tvDatafeed import TvDatafeed, Interval
tv = TvDatafeed(username="...", password="...")
mes_5m = tv.get_hist("MES1!", "CME_MINI", Interval.in_5_minute, n_bars=5000, fut_contract=1)
zl_15m = tv.get_hist("ZL1!", "CBOT", Interval.in_15_minute, n_bars=5000, fut_contract=1)
```

Cache to **Parquet** keyed by `(symbol, interval, end_date)`. TradingView pull is the slowest step — cache aggressively with `joblib.Memory` or `diskcache`.

### 5.2 Re-implementing Pine indicators in Python

One Python module per Pine indicator with same parameter names, vectorised in NumPy/Numba (or `pandas-ta` if exists), then unit test diffing Python output vs CSV exported from TradingView. After that, every parameter is a `trial.suggest_*`.

`pandas-ta-classic` covers 150+ indicators with TA-Lib bridge, actively maintained. For things it doesn't cover (Warbird-specific swing detection, ABC structure validators, measured-move targets), write Numba-jitted helpers under `warbird/indicators/`.

### 5.3 Translating Optuna's best params back to Pine

Once Optuna gives best trial, deployable artefact is a Pine `input` block:

```
//@version=5
strategy("Warbird ZL v17", overlay=true)
fib_entry      = input.float(0.618, "Fib entry")
target_ext     = input.float(1.236, "Target ext")
swing_lookback = input.int(34, "Swing lookback")
vix_thresh     = input.float(22.5, "VIX threshold")
rr_min         = input.float(2.2, "Min R:R")
```

Keep Python config and Pine inputs in **same names**; write `optuna_best_to_pine.py` doing `study.best_trial.params` → text substitution into Pine template.

### 5.4 TA libraries

| Library | Verdict |
|---|---|
| **TA-Lib** | Fastest (C). Gold standard. Annoying install on Apple Silicon. Worth it. |
| **`pandas-ta-classic`** | Active fork; pandas-native; bridges TA-Lib. **Warbird default for 90%.** |
| `pandas-ta` (original) | Use only the classic fork; original unmaintained. |
| `finta` | Slim, pure-pandas; no TA-Lib dependency. Cross-validation. |
| **TradingView's `ta` in Pine** | Ground truth. Diff Python implementations against this regularly. |

---

## 6. Pipeline / Orchestration Architecture

### 6.1 Hydra + Optuna sweeper

```yaml
# conf/config.yaml
defaults:
  - override hydra/sweeper: optuna
  - override hydra/sweeper/sampler: tpe

hydra:
  sweeper:
    sampler:
      seed: 42
    direction: maximize
    study_name: warbird_zl_v17
    storage: journal:///Volumes/MacMiniShare/warbird/zl_v17.log
    n_trials: 500
    n_jobs: 4
    params:
      rr_min:        interval(1.5, 3.5)
      fib_entry:     choice(0.5, 0.618, 0.65)
      swing_lookback: range(8, 80, step=2)
      vix_thresh:    interval(14.0, 30.0)

instrument: ZL
timeframe: 15m
```

`python warbird/sweep.py -m` runs the whole study. Caveat: upstream `hydra-optuna-sweeper` has lagged on Optuna API changes (Distribution names changed). Last major release on PyPI is 1.2.0. For newer features may need master branch or `hydra_optuna_pruning_sweeper` community fork.

### 6.2 MLflow + Optuna

```python
from optuna_integration.mlflow import MLflowCallback
mlflc = MLflowCallback(
    tracking_uri="file:./mlruns",
    metric_name="sharpe",
    create_experiment=True,
    tag_trial_user_attrs=True,
)
study.optimize(objective, n_trials=500, callbacks=[mlflc])
```

Each trial becomes an MLflow run; `tag_trial_user_attrs=True` propagates `trial.set_user_attr` into MLflow tags. Audit log: MLflow tracks artefacts/metrics, Optuna tracks search, both write locally, no service.

### 6.3 W&B + Optuna

`optuna_integration.WeightsAndBiasesCallback`. Skip in favour of MLflow unless you want W&B Sweeps' web UI.

### 6.4 Optuna + Ray Tune

Ray Tune is executor; Optuna is search algorithm. Use `from ray.tune.search.optuna import OptunaSearch` when:
- Heterogeneous resource scheduling (some trials need GPU).
- ASHA scheduler at Ray level + Optuna at search level (caveat: Ray's ASHAScheduler can fight Optuna's MO search).
- Already running Ray cluster.

For two Macs no Docker, Ray adds significant complexity. **Prefer plain `study.optimize` with multiple processes.** Revisit Ray only if scaling beyond 5 machines.

### 6.5 Caching across trials

Three layers, ordered by ROI:
1. **Data load** — `joblib.Memory("./.cache/tvdata")` for Parquet pulls.
2. **Feature engineering** — full feature matrix per `(symbol, timeframe, feature_config_hash)`.
3. **Indicator computation** — individual indicators by `(symbol, timeframe, indicator_name, params_hash)`. `diskcache.Cache` for fine-grained mmap-friendly.

With those three, a Warbird trial spends ~99% time inside backtest loop, not feature prep.

### 6.6 Reproducibility

```python
import os, random, numpy as np, torch
SEED = 42
os.environ["PYTHONHASHSEED"] = str(SEED)
random.seed(SEED); np.random.seed(SEED); torch.manual_seed(SEED)

study = optuna.create_study(
    sampler=optuna.samplers.TPESampler(seed=SEED),
    pruner=optuna.pruners.HyperbandPruner(),
    storage=storage, load_if_exists=True,
)
```

Pruners + parallel workers introduce non-determinism even with seeded samplers. For *strict* reproducibility, single worker `n_jobs=1`, pin LightGBM `deterministic=True`.

---

## 7. Advanced / Cutting-Edge Optuna (2025–2026)

- **OptunaHub** (`pip install optunahub`) — community samplers/pruners/visualisations. As of 2026: AutoSampler, HEBO, c-TPE, CatCMA-with-Margin, SPEA-II, NSGAIIWithTPEWarmup, robust BO methods.
- **`optuna.terminator`** — automatic study-level early stopping when expected improvement < cross-validation noise. `EMMREvaluator` (Expected Minimum Model Regret, late 2024) is recommended. Pair with `MedianErrorEvaluator` over `report_cross_validation_scores`. `study.optimize(..., callbacks=[TerminatorCallback()])`.
- **User attributes / system attributes** — `trial.set_user_attr("equity_curve_path", "...")`, `trial.set_user_attr("regime_label", "trending_high_vix")`. Don't abuse for big blobs (they go in storage); save equity curve as Parquet, store path.
- **Heartbeat** — see §1.5.
- **`study.add_trial` / `study.enqueue_trial`** — warm start. If you know `(rr_min=2.0, fib_entry=0.618, target_ext=1.236, swing_lookback=34, vix_thresh=22)` is current production baseline, enqueue first: `study.enqueue_trial({...}, user_attrs={"memo": "baseline"})`. AutoSampler/TPE explores around it.
- **Importance evaluators** — fANOVA (default; `optuna-fast-fanova` for ≥40 features), `MeanDecreaseImpurityImportanceEvaluator`, `PED-ANOVA`.
- **Optuna v5 roadmap** (May 2025) — changing default sampler away from TPE, Rust-based components for performance, prompt-optimisation features. Watch for breaking changes.

---

## 8. Scaling on Mac Mini M4 Pro 24 GB + MacBook Air M3 8 GB

### 8.1 Concrete plan

- **Mac Mini (primary, 24 GB)**: 4–6 worker processes. Each `study.optimize(n_trials=100, n_jobs=1)`.
- **MacBook Air (secondary, 8 GB)**: 1–2 workers, **only on cheap models** — LightGBM with bagged folds disabled, or pure-rules backtests. Don't run AutoGluon `best_quality` here.
- **Storage**: JournalFileBackend on shared volume visible to both. Heartbeat 60s — close Air's lid, Mini reclaims trials in 2 minutes.
- **Pruning**: aggressive. `WilcoxonPruner(p_threshold=0.2)` early, tightened to `0.1` after 100 trials. Combined with Hyperband on inner ML.
- **Caching**: TradingView Parquet + features Parquet + indicator `diskcache`. After ~10 trials, new trial = backtest time only.

### 8.2 `n_jobs` vs separate processes

`n_jobs > 1` uses Python threads. On Apple Silicon with NumPy/Numba/LightGBM (release GIL), works tolerably for 2–4 jobs but fragile. **Spawning separate processes more robust** — each can crash without taking rest down, memory isolated, storage layer handles concurrent access.

```bash
# Mini:
for i in 1 2 3 4 5 6; do python -m warbird.run_study --study zl_v17 --worker $i & done
# Air:
python -m warbird.run_study --study zl_v17 --worker 7
```

### 8.3 Memory hygiene

- `gc_after_trial=True` — costs ~2% CPU, prevents memory creep.
- Per-trial `del` of large DataFrames at end of `objective`.
- `torch.mps.empty_cache()` if mixing PyTorch.
- Never load both MES and ZL full-resolution histories simultaneously on Air. Stream by symbol.

---

## 9. Pitfalls & Best Practices for Trading Optimisation

1. **Look-ahead bias** — every rolling/lagged feature with `min_periods` and shifted by 1. Unit-test by feeding random future data.
2. **Data leakage via labels** — purge and embargo around test window by at least the label horizon + safety. CPCV with proper `purged_size` handles this.
3. **Overfitting to backtest** — every trial is one statistical test. After 500 trials you'll find Sharpe-3 on noise. Always compute DSR with `nb_trials = len(study.trials)`.
4. **Survivorship bias** — TradingView's continuous futures have rollover artefacts; use `fut_contract=1` for next-month and reconstruct rollover-adjusted yourself or pull individual contracts.
5. **VIX regime-dependent performance** — strategy may have Sharpe=3 low-VIX, Sharpe=-1 high-VIX. Optuna picks parameters winning on average across merged regime. Split VIX regimes into different studies, or add regime-conditional constraint.
6. **Too-wide search spaces** — TPE/AutoSampler need ~10 startup trials per dimension to begin biasing. 30 dims = 300 trials before signal.
7. **Too-narrow search spaces** — if every trial within ±0.1 Sharpe, you don't have a search problem; you've already hand-tuned. Optuna isn't going to find magic.
8. **Categorical-as-ordinal** — `suggest_categorical("rsi_period", [10,14,20,30])` makes TPE treat 10 and 30 as no more related than `"red"` and `"blue"`. Use `suggest_int` if order matters.
9. **Forgetting `study_name` and `storage`** — re-running overwrites. Always `load_if_exists=True` and stable `study_name`.
10. **When Optuna is wrong tool** — combinatorial/discrete (which 100 features), use Boruta/SFS/genetic. Convex with gradients, scipy.optimize/CVXPY beats. Latency-critical real-time, online algorithms (Thompson, contextual bandits) beat batch Optuna.

### Optuna vs alternatives

| Framework | When to choose |
|---|---|
| **Optuna** | Default for ML/HPO. Best community, docs, viz, most active 2025-2026. |
| Hyperopt | Older, smaller community. No reason to start new project on it. |
| Ax / BoTorch | Best-in-class Bayesian/MO. Use *through* Optuna's `BoTorchSampler`. |
| scikit-optimize | Maintenance mode. Skip. |
| Ray Tune (standalone) | When you need cluster resource scheduling. Pair with Optuna as searcher. |

---

## 10. Recommended Starter Architecture for Warbird

### 10.1 Repo layout

```
warbird/
├── pyproject.toml
├── conf/                            # Hydra configs
│   ├── config.yaml
│   ├── instrument/{mes,zl}.yaml
│   ├── strategy/warbird.yaml
│   └── search/{tpe_baseline,auto_mo}.yaml
├── data/parquet/                    # TradingView cache
├── .cache/                          # joblib + diskcache
├── studies/                         # JournalStorage logs
├── mlruns/                          # MLflow store
├── warbird/
│   ├── data/{tvfeed,splits}.py
│   ├── indicators/{warbird,filters,ta_wrap}.py
│   ├── features/build.py
│   ├── models/{lgb,autogluon,neural}.py
│   ├── backtest/{engine,metrics}.py
│   ├── optimize/{objectives,search_spaces,runner}.py
│   ├── live/pine_export.py
│   └── cli.py
└── tests/
```

### 10.2 Sketched objective: AutoGluon + SHAP-pruned features + walk-forward

```python
# warbird/optimize/objectives.py
import numpy as np, optuna
from autogluon.tabular import TabularPredictor
from warbird.features.build import build_feature_matrix
from warbird.backtest.engine import run_warbird_backtest
from warbird.backtest.metrics import sharpe, max_drawdown
from warbird.data.splits import cpcv_splits

SHAP_RANKED = ["atr_14", "rsi_5m_14", "mom_15m_5", "vix", "swing_dist_pct", ...]

def make_objective(symbol: str, timeframe: str):
    def objective(trial: optuna.Trial):
        rr_min       = trial.suggest_float("rr_min", 1.5, 3.5, step=0.1)
        fib_entry    = trial.suggest_categorical("fib_entry", [0.5, 0.618, 0.65])
        target_ext   = trial.suggest_categorical("target_ext", [1.0, 1.236, 1.382, 1.618])
        swing_lb     = trial.suggest_int("swing_lookback", 8, 80, log=True)
        vix_thresh   = trial.suggest_float("vix_thresh", 14.0, 30.0)

        n_keep       = trial.suggest_int("n_features", 8, 35)
        atr_period   = trial.suggest_int("atr_period", 7, 30)
        rsi_period   = trial.suggest_int("rsi_period", 8, 28)
        feat_cfg = dict(atr=atr_period, rsi=rsi_period, columns=SHAP_RANKED[:n_keep])

        ag_preset    = trial.suggest_categorical("ag_preset", ["medium_quality", "high_quality"])
        ag_time      = trial.suggest_int("ag_time_limit", 60, 600, log=True)

        trial.set_user_attr("symbol", symbol); trial.set_user_attr("timeframe", timeframe)

        feats = build_feature_matrix(symbol, timeframe, feat_cfg)
        fold_metrics = []
        splits = cpcv_splits(feats.index, n_folds=6, n_test_folds=2, purged=20, embargo=20)
        for i, (train_idx, test_idx) in enumerate(np.random.permutation(splits)):
            train_df = feats.iloc[train_idx]; test_df = feats.iloc[test_idx]

            predictor = TabularPredictor(
                label="y_long_signal", problem_type="binary",
                eval_metric="roc_auc", path=f"/tmp/ag/{trial.number}_{i}",
            ).fit(train_df, time_limit=ag_time, presets=ag_preset, verbosity=0)
            proba = predictor.predict_proba(test_df)[1].values

            res = run_warbird_backtest(test_df, proba,
                rr_min=rr_min, fib_entry=fib_entry, target_ext=target_ext,
                swing_lb=swing_lb, vix_thresh=vix_thresh)

            fold_sharpe = sharpe(res.returns)
            fold_metrics.append((fold_sharpe, max_drawdown(res.equity)))
            trial.report(fold_sharpe, step=i)

            if trial.should_prune():
                arr = np.array(fold_metrics)
                trial.set_user_attr("pruned_at_fold", i)
                return float(arr[:, 0].mean()), float(arr[:, 1].mean())

        arr = np.array(fold_metrics)
        robust_sharpe = arr[:, 0].mean() - 0.5 * arr[:, 0].std()
        worst_dd      = arr[:, 1].max()
        trial.set_user_attr("constraint", (0.5 - robust_sharpe,))
        np.save(f"./equity/{trial.number}.npy", res.equity)
        trial.set_user_attr("equity_path", f"./equity/{trial.number}.npy")

        return float(robust_sharpe), float(worst_dd)
    return objective
```

### 10.3 Runner

```python
# warbird/optimize/runner.py
import optuna, optunahub
from optuna.storages import JournalStorage
from optuna.storages.journal import JournalFileBackend
from optuna_integration.mlflow import MLflowCallback

def make_study(name: str, log_path: str):
    auto = optunahub.load_module("samplers/auto_sampler")
    sampler = auto.AutoSampler(seed=42,
        constraints_func=lambda t: t.user_attrs.get("constraint", (0.0,)))
    storage = JournalStorage(JournalFileBackend(log_path))
    study = optuna.create_study(
        study_name=name, storage=storage,
        directions=["maximize", "minimize"],
        sampler=sampler,
        pruner=optuna.pruners.WilcoxonPruner(p_threshold=0.1),
        load_if_exists=True,
    )
    study.enqueue_trial({
        "rr_min": 2.0, "fib_entry": 0.618, "target_ext": 1.236,
        "swing_lookback": 34, "vix_thresh": 22.5,
        "n_features": 18, "atr_period": 14, "rsi_period": 14,
        "ag_preset": "medium_quality", "ag_time_limit": 180,
    }, user_attrs={"memo": "warbird_baseline_v16"})
    return study, MLflowCallback(tracking_uri="file:./mlruns",
        metric_name=["robust_sharpe", "max_dd"], tag_trial_user_attrs=True)
```

### 10.4 Day-to-day workflow

1. `python -m warbird.cli pull --symbol ZL --tf 15m` → refresh Parquet cache.
2. `python -m warbird.cli features --symbol ZL --tf 15m` → rebuild feature matrix.
3. **Mac Mini terminal A**: `python -m warbird.cli sweep --symbol ZL --tf 15m --workers 4`.
4. **Mac Mini terminal B**: `optuna-dashboard journal:///path/zl_v17.log` → `http://localhost:8080`.
5. **MacBook Air**: `python -m warbird.cli sweep --symbol ZL --tf 15m --workers 1 --cheap-only`.
6. After 24h, inspect Pareto front, filter by feasibility, pick top 5.
7. **Validate**: `python -m warbird.cli validate` runs CPCV + DSR + PBO.
8. **Promote**: `python -m warbird.cli export-pine --trial 387` → emits Pine `input.float(...)` block.

### 10.5 Stack defaults

| Component | Default |
|---|---|
| Storage | `JournalStorage(JournalFileBackend(...))` shared SSD |
| Sampler | OptunaHub `AutoSampler` with `constraints_func` |
| Pruner | `WilcoxonPruner(p_threshold=0.1)` for backtest folds; `HyperbandPruner` for inner ML |
| CV | CPCV (skfolio) for selection; one final WFO for validation |
| Direction | MO: `["maximize" (robust Sharpe), "minimize" (MaxDD)]` |
| Constraint | Robust Sharpe ≥ 0.5; MaxDD ≤ 10% |
| Termination | `TerminatorCallback()` with `EMMREvaluator` after `min_n_trials=100` |
| Tracking | MLflow file store + Optuna Dashboard |
| Heartbeat | 60s interval, 120s grace, `RetryFailedTrialCallback(max_retry=3)` |
| Warm start | `enqueue_trial(current_production_params)` |
| Post-study | DSR + PBO (pypbo); reject best if DSR p>0.05 |

---

## 11. 2025–2026 Watch List

- **Optuna 4.7** Jan 19 2026 — drops Python 3.8.
- **Optuna 4.6** Nov 2025 — LLM dashboard, AutoSampler full MO/constrained, robust BO on OptunaHub.
- **Optuna 4.5** Sep 2025 — GPSampler constrained MO.
- **Optuna 4.4** Jun 2025 — GP-based MO sampler, MOEA/D additions.
- **Optuna 4.0** mid-2024 — JournalStorage stable.
- **`optuna.integration` migration** ongoing — code from v2.x needs `pip install optuna-integration`.
- **`OptunaSearchCV`** churn against scikit-learn API; third-party `sklearn-optuna` more actively maintained.
- **TPE no longer default** in Optuna v5. Set `sampler=` explicitly to keep behaviour.
- **AutoGluon 1.5** 2025 — `extreme_quality` preset using `zeroshot_2025_tabfm` (tabular foundation models). Heavy — Mini only.
- **`pandas-ta-classic`** is the active fork.

---

## 12. Bottom Line

For a futures trader on Apple Silicon without Docker, the cleanest "Optuna on steroids" stack:

> **`optuna 4.7` + `optuna-integration` + AutoSampler from OptunaHub + `WilcoxonPruner` over CPCV folds + `JournalFileBackend` on shared volume + MLflow file store + `optuna-dashboard` + `vectorbt` for sweeps + custom Numba/pandas event-driven engine for the Warbird rules + `pandas-ta-classic` for indicators + `tvdatafeed` with Parquet/diskcache caching + Hydra for config + Deflated Sharpe Ratio as gatekeeper before promoting to live.**

Don't put SQLite on a network share. Don't run AutoGluon `best_quality` on the Air. Don't trust a single Sharpe from a 500-trial study without deflating it. Don't tune feature engineering separately from model and strategy parameters — let Optuna explore the joint space. Always warm-start with existing production params via `enqueue_trial`. Set `WilcoxonPruner` from day one — biggest trials-per-hour multiplier for walk-forward optimisation.

That stack delivers what was asked: **one go-to platform** where every model (LightGBM, XGBoost, CatBoost, AutoGluon, PyTorch Lightning, sklearn pipelines, classical TS), every backtest engine, every feature-selection trick, every CV scheme, and every trading objective routes through a single Optuna `study.optimize` call, on hardware you already own, with no paid services and no Docker.
