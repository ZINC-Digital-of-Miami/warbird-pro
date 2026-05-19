---
name: tc-advanced-pine
description: Advanced Pine v6 flow control and data structures: if/switch/ternary conditionals, logical operators, the history-reference operator [], arrays (ordered mutable collections). Use when writing non-trivial Pine logic, refactoring conditionals, or managing rolling buffers and state.
---

# Advanced Pine v6 patterns (Kirk priority 3)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## If Statement

_Source: <https://www.tradingcode.net/tradingview/if-statement/>_

### If statement in TradingView Pine

**Syntax:**
```pine
[myVariable =] if condition
    // executes when condition is true (indent 4 spaces or 1 Tab)
```

- When condition is true → indented code runs
- When false → indented code is skipped
- Condition MUST evaluate to true/false (no non-Boolean like `if smaValue`)
- Indentation is critical — 4 spaces or 1 Tab determines what belongs to the if block

**Open trade on condition:**
```pine
if close > close[10]
    strategy.entry("Enter Long", strategy.long, qty=5)
```

**Increment counter:**
```pine
if close > close[1]
    higherCloses := higherCloses + 1
```

**Loop with if statement (volume-filtered average close):**
```pine
//@version=5
indicator(title="If statement example", overlay=true)

closeSum = 0.0
count    = 0

averageVolume = ta.sma(volume, 20)

for i = 0 to 9
    if volume[i] > averageVolume[i]
        closeSum := closeSum + close[i]
        count := count + 1

avgClose = closeSum / count

plot(avgClose, color=color.fuchsia, linewidth=2)
```

**Strategy orders with if statements (SMA crossover):**
```pine
//@version=5
strategy(title="If statement example strategy", overlay=true)

quickMA = ta.sma(close, 20)
slowMA  = ta.sma(close, 60)

plot(quickMA, color=color.blue)
plot(slowMA, color=color.orange, linewidth=2)

if ta.crossover(quickMA, slowMA)
    strategy.entry("Enter Long", strategy.long, qty=5)

if ta.crossunder(quickMA, slowMA)
    strategy.entry("Enter Short", strategy.short, qty=5)
```

---

## Switch Statement

_Source: <https://www.tradingcode.net/tradingview/switch-statement/>_

### Switch statement alternative in Pine Script

Pine Script has no switch statement. Use **cascaded if/else if** instead.

A cascaded if evaluates conditions in order — first true match runs, rest are skipped.

**Pattern:**
```pine
variable = if condition1
    value1
else if condition2
    value2
else if condition3
    value3
// no final else → variable gets na if nothing matches
```

**RSI-based background colour example:**
```pine
//@version=5
indicator(title="Switch statement alternative", overlay=false)

rsiValue = ta.rsi(close, 5)
plot(rsiValue, color=color.new(color.blue, 10), title="RSI")

bgColour = if rsiValue > 90
    color.green
else if rsiValue < 10
    color.red
else if rsiValue > 75
    color.blue
else if rsiValue < 25
    color.orange
else if rsiValue > 45 and rsiValue < 55
    color.yellow

bgcolor(color.new(bgColour, 80))
```

**Key notes:**
- No `else` at end → variable gets `na` when no condition matches
- First true condition wins — later conditions skipped even if also true
- Indent each value 4 spaces under its `if`/`else if`

---

## Conditional Operator

_Source: <https://www.tradingcode.net/tradingview/conditional-operator/>_

### Conditional ternary operator in TradingView Pine

Syntax: `condition ? result1 : result2`

