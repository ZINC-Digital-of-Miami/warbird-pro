---
name: tc-plots
description: Pine v6 plot family — overview of plot types, plotshape() markers, plotarrow() directional arrows scaled by magnitude, and fill()/hline() for horizontal references. Use when choosing how to render a value on the chart and fitting within the 64-output budget.
---

# Pine v6 plot functions (Kirk priority 5)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Plot Types Overview

_Source: <https://www.tradingcode.net/tradingview/overview-plots/>_

### Plot Types Overview in TradingView Pine Script

All plots use `plot(value, style=plot.style_*, ...)`. Default is `plot.style_line`.

**All plot style constants:**
| Style | Constant | Best for |
|-------|----------|----------|
| Regular line | `plot.style_line` (default) | Trending data (MAs, RSI) |
| Step line | `plot.style_stepline` | Data with irregular changes (gaps, position size) |
| Line with breaks | `plot.style_linebr` | Conditional data with gaps |
| Histogram | `plot.style_histogram` | Discrete values, volume, MACD |
| Crosses | `plot.style_cross` | Highlight specific prices |
| Circles | `plot.style_circles` | Signal markers on price |
| Area | `plot.style_area` | Filled area under line |
| Area with breaks | `plot.style_areabr` | Conditional area (gaps allowed) |
| Columns | `plot.style_columns` | Positive/negative bars (volume delta) |

**Line plot (default):**
```pine
plot(ta.ema(close, 10))                                        // default line
plot(ta.sma(close, 40), style=plot.style_line, color=color.orange)
```

**Step line:**
```pine
plot(ta.mom(volume, 10), style=plot.style_stepline)
```

**Line with breaks — use `na` to break the line:**
```pine
emaValue = ta.ema(close, 12)
plot(dayofweek > 4 ? emaValue : na,
     color=color.teal, style=plot.style_linebr, linewidth=3)
```

**Histogram:**
```pine
plot(volume, style=plot.style_histogram, linewidth=4, color=color.orange)
```

**Crosses — good for marking highest/lowest levels:**
```pine
plot(ta.highest(high, 20), style=plot.style_cross, color=color.green, linewidth=2)
plot(ta.lowest(low, 20),   style=plot.style_cross, color=color.red,   linewidth=2)
```

**Circles — good for signal dots on price:**
```pine
plot(ta.ema(ta.sma(close, 10), 20), style=plot.style_circles, linewidth=3)
```

**Area — two layered areas (second should be more transparent):**
```pine
plot(volume, style=plot.style_area, color=color.orange)
plot(ta.sma(volume, 20), style=plot.style_area, color=color.new(color.blue, 75))
```

**Area with breaks:**
```pine
newWeek = dayofweek == dayofweek.sunday or dayofweek == dayofweek.monday
plot(newWeek ? volume : na, style=plot.style_areabr)
```

**Columns — positive/negative coloring:**
```pine
volChange = volume - ta.sma(volume, 50)
plot(volChange, style=plot.style_columns,
     color=volChange > 0 ? color.green : color.red)
```

