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

## Plan File Overwrite (2026-05-29 session f6fe99cc incident)

Before restoring or editing ANY file in `docs/plans/` or `docs/handoffs/`, ALWAYS:

1. Run `git show origin/main:<path>` to see what's already on `main`
2. Compare line counts and content
3. If a newer/larger version already exists on `main`, do NOT overwrite

Session f6fe99cc overwrote Kirk's 705-line plan with a 733-line historical version from `git show`. The current `main` HEAD is always the source of truth for what exists — not git history commits.

## Autonomous "Fix" After Correction (2026-05-29 session f6fe99cc incident)

When Kirk corrects a mistake, do NOT immediately start "fixing" it autonomously. STOP and ask what Kirk wants done. Session f6fe99cc acknowledged a mistake and then immediately started reverting, committing, and pushing — making things worse while Kirk was still escalating.

## Background Process Persistence (2026-05-29 session f6fe99cc incident)

When Kirk says "STOP", kill ALL running shell processes immediately — including background git pushes, pending commits, and any shell with `run_in_background=true`. Check every active shell ID. Session f6fe99cc had a `fix` shell still running `git push` while Kirk was saying "STOP THE FUCKING WORK".
