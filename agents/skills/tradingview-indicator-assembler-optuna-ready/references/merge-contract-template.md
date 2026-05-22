# Combined Indicator Contract Template

This contract is the design document for the merged indicator. Fill it in **before** writing Pine code. If you cannot fill in a section honestly, that section is not designed yet — go back and design it before opening the editor.

---

## Identity

- Final indicator name:
- Pine version: `//@version=6` (default v6; if a source forces v5, justify here)
- Script type: `indicator(...)` | `strategy(...)` | `library(...)`
- Title: `<title="...">`
- Shorttitle: `<shorttitle="...">`
- Overlay: true | false (must match what the user expects on chart)
- `max_lines_count`:
- `max_labels_count`:
- `max_boxes_count`:
- `max_bars_back`:

Justify any non-default values.

## Source ownership map

Carried over from Phase 3. Every major component traces back to one source — or is marked "new" with a reason it was added.

| Component | Owner source | Notes / what was preserved |
|-----------|--------------|----------------------------|
| Fib anchor logic |  |  |
| Fib level math |  |  |
| Moving averages |  |  |
| Trend filter |  |  |
| Signal trigger |  |  |
| Entry / stop / target levels |  |  |
| Label rendering |  |  |
| Color and style system |  |  |
| Watermark / branding |  |  |
| Alert conditions |  |  |
| Hidden export plots (`ml_*`, `nexus_fp_*`, etc.) |  |  |
| Other |  |  |

If a row is "new (not from any source)", add a one-line reason for the addition.

## Naming convention

Document collisions and rename decisions explicitly. Reviewers (and Optuna) need to map merged names back to sources.

| Source name(s) | Final merged name | Reason |
|----------------|-------------------|--------|
| A: `len`, B: `len` | `fibLen`, `maLen` | collision |
| A: `useEma`, B: `enableEma` | `useEma` | dedup |
|                |                   |        |

State the convention you used (e.g., "domain prefix on collisions: `fib*`, `ma*`, `sig*`, `viz*`").

## Input groups (final, in this order)

1. **Fib Structure** — anchors, ladders, fib level enables.
2. **Moving Averages** — MA lengths, sources, gating booleans.
3. **Signal Logic** — trigger thresholds, filters, confirmation toggles.
4. **Visual Style** — colors, line widths, label sizes, transparency.
5. **Labels** — what shows, where, with what text.
6. **Alerts** — alert message templates, payload toggles.
7. **Optuna / Debug** — sweep mode toggles, hidden export enables.
8. **Advanced** — escape hatches the user explicitly requested.

For each group, list which inputs it contains. Do not let a single input span groups.

## Surviving plots and dropped plots

| Final plot | Source | Visible? | Counts toward 64-cap? | Kept because… |
|------------|--------|----------|-----------------------|---------------|
|            |        |          | yes                   |               |

| Dropped from source | Reason |
|---------------------|--------|
|                     |        |

## Repaint policy

- Default policy for this indicator: **no repaint** unless explicitly approved.
- Exceptions in this build:
  - `<exception 1>` — why it is acceptable, how it is communicated to the user (e.g., "intrabar preview, separate plot color, marked PREVIEW in label").
- Confirmation gate(s) used: `barstate.isconfirmed` / closed-bar offset `[1]` / pivot offset / etc.
- HTF/security calls: lookahead setting, justification.
- `request.footprint()` calls: caching strategy (must be per-bar, not per-tick).

## Alert conditions

| Alert title | Fires when | Confirmation rule | Payload (text) | Counts toward 64-cap |
|-------------|-----------|-------------------|----------------|----------------------|
|             |           | `barstate.isconfirmed` |             | yes                 |

Total alertcondition count: `XX`.

## Resource budget (priced before coding)

TradingView's hard cap is 64 outputs per script. Hidden plots and alertconditions count.

| Output kind | Count |
|-------------|-------|
| `plot` |  |
| `plotshape` |  |
| `plotchar` |  |
| `plotarrow` |  |
| `plotbar` |  |
| `plotcandle` |  |
| `bgcolor` |  |
| `fill` |  |
| `hline` |  |
| `alertcondition` |  |
| **Total** | `XX / 64` |

Other budgets:

- `request.security` count: `XX / 40` (Pine cap; warbird-pro warns at >30)
- `request.footprint` count: `XX` (heavy; cache per bar)
- `max_lines_count` headroom: `<set>` vs peak `<observed>`
- `max_labels_count` headroom: `<set>` vs peak `<observed>`
- `max_boxes_count` headroom: `<set>` vs peak `<observed>`

If any line above is at or near its cap, document the mitigation (drop a visual, hide a plot, recycle a drawing, collapse alerts) and update the contract before writing code.

## Open design questions

List anything you are unsure about and need the user to answer before coding. Once answered, write the answer here and continue.

---

## Sign-off (after Phase 5 design review)

- Contract reviewed against source inventories: yes / no
- All ownership rows traceable: yes / no
- Resource budget within caps: yes / no
- Ready to write Pine: yes / no — if no, what is missing:
