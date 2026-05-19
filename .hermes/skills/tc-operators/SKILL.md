---
name: tc-operators
description: Pine v6 operator reference — arithmetic, comparison, logical, and the conditional ternary. Includes operator precedence rules. Use when diagnosing a weird expression result or writing any non-trivial Boolean logic.
---

# Pine v6 operators (Kirk priority 10)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Full operators reference

_Source: <https://www.tradingcode.net/tradingview/order-operations-pine/>_

## The priority of operators in TradingView Pine

TradingView has several operators that we can use when programming scripts, including arithmetic operators, comparison operators, and the conditional ternary operator. But if one line of code has several operators, in what order are they calculated?

## TradingView operators and the operators' priority

An operator is a code element that performs a certain action on one or several values. Those values that an operator 'operates on' are what we call operands. And a piece of code that returns a value is called an expression — these often contain operators.

Operators evaluate in a certain order when an expression has several of them. Pine determines that order of calculations with the operators' priority. Those rules regulate which operator is evaluated first, which one calculates next, and so on until all operations in an expression have been performed.

## The priority of calculations in TradingView Pine

| Priority | Operator | Name | Example |
|----------|----------|------|---------|
| 10 | ( ) | parentheses; overrides operators' priority | ((34 - 3) + (8 - close[2])) / 5 |
| 9 | [ ] | history referencing operator | close[2], myVariable[9] |
| 8 | + | addition operator (unary); leaves operand unchanged | +ta.mom(close, 10) |
| 8 | - | subtraction operator (unary); returns operand's opposite | -ta.ema(high, 3) |
| 8 | not | logical not operator; returns logical opposite | not (high > high[1]) |
| 7 | * | multiplication operator | hl2 * 2 |
| 7 | / | division operator | low / high |
| 7 | % | modulus operator; returns remainder of integer division | 9 % 3 |
| 6 | + | addition operator (binary) | 10 + 6 |
| 6 | - | subtraction operator (binary) | high - low |
| 5 | > | greater than operator | high > high[1] |
| 5 | < | less than operator | 9 < 1 |
| 5 | >= | greater than or equal to operator | close <= ta.sma(close, 10) |
| 5 | <= | less than or equal to operator | high <= high[5] |
| 4 | == | equality operator | high == ta.highest(high, 20) |
| 4 | != | unequal to operator | close != close[4] |
| 3 | and | logical and operator | newHigh and volumeIncrease |
| 2 | or | logical or operator | enterLong or stopTriggered |
| 1 | ?: | conditional ternary operator | highestHigh == true ? 200 : 3 |

Operators with the same priority are calculated left to right.

## Change operator priority with parentheses

Parentheses have the highest priority (10) — use them to override evaluation order.

```pine
//@version=5
indicator(title="Bar midpoint", overlay=true)

// WRONG: division happens before addition due to priority
plot(high + low / 2, color=color.blue, linewidth=2)
```

```pine
//@version=5
indicator(title="Bar midpoint", overlay=true)

// CORRECT: parentheses force addition first
plot((high + low) / 2, color=color.blue, linewidth=2)
```

## Nesting parentheses in TradingView Pine

TradingView evaluates innermost parentheses first (inside out).

```pine
x = (7 % 3) * (4 + (6 / 2))
// Step 1: 6 / 2 = 3  → (7 % 3) * (4 + 3)
// Step 2: 7 % 3 = 1, 4 + 3 = 7  → 1 * 7
// Result: x = 7
```

---

_Source: <https://www.tradingcode.net/tradingview/history-referencing-operator/>_

## Getting historical data with the history referencing operator

The history referencing operator (`[]`) with a positive integer between its square brackets returns previous bar values. For example, `close[1]` returns the closing price of the previous bar; `open[3]` returns the open price from 3 bars ago.

## Key rules for the history referencing operator

