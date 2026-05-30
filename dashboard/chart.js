/**
 * Warbird Pro — LWC v5 Chart (vanilla JS)
 *
 * Settings ported EXACTLY from components/charts/LiveMesChart.tsx.
 * Strips V16FibLinesPrimitive + autofib-v16 (React-only, not portable).
 * Connects to local WebSocket server (Phase 1.5) — static sample data for now.
 */

/* global LightweightCharts */

// ---------------------------------------------------------------------------
// Constants — ported from LiveMesChart.tsx
// ---------------------------------------------------------------------------

const CANDLE_THEME = {
  upColor: "#26C6DA",
  downColor: "#FF0000",
  borderUpColor: "transparent",
  borderDownColor: "transparent",
  wickUpColor: "#FFFFFF",
  wickDownColor: "rgba(178,181,190,0.83)",
};

const GRID_COLOR = "rgba(255,255,255,0.04)";
const CROSSHAIR_COLOR = "rgba(255,255,255,0.55)";
const LABEL_BG = "rgba(20,10,40,0.9)";
const TEXT_COLOR = "rgba(255,255,255,0.4)";

const INITIAL_VISIBLE_BARS = 120;
const RIGHT_PADDING_BARS = 16;
const BAR_SPACING = 10;
const MIN_BAR_SPACING = 8;
const SMA_PERIOD = 200;
const SMA_COLOR = "#FFFFFF";
const SMA_WIDTH = 2;
const CHART_TIME_ZONE = "America/Chicago";

// ---------------------------------------------------------------------------
// EMA settings — exact match to AGENTS.md Live Pine Settings table
// Primary EMA Length=21, Source=close, Offset=1
// Smoothing Type=EMA, Smoothing Length=9
// ---------------------------------------------------------------------------
const EMA_PRIMARY_LENGTH = 21;
const EMA_PRIMARY_COLOR = "#FFFFFF";
const EMA_PRIMARY_WIDTH = 2;
const EMA_PRIMARY_OFFSET = 1;
const EMA_SMOOTHING_LENGTH = 9;
const EMA_SMOOTHING_COLOR = "#26A69A";
const EMA_SMOOTHING_WIDTH = 2;

// ---------------------------------------------------------------------------
// Fib visual configuration — ported from indicators/warbird-pro-v9.pine
// Colors from Kirk’s task spec override Pine defaults where specified.
// ---------------------------------------------------------------------------
const FIB_LEVEL_STYLES = {
  0:     { color: "#FFFFFF", width: 2, style: "Solid",  label: "0" },
  0.236: { color: "#808080", width: 1, style: "Solid",  label: ".236" },
  0.382: { color: "#cc0000", width: 2, style: "Solid",  label: ".382" },
  0.5:   { color: "#FFFFFF", width: 1, style: "Dashed", label: "Pivot" },
  0.618: { color: "#cc0000", width: 2, style: "Solid",  label: ".618" },
  0.786: { color: "#808080", width: 1, style: "Solid",  label: ".786" },
  1:     { color: "#FFFFFF", width: 2, style: "Dotted", label: "1" },
  1.236: { color: "#0097A7", width: 1, style: "Solid",  label: "TP1" },
  1.382: { color: "#808080", width: 1, style: "Solid",  label: "1.382" },
  1.5:   { color: "#808080", width: 1, style: "Solid",  label: "1.5" },
  1.618: { color: "#0097A7", width: 1, style: "Solid",  label: "TP2" },
  2:     { color: "#0097A7", width: 1, style: "Solid",  label: "TP3" },
  2.236: { color: "#0097A7", width: 1, style: "Solid",  label: "TP4" },
};

const ZONE_FILL_COLOR = "rgba(255, 255, 255, 0.25)";
const _FIB_LABEL_BG = "rgba(0, 0, 0, 0.70)";
const _FIB_LABEL_FONT = "#FFFFFF";

const AXIS_TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
  timeZone: CHART_TIME_ZONE,
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const CROSSHAIR_TIME_FORMATTER = new Intl.DateTimeFormat("en-US", {
  timeZone: CHART_TIME_ZONE,
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

// ---------------------------------------------------------------------------
// Time helpers
// ---------------------------------------------------------------------------

function timeToTz(originalTime, timeZone) {
  const zonedDate = new Date(
    new Date(originalTime * 1000).toLocaleString("en-US", { timeZone })
  );
  return Math.floor(zonedDate.getTime() / 1000);
}

function parseTimeToUnix(time) {
  if (typeof time === "number") return time;
  if (typeof time === "string") {
    const parsed = Date.parse(time);
    return Number.isNaN(parsed) ? null : Math.floor(parsed / 1000);
  }
  if (time?.year !== undefined) {
    return Math.floor(
      Date.UTC(time.year, time.month - 1, time.day) / 1000
    );
  }
  return null;
}

function formatAxisTimeLabel(time) {
  const seconds = parseTimeToUnix(time);
  if (seconds == null) return "";
  return AXIS_TIME_FORMATTER.format(new Date(seconds * 1000));
}

function formatCrosshairTimeLabel(time) {
  const seconds = parseTimeToUnix(time);
  if (seconds == null) return "";
  return CROSSHAIR_TIME_FORMATTER.format(new Date(seconds * 1000));
}

// ---------------------------------------------------------------------------
// SMA computation — ported from LiveMesChart.tsx
// ---------------------------------------------------------------------------

function computeSmaData(candles, period) {
  if (candles.length < period) return [];
  const result = [];
  let rollingSum = 0;
  for (let i = 0; i < candles.length; i++) {
    rollingSum += candles[i].close;
    if (i >= period) {
      rollingSum -= candles[i - period].close;
    }
    if (i >= period - 1) {
      result.push({
        time: candles[i].time,
        value: rollingSum / period,
      });
    }
  }
  return result;
}

// ---------------------------------------------------------------------------
// EMA computation — matches Pine ta.ema() exactly
// ---------------------------------------------------------------------------

function computeEmaData(candles, period) {
  if (candles.length < period) return [];
  var result = [];
  var seed = 0;
  for (var i = 0; i < period; i++) {
    seed += candles[i].close;
  }
  seed /= period;
  result.push({ time: candles[period - 1].time, value: seed });
  var mult = 2.0 / (period + 1);
  var prev = seed;
  for (var j = period; j < candles.length; j++) {
    var val = candles[j].close * mult + prev * (1 - mult);
    result.push({ time: candles[j].time, value: val });
    prev = val;
  }
  return result;
}

function computeSmoothedEmaData(ema21Data, period) {
  if (ema21Data.length < period) return [];
  var result = [];
  var seed = 0;
  for (var i = 0; i < period; i++) {
    seed += ema21Data[i].value;
  }
  seed /= period;
  result.push({ time: ema21Data[period - 1].time, value: seed });
  var mult = 2.0 / (period + 1);
  var prev = seed;
  for (var j = period; j < ema21Data.length; j++) {
    var val = ema21Data[j].value * mult + prev * (1 - mult);
    result.push({ time: ema21Data[j].time, value: val });
    prev = val;
  }
  return result;
}

function fibLineStyle(style) {
  switch (style) {
    case "Dashed": return LightweightCharts.LineStyle.Dashed;
    case "Dotted": return LightweightCharts.LineStyle.Dotted;
    default: return LightweightCharts.LineStyle.Solid;
  }
}

// ---------------------------------------------------------------------------
// Data state — chart starts empty, populated by WebSocket feed (Phase 1.5)
// ---------------------------------------------------------------------------

let chartInstance = null;
let candleSeriesRef = null;
let smaSeriesRef = null;
let ema21SeriesRef = null;
let ema9SeriesRef = null;
let fibSeriesRefs = [];
let zoneSeriesRef = null;
let currentFibData = null;
let allCandleData = [];

/**
 * Push a new OHLCV bar into the chart. Called by the WebSocket handler
 * once the live feed is connected (Phase 1.5).
 *
 * @param {{ time: number, open: number, high: number, low: number, close: number }} bar
 */
function pushBar(bar) {
  if (!candleSeriesRef) return;
  const mapped = {
    time: timeToTz(bar.time, CHART_TIME_ZONE),
    open: bar.open,
    high: bar.high,
    low: bar.low,
    close: bar.close,
  };
  candleSeriesRef.update(mapped);
}

/**
 * Load a full array of OHLCV bars (e.g. from historical backfill).
 *
 * @param {Array<{ time: number, open: number, high: number, low: number, close: number }>} bars
 */
function loadBars(bars) {
  if (!candleSeriesRef || !bars.length) return;
  var mapped = bars.map(function (b) {
    return {
      time: timeToTz(b.time, CHART_TIME_ZONE),
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    };
  });
  mapped.sort(function (a, b) { return a.time - b.time; });
  candleSeriesRef.setData(mapped);
  allCandleData = mapped;

  // Compute and set SMA200
  var smaData = computeSmaData(mapped, SMA_PERIOD);
  if (smaData.length > 0 && smaSeriesRef) {
    smaSeriesRef.setData(smaData);
  }

  // Compute and set EMA21 (with offset=1)
  var ema21Data = computeEmaData(mapped, EMA_PRIMARY_LENGTH);
  if (ema21Data.length > 0 && ema21SeriesRef) {
    if (EMA_PRIMARY_OFFSET > 0 && ema21Data.length > EMA_PRIMARY_OFFSET) {
      var shifted = [];
      for (var i = 0; i < ema21Data.length - EMA_PRIMARY_OFFSET; i++) {
        shifted.push({
          time: ema21Data[i + EMA_PRIMARY_OFFSET].time,
          value: ema21Data[i].value,
        });
      }
      ema21SeriesRef.setData(shifted);
    } else {
      ema21SeriesRef.setData(ema21Data);
    }
  }

  // Compute and set EMA9 smoothing (EMA of EMA21 values)
  if (ema21Data.length > 0 && ema9SeriesRef) {
    var ema9Data = computeSmoothedEmaData(ema21Data, EMA_SMOOTHING_LENGTH);
    if (ema9Data.length > 0) {
      ema9SeriesRef.setData(ema9Data);
    }
  }

  // Set visible range
  var total = mapped.length;
  var visible = Math.min(INITIAL_VISIBLE_BARS, total);
  if (chartInstance) {
    chartInstance.timeScale().setVisibleLogicalRange({
      from: Math.max(0, total - visible),
      to: total - 1 + RIGHT_PADDING_BARS,
    });
  }
}

// ---------------------------------------------------------------------------
// Fib rendering — BOUNDED anchored lines (extend.none)
// ---------------------------------------------------------------------------

function clearFibs() {
  if (!chartInstance) return;
  for (var i = 0; i < fibSeriesRefs.length; i++) {
    try { chartInstance.removeSeries(fibSeriesRefs[i]); } catch (_e) { /* ignore */ }
  }
  fibSeriesRefs = [];
  if (zoneSeriesRef) {
    try { chartInstance.removeSeries(zoneSeriesRef); } catch (_e) { /* ignore */ }
    zoneSeriesRef = null;
  }
}

function drawFibs(fibData) {
  if (!chartInstance || !fibData || !fibData.levels) return;
  clearFibs();

  var levels = fibData.levels;
  var anchorHighTime = fibData.anchorHighTime;
  var anchorLowTime = fibData.anchorLowTime;

  var leftTime = timeToTz(
    Math.min(anchorHighTime, anchorLowTime),
    CHART_TIME_ZONE
  );

  var rightTime = null;
  if (allCandleData.length > 0) {
    rightTime = allCandleData[allCandleData.length - 1].time;
  }
  if (!rightTime) return;

  var zone382 = null;
  var zone618 = null;

  // Draw golden zone fill FIRST (behind fib lines)
  for (var k = 0; k < levels.length; k++) {
    if (levels[k].ratio === 0.382) zone382 = levels[k].price;
    if (levels[k].ratio === 0.618) zone618 = levels[k].price;
  }
  if (zone382 !== null && zone618 !== null) {
    var zoneHigh = Math.max(zone382, zone618);
    var zoneLow = Math.min(zone382, zone618);
    var zoneSeries = chartInstance.addSeries(LightweightCharts.BaselineSeries, {
      baseValue: { type: "price", price: zoneLow },
      topLineColor: "transparent",
      topFillColor1: ZONE_FILL_COLOR,
      topFillColor2: ZONE_FILL_COLOR,
      bottomLineColor: "transparent",
      bottomFillColor1: "transparent",
      bottomFillColor2: "transparent",
      lineWidth: 0,
      lastValueVisible: false,
      priceLineVisible: false,
      crosshairMarkerVisible: false,
    });
    zoneSeries.setData([
      { time: leftTime, value: zoneHigh },
      { time: rightTime, value: zoneHigh },
    ]);
    zoneSeriesRef = zoneSeries;
  }

  // Draw each fib level as a bounded LineSeries
  for (var i = 0; i < levels.length; i++) {
    var level = levels[i];
    var ratio = level.ratio;
    var config = FIB_LEVEL_STYLES[ratio];
    if (!config) continue;

    var series = chartInstance.addSeries(LightweightCharts.LineSeries, {
      color: config.color,
      lineWidth: config.width,
      lineStyle: fibLineStyle(config.style),
      priceLineVisible: false,
      lastValueVisible: true,
      crosshairMarkerVisible: false,
      title: config.label,
    });

    series.setData([
      { time: leftTime, value: level.price },
      { time: rightTime, value: level.price },
    ]);

    fibSeriesRefs.push(series);
  }

  currentFibData = fibData;
}

function updateFibRightEdge() {
  if (!currentFibData || !allCandleData.length) return;
  var rightTime = allCandleData[allCandleData.length - 1].time;
  var leftTime = timeToTz(
    Math.min(currentFibData.anchorHighTime, currentFibData.anchorLowTime),
    CHART_TIME_ZONE
  );

  // Update zone fill
  if (zoneSeriesRef) {
    var zone382 = null, zone618 = null;
    for (var k = 0; k < currentFibData.levels.length; k++) {
      if (currentFibData.levels[k].ratio === 0.382) zone382 = currentFibData.levels[k].price;
      if (currentFibData.levels[k].ratio === 0.618) zone618 = currentFibData.levels[k].price;
    }
    if (zone382 !== null && zone618 !== null) {
      zoneSeriesRef.setData([
        { time: leftTime, value: Math.max(zone382, zone618) },
        { time: rightTime, value: Math.max(zone382, zone618) },
      ]);
    }
  }

  // Update each fib line right edge
  var levelIdx = 0;
  for (var i = 0; i < currentFibData.levels.length; i++) {
    var ratio = currentFibData.levels[i].ratio;
    if (!FIB_LEVEL_STYLES[ratio]) continue;
    if (levelIdx < fibSeriesRefs.length) {
      fibSeriesRefs[levelIdx].setData([
        { time: leftTime, value: currentFibData.levels[i].price },
        { time: rightTime, value: currentFibData.levels[i].price },
      ]);
    }
    levelIdx++;
  }
}

// ---------------------------------------------------------------------------
// Chart initialization
// ---------------------------------------------------------------------------

function initChart() {
  const container = document.getElementById("chart-container");
  if (!container) return;

  const chart = LightweightCharts.createChart(container, {
    layout: {
      background: {
        type: LightweightCharts.ColorType.Solid,
        color: "transparent",
      },
      textColor: TEXT_COLOR,
      fontFamily: "Inter, sans-serif",
      fontSize: 11,
      attributionLogo: false,
    },
    localization: {
      timeFormatter: formatCrosshairTimeLabel,
    },
    grid: {
      vertLines: { color: GRID_COLOR },
      horzLines: { color: GRID_COLOR },
    },
    crosshair: {
      vertLine: {
        color: CROSSHAIR_COLOR,
        width: 1,
        style: LightweightCharts.LineStyle.Solid,
        labelBackgroundColor: LABEL_BG,
      },
      horzLine: {
        color: CROSSHAIR_COLOR,
        width: 1,
        style: LightweightCharts.LineStyle.Solid,
        labelBackgroundColor: LABEL_BG,
      },
    },
    rightPriceScale: {
      borderColor: "transparent",
      autoScale: true,
      scaleMargins: { top: 0.05, bottom: 0.05 },
    },
    timeScale: {
      borderColor: "transparent",
      timeVisible: true,
      secondsVisible: false,
      fixLeftEdge: false,
      fixRightEdge: false,
      rightOffset: RIGHT_PADDING_BARS,
      barSpacing: BAR_SPACING,
      minBarSpacing: MIN_BAR_SPACING,
      lockVisibleTimeRangeOnResize: true,
      tickMarkFormatter: function (time) {
        return formatAxisTimeLabel(time);
      },
    },
    handleScroll: {
      mouseWheel: false,
      pressedMouseMove: true,
      horzTouchDrag: true,
      vertTouchDrag: false,
    },
    handleScale: {
      mouseWheel: false,
      pinch: true,
      axisPressedMouseMove: { time: true, price: true },
      axisDoubleClickReset: { time: true, price: true },
    },
  });

  // Candlestick series
  const candleSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
    upColor: CANDLE_THEME.upColor,
    downColor: CANDLE_THEME.downColor,
    borderUpColor: CANDLE_THEME.borderUpColor,
    borderDownColor: CANDLE_THEME.borderDownColor,
    wickUpColor: CANDLE_THEME.wickUpColor,
    wickDownColor: CANDLE_THEME.wickDownColor,
    priceLineVisible: true,
  });

  // SMA 200 line — white, 2pt thick (from LiveMesChart.tsx)
  var smaSeries = chart.addSeries(LightweightCharts.LineSeries, {
    color: SMA_COLOR,
    lineWidth: SMA_WIDTH,
    lineStyle: LightweightCharts.LineStyle.Solid,
    priceLineVisible: false,
    lastValueVisible: false,
    crosshairMarkerVisible: false,
  });

  // EMA 21 — white, 2pt (Pine: plot(out, color=color.white, linewidth=2))
  var ema21Series = chart.addSeries(LightweightCharts.LineSeries, {
    color: EMA_PRIMARY_COLOR,
    lineWidth: EMA_PRIMARY_WIDTH,
    lineStyle: LightweightCharts.LineStyle.Solid,
    priceLineVisible: false,
    lastValueVisible: false,
    crosshairMarkerVisible: false,
  });

  // EMA 9 smoothing — #26A69A (teal green), 2pt (Pine: plot(smoothingMA, color=#26A69A, linewidth=2))
  var ema9Series = chart.addSeries(LightweightCharts.LineSeries, {
    color: EMA_SMOOTHING_COLOR,
    lineWidth: EMA_SMOOTHING_WIDTH,
    lineStyle: LightweightCharts.LineStyle.Solid,
    priceLineVisible: false,
    lastValueVisible: false,
    crosshairMarkerVisible: false,
  });

  // Store refs for WebSocket data push
  chartInstance = chart;
  candleSeriesRef = candleSeries;
  smaSeriesRef = smaSeries;
  ema21SeriesRef = ema21Series;
  ema9SeriesRef = ema9Series;

  // Responsive resize
  const observer = new ResizeObserver(function (entries) {
    if (!entries[0]) return;
    const rect = entries[0].contentRect;
    chart.applyOptions({ width: rect.width, height: rect.height });
  });
  observer.observe(container);

  return { chart, candleSeries, smaSeries };
}

