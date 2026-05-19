---
name: tc-strategies-backtesting
description: Pine Script v6 strategy entry/exit order functions, backtest date-range control, risk primitives (stop, trailing stop, percentage stop), daily-loss limits, losing-streak stops, and the strategy.* performance variables used to read back P&L inside the script. Use when writing any strategy(), tuning backtest behavior, wiring stops, or diagnosing why a backtest report differs from live.
---

# Pine v6 strategy() + backtesting (Kirk priority 1)

Sourced verbatim from tradingcode.net Pine Script course. Raw per-topic originals live under `.claude/skills/_tc_raw/`.

## Entry Orders Overview

_Source: <https://www.tradingcode.net/tradingview/entry-orders-overview/>_

### Pine Script entry orders with strategy.entry()

All entry orders use `strategy.entry(id, direction, ...)`. Always wrap in `if` statement to control when orders fire.

**Required args:** `id` (string name), `direction` (`strategy.long` or `strategy.short`)

---

**Market order (fills immediately at market):**
```pine
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long)

if ta.crossunder(close, ta.ema(close, 20))
    strategy.entry("Enter Short", strategy.short)
```

**Limit order (fills at limit price or better):**
```pine
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long, limit=low)

if ta.crossunder(close, ta.ema(close, 20))
    strategy.entry("Enter Short", strategy.short, limit=high)
```

**Stop order (triggers when price hits stop, fills at market):**
```pine
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long, stop=high + 10 * syminfo.mintick)

if ta.crossunder(close, ta.ema(close, 20))
    strategy.entry("Enter Short", strategy.short, stop=low - 10 * syminfo.mintick)
```

**Stop-limit order (triggers at stop price, fills at limit price or better):**
```pine
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long, stop=high[1], limit=close)

if ta.crossunder(close, ta.ema(close, 20))
    strategy.entry("Enter Short", strategy.short, stop=low[1], limit=close)
```

**Notes:**
- Limit/stop/stop-limit orders remain active until filled — cancel with `strategy.cancel(id)` or `strategy.cancel_all()`
- `strategy.long` = buy/long, `strategy.short` = sell/short
- Optional `qty=` arg to set position size

---

## Strategy Entry

_Source: <https://www.tradingcode.net/tradingview/strategy-entry-function/>_

### strategy.entry() — Open Trades in Pine Script

**Full signature:**
```pine
strategy.entry(id, direction, qty, limit, stop, oca_name, oca_type,
     comment, when, alert_message)
```

**Arguments:**
- `id` — required string; the entry order's name
- `direction` — `strategy.long` or `strategy.short`
- `qty` — number of contracts/shares. Omit = use strategy default order size
- `limit` — price for limit order entry
- `stop` — price for stop order entry. Both `stop` + `limit` = stop-limit order
- `oca_name` — OCA group name (one-cancels-all group)
- `oca_type` — `strategy.oca.cancel`, `strategy.oca.reduce`, `strategy.oca.none`
- `comment` — text label shown on the trade in the strategy tester
- `when` — boolean condition; submit only when true
- `alert_message` — dynamic string for alert message (supports `str.tostring()`)

**Market order — long and short:**
```pine
// Long market order
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long)

// Short market order
if ta.crossunder(close, ta.ema(close, 20))
    strategy.entry("Enter Short", strategy.short)

// With qty
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long, qty=10)
```

**Stop order entry:**
```pine
// Long stop — triggers when price rises 10 ticks above recent high
if close > ta.highest(high, 20)[1]
    strategy.entry("Enter Long", strategy.long, stop=high +
         10 * syminfo.mintick)

// Short stop — triggers below recent low
if close < ta.lowest(low, 20)[1]
    strategy.entry("Enter Short", strategy.short, stop=low -
         10 * syminfo.mintick)
```

**Limit order entry:**
```pine
// Long limit — enter just below breakout high
if high > ta.highest(high, 10)[1]
    strategy.entry("Enter Long", strategy.long, limit=high -
         15 * syminfo.mintick)

// Short limit — enter just above breakdown low
if low < ta.lowest(low, 10)[1]
    strategy.entry("Enter Short", strategy.short, limit=low +
         15 * syminfo.mintick)
```

**Stop-limit order (both stop AND limit set):**
```pine
// Long: activates 20 ticks above high, fills at limit 50 ticks below close
if ta.crossover(close, ta.sma(close, 20))
    strategy.entry("Enter Long", strategy.long, qty=50,
         stop=high + 20 * syminfo.mintick,
         limit=close - 50 * syminfo.mintick)

// Short: activates 20 ticks below low, fills at limit 50 ticks above close
if ta.crossunder(close, ta.sma(close, 20))
    strategy.entry("Enter Short", strategy.short, qty=75,
         stop=low - 20 * syminfo.mintick,
         limit=close + 50 * syminfo.mintick)
```

