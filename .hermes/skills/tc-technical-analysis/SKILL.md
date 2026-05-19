---
name: tc-technical-analysis
description: Pine v6 technical analysis primitives from the ta.* namespace: moving averages overview (SMA, EMA, WMA, HMA, RMA), user-configurable MA-type selectors, ATR and average true range, ta.crossover/ta.crossunder. Use when building an indicator that needs MAs, volatility bands, or cross detection.
---

# Pine v6 ta.* — moving averages, ATR, crosses (Kirk priority 8)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Moving Averages Overview

_Source: <https://www.tradingcode.net/tradingview/moving-averages-overview/>_

### Moving averages in TradingView Pine Script

| Function | Name | Notes |
|----------|------|-------|
| `ta.sma(src, len)` | Simple MA | Arithmetic average |
| `ta.ema(src, len)` | Exponential MA | Exponential weighting, favours recent |
| `ta.wma(src, len)` | Weighted MA | Linear weights, recent > old |
| `ta.hma(src, len)` | Hull MA | Combines 3 WMAs, smooth + responsive |
| `ta.rma(src, len)` | Relative MA | Like EMA but less weight on last bar — slower, less noisy |
| `ta.swma(src)` | Symmetrically-Weighted MA | Fixed 4-bar length, symmetric weights |
| `ta.vwma(src, len)` | Volume-Weighted MA | High-volume bars weighted more |
| `ta.vwap(src)` | Volume-Weighted Avg Price | Anchored from session start |
| `ta.alma(src, len, offset, sigma)` | Arnaud Legoux MA | Gaussian weights; offset=0.70, sigma=7 typical |

**Quick usage:**
```pine
smaValue  = ta.sma(close, 10)
emaValue  = ta.ema(close, 10)
wmaValue  = ta.wma(close, 20)
hmaValue  = ta.hma(close, 8)
rmaValue  = ta.rma(close, 12)
swmaValue = ta.swma(close)
vwmaValue = ta.vwma(close, 20)
vwapValue = ta.vwap(close)
almaValue = ta.alma(close, 12, 0.70, 7)
```

**Plot any average:**
```pine
plot(emaValue, color=color.navy)
plot(smaValue, color=color.orange, linewidth=2)
```

---

## Select Moving Average

_Source: <https://www.tradingcode.net/tradingview/select-moving-average/>_

### Select Moving Average Type with Pine Script (switch pattern)

**Universal MA selector function using `switch`:**
```pine
// Returns the specified MA type. runtime.error on unknown type.
MovAvgType(averageType, averageSource, averageLength) =>
    switch str.upper(averageType)
        "SMA"  => ta.sma(averageSource, averageLength)
        "EMA"  => ta.ema(averageSource, averageLength)
        "WMA"  => ta.wma(averageSource, averageLength)
        "HMA"  => ta.hma(averageSource, averageLength)
        "RMA"  => ta.rma(averageSource, averageLength)
        "SWMA" => ta.swma(averageSource)
        "ALMA" => ta.alma(averageSource, averageLength, 0.85, 6)
        "VWMA" => ta.vwma(averageSource, averageLength)
        "VWAP" => ta.vwap(averageSource)
        => runtime.error("Moving average type '" + averageType +
             "' not found!"), na
```

**Usage examples:**
```pine
// Calculate a 20-bar EMA
emaValue = MovAvgType("EMA", close, 20)

// Nest: smooth a 15-bar RMA with a 3-bar SMA
smoothedMA = MovAvgType("SMA", MovAvgType("RMA", close, 15), 3)

// Instrument-conditional MA type
weightedMA = MovAvgType(syminfo.prefix == "NASDAQ" ? "vwma" : "wma", close, 80)
```

