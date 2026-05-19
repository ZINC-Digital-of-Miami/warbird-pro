---
name: tc-bar-coloring
description: Pine v6 visual coloring — barcolor() for per-bar coloring, bgcolor() for backgrounds, conditional coloring patterns, gradient colors, and the color.new() helper. Use when painting chart bars by condition, tinting regime backgrounds, or building visual diagnostics.
---

# Pine v6 bar + background coloring (Kirk priority 6)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Barcolor

_Source: <https://www.tradingcode.net/tradingview/change-colour-price-bars/>_

### barcolor() — Colour Price Bars in TradingView Pine Script

**Syntax:**
```pine
barcolor(color, offset, title, editable)
```

**Key behaviors:**
- Always colours the chart instrument's bars, even from a separate pane script
- Bar appearance depends on chart type (Candles = filled body, Hollow Candles = different)
- Pass `na` to leave bar colour unchanged on that bar

**Simple conditional barcolor:**
```pine
// Green bars above EMA, red below
emaValue = ta.ema(close, 20)
barcolor(close > emaValue ? color.green : color.red)
```

**Multi-condition barcolor with if/else chain:**
```pine
//@version=5
indicator(title="barcolor() example", overlay=true)

emaLength = input.int(20, title="EMA Length")
emaValue  = ta.ema(close, emaLength)

plot(emaValue, linewidth=2, color=close > emaValue ? #228B22 : #B22222)

// Inside bar: high < prev high AND low > prev low
insideBar  = high < high[1] and low > low[1]
// Outside bar: high > prev high AND low < prev low
outsideBar = high > high[1] and low < low[1]

upTrend   = close > emaValue and close[1] > emaValue[1]
downTrend = close < emaValue and close[1] < emaValue[1]

// Colour based on trend + bar type
barColour = if upTrend and insideBar
    color.green
else if upTrend and outsideBar
    color.lime
else if downTrend and insideBar
    color.maroon
else if downTrend and outsideBar
    color.purple

barcolor(barColour)
```

**Notes:**
- `barcolor(na)` on a bar = no colour change (leaves default)
- Hex colours work: `#228B22` (forest green), `#B22222` (firebrick)
- `insideBar = high < high[1] and low > low[1]` — classic inside bar detection
- `outsideBar = high > high[1] and low < low[1]` — outside bar detection
- For custom candles in a separate pane use `plotcandle()` or `plotbar()` instead

---

## Bgcolor

_Source: <https://www.tradingcode.net/tradingview/colour-tradingview-background/>_

### bgcolor() — Colour Chart Background in TradingView Pine Script

**Syntax:**
```pine
bgcolor(color, offset, editable, title)
```

**Simple conditional bgcolor:**
```pine
bgcolor(close > ta.sma(close, 20) ? color.new(color.green, 85) : color.new(color.red, 85))
```

**`var` + `:=` pattern — persist a state across bars:**
```pine
var enterLong  = false
var enterShort = false

// Only true on the FIRST bar the condition is met (not enterLong[1] prevents repeating)
enterLong  := ema1 > ema2 and ema2 > ema3 and not enterLong[1]
enterShort := ema1 < ema2 and ema2 < ema3 and not enterShort[1]
```

**Full strategy with bgcolor showing position:**
```pine
//@version=5
strategy(title="EMA crosses", overlay=true)

priceData  = input.source(hl2, title="Price data")
ema1Length = input.int(12, title="EMA 1")
ema2Length = input.int(24, title="EMA 2")
ema3Length = input.int(36, title="EMA 3")

ema1 = ta.ema(priceData, ema1Length)
ema2 = ta.ema(priceData, ema2Length)
ema3 = ta.ema(priceData, ema3Length)

var enterLong  = false
var enterShort = false

enterLong  := ema1 > ema2 and ema2 > ema3 and not enterLong[1]
enterShort := ema1 < ema2 and ema2 < ema3 and not enterShort[1]

plot(ema1, color=color.orange, linewidth=2)
plot(ema2, color=color.maroon, linewidth=2)
plot(ema3, color=color.blue,   linewidth=2)

if enterLong
    strategy.entry("Enter Long", strategy.long)
if enterShort
    strategy.entry("Enter Short", strategy.short)

// Green bg when long, red when short/flat
backgroundColour = if strategy.position_size > 0
    color.new(color.green, 85)
else
    color.new(color.red, 85)

bgcolor(backgroundColour)
```

