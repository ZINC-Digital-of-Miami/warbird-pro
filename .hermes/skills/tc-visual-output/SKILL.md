---
name: tc-visual-output
description: Pine v6 drawing objects: line.new() for movable segments extending forward, plus the broader drawing primitive family (labels, boxes). Use when rendering annotated TP/SL overlays, dynamic trend lines through pivots, or dashboards that bypass the 64-output plot budget.
---

# Pine v6 drawings — labels, lines, boxes (Kirk priority 7)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Line New

_Source: <https://www.tradingcode.net/tradingview/make-trend-line/>_

### line.new() — Create Trend Lines in Pine Script

**Minimal syntax (4 required args):**
```pine
line.new(x1, y1, x2, y2)
```

**Full syntax:**
```pine
line.new(x1, y1, x2, y2, xloc, extend, color, style, width)
```

**Simple trend line using bar numbers:**
```pine
//@version=5
indicator(title="Quick example: line.new()", overlay=true)

// On the last price bar, make a new trend line
if barstate.islast
    line.new(x1=bar_index[35], y1=close[35],
         x2=bar_index, y2=close)
```

**Trend line with future time coordinate (xloc.bar_time):**
```pine
//@version=5
indicator(title="Quick example: line.new()", overlay=true)

// Draw a line that extends one day into the future
if barstate.islast
    line.new(x1=time[35], y1=close[35],
         x2=time + 86400000, y2=close * 0.99,
         xloc=xloc.bar_time)
```

**Styled trend line with extend:**
```pine
//@version=5
indicator(title="Quick example: line.new()", overlay=true)

if barstate.islast
    line.new(x1=bar_index[20], y1=high[20],
         x2=bar_index, y2=low, color=color.lime,
         width=10, style=line.style_dashed,
         extend=extend.both)
```

**Store return value to modify the line later:**
```pine
// Draw a new trend line
myLine = line.new(x1=bar_index[10], y1=high[10],
     x2=bar_index, y2=high)

// Change the line's colour to red
line.set_color(id=myLine, color=color.red)
```

**Full example — dynamic highs/lows lines with `var`:**
```pine
//@version=5
indicator(title="Basic trend line example", overlay=true)

// Make both trend lines just once
var highLine = line.new(x1=bar_index[10], y1=close[10],
     x2=bar_index, y2=close, color=color.green,
     extend=extend.both)

var lowLine = line.new(x1=bar_index[10], y1=close[10],
     x2=bar_index, y2=close, color=color.red,
     extend=extend.both)

// Look for new 20-bar highs and lows
newHigh = high == ta.highest(high, 20)
newLow  = low == ta.lowest(low, 20)

// Update the lines when there's a new high or low
if newHigh
    line.set_xy1(highLine, x=bar_index[10], y=high)
    line.set_xy2(highLine, x=bar_index, y=high)

if newLow
    line.set_xy1(lowLine, x=bar_index[10], y=low)
    line.set_xy2(lowLine, x=bar_index, y=low)
```

**Key arguments:**
- `x1`, `x2` — bar_index (bar number) OR time value depending on `xloc`
- `y1`, `y2` — price coordinates
- `xloc` — `xloc.bar_index` (default) or `xloc.bar_time`
- `extend` — `extend.none` (default), `extend.left`, `extend.right`, `extend.both`
- `style` — `line.style_solid`, `line.style_dashed`, `line.style_dotted`, `line.style_arrow_left`, `line.style_arrow_right`, `line.style_arrow_both`
- `width` — line width in pixels

**Line update functions:**
- `line.set_xy1(id, x, y)` — move start point
- `line.set_xy2(id, x, y)` — move end point
- `line.set_color(id, color)` — change color
- `line.set_style(id, style)` — change style
- `line.set_width(id, width)` — change width
- `line.set_extend(id, extend)` — change extension
- `line.delete(id)` — delete the line

**Key patterns:**
- `var line.new(...)` — create once, update each bar (not re-created every bar)
- `if barstate.islast` — draw only on the final bar (one-time static lines)
- Bar numbers (`bar_index`) cannot draw into the future — use `xloc.bar_time` + `time + ms` for future
- `86400000` = 1 day in milliseconds for time arithmetic
- `line.new()` returns a line ID — save it to modify/delete later
- Max lines on chart controlled by `max_lines_count` in `indicator()` (default 50, max 500)


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
