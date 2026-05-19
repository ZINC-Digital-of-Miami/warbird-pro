---
name: tc-math
description: Pine v6 math helpers — how to round numbers, cast types, and keep floating-point precision under control. Small but load-bearing — rounding bugs silently break fill logic.
---

# Pine v6 math — rounding + numeric helpers (Kirk priority 9)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Rounding Numbers

_Source: <https://www.tradingcode.net/tradingview/rounding-numbers/>_

### Rounding numbers in TradingView Pine

Three functions:

| Function | Behaviour | Example |
|----------|-----------|---------|
| `math.round(x)` | Nearest integer, .5 rounds up | `math.round(4.5)` → 5, `math.round(-4.5)` → -4 |
| `math.floor(x)` | Always rounds down (toward −∞) | `math.floor(2.87)` → 2, `math.floor(-2.3)` → -3 |
| `math.ceil(x)` | Always rounds up (toward +∞) | `math.ceil(4.12)` → 5, `math.ceil(-7.75)` → -7 |

**Round SMA to full points:**
```pine
//@version=5
indicator(title="Round example", overlay=true)

roundSMA = math.round(ta.sma(close, 30))

plot(roundSMA, color=color.orange)
```

**Floor for position sizing (never over-size):**
```pine
//@version=5
indicator(title="Floor example", overlay=false)

posSize = math.floor(10000 / close)

plot(posSize, color=color.orange)
```

**Ceil volume to nearest 1,000:**
```pine
//@version=5
indicator(title="Ceil example", overlay=false)

volCeil = math.ceil(volume / 1000)

plot(volCeil, color=color.orange, style=plot.style_columns)
```

**Round to N decimal places:**
```pine
// Round to 1 decimal: multiply by 10, round, divide by 10
math.round(ta.sma(close, 30) * 10) / 10

// Round to pip (4 decimals): multiply by 10000, round, divide
math.round(close * 10000) / 10000
```

**Note:** These functions return a rounded copy — they do NOT modify the original variable.


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