**Notes:**
- `bgcolor(na)` = no background colour on that bar
- Transparency 85–90 is typically right for backgrounds (mostly transparent)
- Works from overlay OR separate-pane scripts — always colours the main chart background
- `var enterLong = false` + `not enterLong[1]` = fires only on the transition bar, not every bar
- `input.source(hl2, ...)` — source input defaults to hl2 (high+low)/2

---

## Conditional Colours

_Source: <https://www.tradingcode.net/tradingview/conditional-colours/>_

### Conditional colours in TradingView Pine

**Supports conditional colours:** `barcolor()`, `bgcolor()`, `plot()`, `plotarrow()`, `plotbar()`, `plotcandle()`, `plotchar()`, `plotshape()`
**Does NOT support conditional colours:** `fill()`, `hline()`

**Simple inline conditional colour:**
```pine
//@version=5
indicator(title="Conditional colours with ?:", overlay=true)

plot(close, color=close > ta.sma(close, 5) ? color.green : color.red)
```

**Triple-EMA alignment colour (full example):**
```pine
//@version=5
indicator(title="Colouring conditionally with ?:", overlay=true)

// Inputs
priceData = input.source(close, title="Price data")
fastMA    = input.int(10, title="Fast MA")
medMA     = input.int(23, title="Medium MA")
slowMA    = input.int(48, title="Slow MA")

// Calculate values
emaFast = ta.ema(priceData, fastMA)
emaMed  = ta.ema(priceData, medMA)
emaSlow = ta.ema(priceData, slowMA)

// Determine colour: green if aligned up, red if aligned down, yellow otherwise
lineColour = emaFast > emaMed and emaMed > emaSlow ? color.green :
     emaFast < emaMed and emaMed < emaSlow ? color.red :
     color.yellow

// Plot moving averages
plot(emaFast, linewidth=2, color=lineColour)
plot(emaMed, linewidth=2, color=lineColour)
plot(emaSlow, linewidth=2, color=lineColour)
```

**Pattern summary:**
- Ternary: `condition ? colorA : colorB`
- Chain: `cond1 ? c1 : cond2 ? c2 : defaultColor`
- Variable: set `myColor = ...` then use `color=myColor` in plot

---

## Gradient Colours

_Source: <https://www.tradingcode.net/tradingview/gradient-colours/>_

### Gradient-like colours in TradingView Pine

No built-in gradient function — create a custom function that returns different hex shades based on value range.

**Pattern: custom shade function + chained ternaries:**
```pine
GreenShade(value) =>
    value >= 75 ? #00b300 : // dark green
     value > 50 ? #00cc00 :
     value > 30 ? #00e600 :
     value > 20 ? #00ff00 : // green
     value > 15 ? #1aff1a :
     value > 10 ? #33ff33 :
         #4dff4d             // light green

RedShade(value) =>
    value >= 75 ? #b30000 : // dark red
     value > 50 ? #cc0000 :
     value > 30 ? #e60000 :
     value > 20 ? #ff0000 : // red
     value > 15 ? #ff1a1a :
     value > 10 ? #ff3333 :
         #ff4d4d             // light red
```

**Full gradient histogram example (ticks per bar):**
```pine
//@version=5
indicator(title="Gradient-like colours", overlay=false, precision=0)

useWholePips = input.bool(false, title="Base ticks on whole pips (fx)?")

GreenShade(value) =>
    value >= 75 ? #00b300 :
     value > 50 ? #00cc00 :
     value > 30 ? #00e600 :
     value > 20 ? #00ff00 :
     value > 15 ? #1aff1a :
     value > 10 ? #33ff33 :
         #4dff4d

RedShade(value) =>
    value >= 75 ? #b30000 :
     value > 50 ? #cc0000 :
     value > 30 ? #e60000 :
     value > 20 ? #ff0000 :
     value > 15 ? #ff1a1a :
     value > 10 ? #ff3333 :
         #ff4d4d

tickCorrection = useWholePips ? 0.1 : 1

ticksInBar = ((high - low) / syminfo.mintick) *
     tickCorrection

plotColour = close > open ?
     GreenShade(ticksInBar) :
     RedShade(ticksInBar)

plot(ticksInBar, style=plot.style_histogram, linewidth=4,
     color=plotColour)
hline(0, linestyle=hline.style_dotted)
```

