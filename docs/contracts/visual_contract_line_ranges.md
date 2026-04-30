# Visual Contract — Protected Line-Range Manifest

**Date:** 2026-04-29
**Status:** Active enforcement contract. SAME ENFORCEMENT TIER as the fib-core lock and the fib-scanner-ban.
**Work surface protected:** `indicators/v7-warbird-institutional-backtest-strategy.pine` on `codex/wb-opt-bt-first-structural-fibs` (paste branch)
**Frozen snapshot:** `.references/visual_contract_frozen_2026-04-29.txt`
**Guard script:** `scripts/guards/check-visual-contract.sh`
**Memory rule:** `feedback_visual_contract_sacred.md` — "verbal commitments don't count, the guard script is the source of truth"

## How This Manifest Works

Each protected region is identified by a START_MARKER and END_MARKER — unique substrings of content that uniquely identify the first and last line of the region in the Pine file. The guard script:

1. Locates START_MARKER and END_MARKER in the current Pine file (line numbers may shift relative to the snapshot if unprotected sections above grow/shrink)
2. Extracts the inclusive line range
3. Compares it byte-for-byte against the equivalent extraction in the frozen snapshot
4. Fails (exit non-zero) if any region's content has changed

This is robust to insertions/deletions ABOVE protected regions — the markers will still find the right lines. It is intentionally NOT robust to changes WITHIN protected regions; that's the entire point.

## Protected Regions

### R01 — Canonical color constants
**Why:** The hex values (`#FFFFFF`, `#B83B55`, `#006064`, `#CB3F3B`, `#6D6E78`, `#B0B0B0`, `#808080`) are the operator-approved palette. Any color change must come from Architect, not from a tuning side-effect.

- START_MARKER: `color COLOR_ANCHOR             = #FFFFFF    // white — 0, .5, 1 levels`
- END_MARKER: `color COLOR_ENTRY_LABEL        = #6D6E78    // gray — entry label`

### R02 — Canonical width constants
**Why:** Line widths (1 / 1 / 3 / 2) define visual hierarchy of fib levels. Tuning must not introduce width changes.

- START_MARKER: `int WIDTH_ANCHOR      = 1`
- END_MARKER: `int WIDTH_TARGET      = 2`

### R03 — Visuals input section (groupViz)
**Why:** All operator-facing visual toggles, color/width overrides, line-style choice, label visibility, label sizing, transparency. Any change here is a UI change to Architect's chart configuration.

- START_MARKER: `string groupViz = "Visuals"`
- END_MARKER: `int zoneFillTransparencyInput = input.int(80, "Zone Fill Alpha", minval=0, maxval=100, group=groupViz)`

### R04 — Brand watermark inputs (groupBrand)
**Why:** Watermark on/off, brand colors, transparencies. Architect's brand layer.

- START_MARKER: `string groupBrand = "Warbird Web Watermark"`
- END_MARKER: `color webWatermarkProColorInput = input.color(color.new(#FF0000, 72), "Pro", inline="wm", group=groupBrand)`

### R05 — Drawing helpers (f_line_style, f_label_size)
**Why:** These map the user's string input to Pine's line-style/label-size enums. Their behavior IS the visual contract.

- START_MARKER: `f_line_style(string styleName) =>`
- END_MARKER: `    sizeName == "Tiny" ? size.tiny : sizeName == "Normal" ? size.normal : sizeName == "Large" ? size.large : size.small`

### R06 — Drawing primitive declarations (var line/label/box/table)
**Why:** These are the actual line/label/box objects rendered on chart. Renaming, reordering, or changing their initial properties would shift the visual layer.

- START_MARKER: `var line lineZero  = line.new(bar_index, close, bar_index, close, color=color(na), width=1)`
- END_MARKER: `var table webWatermarkTable = table.new(position.middle_center, 2, 1, bgcolor=color.new(color.black, 100), border_color=color.new(color.black, 100), border_width=0, frame_color=color.new(color.black, 100), frame_width=0)`

### R07 — drawAnchoredLine function definition
**Why:** This function paints fib lines. Its math (rightBar calc, line.set_xy1/xy2, line.set_color/width/style/extend) defines exactly how lines render.

- START_MARKER: `drawAnchoredLine(line id, bool visible, float price, color col, int width_, int leftBar) =>`
- END_MARKER: `        line.set_color(id, color(na))`

### R08 — setFibLevelLabel function definition
**Why:** This function paints fib level labels. Label creation, positioning, color, size are all here.

- START_MARKER: `setFibLevelLabel(label idIn, bool visible, float price, string levelName, color col) =>`
- END_MARKER: `    id`

