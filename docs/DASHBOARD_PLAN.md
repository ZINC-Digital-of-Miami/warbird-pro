# Warbird Pro Dashboard — Reset Plan

## Current State (What Exists)

### Python Engine (`engine/`)
- FastAPI server on port 3100 serving static HTML dashboard
- Databento Live feed → 1m bars aggregated to 1/3/5/15m/1h/4h
- Fib engine: multi-period confluence (8/13/21/34/55 bar lookbacks) — **matches `autofib-v16.ts` logic, NOT V9 Pine**
- Trigger engine: zone proximity, rejection wick, volume spike, engulfing, squeeze
- Pressure bar: computes from volume delta (30%), RSI (25%), momentum (20%), squeeze (25%)
- Nexus ML RSI: AMF oscillator ported from Pine v1.2.6
- AI analysis card: OpenRouter → `mistralai/ministral-3b-2512` ($0.02/day)
- WebSocket push for all updates

### Dashboard (`dashboard/`)
- Plain HTML/JS/CSS — no React, no Next.js
- Lightweight Charts v5 candlestick chart
- Fib lines as LineSeries (bounded anchor → 8 bars right)
- Pressure bar, Nexus sub-chart, 6 right-panel cards
- **Problems**: Chart candle styling doesn't match Vercel dashboard. Fib colors/behavior don't match V9 Pine. No EMA21/EMA9 overlay. No golden zone fill. No fib labels.

### Next.js/Vercel Dashboard (`components/`, `app/`)
- **This is what Kirk considers "polished"**
- `LiveMesChart.tsx`: transparent bg, Inter font, white wicks, proper bar spacing (10px, min 8px), right padding 16 bars
- `V16FibLinesPrimitive.ts`: Canvas-based fib rendering with zone fill between .382/.618
- `autofib-v16.ts`: Same multi-period confluence algo we ported to Python
- Candle theme: up=#26C6DA, down=#FF0000, borderUp=transparent, borderDown=transparent, wickUp=#FFFFFF, wickDown=rgba(178,181,190,0.83)
- SMA200 white line overlay
- Correlations row, data tables, active setups card

## Gap Analysis

### Chart Styling (dashboard `app.js` vs Vercel `LiveMesChart.tsx`)

| Property | Current (app.js) | Vercel (LiveMesChart.tsx) | V9 Pine |
|----------|-----------------|--------------------------|---------|
| Down candle color | `#F23645` | `#FF0000` | Red |
| Border up | `#26C6DA` | `transparent` | — |
| Border down | `#F23645` | `transparent` | — |
| Wick up | `#26C6DA` | `#FFFFFF` | White |
| Wick down | `#F23645` | `rgba(178,181,190,0.83)` | Gray |
| Background | `#131722` | `transparent` (gradient underneath) | — |
| Font | JetBrains Mono | Inter | — |
| Bar spacing | default | 10px (min 8) | — |
| Right offset | 8 | 16 | — |
| MA overlay | None | SMA200 white | EMA21 white + EMA9 #26A69A |
| Volume histogram | Yes | No | — |
| Price line visible | No | Yes | — |

### Fib Rendering (dashboard `app.js` vs V9 Pine `drawAnchoredLine`)

| Property | Current (app.js) | V9 Pine |
|----------|-----------------|---------|
| Draw span left | anchor time | `anchorStartBar` (min of high/low swing bar) |
| Draw span right | lastBar + 8*barPeriod | `bar_index + fibLabelOffsetBarsInput` (8 bars default) |
| 0 (Zero) color | white 0.35 | `#FFFFFF` (COLOR_ANCHOR) width 2 Solid |
| .236 color | white 0.35 | `#808080` (COLOR_RETRACEMENT) width 1 Solid |
| .382 color | `#cc0000` | `#FFFFFF` (COLOR_ANCHOR) width 1 Solid |
| .500 (Pivot) | white dashed | `#FFFFFF` (COLOR_ANCHOR) width 1 Dashed |
| .618 color | `#cc0000` | `#FFFFFF` (COLOR_ANCHOR) width 1 Solid |
| .786 color | white 0.35 | `#808080` (COLOR_RETRACEMENT) width 1 Solid |
| 1.000 color | white dotted | `#FFFFFF` (COLOR_ANCHOR) width 2 Solid |
| Targets | `#cc0000` dashed | `#006064` (COLOR_TARGET) width 1 Solid |
| Zone fill | None | `.382–.618` fill (in V16FibLinesPrimitive) |
| Labels | None | Yes — "level  price" labels at bar_index + 8 |

**NOTE on V10 vs V9:** Kirk's screenshots showed V10 settings where .382/.618 are RED (`#cc0000`). But the V9 Pine code uses `COLOR_ANCHOR (#FFFFFF)` for .382/.618. The default V9 colors are:
- `.382/.618` = `fibRetracementAccentColorInput` defaults to `COLOR_ANCHOR = #FFFFFF` width 1
- But Kirk's LIVE V10 has RED. Since Kirk said "replicate the indicators", I need to match what he sees on TV — which is RED .382/.618.

→ **Resolution: Use Kirk's screenshot settings (V10 live) for fib colors, not V9 Pine defaults. Kirk explicitly showed the color settings.**

### Missing Features

1. **EMA21 + EMA9 (Smoothing MA)** — V9 Pine plots these. Dashboard has neither.
2. **Golden zone fill** — V16FibLinesPrimitive draws `.382–.618` fill. Dashboard has no fill.
3. **Fib labels** — V9 draws labels 8 bars right. Dashboard has none.
4. **SMA200 or EMA overlay** — Vercel dashboard has SMA200. V9 has EMA21+EMA9.
5. **DuckDB** — config references `data/warbird_trades.duckdb` but nothing creates it.

## Plan

### Phase A: Chart Polish (match Vercel quality)
1. Update candle theme to match Vercel: white wicks, transparent borders, `#FF0000` down
2. Set bar spacing 10px / min 8px / right offset 16
3. Add EMA21 (white, width 2) + EMA9 (#26A69A, width 2) overlays
4. Compute EMAs in Python engine, push via WebSocket
5. Update layout font to Inter for chart, keep JetBrains Mono for data

### Phase B: Fib Rendering (match V9 Pine + Kirk's V10 screenshots)
1. Port `V16FibLinesPrimitive` canvas renderer to dashboard (zone fill + proper line drawing)
2. Use Kirk's V10 color settings: .382/.618 = `#FFFFFF` accent, Pivot = dashed, etc.
3. Add fib labels (ratio + price) positioned 8 bars right of last bar
4. Proper draw span: anchor start bar to `lastBar + 8 bars`
5. Add -.236 stop level, 1.382, 1.5 waypoints, and TP4/TP5 extension levels

### Phase C: DuckDB Setup
1. Create `data/` directory
2. Initialize DuckDB at `data/warbird_trades.duckdb` with trade log schema
3. Wire trade recording into the engine (manual or auto based on trigger signals)

### Phase D: Remaining Features
1. News feed + econ calendar (Finnhub free tier)
2. Trade log + pattern learning
3. Performance optimization
