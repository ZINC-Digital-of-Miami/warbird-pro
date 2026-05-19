---
name: tc-example-strategies
description: Copy-paste Pine v6 example strategies from tradingcode.net: SMA crossover, dual MA, triple MA, Bollinger breakout, Donchian trend, ATR channel breakout. Use when seeding a new strategy from a known archetype or comparing an indicator pattern against a working reference implementation.
---

# Worked Pine v6 example strategies (Kirk priority 2)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Sma Crossover Strategy

_Source: <https://www.tradingcode.net/tradingview/sma-crossover-strategy/>_

### SMA Crossover Strategy for TradingView Pine Script

**Strategy overview:**
- Two SMAs: fast (50-bar) crosses slow (100-bar)
- Long when fast SMA crosses over slow SMA
- Short when fast SMA crosses under slow SMA
- Stop loss: entry price ± 4× ATR(10)
- Position sizing: 2% equity risk per trade, max 10% exposure

**7-step template scaffold:**
```pine
//@version=5
// Step 1. Define strategy settings
// Step 2. Calculate strategy values
// Step 3. Output strategy data
// Step 4. Determine long trading conditions
// Step 5. Code short trading conditions
// Step 6. Submit entry orders
// Step 7. Submit exit orders
```

**Step 1 — strategy() + inputs:**
```pine
strategy(title="SMA Crossover", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

// SMA inputs
fastMALen = input.int(50, title="Fast SMA Length")
slowMALen = input.int(100, title="Slow SMA Length")

// Stop loss inputs
atrLen     = input.int(10, title="ATR Length")
stopOffset = input.float(4, title="Stop Offset Multiple", step=.25)

// Position sizing inputs
usePosSize  = input.bool(true, title="Use Position Sizing?")
maxRisk     = input.float(2, title="Max Position Risk %", step=.25)
maxExposure = input.float(10, title="Max Position Exposure %", step=1)
marginPerc  = input.int(10, title="Margin %")
```

**Step 2 — calculations:**
```pine
fastMA = ta.sma(close, fastMALen)
slowMA = ta.sma(close, slowMALen)
atrValue = ta.atr(atrLen)

// Trade window: stop 3 days before current time to flatten at backtest end
tradeWindow = time <= timenow - (86400000 * 3)

// Position sizing
riskEquity = (maxRisk * 0.01) * strategy.equity
riskTrade  = (atrValue * stopOffset) * syminfo.pointvalue

maxPos = ((maxExposure * 0.01) * strategy.equity) /
     ((marginPerc * 0.01) * (close * syminfo.pointvalue))

posSize = usePosSize ? math.min(math.floor(riskEquity / riskTrade), maxPos) : 1
```

**Steps 3–4 — trade conditions + stops:**
```pine
// Long
enterLong = ta.crossover(fastMA, slowMA) and tradeWindow
longStop = 0.0
longStop := enterLong ? close - (stopOffset * atrValue) : longStop[1]

// Short
enterShort = ta.crossunder(fastMA, slowMA) and tradeWindow
shortStop = 0.0
shortStop := enterShort ? close + (stopOffset * atrValue) : shortStop[1]
```

**Steps 5–7 — plot + orders:**
```pine
// Plot MAs
plot(fastMA, color=color.orange, title="Fast SMA")
plot(slowMA, color=color.teal, linewidth=2, title="Slow SMA")

// Plot stops only when in position
plot(strategy.position_size > 0 ? longStop : na, color=color.green,
     linewidth=2, style=plot.style_circles)
plot(strategy.position_size < 0 ? shortStop : na, color=color.red,
     linewidth=2, style=plot.style_circles)

// Entry orders
if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

// Exit orders (stop loss)
if strategy.position_size > 0
    strategy.exit("XL", from_entry="EL", stop=longStop)
if strategy.position_size < 0
    strategy.exit("XS", from_entry="ES", stop=shortStop)

// Flatten at backtest end
if not tradeWindow
    strategy.close_all()
```