// ---------------------------------------------------------------------------
// WebSocket connection — lifecycle-aware live data feed
// ---------------------------------------------------------------------------

const WS_URL = "ws://" + (location.hostname || "127.0.0.1") + ":3100/ws";
const WS_RECONNECT_BASE_MS = 2000;
const WS_RECONNECT_MAX_MS = 30000;

let wsInstance = null;
let wsReconnectDelay = WS_RECONNECT_BASE_MS;
let currentTf = "5m";

function connectWebSocket() {
  if (wsInstance && wsInstance.readyState <= 1) return;

  wsInstance = new WebSocket(WS_URL);

  wsInstance.onopen = function () {
    wsReconnectDelay = WS_RECONNECT_BASE_MS;
    updateConnectionStatus(true);
  };

  wsInstance.onmessage = function (event) {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch (parseError) {
      console.debug("WebSocket: malformed JSON received", parseError.message);
      return;
    }

    if (msg.type === "snapshot") {
      handleSnapshot(msg);
    } else if (msg.type === "bar") {
      handleLiveBar(msg);
    } else if (msg.type === "pong") {
      // keepalive response
    }
  };

  wsInstance.onclose = function () {
    updateConnectionStatus(false);
    scheduleReconnect();
  };

  wsInstance.onerror = function () {
    wsInstance.close();
  };
}

