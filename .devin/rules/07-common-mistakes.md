# Common Mistakes — Project-Specific

Real incidents from this project's history. These are domain traps, not generic coding advice.

## Settings Contamination (2026-05-05 incident)

Before building ANY dataset, verify builder constants match the intended settings. The contamination incident used dev=4.0/depth=20/floor=0.50 instead of the correct 3.0/10/0.25 — poisoning all training data from that build.

## Trusting Past Test Results

Past testing results (15m/5m/1h baselines from 2026-04-27) are skewed and unreliable. Do not cite them as evidence for model performance or training decisions.

## Stale Baseline Trust

Do not trust prior model artifacts, export CSVs, or cached results as current truth without checking their manifest, settings, and date.

## Pine Output Budget

10 output slots remaining before the 64-call hard cap. Every new `plot()` or `alertcondition()` is expensive. Check the current budget with `scripts/guards/pine-lint.sh`.

## Databento Mislabeling

Databento rows are market data, NOT TradingView indicator CSV exports. Never label Databento source as `TRADINGVIEW_INDICATOR_CSV`.

## Assuming Old Data Restrictions Apply

The project has pivoted to local-first. FRED, macro, news, options data are NOW ALLOWED. The old restrictions ("No FRED, no macro, no news") were TradingView-specific limitations that no longer apply.

## Legacy Code Reactivation

`scripts/ag/train_ag_baseline.py`, `scripts/ag/train_hard_gate.py`, local `ag_training` tables are superseded. Do not use unless Kirk explicitly reopens.

## Deleting Planning Documents (2026-05-29 incident)

Commit e8bdb9cf deleted 3 critical planning documents (launch packet, build playbook,
v2.1 gate-clear patch — 325 lines total) and gitignored them as "scaffolding."
These were NOT scaffolding — they contained the exact Devin prompt, Codex QA gates,
stop conditions, authority state, and QA-required scope/git/reproducibility fixes.
Never delete or gitignore planning artifacts. Mark superseded docs as superseded in-file.