**Full code:**
```pine
//@version=5
strategy(title="SMA Crossover", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

fastMALen = input.int(50, title="Fast SMA Length")
slowMALen = input.int(100, title="Slow SMA Length")
atrLen     = input.int(10, title="ATR Length")
stopOffset = input.float(4, title="Stop Offset Multiple", step=.25)
usePosSize  = input.bool(true, title="Use Position Sizing?")
maxRisk     = input.float(2, title="Max Position Risk %", step=.25)
maxExposure = input.float(10, title="Max Position Exposure %", step=1)
marginPerc  = input.int(10, title="Margin %")

fastMA = ta.sma(close, fastMALen)
slowMA = ta.sma(close, slowMALen)
atrValue = ta.atr(atrLen)
tradeWindow = time <= timenow - (86400000 * 3)

riskEquity = (maxRisk * 0.01) * strategy.equity
riskTrade  = (atrValue * stopOffset) * syminfo.pointvalue
maxPos = ((maxExposure * 0.01) * strategy.equity) /
     ((marginPerc * 0.01) * (close * syminfo.pointvalue))
posSize = usePosSize ? math.min(math.floor(riskEquity / riskTrade), maxPos) : 1

enterLong = ta.crossover(fastMA, slowMA) and tradeWindow
longStop = 0.0
longStop := enterLong ? close - (stopOffset * atrValue) : longStop[1]

enterShort = ta.crossunder(fastMA, slowMA) and tradeWindow
shortStop = 0.0
shortStop := enterShort ? close + (stopOffset * atrValue) : shortStop[1]

plot(fastMA, color=color.orange, title="Fast SMA")
plot(slowMA, color=color.teal, linewidth=2, title="Slow SMA")
plot(strategy.position_size > 0 ? longStop : na, color=color.green,
     linewidth=2, style=plot.style_circles)
plot(strategy.position_size < 0 ? shortStop : na, color=color.red,
     linewidth=2, style=plot.style_circles)

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if strategy.position_size > 0
    strategy.exit("XL", from_entry="EL", stop=longStop)
if strategy.position_size < 0
    strategy.exit("XS", from_entry="ES", stop=shortStop)

if not tradeWindow
    strategy.close_all()
```

**Key patterns:**
- `tradeWindow` pattern flattens strategy at backtest end (3-day buffer)
- Position sizing: `math.min(math.floor(riskEquity / riskTrade), maxPos)`
- `longStop[1]` keeps stop at entry-bar price until next signal
- `strategy.entry()` auto-reverses if opposite position is open
- `strategy.close_all()` at backtest end prevents open-trade distortion
- `syminfo.pointvalue` converts price to currency (ES=50, CL=1000, stocks=1)

---

## Dual Moving Average Strategy

_Source: <https://www.tradingcode.net/tradingview/dual-moving-average-strategy/>_

### Dual Moving Average Strategy for TradingView Pine Script

**Strategy overview:**
- Two SMAs: 100-bar (fast) and 350-bar (slow)
- Long when fast crosses over slow (MA crossover)
- Short when fast crosses under slow (MA crossunder)
- No explicit stop or take profit — holds until opposite crossover
- Position sizing: 0.5% equity / ATR(20)-in-currency
- Flattens at backtest end via `barstate.islastconfirmedhistory`

**Key feature — `bgcolor()` flash on crossover:**
```pine
bgColour = maCrossover  ? color.new(color.green, 90) :
           maCrossunder ? color.new(color.red, 90) :
           na
bgcolor(bgColour)   // flashes transparent green/red on crossover bars
```

**Full code:**
```pine
//@version=5
strategy(title="Dual Moving Average", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

fastMALen  = input.int(100, title="Fast MA Length")
slowMALen  = input.int(350, title="Slow MA Length")
usePosSize = input.bool(true, title="Use Position Sizing?")
riskPerc   = input.float(0.5, title="Risk %", step=0.25)

fastMA = ta.sma(close, fastMALen)
slowMA = ta.sma(close, slowMALen)

riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = ta.atr(20) * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1

maCrossover  = ta.crossover(fastMA, slowMA)
maCrossunder = ta.crossunder(fastMA, slowMA)

plot(fastMA, color=color.teal, linewidth=2, title="Fast MA")
plot(slowMA, color=color.orange, linewidth=2, title="Slow MA")

bgColour = maCrossover  ? color.new(color.green, 90) :
           maCrossunder ? color.new(color.red, 90) :
           na
bgcolor(bgColour)

enterLong  = maCrossover  and barstate.ishistory
enterShort = maCrossunder and barstate.ishistory

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if barstate.islastconfirmedhistory
    strategy.close_all()
```