**OCA group (one-cancels-all):**
```pine
// When one fills, cancel the others in the group
strategy.entry("Enter Long", strategy.long, qty=50,
     stop=high + 10 * syminfo.mintick,
     oca_type=strategy.oca.cancel, oca_name="long-entries")

// oca.reduce — reduce qty when one in group fills
strategy.entry("Enter Long", strategy.long, qty=5,
     limit=high - 15 * syminfo.mintick,
     oca_type=strategy.oca.reduce, oca_name="longs-1")
```

**`when` argument — inline condition:**
```pine
// Equivalent to wrapping in if block
strategy.entry("Enter Long", strategy.long, when=ta.crossunder(low,
     ta.ema(hl2, 30)))
```

**Alert message with dynamic values:**
```pine
strategy.entry("Enter Long", strategy.long, qty=50,
     stop=high + 10 * syminfo.mintick,
     alert_message="Long 50 contracts with stop @ " +
         str.tostring(high + 10 * syminfo.mintick))
```

**Key patterns:**
- `strategy.long` / `strategy.short` — direction constants
- `syminfo.mintick` — one tick; use for precise stop/limit offsets
- Omit `qty` to use the strategy's configured default order size
- `stop` only = stop order; `limit` only = limit order; both = stop-limit
- `oca_type=strategy.oca.cancel` — first fill cancels all others in `oca_name` group
- `when=` inline is equivalent to an `if` block — preference only
- `alert_message` supports dynamic `str.tostring()` — unlike `alertcondition()` message
- `comment=` text appears on the strategy tester trade list

---

## Strategy Exit

_Source: <https://www.tradingcode.net/tradingview/strategy-exit-function/>_

### strategy.exit() — Close Trades in Pine Script

**Full signature:**
```pine
strategy.exit(id, from_entry, qty, qty_percent, profit, limit,
    loss, stop, trail_price, trail_points, trail_offset,
    oca_name, comment, comment_profit, comment_loss, comment_trailing,
    when, alert_message, alert_profit, alert_loss, alert_trailing)
```

**Standard arguments:**
- `id` — required string; the exit order's name
- `from_entry` — string; which entry order to exit from. Omit to exit ALL open orders
- `qty` — number of contracts to close. Omit / `na` = close 100%
- `qty_percent` — percentage (0-100) of open order to close. Takes priority over `qty`

**Order arguments (choose one or combine):**
- `profit` — ticks of profit for take-profit limit order
- `limit` — exact price for take-profit limit order
- `loss` — ticks of loss for stop-loss order
- `stop` — exact price for stop-loss order
- `trail_price` — price at which trailing stop activates
- `trail_points` — ticks of profit before trailing stop activates (0 = immediate)
- `trail_offset` — ticks the trailing stop follows behind the best price

**`when` argument — conditional execution:**
```pine
// Move stop to break-even when 100 currency open profit
strategy.exit("Exit Long", from_entry="Enter Long",
    stop=strategy.position_avg_price, when=strategy.openprofit > 100)
```

**Limit (take profit) examples:**
```pine
// Profit target 200 ticks from entry
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", profit=200)

// Exact price limit — 10% below low for short
if ta.crossunder(close, ta.sma(close, 30))
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", limit=low * 0.90)

// Partial exit — close 50% at profit target
if ta.crossunder(close, ta.sma(close, 30))
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", limit=low * 0.90,
         qty_percent=50)
```

**Stop-loss examples:**
```pine
// Stop 300 ticks from entry
if high > ta.highest(high, 20)[1]
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", loss=300)

// Exact stop price — 8% above high for short
if low < ta.lowest(low, 20)[1]
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", stop=high * 1.08)
```

**Trailing stop examples:**
```pine
// trail_points: activates after 5 ticks profit, follows with 20 ticks
if ta.crossover(ta.rsi(close, 7), 30)
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", trail_points=5,
         trail_offset=20)

// trail_price: activates at signal bar's low, trails with 25 ticks
if ta.crossunder(ta.rsi(close, 7), 70)
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", trail_price=low,
         trail_offset=25)

// trail_points=0: immediate trailing stop from first tick
if ta.crossover(ta.rsi(close, 5), 70)
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", trail_points=0,
         trail_offset=30)
```

**Two exit orders from same entry (scale out):**
```pine
// Close 50% at 100 ticks, rest at 200 ticks
if ta.crossover(close, ta.ema(close, 20))
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long 1", from_entry="Enter Long", profit=10, qty_percent=50)
    strategy.exit("Exit Long 2", from_entry="Enter Long", profit=20)
```

**Combined stop + limit + comment:**
```pine
if ta.crossover(close, ta.wma(close, 25))
    strategy.exit("Exit Long", qty=5, profit=200, loss=120,
         comment="Partial long exit of 5 contracts")
```

**Alert message with dynamic values:**
```pine
strategy.exit("Exit Short", from_entry="Enter Short", limit=low * 0.90,
     qty_percent=50, alert_message="Hit profit target at " +
     str.tostring(low * 0.90))
```

