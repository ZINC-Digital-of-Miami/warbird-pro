# Pine Validation Checklist

This is the only acceptable evidence catalog for Phase 10. Generic tests do not appear here, and that is on purpose.

A note on the standard: a Pine indicator can pass every JS/TS/Python test in the repo and still be wrong. Pine compiles and runs inside TradingView, so its validation must happen against TradingView's compiler and against patterns specific to Pine's bar-by-bar evaluation model. If you cannot run any of the Pine-specific checks below, return `NOT VERIFIED` and explain what is missing.

---

## Section 1 — Mandatory: real Pine compile

Run TradingView's pine-facade compiler against the merged file. This is a real network call to `pine-facade.tradingview.com`.

```bash
./scripts/guards/compile-pine.sh <path-to-merged.pine>
```

- Pass criterion: 0 compile errors. Warnings allowed unless the user requested `--strict`.
- Fail handling: do not present the indicator as done. Capture errors verbatim in the proof packet, fix, re-run.
- Record in proof packet: command, exit code, error count, warning count, full error text for any errors.

If you cannot reach `pine-facade.tradingview.com` from this session (offline, blocked egress, etc.), say so explicitly. Do not substitute "I read the script" for a compiler hit.

## Section 2 — Mandatory: Pine static lint

Run the warbird-pro Pine linter against the merged file.

```bash
./scripts/guards/pine-lint.sh <path-to-merged.pine>
```

This guard checks Pine-specific failure modes that the compiler may accept but TradingView will reject or behave unexpectedly on:

- `ta.highest` / `ta.lowest` / `ta.highestbars` / `ta.lowestbars` inside ternary operators (must be precomputed).
- Function definitions with typed params inside `if` blocks (Pine requires global scope).
- Forward references in functions (e.g., `htfConfluenceCheck` reading `fibRange` directly instead of as a parameter).
- `request.security()` count vs the 40 cap (warn at 30+).
- `barstate.isconfirmed` gates missing on structure conditions (`breakInDir`, `acceptInDir`, `rejectAtZone`, `breakAgainst`).
- `var` declarations inside indented blocks (often unintentional).
- `plot()` calls without explicit `display=` (visible-by-default may exceed budget).
- Output count vs TradingView's 64 hard cap (`plot*` + `bgcolor` + `fill` + `hline` + `alertcondition`).
- `alertcondition()` inside `if` blocks (must be at global scope).
- `riskOnBase` / `riskOffBase` contradiction.
- `max_boxes_count` vs `box.new()` call sites.
- `import TradingView/ZigZag` present when `zigzag.*` is used.

Record the full lint output in the proof packet. Errors must be zero. Warnings should be reviewed and either fixed or explained.

## Section 3 — Mandatory: repo-wide Pine guards

These guards do not target the merged file specifically — they protect the repo from regressions the merged file could reintroduce. Run all that apply.

```bash
./scripts/guards/check-fib-scanner-guardrails.sh
./scripts/guards/check-contamination.sh
./scripts/guards/check-no-tv-force.sh
```

Specifics:

- **`check-fib-scanner-guardrails.sh`** — bans the `ta.barssince(...)` + `pivotHighInWindow` / `pivotLowInWindow` / `ta.valuewhen(hasPivotHigh|Low)` pattern inside `fibHtfSnapshot()`. This pattern caused repeated wide-fib regressions; the merge must not bring it back.
- **`check-contamination.sh`** — blocks rabid-raccoon imports and data paths from leaking into runtime code. Pine doesn't import code from JS/TS, but if the merge introduces or moves auxiliary scripts (e.g., a runner config), this guard must still pass.
- **`check-no-tv-force.sh`** — blocks any new `tv_launch`, `launch_tv_debug_mac.sh`, `pkill -f TradingView`, or `killall TradingView` invocations in `scripts/` or `.claude/`. The skill should never recommend any of these patterns.

If you touched the visual contract (colors, widths, fib drawing, label semantics), also run:

```bash
./scripts/guards/check-visual-contract.sh
```

This diffs protected drawing/style regions against the frozen snapshot. A FAIL here means you changed protected scope without explicit approval — revert or get approval and use the snapshot regeneration procedure.

If a strategy harness was explicitly reopened in this session and the merge couples to it:

```bash
./scripts/guards/check-indicator-strategy-parity.sh
```

Otherwise skip — there is currently no active strategy Pine in `indicators/`.

## Section 4 — Mandatory: static review for behavior

The compiler and lint catch syntactic and structural issues. Review for behavioral correctness yourself, against the source inventories, with these checks:

### 4a. Repaint review