**Key patterns:**
- Simplest crossover strategy — no stop, no take profit, just MA reversal
- `bgcolor()` with `color.new(color, 90)` = 90% transparent flash on signal bars
- `barstate.ishistory` in entry condition — prevents entries on live bar
- `barstate.islastconfirmedhistory` — closes all at end of backtest period
- `strategy.entry()` auto-reverses: long → short on crossunder, no explicit close needed
- Position sizing identical to Bollinger/ATR strategies: `floor(riskEquity / atrCurrency)`

---

## Triple Moving Average Strategy

_Source: <https://www.tradingcode.net/tradingview/triple-moving-average-strategy/>_

### Triple Moving Average Strategy for TradingView Pine Script

**Strategy overview (3 SMAs with trend alignment filter):**
- 3 SMAs: 150-bar (fast), 250-bar (medium), 350-bar (slow)
- Long: fast crosses over medium AND both fast+medium are above slow
- Exit long: fast crosses under medium
- Short: fast crosses under medium AND both fast+medium are below slow
- Exit short: fast crosses over medium
- `timestamp()` trade window instead of `timenow` offset

**Trading rules:**
- Long entry needs ALL 3 MAs aligned bullish: crossover + trend filter
- Short entry needs ALL 3 MAs aligned bearish: crossunder + trend filter
- Exits only need the fast/medium crossover (slow filter not required to exit)

**`timestamp()` pattern for fixed backtest end date:**
```pine
endMonth = input.int(9, title="End Month Backtest")
endYear  = input.int(2018, title="End Year Backtest")

tradeWindow = time <= timestamp(endYear, endMonth, 1, 0, 0)
// timestamp(year, month, day, hour, minute)
```

**Advanced `bgcolor()` — 4 different colors for 4 signal types:**
```pine
bgColour = if enterLong and strategy.position_size < 1
    color.new(color.green, 85)      // new long entry
else if enterShort and strategy.position_size > -1
    color.new(color.red, 85)        // new short entry
else if exitLong and strategy.position_size > 0
    color.new(color.navy, 85)       // closing long
else if exitShort and strategy.position_size < 0
    color.new(color.orange, 85)     // closing short

bgcolor(bgColour)
```

**Full code:**
```pine
//@version=5
strategy(title="Triple Moving Average", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

fastMALen = input.int(150, title="Fast MA Length")
medMALen  = input.int(250, title="Medium MA Length")
slowMALen = input.int(350, title="Slow MA Length")
endMonth  = input.int(9, title="End Month Backtest")
endYear   = input.int(2018, title="End Year Backtest")
usePosSize = input.bool(true, title="Use Position Sizing?")
riskPerc   = input.float(0.5, title="Risk %", step=0.25)

fastMA = ta.sma(close, fastMALen)
medMA  = ta.sma(close, medMALen)
slowMA = ta.sma(close, slowMALen)

riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = ta.atr(20) * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1

tradeWindow = time <= timestamp(endYear, endMonth, 1, 0, 0)

enterLong = ta.crossover(fastMA, medMA) and
     fastMA > slowMA and medMA > slowMA and tradeWindow
exitLong  = ta.crossunder(fastMA, medMA)

enterShort = ta.crossunder(fastMA, medMA) and
     fastMA < slowMA and medMA < slowMA and tradeWindow
exitShort  = ta.crossover(fastMA, medMA)

plot(fastMA, color=color.teal, title="Fast MA")
plot(medMA, color=color.orange, title="Medium MA")
plot(slowMA, color=color.navy, title="Slow MA", linewidth=2)

bgColour = if enterLong and strategy.position_size < 1
    color.new(color.green, 85)
else if enterShort and strategy.position_size > -1
    color.new(color.red, 85)
else if exitLong and strategy.position_size > 0
    color.new(color.navy, 85)
else if exitShort and strategy.position_size < 0
    color.new(color.orange, 85)
bgcolor(bgColour)

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")

if not tradeWindow
    strategy.close_all()
```

**Key patterns:**
- `timestamp(year, month, day, hour, minute)` — absolute date for trade window end
- `not tradeWindow` + `strategy.close_all()` — flatten at fixed end date
- Triple MA trend filter: `fastMA > slowMA and medMA > slowMA` — all aligned required
- `strategy.position_size < 1` in bgcolor check — prevents double-coloring when already long
- `bgcolor()` if/else chain — shows 4 distinct signal types with different colors

---

## Bollinger Breakout Strategy

_Source: <https://www.tradingcode.net/tradingview/bollinger-breakout-strategy/>_

