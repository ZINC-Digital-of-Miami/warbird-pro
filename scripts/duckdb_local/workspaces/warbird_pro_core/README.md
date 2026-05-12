# Warbird Pro V9 Core Workspace

Operator-facing workspace for the current V9 Core DuckDB/Pandera/AutoGluon
training lane:

`2026-05-09 - Warbird Pro Autogluon Core`

Current status:

- Smoke/validation wrapper is local DuckDB/Core validation only.
- Full V9 training is launched directly with `scripts/ag/train_v9_locked.py`.
- Full 1y Core build/training is still approval-gated.
- Smoke runs are wiring evidence only; they are not model-quality evidence.

Smoke card command:

```bash
python scripts/duckdb_local/cards/core_training/2026_05_09_warbird_pro_autogluon_core.py \
  --mode smoke \
  --symbol-root ES \
  --timeframe 5
```

Expected default smoke validation artifact area:

```text
scripts/duckdb_local/workspaces/warbird_pro_core/experiments/es_5m/
```

For the 15m prep lane, use:

```text
scripts/duckdb_local/workspaces/warbird_pro_core/exports/es_15m_core.manifest.json
```

Do not run full AutoGluon training from this workspace until the full 1y Core
dataset gate is green and Kirk approves launch.
