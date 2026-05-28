# Common Mistakes to Avoid

These are patterns that have caused real incidents in this project. Learn from history.

## Settings Contamination

Before building ANY dataset, verify that builder constants match the live Pine settings table in `AGENTS.md` lines 181–204. The 2026-05-05 contamination incident used dev=4.0/depth=20/floor=0.50 instead of the correct 3.0/10/0.25 — poisoning training data.

## Claiming Completion Without Verification

Never claim a task is done without running the required verification gates. Run the gates, check the output, report results honestly. If a gate fails, say so — do not rationalize why the failure doesn't matter.

## Stale Baseline Trust

Do not trust prior model artifacts, export CSVs, or cached results as current truth without checking their manifest, settings, and date. The locked model artifact predates the current 5-TP / 10-bar contract.

## Feature Scope Creep

When adding features to the training pipeline, they MUST come from approved sources only. No FRED, macro, news, options, Supabase, or unapproved cross-asset data. If you think a new data source would help, propose it — do not add it.

## Pine Output Budget

With only 10 output slots remaining before the 64-call hard cap, every new `plot()` or `alertcondition()` is expensive. Price the cost before writing code. Check the current budget with `scripts/guards/pine-lint.sh`.

## Databento Mislabeling

Databento rows are market data. They are NOT TradingView indicator CSV exports. Never label Databento source as `TRADINGVIEW_INDICATOR_CSV`. Keep manifests honest.

## Legacy Code Reactivation

`scripts/ag/train_ag_baseline.py`, `scripts/ag/train_hard_gate.py`, local `ag_training` tables, and the old warehouse/FRED/macro plan are all superseded. Do not use them unless Kirk explicitly reopens that architecture.