### Bollinger Breakout Strategy for TradingView Pine Script

**Strategy overview (Faith, 2007 / LeBeau & Lucas, 1992):**
- 350-bar SMA ± 2.5 standard deviations = Bollinger bands
- Long when close crosses ABOVE upper band
- Exit long when close crosses BELOW SMA
- Short when close crosses BELOW lower band
- Exit short when close crosses ABOVE SMA
- No explicit stop-loss — SMA crossover is the exit
- Position sizing: 0.5% equity / ATR(20) in currency value

**Key calculations:**
```pine
smaValue  = ta.sma(close, smaLength)       // 350-bar SMA
stdDev    = ta.stdev(close, stdLength)     // 350-bar StdDev

upperBand = smaValue + (stdDev * ubOffset) // +2.5 SD
lowerBand = smaValue - (stdDev * lbOffset) // -2.5 SD

// Position sizing: 0.5% equity / ATR-in-dollars
riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = ta.atr(20) * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1
```

**Trade conditions:**
```pine
// Long
enterLong = ta.crossover(close, upperBand)   // close breaks above upper band
exitLong  = ta.crossunder(close, smaValue)   // close drops below SMA

// Short
enterShort = ta.crossunder(close, lowerBand) // close breaks below lower band
exitShort  = ta.crossover(close, smaValue)   // close rises above SMA
```

**Orders — uses strategy.close() not strategy.exit():**
```pine
if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")
```

**Full code:**
```pine
//@version=5
strategy(title="Bollinger Breakout", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

smaLength = input.int(350, title="SMA Length")
stdLength = input.int(350, title="StdDev Length")
ubOffset  = input.float(2.5, title="Upper Band Offset", step=0.5)
lbOffset  = input.float(2.5, title="Lower Band Offset", step=0.5)
usePosSize = input.bool(true, title="Use Position Sizing?")
riskPerc   = input.float(0.5, title="Risk %", step=0.25)

smaValue  = ta.sma(close, smaLength)
stdDev    = ta.stdev(close, stdLength)
upperBand = smaValue + (stdDev * ubOffset)
lowerBand = smaValue - (stdDev * lbOffset)

riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = ta.atr(20) * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1

plot(smaValue, title="SMA", color=color.teal)
plot(upperBand, title="UB", color=color.green, linewidth=2)
plot(lowerBand, title="LB", color=color.red, linewidth=2)

enterLong  = ta.crossover(close, upperBand)
exitLong   = ta.crossunder(close, smaValue)
enterShort = ta.crossunder(close, lowerBand)
exitShort  = ta.crossover(close, smaValue)

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")
```

**Key patterns:**
- `ta.stdev(close, length)` — standard deviation of closing prices
- `strategy.close("id")` exits by entry ID (no stop price needed)
- ATR position sizing: `math.floor(riskEquity / atrCurrency)` rounds to whole contracts
- Bands: SMA ± (stdDev × multiplier) — same formula as classic Bollinger Bands
- No stop-loss — implicit exit via SMA crossover

---

## Donchian Trend Strategy

_Source: <https://www.tradingcode.net/tradingview/donchian-trend-strategy/>_

### Donchian Trend Strategy for TradingView Pine Script

**Strategy overview (Faith, 2007 — Turtle Trading variant):**
- Entry: price breaks above/below 20-bar Donchian channel, filtered by EMA trend
- Exit: price breaks opposite 10-bar Donchian channel OR ATR stop hit
- Trend filter: 25-bar EMA above/below 350-bar EMA
- Stop: 2× ATR(20) from entry price
- Position sizing: 0.5% equity / ATR-in-currency

**Trading rules:**
- Long: close > highest high of prev 20 bars AND fast EMA > slow EMA
- Exit long: close < lowest low of prev 10 bars OR 2×ATR stop hit
- Short: close < lowest low of prev 20 bars AND fast EMA < slow EMA
- Exit short: close > highest high of prev 10 bars OR 2×ATR stop hit

**Key technique — `ta.highest/lowest` with `[1]` offset (previous bars only):**
```pine
highsEntry = ta.highest(high, hiLenEntry)[1]  // 20-bar high, excluding current bar
lowsEntry  = ta.lowest(low, loLenEntry)[1]    // 20-bar low, excluding current bar
highsExit  = ta.highest(high, hiLenExit)[1]   // 10-bar high
lowsExit   = ta.lowest(low, loLenExit)[1]     // 10-bar low
```