### R09 — drawAnchoredLine call block (the 16 fib level draws)
**Why:** The exact set of fib levels drawn (0, .236, .382, .500, .618, .786, 1.000, T1-T5, 1.382, 1.500, 1.786) and their color/width assignments is the visual fib ladder Architect dialed in.

- START_MARKER: `drawAnchoredLine(lineZero,  true, effectivePZero,  fibAnchorColorInput,             fibAnchorWidthInput,             effectiveDrawLeftBar)`
- END_MARKER: `drawAnchoredLine(lineT5,    true, effectivePT5,    fibTargetColorInput,             fibTargetWidthInput,             effectiveDrawLeftBar)`

### R10 — setFibLevelLabel call block (in barstate.islastconfirmedhistory)
**Why:** The fib level labels rendered on the right edge with their text formatting and colors.

- START_MARKER: `if barstate.islastconfirmedhistory`
- END_MARKER: `    _fibLblT5 := setFibLevelLabel(_fibLblT5, showFibLevelLabelsInput, pT5, "T5", fibTargetColorInput)`

### R11 — Trade label drawing block (ENTRY/SL/T1-T5 paint when trade visible)
**Why:** When a trade is in flight, the ENTRY/SL/T1/T2/T3/T4/T5 labels paint with operator-approved colors, transparencies, and sizes.

- START_MARKER: `if barstate.islast and showTradeLevels and not na(_lblEntry) and not na(_lblSl)`
- END_MARKER: `    label.set_color(_lblT5, color(na))`

### R12 — Zone box drawing block
**Why:** The pivot zone fill rendering — top/bottom/bgcolor/border.

- START_MARKER: `if not na(zoneFillUpper) and not na(zoneFillLower)`
- END_MARKER: `    box.set_border_color(zoneBox, color(na))`

### R13 — Watermark table cells render block
**Why:** WARBIRD/PRO text rendering, colors, alignment, formatting.

- START_MARKER: `if barstate.islast`
- END_MARKER: `    table.cell(webWatermarkTable, 1, 0, showWebWatermarkInput ? "PRO" : "", text_color=webWatermarkProColorInput, text_size=size.huge, text_halign=text.align_left, bgcolor=color.new(color.black, 100))`

NOTE: `if barstate.islast` appears multiple times in the file. The guard locates this specific block by looking for the END_MARKER (unique to the watermark) and walking backwards to the most-recent matching START_MARKER above it.

### R14 — EMA/VWAP plot calls
**Why:** EMA9/EMA21/EMA50/VWAP plot lines with their input-driven colors and widths. These ARE on chart and tuning must not redirect them.

- START_MARKER: `plot(showEma9Input ? ema9 : na, "EMA 9", ema9ColorInput, ema9WidthInput)`
- END_MARKER: `plot(showVwapInput ? vwapVal : na, "VWAP", vwapColorInput, vwapWidthInput)`

## What Is NOT in the Visual Contract (free to tune)

- Pattern detection logic (`longLowerShadow`, `dragonflyDoji`, `longUpperShadow`, etc.)
- Trade state machine (TRADE_NONE → SETUP → ACTIVE → resolution)
- Stop / target math (`optStopAtrMult`, `optMaxRiskAtr`)
- ADX / regime detection
- Setup expiry, cooldown
- Footprint analysis (`mlExhAbsorption`, `mlExhZeroPrint`, `bullFpTriple`, etc.)
- Diamond AND-chain (`bullishExhaustion`, `bearishExhaustion`)
- Strategy.entry / strategy.exit calls
- Optuna input.* knobs that drive signal/exit logic (NOT visual inputs)
- AG export plots (`plot(..., display=display.none)` calls)

These are the SIGNAL surfaces tuning Phases 1-7 may alter with explicit per-session approval.

## What Happens When the Guard Fires

If `scripts/guards/check-visual-contract.sh` reports any region as changed:

1. The Pine edit MUST be reverted in the protected ranges.
2. The change must be re-applied in unprotected regions only, OR escalated to Architect for explicit per-region unlock.
3. No commit lands until the guard returns green.

## Update Procedure (when Architect intentionally changes the visual layer)

When Architect deliberately wants to change a color, width, label, etc.:

1. Make the change in the Pine file.
2. Re-extract the frozen snapshot: regenerate `.references/visual_contract_frozen_<YYYY-MM-DD>.txt` from the new Pine state.
3. Update this manifest if any markers shifted.
4. Update the symlink or path in `scripts/guards/check-visual-contract.sh` to point to the new snapshot file (keep the old snapshot in `.references/` for history).
5. Commit all four (Pine + new snapshot + manifest + guard script change) in one atomic commit.

This makes intentional changes fully traceable while preventing accidental drift.
