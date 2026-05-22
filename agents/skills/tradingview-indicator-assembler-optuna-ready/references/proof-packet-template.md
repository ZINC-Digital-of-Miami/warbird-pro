# Proof Packet Template

This is the final deliverable shape for any indicator assembled by this skill. Return it verbatim. Do not collapse sections. Do not declare `VERIFIED` unless every required validation actually passed (see `pine-validation-checklist.md`).

A `NOT VERIFIED` packet is still a valid deliverable — in fact, it is the honest one when proof is incomplete. The skill's value comes from refusing to claim what it has not proven.

---

# Indicator Assembly Proof Packet

## 0. Status

```
VERDICT: VERIFIED | NOT VERIFIED
DATE: YYYY-MM-DD
ASSEMBLED BY: <agent / skill version>
SOURCES MERGED: A=<path>, B=<path>, C=<path>, …
TARGET FILE: <path-to-merged.pine>
TRIGGER FAMILY: LIVE_ANCHOR_FOOTPRINT | NEXUS_FOOTPRINT_DELTA | <other>
```

If `NOT VERIFIED`, list every missing or failing item now, before the rest of the packet, so it is impossible to miss:

```
NOT VERIFIED — missing or failing:
- <item 1>
- <item 2>
```

## 1. Final Pine script (or exact patch)

Inline the full script if it is new. If the change is incremental, provide the exact patch (unified diff) and the file it applies to.

```pine
// merged indicator here, or:
// patch attached as <path>
```

## 2. Source component map

Reproduce the table from the merge contract. Every major component traces back to one source — or is marked "new" with a one-line reason.

| Component | Owner source | Notes / what was preserved |
|-----------|--------------|----------------------------|
| Fib anchor logic |  |  |
| Moving averages |  |  |
| Label style |  |  |
| Alerts |  |  |
| Hidden export plots |  |  |
| ... |  |  |

## 3. Final indicator contract

Reproduce or summarize the merge contract:

- Identity (name, version, type, overlay, max_*_count).
- Final input groups (in order).
- Naming convention and rename log.
- Surviving plots and dropped plots.
- Repaint policy and any documented exceptions.
- Alert conditions.
- Resource budget priced at design time.

## 4. Optuna tuning contract

Reproduce or summarize:

- Trigger family declaration.
- Hidden export plots emitted.
- Tunable parameters table (Pine name, type, min/max/options, default, why tunable, freeze warnings).
- Frozen parameters list.
- Cross-input constraints.
- Suggested sweep recipes.

The Pine input names in this section must match the actual Pine file exactly. If they don't, the verdict cannot be `VERIFIED`.

## 5. No-repaint proof

For each signal-bearing branch, state:

- The branch (e.g., "long entry trigger at line 412").
- The confirmation gate used (`barstate.isconfirmed`, `[1]` offset, pivot offset, etc.).
- Any HTF data it reads and the `lookahead` setting.
- Why this is no-repaint by construction.

If any branch is intentionally realtime/intrabar, declare it explicitly:

```
INTENTIONAL REPAINT: <branch>
  reason: <why>
  user-visible signal: <how the user can tell this is preview, not confirmed>
  user-approved this in session: yes / no
```

If `user-approved: no`, the verdict cannot be `VERIFIED`.

## 6. Pine / TradingView validation report

Use the verdict template from `references/pine-validation-checklist.md`:

```
PINE COMPILE: PASS | FAIL
  command: scripts/guards/compile-pine.sh <file>
  errors: N
  warnings: N
  details: <inline or attached>

PINE LINT: PASS | PASS WITH WARNINGS | FAIL
  command: scripts/guards/pine-lint.sh <file>
  errors: N
  warnings: N
  details: <inline>

REPO GUARDS:
  check-fib-scanner-guardrails.sh: PASS | FAIL | NOT RUN — reason
  check-contamination.sh:          PASS | FAIL | NOT RUN — reason
  check-no-tv-force.sh:            PASS | FAIL | NOT RUN — reason
  check-visual-contract.sh:        PASS | FAIL | NOT RUN — reason
  check-indicator-strategy-parity.sh: PASS | FAIL | NOT RUN — reason

REPAINT REVIEW: PASS | FAIL — notes
RESOURCE BUDGET: PASS | FAIL — current vs caps
OPTUNA NAME PARITY: PASS | FAIL — notes
SOURCE PARITY: PASS | FAIL — notes
TRADINGVIEW CHART INSPECTION: PASS | NOT PERFORMED — what was checked
```

If any line is `FAIL` or `NOT RUN` (without explicit user waiver), the verdict cannot be `VERIFIED`.

## 7. Resource budget report

Counted against the assembled file:

| Output kind | Count | Cap | Headroom |
|-------------|-------|-----|----------|
| `plot` |  |  |  |
| `plotshape` / `plotchar` / `plotarrow` / `plotbar` / `plotcandle` |  |  |  |
| `bgcolor` |  |  |  |
| `fill` |  |  |  |
| `hline` |  |  |  |
| `alertcondition` |  |  |  |
| **Total outputs** | `XX` | `64` | `XX` |

| Other budget | Count | Cap | Headroom |
|--------------|-------|-----|----------|
| `request.security` |  | 40 |  |
| `request.footprint` |  | n/a (treat as heavy) |  |
| `max_lines_count` setting | `XX` | — | observed peak `XX` |
| `max_labels_count` setting | `XX` | — | observed peak `XX` |
| `max_boxes_count` setting | `XX` | — | observed peak `XX` |

Highlight any line at or above 75% of cap.

## 8. Suggestions for improvement

Always present, even when the verdict is `VERIFIED`. Cover at least:

- Better structure (input grouping, signal/visual separation, helper extraction).
- Safer no-repaint patterns the current build could adopt.
- Cleaner Optuna surface (inputs to add, remove, tighten, or freeze).
- Inputs that should be frozen in early sweeps and unlocked later.
- Inputs that look hardcoded but should be tunable.
- Visuals that could be simplified to free output budget.
- Alerts or hidden export plots that would improve external validation (for example, exposing a stop or target series the runner currently can't see).
- Risky logic that should be removed or isolated behind a debug flag.

Suggestions should be concrete and actionable, not generic ("write cleaner code").

## 9. Known risks and unverified assumptions

Be explicit about what you did not prove. Examples:

- "Source D's alert payload was assumed to match the user's runner config; not verified."
- "request.security on `XAUUSD` 1H was preserved from source B without confirming the runner needs it."
- "Pivot offset for the right-side window was set to 2; assumes user wants the same confirmation lag as source A."
- "TradingView chart inspection was not performed in this session."

If a risk would change the verdict if it were resolved unfavorably, say so.

## 10. Hand-off checklist for the user

Short list of what the user should do to fully accept the merged indicator:

1. Paste the merged Pine into TradingView on the target symbol/timeframe.
2. Confirm visuals appear in the expected places.
3. Set up alerts on the new alertcondition titles and watch a session for confirmed-bar fires only.
4. If running Optuna, regenerate the runner's input map from this packet's section 4 to ensure name parity.
5. If the merge touched protected scope (fib anchor, ladder math, label semantics), explicitly approve and capture before/after TradingView screenshots before treating the build as production-ready.

---

End of proof packet.