**Key patterns:**
- `from_entry=` — links exit to specific entry ID; omit to exit all open positions
- `profit` / `loss` are in **ticks** (not price); `limit` / `stop` are in **price**
- `qty_percent` takes priority over `qty` when both set
- `trail_points=0` — trailing stop activates immediately from entry, no profit threshold
- `trail_price` — useful for short: set to `low` of signal bar to activate once price drops
- Call `strategy.exit()` every bar while in position — TV updates the order each bar
- Two `strategy.exit()` calls with same `from_entry` = scale out (different exit IDs required)
- `when=` parameter — conditionally submit the exit (e.g., only after X profit)

---

## Strategy Close

_Source: <https://www.tradingcode.net/tradingview/strategy-close-function/>_

### strategy.close() — Market Exit Orders in Pine Script

**Signature:**
```pine
strategy.close(id, when, comment, qty, qty_percent, alert_message)
```

**Arguments:**
- `id` — string matching the entry order ID to close
- `when` — boolean; only close when true (inline alternative to `if` block)
- `comment` — text shown on the trade in strategy tester
- `qty` — fixed number of contracts to close
- `qty_percent` — percentage (0–100) of the entry to close
- `alert_message` — dynamic message string (supports `str.tostring()`)

**Basic close — exit entire position:**
```pine
// Exit long on crossunder of 20-bar SMA
if ta.crossunder(close, ta.sma(close, 20))
    strategy.close("Enter Long")

// Exit short on crossover
if ta.crossover(close, ta.sma(close, 20))
    strategy.close("Enter Short")
```

**With comment:**
```pine
if ta.crossunder(close, ta.sma(close, 20))
    strategy.close("Enter Long", comment="Exit Long")
```

**Partial close — fixed qty:**
```pine
// Exit 3 contracts from the long
if ta.crossunder(close, ta.sma(close, 20))
    strategy.close("Enter Long", qty=3)
```

**Partial close — percentage:**
```pine
// Close 50% of the short
if ta.crossover(close, ta.ema(close, 20))
    strategy.close("Enter Short", qty_percent=50)
```

**Close multiple entries in one `if` block:**
```pine
if ta.crossunder(close, ta.ema(close, 12))
    strategy.close("Enter Long #1")
    strategy.close("Enter Long #2")

// Close three shorts at different percentages
if ta.crossover(close, ta.wma(close, 45))
    strategy.close("Enter Short #1")
    strategy.close("Enter Short #2", qty_percent=50)
    strategy.close("Enter Short #3", qty_percent=20)
```

**`when` inline condition:**
```pine
// Equivalent: close when condition is true
strategy.close("Enter Long", when=close < ta.wma(close, 20))
```

**With alert message:**
```pine
if ta.crossover(close, ta.ema(close, 20))
    strategy.close("Enter Short", qty_percent=50,
         alert_message="Closed half (50%) of 'Enter Short' entry")
```

**Key patterns:**
- `id` must match the `id` used in the corresponding `strategy.entry()` call
- Omit `qty` and `qty_percent` to close 100% of the entry
- `qty_percent=50` closes half; re-call on next signal to close the rest
- Multiple `strategy.close()` calls in one bar = close multiple pyramided entries
- `strategy.close()` submits a **market** order — for limit/stop exits use `strategy.exit()`
- `strategy.close_all()` = close all open positions regardless of entry ID
- `when=` inline is equivalent to wrapping in `if` — same result, different style

---

## Backtest Date Range

_Source: <https://www.tradingcode.net/tradingview/backtest-between-dates/>_

### Backtest Between Dates in Pine Script — 4-Step Pattern

**Step 1 — Date range inputs:**
```pine
useDateFilter = input.bool(true, title="Filter Date Range of Backtest",
     group="Backtest Time Period")
backtestStartDate = input.time(timestamp("1 Jan 2021"),
     title="Start Date", group="Backtest Time Period",
     tooltip="This start date is in the time zone of the exchange " +
     "where the chart's instrument trades. It doesn't use the time " +
     "zone of the chart or of your computer.")
backtestEndDate = input.time(timestamp("1 Jan 2022"),
     title="End Date", group="Backtest Time Period",
     tooltip="This end date is in the time zone of the exchange " +
     "where the chart's instrument trades. It doesn't use the time " +
     "zone of the chart or of your computer.")
```

**Step 2 — Boolean window check:**
```pine
inTradeWindow = not useDateFilter or (time >= backtestStartDate and
     time < backtestEndDate)
```

**Step 3 — Gate entries with `inTradeWindow`:**
```pine
if inTradeWindow and high > highestHigh
    strategy.entry("Enter Long", strategy.long)

if inTradeWindow and low < lowestLow
    strategy.entry("Enter Short", strategy.short)
```

**Step 4 — Close + cancel when window ends:**
```pine
if not inTradeWindow and inTradeWindow[1]
    strategy.cancel_all()
    strategy.close_all(comment="Date Range Exit")
```