- Cannot be applied to the same operand repeatedly: `open[1][2]` is invalid; use `open[3]` instead.
- Only positive values allowed; `high[-1]` is not permitted.
- Only works with series data — not hard-coded values or non-historical variables like `syminfo.ticker`.
- Returns `NaN` when accessing bars beyond the chart history.
- `close[0]` and `close` are equivalent (current bar).

## Context-dependence

The script executes bar by bar (oldest to newest), so `close[1]` always means "1 bar before the current calculation bar."

## Values returned

`close[5]` returns a series — the closing price of 5 bars ago on every bar. This means it can be used as an argument to functions:

```pine
ta.ema(close[5], 20)  // 20-period EMA calculated on prices from 5 bars ago
```

## Example: variable history

```pine
//@version=5
indicator(title="History referencing operator - 1", overlay=false)

priceDiff = hl2 - hl2[10]

colour = priceDiff > priceDiff[1] ? color.orange : color.blue

plot(priceDiff, color=colour, style=plot.style_histogram,
     linewidth=3)
```

## Example: function history

```pine
//@version=5
indicator(title="History referencing operator - 2", overlay=true)

highestHigh = ta.highest(high, 20)[1]    // [] after function
lowestLow = ta.lowest(low[1], 20)        // [] inside function argument

plot(highestHigh, color=color.green)
plot(lowestLow, color=color.red)
```

Both forms work: `ta.highest(high, 20)[1]` and `ta.lowest(low[1], 20)`. The `[1]` offset excludes the current bar from the lookback, preventing the current bar's value from always being the extreme.

---

_Source: <https://www.tradingcode.net/tradingview/conditional-operator/>_
<!-- NOTE: Page was blocked by Cloudflare rate limit during fetch session -->

## Conditional (ternary) operator ?:

The conditional ternary operator `?:` evaluates a condition and returns one of two values:

```pine
condition ? value_if_true : value_if_false
```

**Priority**: 1 (lowest of all operators — evaluated last).

```pine
//@version=5
indicator("Ternary example", overlay=true)

barColour = close > open ? color.green : color.red
bgcolor(barColour)
```

Ternary operators can be nested:

```pine
result = condition1 ? val1 : condition2 ? val2 : val3
```

---

_Source: <https://www.tradingcode.net/tradingview/comparison-operators/>_
<!-- NOTE: Page was blocked by Cloudflare rate limit during fetch session -->

## Comparison operators

Pine Script comparison operators return `true` or `false`:

| Operator | Meaning |
|----------|---------|
| `>` | greater than |
| `<` | less than |
| `>=` | greater than or equal to |
| `<=` | less than or equal to |
| `==` | equal to |
| `!=` | not equal to |

```pine
//@version=5
indicator("Comparison example")

isUp = close > open          // true when close above open
isNew52wHigh = high >= ta.highest(high, 252)[1]

plot(isUp ? 1 : 0)
```

Comparing series values produces a bool series. Use `==` for equality, not `=` (which is assignment).

---

_Source: <https://www.tradingcode.net/tradingview/logical-operators/>_
<!-- NOTE: Page was blocked by Cloudflare rate limit during fetch session -->

## Logical operators

Three logical operators: `and`, `or`, `not`.

| Operator | Priority | Description |
|----------|----------|-------------|
| `not` | 8 | Unary; inverts true/false |
| `and` | 3 | True only if both operands true |
| `or` | 2 | True if at least one operand true |

```pine
//@version=5
indicator("Logical operators example")

bullSignal = close > open and volume > volume[1]
bearSignal = close < open or close < ta.sma(close, 20)
notBull = not bullSignal

plotshape(bullSignal, style=shape.triangleup, color=color.green)
plotshape(bearSignal, style=shape.triangledown, color=color.red)
```

`and` has higher priority than `or`, so `a and b or c` evaluates as `(a and b) or c`. Use parentheses to clarify complex conditions.

---

_Source: <https://www.tradingcode.net/tradingview/modulus-operator/>_