**`fixnan()` pattern — persist ATR stop from entry bar:**
```pine
// Only compute stop on entry bar (when flat), then hold it with fixnan
atrLongEntry = strategy.position_size == 0 ?
     close - (atrValue * stopOffset) :
     na
longStop = fixnan(atrLongEntry)   // holds last non-na value

atrShortEntry = strategy.position_size == 0 ?
     close + (atrValue * stopOffset) :
     na
shortStop = fixnan(atrShortEntry)
```

**Plot stop only when in position:**
```pine
stopPrice = if strategy.position_size > 0
    longStop
else if strategy.position_size < 0
    shortStop

plot(stopPrice, style=plot.style_linebr, title="ATR Stop",
     color=color.blue, linewidth=2)
```

**Trend filter + conditional channel plots:**
```pine
upTrend   = fastMA > slowMA
downTrend = fastMA < slowMA

// Only show entry levels when trend aligned
plot(upTrend ? highsEntry : na, style=plot.style_linebr, color=color.green, linewidth=2)
plot(downTrend ? lowsEntry : na, style=plot.style_linebr, color=color.red, linewidth=2)

// Color MA by trend direction
plot(fastMA, linewidth=2, color=upTrend ? color.green : color.red)
```

**Dual exit: channel break + ATR stop:**
```pine
// Channel break exits
if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")

// ATR hard stop exits (fires first if price gaps through channel)
if strategy.position_size > 0
    strategy.exit("XL", from_entry="EL", stop=longStop)
if strategy.position_size < 0
    strategy.exit("XS", from_entry="ES", stop=shortStop)

// Flatten at backtest end
if barstate.islastconfirmedhistory
    strategy.close_all()
```

**Full code:**
```pine
//@version=5
strategy(title="Donchian Trend", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

hiLenEntry = input.int(20, title="High Length (Entry)")
loLenEntry = input.int(20, title="Low Length (Entry)")
hiLenExit  = input.int(10, title="High Length (Exit)")
loLenExit  = input.int(10, title="Low Length (Exit)")
fastMALen  = input.int(25, title="Fast EMA Length")
slowMALen  = input.int(350, title="Slow EMA Length")
atrLen     = input.int(20, title="ATR Length")
stopOffset = input.float(2.0, title="Stop Offset", step=0.25)
usePosSize = input.bool(true, title="Use Position Sizing?")
riskPerc   = input.float(0.5, title="Risk %", step=0.25)

highsEntry = ta.highest(high, hiLenEntry)[1]
lowsEntry  = ta.lowest(low, loLenEntry)[1]
highsExit  = ta.highest(high, hiLenExit)[1]
lowsExit   = ta.lowest(low, loLenExit)[1]

fastMA = ta.ema(close, fastMALen)
slowMA = ta.ema(close, slowMALen)
atrValue = ta.atr(atrLen)

riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = atrValue * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1

atrLongEntry  = strategy.position_size == 0 ? close - (atrValue * stopOffset) : na
longStop      = fixnan(atrLongEntry)
atrShortEntry = strategy.position_size == 0 ? close + (atrValue * stopOffset) : na
shortStop     = fixnan(atrShortEntry)

upTrend   = fastMA > slowMA
downTrend = fastMA < slowMA

plot(upTrend ? highsEntry : na, style=plot.style_linebr,
     color=color.green, linewidth=2, title="Highs Entry")
plot(downTrend ? lowsEntry : na, style=plot.style_linebr,
     color=color.red, linewidth=2, title="Lows Entry")
plot(fastMA, linewidth=2, color=upTrend ? color.green : color.red, title="Fast MA")
plot(downTrend ? highsExit : na, style=plot.style_circles,
     title="Highs Exit", color=color.fuchsia, linewidth=3)
plot(upTrend ? lowsExit : na, style=plot.style_circles,
     title="Lows Exit", color=color.fuchsia, linewidth=3)

stopPrice = if strategy.position_size > 0
    longStop
else if strategy.position_size < 0
    shortStop
plot(stopPrice, style=plot.style_linebr, title="ATR Stop",
     color=color.blue, linewidth=2)

enterLong  = upTrend and close > highsEntry and barstate.ishistory
exitLong   = close < lowsExit
enterShort = downTrend and close < lowsEntry and barstate.ishistory
exitShort  = close > highsExit

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")

if strategy.position_size > 0
    strategy.exit("XL", from_entry="EL", stop=longStop)
if strategy.position_size < 0
    strategy.exit("XS", from_entry="ES", stop=shortStop)

if barstate.islastconfirmedhistory
    strategy.close_all()
```

