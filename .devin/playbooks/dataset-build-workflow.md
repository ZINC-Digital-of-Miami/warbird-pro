# Dataset Build Workflow

Step-by-step for building a V9 Core training dataset.

1. **Confirm approval** — Do not build a dataset without explicit approval
2. **Verify Pine settings match** — Compare live TradingView settings (AGENTS.md lines 181–204) against dataset builder constants in `scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py`. Every value must match exactly. The 2026-05-05 contamination incident used wrong settings.
3. **Check manifest** — Verify the source manifest at `scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.manifest.json` is current
4. **Build the dataset:**
   ```bash
   python3 scripts/duckdb_local/workspaces/warbird_pro_core/build_core_dataset.py --timeframe 15
   ```
5. **Validate export** — Check row counts, date range, feature columns against the Pandera schema
6. **Run contract tests:**
   ```bash
   pytest tests/ag/test_v9_core_indicator_input_contract.py -q
   pytest tests/ag/test_v9_core_training_targets.py -q
   ```
7. **Generate profiling report** — Verify fg-data-profiling output exists
8. **Do NOT build 5m** until 15m model is fit, SHAP'd, and Monte-Carlo-validated
