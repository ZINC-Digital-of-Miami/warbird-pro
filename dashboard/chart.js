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
// Data state — chart starts empty, populated by WebSocket feed (Phase 1.5)
// ---------------------------------------------------------------------------

let chartInstance = null;
let candleSeriesRef = null;
let smaSeriesRef = null;

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
  const mapped = bars.map(function (b) {
    return {
      time: timeToTz(b.time, CHART_TIME_ZONE),
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    };
  });
  candleSeriesRef.setData(mapped);

  // Compute and set SMA after loading bars
  const smaData = computeSmaData(mapped, SMA_PERIOD);
  if (smaData.length > 0 && smaSeriesRef) {
    smaSeriesRef.setData(smaData);
  }

  // Set visible range
  const total = mapped.length;
  const visible = Math.min(INITIAL_VISIBLE_BARS, total);
  if (chartInstance) {
    chartInstance.timeScale().setVisibleLogicalRange({
      from: Math.max(0, total - visible),
      to: total - 1 + RIGHT_PADDING_BARS,
    });
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

  // SMA 200 line
  const smaSeries = chart.addSeries(LightweightCharts.LineSeries, {
    color: SMA_COLOR,
    lineWidth: SMA_WIDTH,
    lineStyle: LightweightCharts.LineStyle.Solid,
    priceLineVisible: false,
    lastValueVisible: false,
    crosshairMarkerVisible: false,
  });

  // Store refs for WebSocket data push (Phase 1.5)
  chartInstance = chart;
  candleSeriesRef = candleSeries;
  smaSeriesRef = smaSeries;

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
    var msg;
    try {
      msg = JSON.parse(event.data);
    } catch (_e) {
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
  var bars = msg.bars && msg.bars[currentTf];
  if (bars && bars.length > 0) {
    loadBars(bars);
  }
  // Update lifecycle status indicator
  if (msg.lifecycle) {
    updateLifecycleStatus(msg.lifecycle.state);
  }
}

function handleLiveBar(msg) {
  if (msg.tf === currentTf) {
    pushBar(msg.bar);
    // Update SMA incrementally
    if (smaSeriesRef && candleSeriesRef) {
      updateSmaIncremental(msg.bar);
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

function updateSmaIncremental(_bar) {
  // SMA update handled via full data on snapshot; live bars append incrementally
  if (!candleSeriesRef) return;
}

function updateConnectionStatus(connected) {
  var dot = document.querySelector(".chart-status-dot");
  if (dot) {
    dot.style.backgroundColor = connected ? "#26C6DA" : "#FF0000";
    dot.title = connected ? "Connected" : "Disconnected";
  }
}

function updateLifecycleStatus(state) {
  var desc = document.querySelector(".chart-desc");
  if (desc) {
    var tfLabel = currentTf.toUpperCase();
    desc.textContent = "Micro E-mini S&P 500 \u2022 " + tfLabel + " \u2022 " + state;
  }
}

// Keepalive ping every 30s
setInterval(function () {
  if (wsInstance && wsInstance.readyState === WebSocket.OPEN) {
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

// Expose data API on globalThis
globalThis.pushBar = pushBar;
globalThis.loadBars = loadBars;