**Full indicator with instrument-type routing:**
```pine
//@version=5
indicator(title="Moving average type example", overlay=true)

MovAvgType(averageType, averageSource, averageLength) =>
    switch str.upper(averageType)
        "SMA"  => ta.sma(averageSource, averageLength)
        "EMA"  => ta.ema(averageSource, averageLength)
        "WMA"  => ta.wma(averageSource, averageLength)
        "HMA"  => ta.hma(averageSource, averageLength)
        "RMA"  => ta.rma(averageSource, averageLength)
        "SWMA" => ta.swma(averageSource)
        "ALMA" => ta.alma(averageSource, averageLength, 0.85, 6)
        "VWMA" => ta.vwma(averageSource, averageLength)
        "VWAP" => ta.vwap(averageSource)
        => runtime.error("Moving average type '" + averageType +
             "' not found!"), na

// Route by instrument type
fastAverage = if syminfo.type == "crypto"
    MovAvgType("EMA", close, 20)
else if syminfo.type == "index"
    MovAvgType("RMA", close, 40)
else if syminfo.type == "futures"
    MovAvgType("HMA", hlc3, 30)

slowAverage = MovAvgType(syminfo.prefix == "NASDAQ" ? "vwma" : "wma", close, 80)

plot(fastAverage, color=color.blue,   title="Fast Average")
plot(slowAverage, color=color.orange, title="Slow Average")
```

**With user input for MA type:**
```pine
maType   = input.string("EMA", title="MA Type",
     options=["SMA", "EMA", "WMA", "HMA", "RMA", "ALMA", "VWMA"])
maLength = input.int(20, title="Length")
maSource = input.source(close, title="Source")

maValue = MovAvgType(maType, maSource, maLength)
plot(maValue, color=color.teal)
```

**Key patterns:**
- `switch str.upper(averageType)` — case-insensitive matching
- `runtime.error("msg")` — shows red error on chart for unknown types
- `=> runtime.error(...), na` — last branch is the default (no match)
- `ta.swma()` and `ta.vwap()` don't take length — handled by passing `averageSource` only
- `syminfo.type` values: `"crypto"`, `"index"`, `"futures"`, `"stock"`, `"forex"`, `"fund"`
- `syminfo.prefix` — exchange prefix (e.g., `"NASDAQ"`, `"NYSE"`, `"BINANCE"`)

---

## Average True Range

_Source: <https://www.tradingcode.net/tradingview/average-true-range-indicator/>_

### Average True Range (ATR) in TradingView Pine