**Full strategy:**
```pine
//@version=5
strategy(title="Backtest specific date range", overlay=true)

useDateFilter = input.bool(true, title="Filter Date Range of Backtest",
     group="Backtest Time Period")
backtestStartDate = input.time(timestamp("1 Jan 2021"),
     title="Start Date", group="Backtest Time Period")
backtestEndDate = input.time(timestamp("1 Jan 2022"),
     title="End Date", group="Backtest Time Period")

inTradeWindow = not useDateFilter or (time >= backtestStartDate and
     time < backtestEndDate)

highestHigh = ta.highest(high, 20)[1]
lowestLow   = ta.lowest(low, 20)[1]
midPoint    = (highestHigh + lowestLow) / 2

plot(highestHigh, color=color.green, title="Highest High")
plot(lowestLow, color=color.red, title="Lowest Low")
plot(midPoint, color=color.blue, title="Middle Line")

if inTradeWindow and high > highestHigh
    strategy.entry("Enter Long", strategy.long)

if inTradeWindow and low < lowestLow
    strategy.entry("Enter Short", strategy.short)

if ta.crossunder(close, midPoint)
    strategy.close("Enter Long", comment="Exit Long")

if ta.crossover(close, midPoint)
    strategy.close("Enter Short", comment="Exit Short")

if not inTradeWindow and inTradeWindow[1]
    strategy.cancel_all()
    strategy.close_all(comment="Date Range Exit")
```

**Key patterns:**
- `input.time(timestamp("1 Jan 2021"))` — date picker input using `timestamp()` for default
- `timestamp("1 Jan 2021")` — converts human-readable date to milliseconds
- `inTradeWindow = not useDateFilter or (...)` — toggle: when filter disabled, always true
- `not inTradeWindow and inTradeWindow[1]` — detects the FIRST bar AFTER window ends
- `strategy.cancel_all()` — cancels all pending (unfilled) orders
- `strategy.close_all(comment=...)` — closes all open positions
- Time comparisons use `time` (bar open time) not `timenow`
- Exchange timezone warning: date inputs use instrument's exchange timezone, not chart/local TZ
- `group="Backtest Time Period"` — groups related inputs in the settings panel

---

## Limit Order Exit

_Source: <https://www.tradingcode.net/tradingview/limit-order-exit/>_

### Profit target exits with strategy.exit() in Pine Script

**Required args for profit target:** `id`, `from_entry`, and either `profit` (ticks) or `limit` (price)

**Long profit target — ticks:**
```pine
strategy.exit("Exit Long", from_entry="Enter Long", profit=200)
```

**Long profit target — price:**
```pine
strategy.exit("Exit Long", from_entry="Enter Long", limit=close * 1.05)
```

**Short profit target — ticks:**
```pine
strategy.exit("Exit Short", from_entry="Enter Short", profit=175)
```

**Short profit target — price:**
```pine
strategy.exit("Exit Short", from_entry="Enter Short", limit=close * 0.97)
```

**Best practice: generate exit on same bar as entry:**
```pine
if ta.crossover(close, ta.sma(close, 20))
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", profit=200)

if ta.crossunder(close, ta.sma(close, 20))
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", profit=175)
```

**Full RSI strategy with limit exits:**
```pine
//@version=5
strategy(title="Limit order exits")

rsiValue = ta.rsi(hlcc4, 4)

plot(rsiValue, color=color.teal, title="RSI")
hline(20, title="Oversold")
hline(80, title="Overbought")

if ta.crossover(rsiValue, 20)
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long",
         limit=high * 1.03)

if ta.crossunder(rsiValue, 80)
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short",
         limit=low * 0.97)
```

**Notes:**
- `from_entry` links exit to the matching entry order by name
- When entry closes for any reason, TradingView auto-removes connected exit orders
- `profit` = ticks from entry; `limit` = absolute price

---

## Stop Order Exit

_Source: <https://www.tradingcode.net/tradingview/stop-order-exit/>_

### Stop-loss exits with strategy.exit() in Pine Script

**Required args for stop loss:** `id`, `from_entry`, and either `loss` (ticks) or `stop` (price)

**Long stop — ticks:**
```pine
strategy.exit("Exit Long", from_entry="Enter Long", loss=150)
```

**Long stop — price:**
```pine
strategy.exit("Exit Long", from_entry="Enter Long", stop=low * 0.98)
```

**Short stop — ticks:**
```pine
strategy.exit("Exit Short", from_entry="Enter Short", loss=235)
```

**Short stop — price:**
```pine
strategy.exit("Exit Short", from_entry="Enter Short", stop=high * 1.02)
```

**Best practice: generate stop on same bar as entry:**
```pine
if ta.crossover(high, ta.highest(high, 20)[1])
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long", loss=150)

if ta.crossunder(low, ta.lowest(low, 20)[1])
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short", loss=235)
```

