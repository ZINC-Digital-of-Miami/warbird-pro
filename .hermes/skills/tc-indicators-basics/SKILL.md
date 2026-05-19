---
name: tc-indicators-basics
description: Pine v6 indicator basics: input.* functions for user-configurable settings, strings, and time handling. Use when starting a new indicator and deciding which inputs to expose.
---

# Pine v6 inputs + primer (Kirk priority 11)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Pine Script Inputs

_Source: <https://www.tradingcode.net/tradingview/pine-script-inputs/>_

### Pine Script inputs overview

All input functions add user-configurable settings to the 'Inputs' tab of the script settings window.

| Function | Type | Use case |
|----------|------|----------|
| `input.int()` | Integer | Lengths, quantities, tick distances |
| `input.float()` | Decimal | Multipliers, percentages, ATR factors |
| `input.bool()` | Checkbox | Enable/disable features |
| `input.string()` | Text | Alert messages, labels, dropdown options |
| `input.color()` | Colour picker | Plot/drawing/background colours |
| `input.source()` | Price data dropdown | close/open/hl2/hlc3 etc. |
| `input.symbol()` | Instrument search | Load other symbol's data |
| `input.session()` | Time interval | Trading window start/end |
| `input.timeframe()` | Timeframe dropdown | Resolution for background data |
| `input.time()` | Date+time | Specific point in time |
| `input.price()` | Price value | Price levels, coordinates |

**Code examples:**
```pine
rsiLength    = input.int(9, title="RSI Length")
atrMultiplier = input.float(1.75, title="ATR Multiplier")
plotAverage  = input.bool(true, title="Plot Moving Average")
alertMsgText = input.string("New signal!", title="Alert Text")
plotColour   = input.color(color.teal, title="Plot Colour")
rsiData      = input.source(close, title="RSI Price Data")
otherSymbol  = input.symbol("NASDAQ:QQQ", title="Instrument Symbol")
tradeTimes   = input.session("0700-1300", title="Trading Times")
timeFrameTest = input.timeframe("240", title="Time Frame")
lineDate     = input.time(timestamp("1 Feb 2022 12:00"), title="Line Location")
plotPrice    = input.price(1.1500, title="Price Level")
```

**Common input.int() extras:**
```pine
// With min/max bounds and step
len = input.int(14, title="Length", minval=1, maxval=500)

// With group label
len = input.int(14, title="Length", group="Settings")

// Dropdown via options
maType = input.string("EMA", title="MA Type", options=["EMA","SMA","WMA"])
```


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
