---
name: tc-alerts
description: Pine v6 alert mechanisms: alertcondition() for UI-configured boolean alerts and alert() for dynamic runtime messages. Covers webhook-ready JSON payloads, freq control (bar close vs tick), and the create/configure flow inside TradingView. Use when wiring indicators or strategies to TV alerts or external webhook receivers.
---

# Pine v6 alerts and webhooks (Kirk priority 4)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Alertcondition

_Source: <https://www.tradingcode.net/tradingview/program-alerts/>_

### alertcondition() — Program Alerts in TradingView Pine Script

**Syntax:**
```pine
alertcondition(condition, title, message)
```
- `condition` — true/false expression; when true the alert CAN fire
- `title` — name shown in the Create Alert window (constant string)
- `message` — default alert message text (constant string — NO dynamic values)

**Important rules:**
- `alertcondition()` does NOT fire alerts by itself — it only creates the alert option
- Must still manually enable + configure the alert in the Create Alert window
- Does NOT work in `strategy()` scripts — use `alert()` for strategies
- Message must be a literal string — dynamic values (e.g., `str.tostring(close)`) will error
- Script must also have at least one output function (`plot()`, `bgcolor()`, etc.)

**Simple single alert:**
```pine
//@version=5
indicator(title="Volume alert example", overlay=false)

emaLength = input.int(20, title="EMA Length")
volEMA    = ta.ema(volume, emaLength)

alertcondition(condition=volume > volEMA,
     message="Volume is higher than its EMA")

plot(volume, style=plot.style_histogram, color=color.teal, linewidth=3)
plot(volEMA, style=plot.style_line, color=color.orange)
```

**Multiple alert conditions in same script:**
```pine
//@version=5
indicator(title="Highs and lows - alert example", overlay=true)

highLen = input.int(20, title="Highs Length")
lowLen  = input.int(20, title="Lows Length")

highs = ta.highest(high, highLen)[1]
lows  = ta.lowest(low, lowLen)[1]

// Two separate alert conditions — each gets its own entry in Create Alert window
alertcondition(condition=ta.crossover(close, highs),
     title="High breakout",
     message="Closing price crossed highest high")

alertcondition(condition=ta.crossunder(close, lows),
     title="Low breakout",
     message="Closing price crossed lowest low")

plot(highs, color=color.green, linewidth=2)
plot(lows,  color=color.red,   linewidth=2)
```

**Dynamic alert messages → use `alert()` instead:**
```pine
// alertcondition() won't work for dynamic messages:
// alertcondition(condition=open > close, message="Close at " + str.tostring(close))  // ERROR

// Use alert() for dynamic messages in strategies or indicators:
if open > close
    alert("Close at " + str.tostring(close), alert.freq_once_per_bar)
```

**Visualize when alert fires (since alertcondition has no visual output):**
```pine
// Add bgcolor or plotshape to verify alert logic visually
alertSignal = volume > ta.ema(volume, 20)
alertcondition(alertSignal, title="Volume spike")
bgcolor(alertSignal ? color.new(color.orange, 85) : na)  // visual confirmation
```

**Notes:**
- Multiple `alertcondition()` calls = multiple selectable alerts in Create Alert window
- Existing configured alerts do NOT update when script code changes — must delete + recreate
- `alert.freq_once_per_bar` / `alert.freq_once_per_bar_close` / `alert.freq_all` — frequency options for `alert()`
- `ta.highest(high, len)[1]` — previous N-bar high (excludes current bar)


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