## Modulus operator %

The `%` operator returns the remainder of integer division (priority 7, same as `*` and `/`).

```pine
//@version=5
indicator("Modulus example")

// True on every 20th bar
everyTwentieth = bar_index % 20 == 0

// Alternate between two values
alternate = bar_index % 2 == 0 ? color.blue : color.red
bgcolor(alternate)
```

Common use: detect periodicity, create alternating conditions, check even/odd bar counts.

---

_Source: <https://www.tradingcode.net/tradingview/if-statement/>_

## if statement

Pine `if` executes a block of code conditionally. The indented block runs only when the condition is `true`.

```pine
//@version=5
indicator("if example", overlay=true)

var label lbl = na

if high > ta.highest(high, 20)[1]
    lbl := label.new(bar_index, high, "New high", color=color.green)
```

## if-else

```pine
if close > open
    barDir = 1
else
    barDir = -1
```

## if-else if-else chain

```pine
if close > ta.sma(close, 50)
    trend = "up"
else if close < ta.sma(close, 50)
    trend = "down"
else
    trend = "flat"
```

## if as expression (returns a value)

```pine
//@version=5
indicator("if expression")

val = if close > open
    close - open
else
    0.0

plot(val)
```

The last expression in each branch is the returned value. Both branches must return compatible types.

---

_Source: <https://www.tradingcode.net/tradingview/switch-statement/>_

## switch statement

`switch` matches an expression against multiple values. Cleaner than long `if/else if` chains.

```pine
//@version=5
indicator("switch example")

dayOfWeek = dayofweek(time)

dayName = switch dayOfWeek
    dayofweek.monday    => "Monday"
    dayofweek.tuesday   => "Tuesday"
    dayofweek.wednesday => "Wednesday"
    dayofweek.thursday  => "Thursday"
    dayofweek.friday    => "Friday"
    => "Weekend"
```

The last `=>` (no value before it) is the default case — matches anything not listed above.

## switch with no expression (boolean matching)

```pine
direction = switch
    close > open  => "bull"
    close < open  => "bear"
    => "doji"
```

Each branch condition is evaluated top to bottom; first `true` wins.

---

_Source: <https://www.tradingcode.net/tradingview/ways-to-round/>_

## Rounding in Pine Script

Four rounding functions:

| Function | Description |
|----------|-------------|
| `math.round(x)` | Round to nearest integer (0.5 rounds up) |
| `math.round(x, precision)` | Round to N decimal places |
| `math.floor(x)` | Round down (toward negative infinity) |
| `math.ceil(x)` | Round up (toward positive infinity) |
| `int(x)` | Truncate toward zero (cast to int) |

```pine
//@version=5
indicator("Rounding examples")

x = 3.7

r1 = math.round(x)         // 4
r2 = math.round(x, 1)      // 3.7
r3 = math.floor(x)         // 3
r4 = math.ceil(x)          // 4
r5 = int(x)                // 3  (truncates, not rounds)

plot(r1)
```

Use `math.round(price / tick) * tick` to snap prices to tick increments.

---

_Source: <https://www.tradingcode.net/tradingview/math-minimum-value/>_

## math.min() and math.max()

```pine
math.min(val1, val2, ...)   // returns the smallest value
math.max(val1, val2, ...)   // returns the largest value
```

Both accept 1–n arguments. When given series, they operate element-wise per bar.

```pine
//@version=5
indicator("min/max example")

// Clamp ATR-based stop to a range
atr = ta.atr(14)
stopDist = math.max(math.min(atr * 2, 20.0), 5.0)  // clamp between 5 and 20

plot(stopDist)
```

```pine
// Lowest of three MAs
ema20  = ta.ema(close, 20)
ema50  = ta.ema(close, 50)
ema200 = ta.ema(close, 200)
lowestMA = math.min(ema20, ema50, ema200)
```


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
