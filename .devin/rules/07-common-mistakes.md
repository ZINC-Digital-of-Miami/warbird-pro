# Common Mistakes — Project-Specific

Real incidents from this project's history. These are domain traps, not generic coding advice.

## Settings Contamination (2026-05-05 incident)

Before building ANY dataset, verify builder constants match the live Pine settings table in `AGENTS.md` lines 181–204. The contamination incident used dev=4.0/depth=20/floor=0.50 instead of the correct 3.0/10/0.25 — poisoning all training data from that build.

## Stale Baseline Trust

Do not trust prior model artifacts, export CSVs, or cached results as current truth without checking their manifest, settings, and date.

## Feature Scope Creep

Features MUST come from approved sources only. If you think a new data source would help, propose it — do not add it.

## Pine Output Budget

10 output slots remaining before the 64-call hard cap. Every new `plot()` or `alertcondition()` is expensive. Check the current budget with `scripts/guards/pine-lint.sh`.

## Databento Mislabeling

Databento rows are market data, NOT TradingView indicator CSV exports. Never label Databento source as `TRADINGVIEW_INDICATOR_CSV`.

## Legacy Code Reactivation

`scripts/ag/train_ag_baseline.py`, `scripts/ag/train_hard_gate.py`, local `ag_training` tables, and the old warehouse/FRED/macro plan are superseded. Do not use unless Kirk explicitly reopens.
