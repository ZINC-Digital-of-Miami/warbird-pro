# Source Inventory Template

Fill out one of these per source indicator before merging. The point is to have a written record of what each source contains, so the merge has an audit trail and nothing is "lifted from memory."

If the source is large, fill the inventory by section rather than line-by-line. Coverage matters more than precision — but inputs, plots, alerts, request.security/footprint, and var state must be exhaustive.

---

## Source identifier

- Source label: A | B | C | … (use the labels the user used, or assign A/B/C if not given)
- File path: `<absolute or repo-relative path>`
- Git ref or version: `<branch / commit / TradingView version note>`
- One-line role: `<what this source contributes to the merge — fib anchor, MA stack, label style, alert engine, etc.>`

## Header

- Pine version declaration: `//@version=?`
- Script type: `indicator(...)` | `strategy(...)` | `library(...)`
- Title / shorttitle:
- Overlay: true | false
- `max_lines_count`:
- `max_labels_count`:
- `max_boxes_count`:
- `max_bars_back`:
- Other declaration args:

## Inputs

List every `input.*()` call. One row per input.

| Name | Type | Default | Group | Tooltip / notes |
|------|------|---------|-------|-----------------|
|      |      |         |       |                 |

Note any input that is referenced in signal logic vs. visual-only logic.

## Plots and other output calls

TradingView caps total output calls at 64 per script. Hidden plots (`display=display.none`) and `alertcondition()` calls count.

| Kind | Name / first arg | Visible? | Notes |
|------|------------------|----------|-------|
| plot |                  |          |       |
| plotshape |             |          |       |
| plotchar |              |          |       |
| plotarrow |             |          |       |
| plotbar |               |          |       |
| plotcandle |            |          |       |
| bgcolor |               |          |       |
| fill |                  |          |       |
| hline |                 |          |       |
| alertcondition |        |          |       |

Total output calls counted: `XX / 64`.

## Drawing primitives

- `label.new(...)` call sites and how they are deleted/updated:
- `line.new(...)` call sites:
- `box.new(...)` call sites:
- `table.new(...)` call sites:

Note whether drawings are bounded (deleted/recycled) or accumulate. Unbounded growth blows past `max_*_count`.

## Higher-timeframe and footprint requests

| Call | Symbol | Timeframe | Expression | Lookahead | Cached per bar? |
|------|--------|-----------|------------|-----------|-----------------|
| `request.security(...)` |  |  |  | `barmerge.lookahead_off` / `_on` |  |
| `request.footprint(...)` |  |  |  | n/a |  |

Total `request.security()` count: `XX` (Pine cap 40; warbird-pro warns at >30).
Total `request.footprint()` count: `XX`.

## Persistent state

List every `var` and `varip` declaration with what it holds.

| Identifier | Storage | Initial value | What it persists | Reset rules |
|------------|---------|---------------|------------------|-------------|
|            | var / varip |           |                  |             |

## Helper functions

For each function definition, record:

- Signature: `f_name(arg1, arg2) =>`
- Returns:
- Globals it reads:
- Side effects (label/line/box/table mutations):
- Whether it is safe to lift in isolation, or whether it requires neighboring helpers / globals.

## Core logic blocks

Identify the major logic blocks. For each:

- Block name (e.g., "fib anchor selection", "MA gate", "entry trigger").
- Inputs it consumes.
- Outputs it produces (variables, plots, drawings, alerts).
- Bar-state assumption (`barstate.isconfirmed`, `barstate.islast`, intrabar, etc.).
- Repaint risk: none / preview-only / signal-bearing.

## Inter-block dependencies

Sketch the dependency graph between blocks. Example:

```
fibAnchor -> fibLevels -> entryTrigger -> alertconditions
maStack   -> trendOk   -> entryTrigger
labelStyle -------------> labels (visual only)
```

Note any cycles or hidden dependencies (e.g., a helper that reads a global set later in the file).

## Extraction risk

For each component the merge will lift, write down what would break if it were lifted in isolation. Examples:

- "fibAnchor depends on `var float anchorHigh` initialized at bar 0; lifting requires lifting the init too."
- "labelStyle reads `var label _lblEntry`; lifting requires preserving the declaration order."
- "alertcondition for `entryLong` references `entryConfirmed`, which is set inside an if block — moving the alert to a different scope will break it."

## Repaint posture

- Does this source repaint? yes / no / mixed
- Where does it use `barstate.isconfirmed`?
- Where does it use `request.security(..., lookahead=...)`?
- Where does it use pivot detection without right-side offset?
- Does it ever read `close` on the live bar as if it were closed?

## Visual budget snapshot

- Output count: `XX / 64`
- `request.security` count: `XX / 40`
- `request.footprint` count: `XX`
- `max_lines_count`: `XX`, peak observed lines: `XX`
- `max_labels_count`: `XX`, peak observed labels: `XX`
- `max_boxes_count`: `XX`, peak observed boxes: `XX`

## Free-form notes

Anything else worth writing down before the merge — known bugs, areas the source author flagged as fragile, or behaviors the user has called out.