For every signal-bearing branch (any branch that produces an export plot, alert condition, or label that traders or Optuna will treat as authoritative):

- Confirm the gate is `barstate.isconfirmed` (or an equivalent closed-bar offset like `[1]`).
- Confirm `request.security(...)` calls use `lookahead=barmerge.lookahead_off`. If `_on` is used, confirm the surrounding code is built around it and document why.
- Confirm pivot detection (`ta.pivothigh`, `ta.pivotlow`) accounts for the right-side window — pivots are only confirmed `rightBars` after the pivot bar.
- Confirm no `close[0]` / `high[0]` / `low[0]` is read on the live bar as if it were closed (the live bar is intrabar until the close).
- Confirm preview-only visuals are visually distinct from confirmed signals and never feed back into the confirmed signal stream.

### 4b. `request.security()` and `request.footprint()` review

- Total count vs cap (40 hard, warn at 30).
- Each call's `lookahead` setting.
- For `request.footprint()`: cached per bar (not per tick), guarded by `barstate.isconfirmed` for any signal-bearing read.
- Symbol/timeframe arguments: are they intentional, or did a placeholder leak in from a source?

### 4c. Resource budget audit

Re-count after assembly — the lint script reports counts but only on what made it into the file:

| Output kind | Count |
|-------------|-------|
| `plot` |  |
| `plotshape` / `plotchar` / `plotarrow` / `plotbar` / `plotcandle` |  |
| `bgcolor` |  |
| `fill` |  |
| `hline` |  |
| `alertcondition` |  |
| **Total** | `XX / 64` |

Plus:

- `request.security`: `XX / 40`
- `request.footprint`: `XX`
- `max_lines_count` setting vs peak observed lines
- `max_labels_count` setting vs peak observed labels
- `max_boxes_count` setting vs peak observed boxes

### 4d. Optuna name parity

- Every input listed in the Optuna tuning contract exists in the Pine file with the exact same name and type.
- Every export plot listed in the Optuna contract exists in the Pine file under the exact same `title=` argument.
- No magic constants remain inside signal logic (each numeric should be either an input or a documented derived value).

### 4e. Source parity

- Every component in the source ownership map (Phase 3) appears in the merged file.
- Components marked "preserve exact logic" are byte-comparable to the source (modulo intentional renames documented in the contract).
- No component is silently rewritten "from memory."

## Section 5 — Optional but encouraged: TradingView chart inspection

If the user can paste the script into TradingView and run it on the target symbol/timeframe:

- Confirm the indicator loads without runtime errors.
- Confirm visuals appear in the expected places.
- Confirm alerts fire on confirmed bars only (set up an alert and watch for fires on the live bar).
- Compare hidden export plots to the source indicator's exports on the same symbol/timeframe — values should match where the merge claims to preserve behavior.
- Verify resource caps are not hit (`max_lines_count`, `max_labels_count`, `max_boxes_count`) over a long history.

Record what was inspected and what was confirmed. This is the strongest evidence available short of automated runtime testing.

## Section 6 — Things that are NOT validation

Do not cite any of the following as proof the merged Pine indicator is correct:

- `npm run lint` / `npm run build` — those validate the dashboard, not Pine.
- `pytest` / `unittest` / `jest` / `vitest` — those validate non-Pine code.
- Generic linters (`eslint`, `prettier`, `ruff`, `black`, `shellcheck`).
- "I read the script and it looks right."
- "It compiled in my head."
- "The structure matches the source so the behavior must too."
- "A previous version passed, and this one is similar."
- "TypeScript types compile cleanly" (irrelevant — Pine isn't TypeScript).

If the only evidence available is from this list, return `NOT VERIFIED` and request the user (or the session shell) run the Pine-specific guards above.

## Section 7 — Verdict template

Capture in the proof packet:

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
  check-visual-contract.sh:        PASS | FAIL | NOT RUN — reason (only required if visual scope touched)
  check-indicator-strategy-parity.sh: PASS | FAIL | NOT RUN — reason (only if strategy harness reopened)

REPAINT REVIEW: PASS | FAIL — notes
RESOURCE BUDGET: PASS | FAIL — current vs caps
OPTUNA NAME PARITY: PASS | FAIL — notes
SOURCE PARITY: PASS | FAIL — notes
TRADINGVIEW CHART INSPECTION: PASS | NOT PERFORMED — what was checked

VERDICT: VERIFIED | NOT VERIFIED
  if NOT VERIFIED: list every item missing or failing.
```

A single FAIL or NOT RUN that the user did not explicitly waive means the verdict is `NOT VERIFIED`.
