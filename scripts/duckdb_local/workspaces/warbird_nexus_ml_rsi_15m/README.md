# Warbird Nexus ML RSI 15m — Isolated Heavy-Training Prep

- key: `warbird_nexus_ml_rsi_15m`
- trigger family: `NEXUS_FOOTPRINT_DELTA`
- source: TradingView/Pine export from `indicators/warbird-nexus-machine-learning-rsi-optuna-fast-test.pine`
- scope: Nexus-only 15m dataset and pre-training label audit
- excluded: Warbird V9 Pine, V9 trainer, V9 exports, V9 model artifacts, V9 fib semantics

This workspace is a separate 15m lane for the heavier Nexus model setup. It does
not replace the periodic Optuna workspace at `warbird_nexus_ml_rsi`; Optuna may
continue there separately.

## Build / audit

```bash
python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/build_nexus_15m_dataset.py   --source-csv "/Users/zincdigital/Downloads/CME_MINI_MES1!, 15_d464a.csv"
```

Outputs:

- `exports/nexus_15m_dataset.parquet`
- `exports/nexus_15m_dataset.csv`
- `exports/nexus_15m_dataset.manifest.json`
- `reports/pretrain_label_audit.json`
- `reports/pretrain_label_audit.md`

The builder performs no training. It only validates the export, builds labels,
sets chronological split boundaries with embargo, and reports whether labels are
sane enough for the next sequential training configuration step.


## Heavy training

After the pre-training audit passes and the operator explicitly approves model
training, run the first sequential Nexus target:

```bash
python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/train_nexus_15m_heavy.py \
  --section signal_tier_composite \
  --time-limit 14400 \
  --hpo-trials 80 \
  --num-bag-folds 5 \
  --num-bag-sets 2 \
  --num-stack-levels 1 \
  --dynamic-stacking auto \
  --model-profile neural_scout
```

The trainer is Nexus-only, uses the audited chronological split, and fits the
first footprint-quality target before any secondary family. Model artifacts are
written under `models/warbird_nexus_ml_rsi_15m/`; latest summary copies are
written to `reports/heavy_training_latest.json` and
`reports/heavy_training_latest.md`.

Path and target overrides are intentionally disabled for hardening.
Do not pass `--manifest`, `--output-root`, `--reports-dir`, or `--target`.


This is the research-heavy path, not the quick proof run. It uses AutoGluon
bagging/stacking only inside the historical training segment. The chronological
validation split is passed as `tuning_data` with bag holdout enabled, and the
future test split remains untouched proof. Internal k-fold scores are not OOS proof.


## Section chain

Run one indicator area at a time. The default sequence is:

1. `footprint_delta_flow`
2. `volume_flow`
3. `oscillator_regime`
4. `divergence_exhaustion`
5. `signal_tier_composite`

Start with the first section only:

```bash
python scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/run_nexus_15m_section_chain.py \
  --manifest scripts/duckdb_local/workspaces/warbird_nexus_ml_rsi_15m/exports/nexus_15m_dataset.manifest.json \
  --sections footprint_delta_flow \
  --stop-after-one \
  --time-limit 14400 \
  --hpo-trials 80 \
  --num-bag-folds 5 \
  --num-bag-sets 2 \
  --num-stack-levels 1 \
  --dynamic-stacking auto \
  --model-profile neural_scout
```

Each section writes a decision of `save_and_proceed` or
`rerun_or_expand_section` from chronological test metrics.


The default `neural_scout` profile runs full HPO on `FASTAI` and `NN_TORCH`, keeps fixed tiny `GBM`/`CAT`/`XGB` scouts for grounding, and drops `RF`/`XT` after Sections 01-02 showed weak chronological-test fit.