**What ATR measures:** True range = greatest of:
- `high - low` (bar's range)
- `|high - close[1]|` (gap up)
- `|low - close[1]|` (gap down)

ATR = RMA (default) of true range over N bars (default 14).

**Basic calculation:**
```pine
atrValue = ta.atr(14)
```

**Full ATR indicator scaffold (5-step template):**
```pine
//@version=5
// Step 1. Script settings
indicator(title="Average True Range", shorttitle="ATR", overlay=false)

// ATR input options
atrType = input.string("Regular", title="ATR Type",
     options=["Regular", "Percentage", "Ticks", "Currency"])

atrLen    = input.int(14, title="ATR Length")
atrSmooth = input.string("RMA", title="Smoothing Type",
     options=["EMA", "RMA", "SMA", "WMA"])

posSize = input.int(1, title="Position Size (For Currency ATR)")

// Step 2. Calculate indicator values
atrValue = ta.atr(atrLen)

// Step 3. Determine indicator signals
// (crossover ATR MA, new highs/lows, etc.)

// Step 4. Output indicator data
plot(atrValue, title="ATR", color=color.orange)

// Step 5. Create indicator alerts
```

**ATR-based stop-loss pattern:**
```pine
atr = ta.atr(14)
stopLoss  = close - 1.5 * atr   // 1.5 ATR below entry
stopShort = close + 1.5 * atr   // 1.5 ATR above short entry
```

**ATR as percentage of price:**
```pine
atrPct = (ta.atr(14) / close) * 100
```

**Key uses:**
- Stop-loss sizing (ATR multiple avoids noise)
- Profit target estimation (daily ATR = expected range)
- Trend strength (rising ATR = strong trend)
- Breakout validity (require 1× ATR move to confirm)
- Compare intra-day progress vs. daily ATR (80% = time to exit)

---

## Atr Indicator

_Source: <https://www.tradingcode.net/tradingview/average-true-range-indicator/>_

### Average True Range (ATR) Indicator in Pine Script

**ATR type variants:**
- `Regular` — raw ATR in price units: `ta.rma(ta.tr, 14)`
- `Percentage` — ATR as % of close: `(atr / close) * 100`
- `Ticks` — ATR in ticks: `atr / syminfo.mintick`
- `Currency` — ATR × point value × position size: `atr * syminfo.pointvalue * posSize`

**Custom ATR function (selectable smoothing):**
```pine
AvgTrueRange() =>
    if atrSmooth == "EMA"
        ta.ema(ta.tr, atrLen)
    else if atrSmooth == "RMA"
        ta.rma(ta.tr, atrLen)
    else if atrSmooth == "SMA"
        ta.sma(ta.tr, atrLen)
    else
        ta.wma(ta.tr, atrLen)
```

**ATR type calculation:**
```pine
atrValue = if atrType == "Regular"
    AvgTrueRange()
else if atrType == "Percentage"
    (AvgTrueRange() / close) * 100
else if atrType == "Ticks"
    AvgTrueRange() / syminfo.mintick
else
    // Currency ATR with two decimals
    math.round(AvgTrueRange() * syminfo.pointvalue * posSize * 100) / 100
```

**Full ATR indicator (5-step pattern):**
```pine
//@version=5
indicator(title="Average True Range", shorttitle="ATR", overlay=false)

// ATR input options
atrType = input.string("Regular", title="ATR Type",
     options=["Regular", "Percentage", "Ticks", "Currency"])

atrLen    = input.int(14, title="ATR Length")
atrSmooth = input.string("RMA", title="Smoothing Type",
     options=["EMA", "RMA", "SMA", "WMA"])

posSize = input.int(1, title="Position Size (For Currency ATR)")

// To disable the ATR's moving average, set its length to 1
maLength = input.int(21, title="MA Length", minval=1)
colourMA = input.bool(true, title="Colour MA Line?")

highlight = input.bool(false, title="Highlight ATR Signals?")

// Step 2. Calculate indicator values
AvgTrueRange() =>
    if atrSmooth == "EMA"
        ta.ema(ta.tr, atrLen)
    else if atrSmooth == "RMA"
        ta.rma(ta.tr, atrLen)
    else if atrSmooth == "SMA"
        ta.sma(ta.tr, atrLen)
    else
        ta.wma(ta.tr, atrLen)

atrValue = if atrType == "Regular"
    AvgTrueRange()
else if atrType == "Percentage"
    (AvgTrueRange() / close) * 100
else if atrType == "Ticks"
    AvgTrueRange() / syminfo.mintick
else
    math.round(AvgTrueRange() * syminfo.pointvalue * posSize * 100) / 100

// Calculate ATR moving average, provided input length is > 1
atrMA  = maLength > 1 ? ta.ema(atrValue, maLength) : na

// Step 3. Determine indicator signals
risingMA  = atrMA > atrMA[1] and atrMA[1] > atrMA[2]
fallingMA = atrMA < atrMA[1] and atrMA[1] < atrMA[2]

atrCrossover  = ta.crossover(atrValue, atrMA)
atrCrossunder = ta.crossunder(atrValue, atrMA)

highAtr = atrValue > ta.highest(atrValue, 20)[1]
lowAtr  = atrValue < ta.lowest(atrValue, 20)[1]

// Step 4. Output indicator data
plot(atrValue, color=color.orange, title="ATR")

// Show ATR moving average
maColour = not colourMA ? color.teal :
     risingMA ? color.green :
     fallingMA ? color.red :
     color.teal

plot(atrMA, color=maColour, title="ATR EMA")

// Highlight ATR signals
bgColour = (atrCrossover or atrCrossunder) ? color.new(color.orange, 80) :
     highAtr ? color.new(color.red, 80) :
     lowAtr ? color.new(color.green, 80) :
     na

bgcolor(highlight ? bgColour : na)

// Step 5. Create indicator alerts
alertcondition(condition=risingMA,
     title="Rising ATR",
     message="The Average True Range's average increased 2 bars in a row")

alertcondition(condition=fallingMA,
     title="Declining ATR",
     message="The Average True Range's average decreased 2 bars in a row")

alertcondition(condition=atrCrossover,
     title="ATR Crossover",
     message="The Average True Range crossed above its EMA")

alertcondition(condition=atrCrossunder,
     title="ATR Crossunder",
     message="The Average True Range crossed under its EMA")

alertcondition(condition=highAtr,
     title="ATR New High",
     message="The Average True Range crossed its 20-bar high")

alertcondition(condition=lowAtr,
     title="ATR New Low",
     message="The Average True Range crossed its 20-bar low")
```

**Key patterns:**
- `ta.tr` — true range (single bar); `ta.atr(len)` = `ta.rma(ta.tr, len)` shorthand
- `ta.rma` is the default ATR smoothing (Wilder's MA) — matches TradingView's built-in ATR
- `syminfo.mintick` — convert ATR to ticks
- `syminfo.pointvalue` — convert ATR to currency (e.g., $12.50/tick for MES)
- `math.round(... * 100) / 100` — round to 2 decimal places
- `maLength > 1 ? ta.ema(atrValue, maLength) : na` — conditionally disable the MA line
- `risingMA = atrMA > atrMA[1] and atrMA[1] > atrMA[2]` — 2-bar rising check
- `highAtr = atrValue > ta.highest(atrValue, 20)[1]` — new 20-bar ATR high

---

## Crossover Crossunder

_Source: <https://www.tradingcode.net/tradingview/crossover-crossunder/>_

### Crossover & Crossunder in TradingView Pine

Three functions:
- `ta.crossover(a, b)` → true when a crossed ABOVE b (previous bar a ≤ b, current bar a > b)
- `ta.crossunder(a, b)` → true when a crossed BELOW b (previous bar a ≥ b, current bar a < b)
- `ta.cross(a, b)` → true when a crossed b in EITHER direction

Both accept: series vs series, or series vs fixed value.

**RSI crossing over its EMA (series vs series):**
```pine
//@version=5
indicator(title="Crossover example", overlay=false)

rsiValue = ta.rsi(close, 14)
rsiEMA   = ta.ema(rsiValue, 5)

bgcolor(ta.crossover(rsiValue, rsiEMA) ? color.new(color.fuchsia, 90) : na)

plot(rsiValue, color=color.orange)
plot(rsiEMA, color=color.teal, linewidth=2)

hline(30)
hline(70)
```

**RSI crossing over fixed level 50 (series vs value):**
```pine
//@version=5
indicator(title="Crossover example", overlay=false)

rsiValue = ta.rsi(close, 14)

bgcolor(ta.crossover(rsiValue, 50) ? color.new(color.purple, 80): na)

plot(rsiValue, color=color.teal)

hline(30)
hline(50, linestyle=hline.style_solid, color=color.new(color.gray, 60))
hline(70)
```

**Strategy entry on MA cross:**
```pine
if ta.crossover(quickMA, slowMA)
    strategy.entry("Long", strategy.long)

if ta.crossunder(quickMA, slowMA)
    strategy.entry("Short", strategy.short)
```

**Notes:**
- Returns true only on the exact bar of the cross, not while one is above the other
- Historical bars: based on confirmed OHLC; real-time bar: may repaint until bar closes
- `ta.cross(a, b)` is shorthand for `ta.crossover(a,b) or ta.crossunder(a,b)`


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