**Key patterns:**
- `ta.highest(high, len)[1]` — previous N-bar high (excludes current bar, no lookahead)
- `fixnan(series)` — holds last non-na value; persists stop from entry bar through entire trade
- `strategy.position_size == 0` — true when flat; use to set entry-only values
- `barstate.islastconfirmedhistory` — fires on last fully closed historical bar
- `barstate.ishistory` in entry condition — avoids entries on live/realtime bar
- Dual exit: `strategy.close()` for channel break + `strategy.exit()` for hard stop
- `plot.style_linebr` — line that breaks when value is `na` (won't connect across gaps)

---

## Atr Channel Breakout Strategy

_Source: <https://www.tradingcode.net/tradingview/atr-channel-breakout/>_

### ATR Channel Breakout Strategy for TradingView Pine Script

**Strategy overview (Faith, 2007):**
- 350-bar SMA ± ATR(20) multiples = channels
- Long when close crosses ABOVE upper band (SMA + 7×ATR)
- Exit long when close crosses BELOW SMA
- Short when close crosses BELOW lower band (SMA - 3×ATR)
- Exit short when close crosses ABOVE SMA
- No explicit stop-loss — SMA crossover is implicit exit
- Position sizing: 0.5% equity / ATR-in-currency

**Key difference from Bollinger Breakout:** uses ATR multiples (volatility in price units) instead of standard deviations. Asymmetric bands — upper band farther from SMA than lower band.

**Calculations:**
```pine
smaValue  = ta.sma(close, smaLength)        // 350-bar SMA
atrValue  = ta.atr(atrLength)               // 20-bar ATR

upperBand = smaValue + (ubOffset * atrValue) // +7 ATR
lowerBand = smaValue - (lbOffset * atrValue) // -3 ATR

// Position sizing
riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = atrValue * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1
```

**Trade conditions:**
```pine
enterLong  = ta.crossover(close, upperBand)
exitLong   = ta.crossunder(close, smaValue)
enterShort = ta.crossunder(close, lowerBand)
exitShort  = ta.crossover(close, smaValue)
```

**Full code:**
```pine
//@version=5
strategy(title="ATR Channel Breakout", overlay=true,
     pyramiding=0, initial_capital=100000,
     commission_type=strategy.commission.cash_per_order,
     commission_value=4, slippage=2)

smaLength  = input.int(350, title="SMA Length")
atrLength  = input.int(20, title="ATR Length")
ubOffset   = input.float(7, title="Upperband Offset", step=0.50)
lbOffset   = input.float(3, title="Lowerband Offset", step=0.50)
usePosSize = input.bool(true, title="Use Position Sizing?")
riskPerc   = input.float(0.5, title="Risk %", step=0.25)

smaValue  = ta.sma(close, smaLength)
atrValue  = ta.atr(atrLength)
upperBand = smaValue + (ubOffset * atrValue)
lowerBand = smaValue - (lbOffset * atrValue)

riskEquity  = (riskPerc / 100) * strategy.equity
atrCurrency = atrValue * syminfo.pointvalue
posSize     = usePosSize ? math.floor(riskEquity / atrCurrency) : 1

plot(smaValue, title="SMA", color=color.orange)
plot(upperBand, title="UB", color=color.green, linewidth=2)
plot(lowerBand, title="LB", color=color.red, linewidth=2)

enterLong  = ta.crossover(close, upperBand)
exitLong   = ta.crossunder(close, smaValue)
enterShort = ta.crossunder(close, lowerBand)
exitShort  = ta.crossover(close, smaValue)

if enterLong
    strategy.entry("EL", strategy.long, qty=posSize)
if enterShort
    strategy.entry("ES", strategy.short, qty=posSize)

if exitLong
    strategy.close("EL")
if exitShort
    strategy.close("ES")
```

**Key patterns:**
- ATR channels: `sma ± (multiplier × atr)` — volatility-scaled bands
- Asymmetric offsets (7 up, 3 down) — intentional, tune to instrument
- `strategy.close("id")` closes by entry ID, market order at next bar open
- Same position sizing formula as Bollinger Breakout: `floor(riskEquity / atrCurrency)`


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