function scheduleReconnect() {
  setTimeout(function () {
    connectWebSocket();
    wsReconnectDelay = Math.min(wsReconnectDelay * 2, WS_RECONNECT_MAX_MS);
  }, wsReconnectDelay);
}

function handleSnapshot(msg) {
  var bars = msg.bars?.[currentTf];
  if (bars && bars.length > 0) {
    loadBars(bars);
  }
  // Draw fibs from server-computed data
  var fibData = msg.fibs?.[currentTf];
  if (fibData) {
    drawFibs(fibData);
  }
  // Update lifecycle status indicator
  if (msg.lifecycle) {
    updateLifecycleStatus(msg.lifecycle.state);
  }
}

function handleLiveBar(msg) {
  if (msg.tf === currentTf) {
    pushBar(msg.bar);
    // Update candle data for fib right-edge extension
    if (msg.bar) {
      var mappedBar = {
        time: timeToTz(msg.bar.time, CHART_TIME_ZONE),
        open: msg.bar.open,
        high: msg.bar.high,
        low: msg.bar.low,
        close: msg.bar.close,
      };
      if (allCandleData.length > 0 && allCandleData[allCandleData.length - 1].time === mappedBar.time) {
        allCandleData[allCandleData.length - 1] = mappedBar;
      } else {
        allCandleData.push(mappedBar);
      }
    }
    // Update fibs from server-computed data (recomputed each bar close)
    if (msg.fibs) {
      drawFibs(msg.fibs);
    } else {
      updateFibRightEdge();
    }
  }
  // Update price display for 1m bars
  if (msg.tf === "1m" && msg.bar) {
    var priceEl = document.getElementById("chart-price");
    if (priceEl) {
      priceEl.textContent = msg.bar.close.toFixed(2);
    }
  }
}

