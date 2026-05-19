# Warbird chart-review gate before training

Session-derived workflow correction from a V9 rebuild cleanup/training attempt.

## Durable lesson

For Warbird V9, training/modeling is not authorized merely because exports exist, validators pass, or the user previously said they want to train. The operator reviews the current indicator on chart before training.

If `indicators/warbird-pro-v9.pine` changes after the last chart review, the next training/modeling step is blocked until the user reviews that exact changed build on-chart and gives explicit post-review approval.

## Stop conditions

- TradingView/CDP preflight failure is a hard stop for the lifecycle. Do not fall through to local export rebuilds or AutoGluon training as a workaround.
- If the user asks what happened or shows frustration, immediately stop active training/Ray processes, delete unauthorized model/Ray artifacts if requested, and give a concise status report.
- Do not touch hardware, mounts, Thunderbolt/Satechi connection state, or disk connection state while cleaning up training processes/artifacts.

## Practical cleanup pattern

When asked to terminate unauthorized training:

1. List/kill `train_v9_locked.py`, AutoGluon, Ray, and dataset-build processes tied to training.
2. Remove only the specific model directories produced by that run, e.g. `models/warbird_pro_v9/locked_<timestamp>`.
3. Remove only the matching `/tmp/ray/session_<timestamp>...` directories and stale `session_latest` pointer.
4. Re-check that no Ray/training processes remain.
5. Mark training cancelled, not complete.