- Returns `result1` when condition is true, `result2` otherwise
- Both results must be the same type (can't mix string + colour)
- Condition can be Boolean (`close > open`) or numeric (0/NaN/±Infinity = false, everything else = true)

**Basic variable assignment:**
```pine
barColour = close > open ? color.blue : color.red
```

**Background colour example:**
```pine
//@version=5
indicator(title="Conditional operator - example 1", overlay=true)

background = volume > volume[1] ? color.green : color.yellow

bgcolor(color.new(background, 85))
```

**Nested/chained conditionals (multi-condition chain):**
```pine
//@version=5
indicator(title="Conditional operator - example 2", overlay=true)

height = input.int(20, title="Arrow height")

arrowPlot =
     close > close[1] and close[1] > close[2] ? 1 :
     high > high[1] and high[1] > high[2] ? 1 :
     close < close[1] and close[1] < close[2] ? -1 :
     low < low[1] and low[1] < low[2] ? -1 :
     na

plotarrow(arrowPlot, colordown=color.red, colorup=color.lime,
     maxheight=height, minheight=height)
```

**Rules for chaining:**
- The very last argument is the default value when no condition is true
- Chain as many `? :` as needed — evaluated left to right
- Use `na` as fallback when nothing should plot

**Memory aid:** `?` = "is this true?", `:` = "choose between two options"

---

## Logical Operators

_Source: <https://www.tradingcode.net/tradingview/logical-operators/>_

### Logical operators in TradingView Pine

Three logical operators: `and`, `or`, `not`

| Operator | Returns true when... |
|----------|----------------------|
| `and` | both operands are true |
| `or` | at least one operand is true |
| `not` | its single operand is false (logical opposite) |

**EMA colour example using `and` + `or`:**
```pine
//@version=5
indicator(title="Logical operators - 1", overlay=true)

emaPeriod = timeframe.isdaily or timeframe.isweekly ? 30 : 50

emaValues = ta.ema(close, emaPeriod)

emaColour = close > emaValues and close[1] > emaValues[1] ? color.green :
     close < emaValues and close[1] < emaValues[1] ? color.red :
         color.blue

plot(emaValues, color=emaColour, linewidth=2)
```

**`not` operator — gap detection example:**
```pine
//@version=5
indicator(title="Logical operators - 2", overlay=true)

gapUp = low > high[1]
gapDown = high < low[1]

backgroundColour = gapUp ? color.green :
     gapDown ? color.red :
     na

bgcolor(color.new(backgroundColour, 60))

noGap = not(gapUp or gapDown)

plotshape(noGap, style=shape.xcross,
     location=location.abovebar)
```

**Key notes:**
- `not` flips true↔false: `not true` = false, `not false` = true
- Comparison operators produce true/false; logical operators combine them
- Can chain: `a and b and c` — ALL must be true for `and`; ANY for `or`

---

## History Operator

_Source: <https://www.tradingcode.net/tradingview/history-referencing-operator/>_

### Getting historical data with the history referencing operator

The history referencing operator `[]` returns previous bar values. Place it behind any variable or function with a positive integer to get that many bars back.

- `close[1]` → previous bar's close
- `open[3]` → open price 3 bars ago
- `ta.ema(close, 10)[1]` → previous bar value of 10-bar EMA
- `close[0]` and `close` are equivalent (current bar)

**Rules:**
- Cannot chain: `open[1][2]` is invalid — use `open[3]`
- Negative values like `high[-1]` are not allowed
- Only works on series (price data, indicators) — not `syminfo.ticker`
- Returns `na` when accessing beyond available bars

```pine
//@version=5
indicator(title="History referencing operator", overlay=true)
plot(close[5], linewidth=2)
```

```pine
//@version=5
indicator(title="History referencing operator - 1", overlay=false)

priceDiff = hl2 - hl2[10]
colour = priceDiff > priceDiff[1] ? color.orange : color.blue
plot(priceDiff, color=colour, style=plot.style_histogram, linewidth=3)
```

```pine
//@version=5
indicator(title="History referencing operator - 2", overlay=true)

highestHigh = ta.highest(high, 20)[1]
lowestLow   = ta.lowest(low[1], 20)

plot(highestHigh, color=color.green)
plot(lowestLow,   color=color.red)
```

Note: `ta.highest(high, 20)[1]` vs `ta.lowest(low[1], 20)` — both avoid including current bar but via different placements of `[]`.


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