function _updateSmaIncremental(_bar) {
  // SMA update handled via full data on snapshot; live bars append incrementally
  if (!candleSeriesRef) return;
}

function updateConnectionStatus(connected) {
  const dot = document.querySelector(".chart-status-dot");
  if (dot) {
    dot.style.backgroundColor = connected ? "#26C6DA" : "#FF0000";
    dot.title = connected ? "Connected" : "Disconnected";
  }
}

function updateLifecycleStatus(state) {
  const desc = document.querySelector(".chart-desc");
  if (desc) {
    const tfLabel = currentTf.toUpperCase();
    desc.textContent = "Micro E-mini S&P 500 \u2022 " + tfLabel + " \u2022 " + state;
  }
}

// Keepalive ping every 30s
setInterval(function () {
  if (wsInstance?.readyState === WebSocket.OPEN) {
    wsInstance.send(JSON.stringify({ type: "ping" }));
  }
}, 30000);

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  initChart();
  connectWebSocket();
});

// ---------------------------------------------------------------------------
// TF switching — full state recompute (Phase 2: fibs, MAs, price)
// ---------------------------------------------------------------------------

function switchTimeframe(newTf) {
  if (newTf === currentTf) return;
  currentTf = newTf;

  // Clear existing fib series
  clearFibs();
  currentFibData = null;
  allCandleData = [];

  // Re-fetch data for new TF via REST fallback
  var host = location.hostname || "127.0.0.1";
  fetch("http://" + host + ":3100/api/bars/" + newTf + "?limit=500")
    .then(function (res) { return res.json(); })
    .then(function (bars) {
      if (bars && bars.length > 0) {
        loadBars(bars);
      }
      return fetch("http://" + host + ":3100/api/fibs/" + newTf);
    })
    .then(function (res) { return res.json(); })
    .then(function (fibData) {
      if (fibData && fibData.levels) {
        drawFibs(fibData);
      }
    })
    .catch(function (err) {
      console.debug("TF switch fetch error:", err.message);
    });

  // Update header
  var desc = document.querySelector(".chart-desc");
  if (desc) {
    desc.textContent = "Micro E-mini S&P 500 \u2022 " + newTf.toUpperCase();
  }
}

// Expose data API on globalThis
globalThis.pushBar = pushBar;
globalThis.loadBars = loadBars;
globalThis.switchTimeframe = switchTimeframe;
globalThis.drawFibs = drawFibs;