**Full EMA crossover strategy with stop exits:**
```pine
//@version=5
strategy(title="Stop order exits", overlay=true)

fastEMA = ta.ema(close, 10)
slowEMA = ta.ema(close, 30)

plot(fastEMA, color=color.orange, title="Fast EMA")
plot(slowEMA, color=color.teal, linewidth=2, title="Slow EMA")

if ta.crossover(fastEMA, slowEMA)
    strategy.entry("Enter Long", strategy.long)
    strategy.exit("Exit Long", from_entry="Enter Long",
         stop=slowEMA - 10 * syminfo.mintick)

if ta.crossunder(fastEMA, slowEMA)
    strategy.entry("Enter Short", strategy.short)
    strategy.exit("Exit Short", from_entry="Enter Short",
         stop=slowEMA + 10 * syminfo.mintick)
```

**Notes:**
- `from_entry` binds the stop to a specific entry — auto-cancelled when entry closes
- Generate stop on same bar as entry: protects on entry bar, prevents stop from drifting
- `loss` in ticks; `stop` in price — don't mix up
- ATR-based stop: `stop=close - ta.atr(14) * 1.5`

---

## Trailing Stop

_Source: <https://www.tradingcode.net/tradingview/percentage-trail/>_

### Trailing Stop Loss in TradingView Pine Script

**Percentage-based trailing stop — 3-step pattern:**

**Step 1 — Input the trail percentage:**
```pine
longTrailPerc  = input.float(3, title="Trail Long Loss (%)",  minval=0.0, step=0.1) * 0.01
shortTrailPerc = input.float(3, title="Trail Short Loss (%)", minval=0.0, step=0.1) * 0.01
```

**Step 2 — Track the trailing stop price (ratchets, never moves against position):**
```pine
longStopPrice  = 0.0
shortStopPrice = 0.0

// Long: stop rises with price, never falls — math.max() ratchets it up
longStopPrice := if strategy.position_size > 0
    stopValue = close * (1 - longTrailPerc)
    math.max(stopValue, longStopPrice[1])   // never allow stop to go lower
else
    0

// Short: stop falls with price, never rises — math.min() ratchets it down
shortStopPrice := if strategy.position_size < 0
    stopValue = close * (1 + shortTrailPerc)
    math.min(stopValue, shortStopPrice[1])  // never allow stop to go higher
else
    999999
```

**Step 3 — Submit exit orders with the trailing stop price:**
```pine
if strategy.position_size > 0
    strategy.exit("XL TRL STP", stop=longStopPrice)

if strategy.position_size < 0
    strategy.exit("XS TRL STP", stop=shortStopPrice)
```

**Full strategy:**
```pine
//@version=5
strategy(title="Trailing stop loss (% of instrument price)",
     overlay=true, pyramiding=3)

longTrailPerc  = input.float(3, title="Trail Long Loss (%)",  minval=0.0, step=0.1) * 0.01
shortTrailPerc = input.float(3, title="Trail Short Loss (%)", minval=0.0, step=0.1) * 0.01

fastSMA = ta.sma(close, 20)
slowSMA = ta.sma(close, 60)

enterLong  = ta.crossover(fastSMA, slowSMA)
enterShort = ta.crossunder(fastSMA, slowSMA)

plot(fastSMA, color=color.teal)
plot(slowSMA, color=color.orange)

longStopPrice  = 0.0
shortStopPrice = 0.0

longStopPrice := if strategy.position_size > 0
    stopValue = close * (1 - longTrailPerc)
    math.max(stopValue, longStopPrice[1])
else
    0

shortStopPrice := if strategy.position_size < 0
    stopValue = close * (1 + shortTrailPerc)
    math.min(stopValue, shortStopPrice[1])
else
    999999

// Visualize stop — only when in position
plot(strategy.position_size > 0 ? longStopPrice : na,
     color=color.fuchsia, style=plot.style_cross,
     linewidth=2, title="Long Trail Stop")

plot(strategy.position_size < 0 ? shortStopPrice : na,
     color=color.fuchsia, style=plot.style_cross,
     linewidth=2, title="Short Trail Stop")

if enterLong
    strategy.entry("EL", strategy.long)
if enterShort
    strategy.entry("ES", strategy.short)

if strategy.position_size > 0
    strategy.exit("XL TRL STP", stop=longStopPrice)
if strategy.position_size < 0
    strategy.exit("XS TRL STP", stop=shortStopPrice)
```

**Key patterns:**
- `math.max(stopValue, longStopPrice[1])` — ratchet up: stop only moves in favor of trade
- `math.min(stopValue, shortStopPrice[1])` — ratchet down: short stop only tightens
- Reset to `0` / `999999` when flat — ensures clean state on next entry
- `input.float(3) * 0.01` — converts 3% to 0.03 decimal
- `strategy.exit("id", stop=longStopPrice)` — called every bar while in position; TV updates the order
- No `from_entry=` needed when only one entry order per direction

---

## Risk Functions

