# Optuna Tuning Contract Template

This contract defines the tunable surface of the merged indicator. It is a structural property of the script — not a postscript. Fill this out **before** writing Pine code, and revisit after the script is assembled to confirm names match.

The runner and the Pine inputs must agree on names exactly. A typo here breaks every sweep silently.

---

## Sweep boundaries

Declare what is being tuned and what is not.

- Tunable: signal logic inputs in the **Signal Logic**, **Moving Averages**, and **Fib Structure** groups (subject to per-input freeze flags below).
- Frozen by default: visuals, labels, alerts, watermark, color/style — the script's behavior should not depend on them.
- Frozen unless explicitly approved: anything in **Advanced**.
- Out of scope: indicator declaration args (`max_*_count`, overlay, title), `request.security` symbols and timeframes (categorical-but-fragile; admit case-by-case).

## Trigger family declaration

This indicator's outputs feed Optuna under exactly one trigger family. Pick one and declare it:

- `LIVE_ANCHOR_FOOTPRINT` — main-chart anchor + footprint trigger.
- `NEXUS_FOOTPRINT_DELTA` — Nexus footprint delta trigger.
- `<other>` — only with explicit user approval.

Outputs (hidden plots / alert conditions) emitted by this build:

| Output name | Type | Semantics | Required by family? |
|-------------|------|-----------|---------------------|
| `ml_setup_long` | plot (display.none) | 1 when long setup confirmed | yes |
| `ml_setup_short` | plot (display.none) | 1 when short setup confirmed | yes |
| `ml_entry_long` | plot (display.none) | 1 on entry bar (confirmed) | yes |
| `ml_entry_short` | plot (display.none) | 1 on entry bar (confirmed) | yes |
| `ml_stop` | plot (display.none) | stop level price | yes |
| `ml_target_1` | plot (display.none) | first target price | yes |
| ... |  |  |  |

All export plots must use confirmed-bar logic. Document any exception explicitly.

## Tunable parameters

One row per tunable input. The name column must match the Pine `input.*()` exactly.

| Pine name | Type | Min | Max | Step | Options | Default | Group | Tunable because… | Freeze warning |
|-----------|------|-----|-----|------|---------|---------|-------|------------------|----------------|
| `fibLen` | int | 5 | 80 | 1 | — | 21 | Fib Structure | Controls fib anchor lookback; affects which swing the ladder anchors to. | Do not sweep with `anchorMode` simultaneously. |
| `maFastLen` | int | 5 | 50 | 1 | — | 9 | Moving Averages | Fast MA length; controls trend slope sensitivity. | None. |
| `maSlowLen` | int | 20 | 200 | 1 | — | 50 | Moving Averages | Slow MA length; defines trend baseline. | Constraint: `maSlowLen > maFastLen`. |
| `useTrendGate` | bool | — | — | — | — | true | Signal Logic | Enables MA trend gate. | None. |
| `triggerMode` | string | — | — | — | `["close","wick","footprint"]` | `"close"` | Signal Logic | Selects entry trigger style. | Categorical: keep options stable across sweeps. |
| `entryConfirmBars` | int | 0 | 3 | 1 | — | 1 | Signal Logic | Bars of confirmation required after setup. | None. |
| `stopAtrMult` | float | 0.5 | 4.0 | 0.1 | — | 1.5 | Signal Logic | Stop placement in ATR units. | Pair with `atrLen` for sweep. |
| `atrLen` | int | 5 | 50 | 1 | — | 14 | Signal Logic | ATR lookback for stop sizing. | None. |
| ... |  |  |  |  |  |  |  |  |  |

Notes on the table:

- **Type**: `int`, `float`, `bool`, or `categorical` (string with `options=[...]`).
- **Step**: Optuna's quantization. Use coarser steps early; tighten later.
- **Options**: For categorical only. Keep the option list stable across sweeps — adding/removing values invalidates trial history.
- **Tunable because**: One sentence explaining what behavior this knob controls. If you cannot write that sentence, the parameter probably should not be tunable.
- **Freeze warning**: Inputs that interact, constraints (e.g., `slow > fast`), or reasons to lock during specific sweeps.

## Frozen parameters (must NOT be tuned)

Inputs that exist for visual/operational reasons and must be excluded from any sweep.

| Pine name | Reason for freeze |
|-----------|-------------------|
| `showFibLevels` | Visual only. |
| `lineWidth` | Visual only. |
| `labelTextColor` | Visual only. |
| ... |  |

If a frozen input is read inside signal logic, that is a bug in the design — surface it and refactor before sweeping.

## Cross-input constraints

Sweeps must respect these:

- `maSlowLen > maFastLen` (else the MA stack inverts meaning).
- `entryConfirmBars >= 0` (Pine doesn't constrain it but negative values break confirmation logic).
- `stopAtrMult > 0`.
- Any others specific to this indicator…

The runner is responsible for honoring these. The skill should call them out so the runner config sets them.

## Sweep recipes (suggested)

Concrete sweep slices the user can launch:

1. **Trend gate sensitivity** — sweep `maFastLen`, `maSlowLen`, `useTrendGate` only.
2. **Trigger family** — sweep `triggerMode`, `entryConfirmBars` only.
3. **Stop sizing** — sweep `atrLen`, `stopAtrMult` only.
4. **Joint search** — only after individual sweeps converge.

Recommend running coordinated sweeps last. Joint sweeps with everything unlocked produce noise.

## Output stability check

Before any sweep is treated as evidence:

- Run the unmodified default settings and confirm export plots match the prior run's golden snapshot (within tolerance for non-deterministic series).
- Confirm no input renames occurred without updating both the Pine script and the runner config.
- Confirm hidden export plots are still under the 64-output cap.

## Open questions

- Which trigger family should Optuna evaluate against this build?
- Which sweep recipe runs first?
- Are there inputs the user wants frozen even though they are mechanically tunable?