**Notes:**
- `linewidth` controls thickness (1–4); for circles/crosses controls size
- Pass `na` to stop/break any plot type on that bar
- Multiple histograms overlay each other — use columns instead for side-by-side effect
- `plot.style_linebr` and `plot.style_areabr` are the "with breaks" variants
- Columns price scale starts at 0; line scale is adaptive (doesn't start at 0)

---

## Plotshape

_Source: <https://www.tradingcode.net/tradingview/show-alerts-shapes/ + https://www.tradingcode.net/tradingview/show-alert-shapes-text/>_

### plotshape() — Plot Shapes on Chart in TradingView Pine Script

**Syntax:**
```pine
plotshape(series, title, style, location, color, offset, text, textcolor, editable, size, show_last, xloc)
```

**Key args:**
- `series` — true/false condition; shape appears when true
- `style` — shape type (see constants below)
- `location` — where on bar (default: `location.abovebar`)
- `text` — label text shown with shape; use `\n` for line break
- `textcolor` — colour of the text
- `color` — colour of the shape
- `size` — shape size (`size.tiny`, `size.small`, `size.normal`, `size.large`, `size.huge`)

**Shape style constants:**
```pine
shape.circle        shape.square        shape.diamond
shape.cross         shape.xcross        shape.triangleup
shape.triangledown  shape.flag          shape.arrowup
shape.arrowdown     shape.labelup       shape.labeldown
```

**Location constants:**
```pine
location.abovebar    // above the bar (default)
location.belowbar    // below the bar
location.top         // top of chart pane
location.bottom      // bottom of chart pane
location.absolute    // uses the series value as price level
```

**Simple shape on crossover:**
```pine
emaCross = ta.crossover(close, ta.ema(close, 10))
plotshape(emaCross, style=shape.diamond)
```

**Shape with text:**
```pine
plotshape(emaCross, style=shape.flag, text="EMA cross")
alertcondition(condition=emaCross, message="EMA crossover!")
```

**Full example — dual shapes above/below bar with text:**
```pine
//@version=5
indicator(title="Highlighting alerts with shapes and text", overlay=true)

priceBreakout  = close > ta.highest(close, 20)[1]
volumeBreakout = volume > ta.highest(volume, 10)[1]

plotshape(priceBreakout, style=shape.flag,
     color=color.green, text="Price\nbreakout")

plotshape(volumeBreakout, style=shape.diamond,
     color=color.orange, location=location.belowbar,
     text="Volume\nbreakout", textcolor=color.blue)

alertcondition(condition=priceBreakout,
     title="Price breakout",
     message="Closing price is above 20-bar highest close")

alertcondition(condition=volumeBreakout,
     title="Volume breakout",
     message="Volume above the 10-bar highest volume")
```

**Volume spike detection pattern:**
```pine
avgVolume  = ta.sma(volume, 10)
lowVolume  = volume < avgVolume * 0.8
highVolume = volume > avgVolume * 1.2

plotshape(lowVolume,  style=shape.flag,    color=color.new(color.navy, 50))
plotshape(highVolume, style=shape.diamond, color=color.orange)
```

**Notes:**
- `plotshape()` counts toward the 64 output budget
- `text="\n"` — newline inside shape label
- `location.belowbar` — useful for buy signals; `location.abovebar` for sells
- Pair `plotshape()` with same boolean as `alertcondition()` to visually verify alerts
- `ta.highest(close, 20)[1]` — highest of prev 20 bars (excludes current)

---

## Plotarrow

_Source: <https://www.tradingcode.net/tradingview/show-alerts-arrows/>_

### plotarrow() — Up and Down Arrows in Pine Script

**Syntax:**
```pine
plotarrow(series, colorup, colordown, offset, minheight, maxheight, editable, show_last, title)
```

**How arrows are triggered by the first argument:**
- Positive value → up arrow
- Negative value → down arrow
- `na` → no arrow (hide)

**Simple RSI crossover arrows:**
```pine
rsiCrossDown = ta.crossunder(ta.rsi(close, 7), ta.rsi(close, 21))
rsiCrossUp   = ta.crossover(ta.rsi(close, 7), ta.rsi(close, 21))

plotarrow(rsiCrossDown ? -1 :
     rsiCrossUp ? 1 :
     na)
```

**Full example — inside/outside bar arrows with alerts:**
```pine
//@version=5
indicator(title="Alerts highlighted with arrows", overlay=true)

// Determine alert condition
insideBar = low > low[1] and
     high < high[1]

outsideBar = low < low[1] and
     high > high[1]

// Plot arrow
plotarrow(insideBar ? 1 :
         outsideBar ? -1 :
         na,
     colorup=color.fuchsia, colordown=color.yellow,
     maxheight=30)

// Create alert conditions
alertcondition(condition=insideBar,
     title="Inside bar",
     message="The current bar is an inside bar")

alertcondition(condition=outsideBar,
     title="Outside bar",
     message="The instrument just formed an outside bar")
```

**3-step pattern for arrows + alerts:**
1. Store alert condition in Boolean variable
2. Use that variable with `plotarrow()` (positive/negative/na)
3. Use that same variable with `alertcondition()` — ensures visual and alert fire together

**Key patterns:**
- `plotarrow(cond ? 1 : na)` — up arrow when true, nothing when false
- `plotarrow(bullish ? 1 : bearish ? -1 : na)` — dual direction arrows
- `colorup=` / `colordown=` — separate colors for up vs down arrows
- `maxheight=30` — limit arrow height in pixels
- `minheight=` — enforce minimum arrow size
- `plotarrow()` counts toward the 64 output budget
- Unlike `plotshape()`, `plotarrow()` doesn't support text labels
- Real-time bars may fire more alerts than historical data suggests (intra-bar vs bar-close)

---

## Fill Hline

_Source: <https://www.tradingcode.net/tradingview/colour-support-resistance/>_

### fill() and hline() — Filled Areas & Horizontal Lines in Pine Script

### fill() — Fill Area Between Two Plots

**Syntax:**
```pine
fill(plot1, plot2, color, title, editable, fillgaps, show_last)
```

**Must pass plot() return values — inline or stored:**
```pine
// Method 1: inline fill
fill(plot(upperBand), plot(lowerBand), color=color.new(color.blue, 80))

// Method 2: store plot() return, then fill
p1 = plot(upperBand, color=color.green)
p2 = plot(lowerBand, color=color.red)
fill(p1, p2, color=color.new(color.green, 85))
```

**Camarilla pivot zones with fill:**
```pine
//@version=5
indicator(title="Camarilla Pivots", overlay=true)

rangeSize = input.int(10, title="Shaded area size (in ticks)") * syminfo.mintick

dayClose = request.security(syminfo.tickerid, "D", close[1])
dayHigh  = request.security(syminfo.tickerid, "D", high[1])
dayLow   = request.security(syminfo.tickerid, "D", low[1])

r4 = dayClose + (dayHigh - dayLow) * 1.1 / 2
r3 = dayClose + (dayHigh - dayLow) * 1.1 / 4
s3 = dayClose - (dayHigh - dayLow) * 1.1 / 4
s4 = dayClose - (dayHigh - dayLow) * 1.1 / 2

// Shade zones around key levels
fill(plot1=plot(r4 + rangeSize, color=color.green),
     plot2=plot(r4 - rangeSize, color=color.green),
     color=color.new(color.green, 90))

fill(plot1=plot(r3 + rangeSize, color=color.red),
     plot2=plot(r3 - rangeSize, color=color.red),
     color=color.new(color.red, 90))

fill(plot1=plot(s3 + rangeSize, color=color.green),
     plot2=plot(s3 - rangeSize, color=color.green),
     color=color.new(color.green, 90))

fill(plot1=plot(s4 + rangeSize, color=color.red),
     plot2=plot(s4 - rangeSize, color=color.red),
     color=color.new(color.red, 90))
```

**Band fill (e.g., Bollinger Bands):**
```pine
basis = ta.sma(close, 20)
dev   = ta.stdev(close, 20) * 2
upper = basis + dev
lower = basis - dev

pUpper = plot(upper, color=color.blue)
pLower = plot(lower, color=color.blue)
fill(pUpper, pLower, color=color.new(color.blue, 85))
```

### hline() — Static Horizontal Line

**Syntax:**
```pine
hline(price, title, color, linestyle, linewidth, editable)
```

**Line style constants:**
```pine
hline.style_solid    // solid line (default)
hline.style_dotted   // dotted line
hline.style_dashed   // dashed line
```

**Common patterns:**
```pine
// RSI overbought/oversold levels
hline(70, "Overbought", color=color.red,   linestyle=hline.style_dashed)
hline(30, "Oversold",   color=color.green, linestyle=hline.style_dashed)
hline(50, "Midline",    color=color.gray,  linestyle=hline.style_dotted)

// Fill between two hlines
h1 = hline(70, color=color.red)
h2 = hline(30, color=color.green)
fill(h1, h2, color=color.new(color.gray, 90))  // fill() also accepts hline pairs
```

**Key notes:**
- `fill()` can take two `plot()` OR two `hline()` returns — not one of each
- `hline()` draws at a FIXED price — cannot be a series (use `plot()` for dynamic levels)
- `rangeSize = input.int(10) * syminfo.mintick` — tick-based range input pattern
- `request.security(syminfo.tickerid, "D", close[1])` — prev-day close (the `[1]` avoids lookahead)


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