_Source: <https://www.tradingcode.net/tradingview/risk-functions/>_

### Risk management functions in TradingView Pine

**Global risk functions** (stop strategy for entire backtest when triggered):

```pine
// Only trade long or short direction
strategy.risk.allow_entry_in(value=strategy.direction.long)
strategy.risk.allow_entry_in(value=strategy.direction.short)

// Stop after N consecutive losing days
strategy.risk.max_cons_loss_days(count=5)

// Max drawdown in cash
strategy.risk.max_drawdown(value=5000, type=strategy.cash)

// Max drawdown as % of equity
strategy.risk.max_drawdown(value=10, type=strategy.percent_of_equity)

// Max position size (contracts/shares/units)
strategy.risk.max_position_size(contracts=15)
```

**Intra-day risk functions** (stop strategy for the day, resume next session):

```pine
// Max filled orders per day
strategy.risk.max_intraday_filled_orders(count=20)

// Max intra-day loss in cash
strategy.risk.max_intraday_loss(value=450, type=strategy.cash)

// Max intra-day loss as % of equity
strategy.risk.max_intraday_loss(value=0.03, type=strategy.percent_of_equity)
```

**Notes:**
- Global rules: once triggered, strategy halts for ENTIRE backtest period
- Intra-day rules: halt for current day only, resume next session
- None of these have UI settings — must be coded explicitly
- Place these calls outside of `if` blocks (global scope, execute every bar evaluation)

---

## Percentage Stop

_Source: <https://www.tradingcode.net/tradingview/percentage-stop/>_

### Percentage Stop Loss in Pine Script — 3-Step Pattern

**Step 1 — Inputs:**
```pine
longLossPerc = input.float(1, title="Long Stop Loss (%)",
     minval=0.0, step=0.1) * 0.01

shortLossPerc = input.float(1, title="Short Stop Loss (%)",
     minval=0.0, step=0.1) * 0.01
```

**Step 2 — Calculate stop price from avg entry:**
```pine
longStopPrice  = strategy.position_avg_price * (1 - longLossPerc)
shortStopPrice = strategy.position_avg_price * (1 + shortLossPerc)
```

**Step 3 — Submit exit orders:**
```pine
if strategy.position_size > 0
    strategy.exit("XL STP", stop=longStopPrice)

if strategy.position_size < 0
    strategy.exit("XS STP", stop=shortStopPrice)
```

**Full strategy:**
```pine
//@version=5
strategy(title="Stop loss (% of instrument price)",
     overlay=true, pyramiding=3)

longLossPerc = input.float(1, title="Long Stop Loss (%)",
     minval=0.0, step=0.1) * 0.01

shortLossPerc = input.float(1, title="Short Stop Loss (%)",
     minval=0.0, step=0.1) * 0.01

fastSMA = ta.sma(close, 20)
slowSMA = ta.sma(close, 60)

enterLong  = ta.crossover(fastSMA, slowSMA)
enterShort = ta.crossunder(fastSMA, slowSMA)

plot(fastSMA, color=color.teal)
plot(slowSMA, color=color.orange)

longStopPrice  = strategy.position_avg_price * (1 - longLossPerc)
shortStopPrice = strategy.position_avg_price * (1 + shortLossPerc)

// Visualize stop — only when in position
plot(strategy.position_size > 0 ? longStopPrice : na,
     color=color.red, style=plot.style_cross,
     linewidth=2, title="Long Stop Loss")

plot(strategy.position_size < 0 ? shortStopPrice : na,
     color=color.red, style=plot.style_cross,
     linewidth=2, title="Short Stop Loss")

if enterLong
    strategy.entry("EL", strategy.long)

if enterShort
    strategy.entry("ES", strategy.short)

if strategy.position_size > 0
    strategy.exit("XL STP", stop=longStopPrice)

if strategy.position_size < 0
    strategy.exit("XS STP", stop=shortStopPrice)
```

**Key patterns:**
- `strategy.position_avg_price` — average fill price of current open position (handles pyramiding)
- `* (1 - lossPerc)` — long stop below entry; `* (1 + lossPerc)` — short stop above entry
- `input.float(1) * 0.01` — converts 1% to 0.01 decimal
- `strategy.position_size > 0` — check if long; `< 0` = short; `== 0` = flat
- Call `strategy.exit()` every bar while in position — TV updates the order each bar
- `plot(...? stopPrice : na)` — show stop line only while in position (hides when flat)
- `plot.style_cross` — crosses on every bar at stop price level (clear visual for stops)

---

## Limit Daily Loss

_Source: <https://www.tradingcode.net/tradingview/limit-daily-loss/>_

### Limit Intra-Day Loss in Pine Script

**Syntax:**
```pine
strategy.risk.max_intraday_loss(value, type)
```

**Fixed currency loss limit:**
```pine
strategy.risk.max_intraday_loss(value=450, type=strategy.cash)
```

**Equity percentage loss limit:**
```pine
strategy.risk.max_intraday_loss(value=0.03, type=strategy.percent_of_equity)
```