**Key notes:**
- `syminfo.mintick` = minimum tick size for the symbol
- Custom functions declared with `FuncName(arg) => ...` pattern
- Last expression in a function is its return value
- `color.from_gradient()` is the built-in v5 alternative (see pine-colour-functions.md)

---

## Color New Function

_Source: <https://www.tradingcode.net/tradingview/color-function/>_

### color.new() function in TradingView Pine

**Syntax:** `color.new(color, transp)`
- `color`: a built-in color constant or hex value
- `transp`: 0 (opaque/solid) → 100 (fully invisible)

**fill() between plots with transparency:**
```pine
//@version=5
indicator(title="Reference indicator - color() example", overlay=true)

len1 = input.int(10, title="Short Length")
len2 = input.int(20, title="Middle Length")
len3 = input.int(30, title="Long Length")

hh1 = ta.highest(high, len1)[1]
hh2 = ta.highest(high, len2)[1]
hh3 = ta.highest(high, len3)[1]

ll1 = ta.lowest(low, len1)[1]
ll2 = ta.lowest(low, len2)[1]
ll3 = ta.lowest(low, len3)[1]

hpl1 = plot(hh1, color=color.green, linewidth=3)
hpl2 = plot(hh2, color=color.green, linewidth=2)
hpl3 = plot(hh3, color=color.green)

lpl1 = plot(ll1, color=color.red, linewidth=3)
lpl2 = plot(ll2, color=color.red, linewidth=2)
lpl3 = plot(ll3, color=color.red)

fill(plot1=hpl1, plot2=hpl2, color=color.new(color.green, 30))
fill(plot1=hpl2, plot2=hpl3, color=color.new(color.green, 70))

fill(plot1=lpl1, plot2=lpl2, color=color.new(color.red, 30))
fill(plot1=lpl2, plot2=lpl3, color=color.new(color.red, 70))
```

**Conditional transparent colour with ternary:**
```pine
myColour = close > close[1] ?
     color.new(color.teal, 30) :
     color.new(color.yellow, 80)

plot(ta.ema(close, 20), color=myColour, linewidth=3)
```

**Conditional transparent colour with if/else:**
```pine
myColour = if close < ta.sma(close, 10)
    color.new(color.teal, 30)
else
    color.new(color.yellow, 80)

plot(ta.ema(close, 20), color=myColour, linewidth=3)
```

**Notes:**
- Works with standard colors (`color.green`) and hex values (`#FF0000`)
- Multiple instances of same script on chart = TV shifts colors automatically
- Use with: `plot()`, `bgcolor()`, `fill()`, `barcolor()`, `plotshape()`, `plotarrow()`

---

## Pine Colour Functions

_Source: <https://www.tradingcode.net/tradingview/pine-colour-functions/>_

### Pine Script colour function groups

Four groups:

**1. Show colours on chart** (plotting/drawing functions that accept colour args):
- `plot()` — `color=` param
- `plotshape()` — `color=`, `textcolor=`
- `plotarrow()` — `colorup=`, `colordown=`
- `bgcolor()` — background colour
- `barcolor()` — candle/bar colour
- `fill()` — fill between two plots
- `line.new()` — `color=`
- `label.new()` — `color=`, `textcolor=`
- `box.new()` — `border_color=`, `bgcolor=`

**2. Generate colours** (modify/prepare colour values):
- `color.new(color, transp)` — apply transparency 0-100
- `color.rgb(r, g, b, transp)` — create from RGB + optional transparency
- `color.from_gradient(value, bottom_value, top_value, bottom_color, top_color)` — gradient between two colours

**3. Colour information** (inspect a colour):
- `color.r(color)` — red component (0-255)
- `color.g(color)` — green component (0-255)
- `color.b(color)` — blue component (0-255)
- `color.t(color)` — transparency (0-100)

**4. Work with colour values**:
- `color.na` — na/transparent color constant
- `input.color(defval, title)` — add colour picker input to indicator settings

**Standard built-in colours:**
`color.red`, `color.green`, `color.blue`, `color.orange`, `color.yellow`,
`color.purple`, `color.teal`, `color.lime`, `color.fuchsia`, `color.aqua`,
`color.white`, `color.black`, `color.gray`, `color.silver`, `color.maroon`,
`color.navy`, `color.olive`


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