**With user input (cash):**
```pine
maxLoss = input.int(750, title="Max Intra-Day Loss")
strategy.risk.max_intraday_loss(maxLoss, type=strategy.cash)
```

**With user input (equity %):**
```pine
maxPercLoss = input.int(10, title="Max Intra-Day Equity Loss(%)", minval=1,
     maxval=100) / 100
strategy.risk.max_intraday_loss(maxPercLoss,
     type=strategy.percent_of_equity)
```

**Conditional daily limit (e.g., higher limit above 200 SMA):**
```pine
if close > ta.sma(close, 200)
    strategy.risk.max_intraday_loss(value=2500, type=strategy.cash)
```

**Dynamic limit based on volume:**
```pine
strategy.risk.max_intraday_loss(value=
     volume < ta.sma(volume, 50) ? 2000 : 4500, type=strategy.cash)
```

**Visualize today's loss vs limit:**
```pine
// Get the equity at the close of trading yesterday
newDay = dayofmonth != dayofmonth[1]

closeEquity = 0.0
closeEquity := newDay ? strategy.equity[1] : closeEquity[1]

// Figure out today's losses (0 when profitable, negative when losing)
todaysLosses = math.min(strategy.equity - closeEquity, 0)

plot(todaysLosses, style=plot.style_area, color=color.red)
hline(-1000, color=color.blue, linestyle=hline.style_solid)
```

**Full strategy example:**
```pine
//@version=5
strategy(title="Max intra-day loss example", overlay=false,
     default_qty_type=strategy.fixed, default_qty_value=15)

momValue = ta.mom(close, 9)
emaMom   = ta.ema(momValue, 15)

plot(momValue, color=color.blue)
plot(emaMom, color=color.orange)
hline(0, color=color.gray)

// Limit intra-day loss to 100
strategy.risk.max_intraday_loss(value=100, type=strategy.cash)

enterLong = ta.crossover(momValue, 0) or
     ta.crossover(momValue, emaMom)

enterShort = ta.crossunder(momValue, 0) or
     ta.crossunder(momValue, emaMom)

if enterLong
    strategy.entry("EL", strategy.long)

if enterShort
    strategy.entry("ES", strategy.short)
```

**Key patterns:**
- `strategy.risk.max_intraday_loss()` — built-in: TV halts new entries once daily loss limit hit
- `type=strategy.cash` — limit in currency units; `type=strategy.percent_of_equity` — limit as decimal (0.03 = 3%)
- Call it unconditionally each bar OR inside an `if` block to make it conditional
- The function halts NEW entries; it does NOT close open positions
- `strategy.equity` — current equity (changes in real-time)
- `dayofmonth != dayofmonth[1]` — detects first bar of a new calendar day
- `newDay ? strategy.equity[1] : closeEquity[1]` — latch previous day's close equity using `var`-style pattern
- `math.min(equity - closeEquity, 0)` — clamp to 0 (never shows profit as "loss")

---

## Losing Streak Stop

_Source: <https://www.tradingcode.net/tradingview/losing-streak/>_

### Losing Streak Stop in Pine Script — 6-Step Pattern

**Step 1 — Input:**
```pine
maxLosingStreak = input.int(15, title="Max Losing Streak Length", minval=1)
```

**Step 2 — Detect new losing trade:**
```pine
newLoss = strategy.losstrades > strategy.losstrades[1] and
     strategy.wintrades == strategy.wintrades[1] and
     strategy.eventrades == strategy.eventrades[1]
```

**Step 3 — Track streak length (resets on win or even trade):**
```pine
streakLen = 0

streakLen := if newLoss
    nz(streakLen[1]) + 1
else
    if strategy.wintrades > strategy.wintrades[1] or
         strategy.eventrades > strategy.eventrades[1]
        0
    else
        nz(streakLen[1])
```

**Step 4 — Gate:**
```pine
okToTrade = streakLen < maxLosingStreak
```

**Step 5 — Gate entries:**
```pine
if okToTrade and enterLong
    strategy.entry("EL", strategy.long)

if okToTrade and enterShort
    strategy.entry("ES", strategy.short)
```

**Step 6 — Flatten when limit reached:**
```pine
if not okToTrade
    strategy.close_all()
```

**Full strategy:**
```pine
//@version=5
strategy(title="Stop after losing streak", overlay=false, precision=0,
     default_qty_type=strategy.fixed, default_qty_value=5)

maxLosingStreak = input.int(15, title="Max Losing Streak Length", minval=1)

fastMA = ta.ema(close, 5)
slowMA = ta.ema(close, 25)

enterLong  = ta.crossover(fastMA, slowMA)
enterShort = ta.crossunder(fastMA, slowMA)

newLoss = strategy.losstrades > strategy.losstrades[1] and
     strategy.wintrades == strategy.wintrades[1] and
     strategy.eventrades == strategy.eventrades[1]

streakLen = 0

streakLen := if newLoss
    nz(streakLen[1]) + 1
else
    if strategy.wintrades > strategy.wintrades[1] or
         strategy.eventrades > strategy.eventrades[1]
        0
    else
        nz(streakLen[1])

plot(streakLen, style=plot.style_columns,
     color=streakLen < maxLosingStreak ? color.maroon : color.red)

bgcolor(newLoss ? color.new(color.red, 80) : na)

hline(maxLosingStreak, color=color.red, linestyle=hline.style_solid,
     linewidth=2)
hline(0, linestyle=hline.style_solid, color=color.gray)

okToTrade = streakLen < maxLosingStreak

if okToTrade and enterLong
    strategy.entry("EL", strategy.long)

if okToTrade and enterShort
    strategy.entry("ES", strategy.short)

if not okToTrade
    strategy.close_all()
```

**Key patterns:**
- `strategy.losstrades` / `strategy.wintrades` / `strategy.eventrades` — running trade counts
- `strategy.losstrades > strategy.losstrades[1]` — detects when a new loss was recorded
- Triple check (losstrades up, wintrades unchanged, eventrades unchanged) — confirms only losses caused the increment
- `nz(streakLen[1])` — safe access to prior bar (handles `na` on first bar)
- `streakLen := 0` then `:=` update — mutable series pattern
- Streak resets on ANY win or even trade
- `strategy.close_all()` — flattens entire position (both long and short)
- Also see `winning-streak` page for the symmetric winning streak version

---

## Strategy Performance Vars

_Source: <https://www.tradingcode.net/tradingview/strategy-net-profit/ and related pages>_

### Strategy Performance Variables in Pine Script

### Profit variables
- `strategy.netprofit` — total closed P&L in currency (gross profit - gross loss - commissions)
- `strategy.grossprofit` — sum of all winning trades (before commissions)
- `strategy.grossloss` — sum of all losing trades (before commissions; negative number)
- `strategy.openprofit` — unrealized P&L of currently open position

### Equity variables
- `strategy.equity` — current total equity (initial capital + netprofit + openprofit)
- `strategy.max_equity` — all-time peak equity
- `strategy.max_drawdown` — maximum peak-to-trough equity decline

### Trade count variables
- `strategy.closedtrades` — total number of closed trades
- `strategy.opentrades` — number of currently open trades
- `strategy.wintrades` — number of winning closed trades
- `strategy.losstrades` — number of losing closed trades
- `strategy.eventrades` — number of break-even closed trades

### Position variables
- `strategy.position_size` — current position size (positive = long, negative = short, 0 = flat)
- `strategy.position_avg_price` — average entry price of current open position
- `strategy.position_entry_name` — ID of the most recent entry order

### Usage examples

**Track peak/trough net profit:**
```pine
var highestNetProfit = 0.0
var lowestNetProfit  = 0.0

highestNetProfit := math.max(highestNetProfit, strategy.netprofit)
lowestNetProfit  := math.min(lowestNetProfit, strategy.netprofit)

plot(strategy.netprofit, style=plot.style_area, title="Net profit",
     color=strategy.netprofit > 0 ? color.green : color.red)

plot(highestNetProfit, color=color.green, title="Highest net profit")
plot(lowestNetProfit, color=color.red, title="Lowest net profit")
```

**Detect when a losing trade closed:**
```pine
if strategy.netprofit < strategy.netprofit[1]
    label.new(bar_index, high, text="Net profit decreased!")
```

**Measure profit growth over N bars:**
```pine
netGrowth = strategy.netprofit - strategy.netprofit[20]
```

**Win rate calculation:**
```pine
winRate = strategy.closedtrades > 0 ?
     strategy.wintrades / strategy.closedtrades * 100 : 0
```

**Profit factor calculation:**
```pine
profitFactor = strategy.grossloss != 0 ?
     strategy.grossprofit / math.abs(strategy.grossloss) : na
```

**Today's loss tracking (for daily loss limit display):**
```pine
newDay = dayofmonth != dayofmonth[1]
closeEquity = 0.0
closeEquity := newDay ? strategy.equity[1] : closeEquity[1]
todaysLosses = math.min(strategy.equity - closeEquity, 0)
```

**Key patterns:**
- All `strategy.*` variables update on bar close after trades execute
- `strategy.netprofit[1]` — prior bar's net profit; compare to detect new closed trade
- `strategy.position_size > 0` — long; `< 0` — short; `== 0` — flat
- `strategy.openprofit` + `strategy.netprofit` = realized + unrealized = `strategy.equity - initial_capital`
- `strategy.losstrades > strategy.losstrades[1]` — detects a new loss was recorded this bar
- `nz(series[1])` — safely access prior bar value (handles `na` on first bar)


## Further reading

- tradingcode.net Pine Script course index: https://www.tradingcode.net/tradingview-pine-script-course/
- Official Pine v6 reference via `mcp__pinescript-server__pine_reference`
