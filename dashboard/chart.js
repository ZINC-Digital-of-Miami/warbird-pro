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
  if (time && time.year !== undefined) {
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
// Sample data — static MES 5m bars for chart rendering verification
// ---------------------------------------------------------------------------

function generateSampleData() {
  const bars = [];
  const startTime = Math.floor(Date.UTC(2026, 4, 28, 14, 30) / 1000);
  let price = 5400;

  for (let i = 0; i < 300; i++) {
    const ts = startTime + i * 300;
    const change = (Math.random() - 0.48) * 8;
    const open = price;
    const close = price + change;
    const high = Math.max(open, close) + Math.random() * 4;
    const low = Math.min(open, close) - Math.random() * 4;
    price = close;

    bars.push({
      time: timeToTz(ts, CHART_TIME_ZONE),
      open: parseFloat(open.toFixed(2)),
      high: parseFloat(high.toFixed(2)),
      low: parseFloat(low.toFixed(2)),
      close: parseFloat(close.toFixed(2)),
    });
  }

  return bars;
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

  const candleData = generateSampleData();
  candleSeries.setData(candleData);

  // SMA 200 line
  const smaData = computeSmaData(candleData, SMA_PERIOD);
  if (smaData.length > 0) {
    const smaSeries = chart.addSeries(LightweightCharts.LineSeries, {
      color: SMA_COLOR,
      lineWidth: SMA_WIDTH,
      lineStyle: LightweightCharts.LineStyle.Solid,
      priceLineVisible: false,
      lastValueVisible: false,
      crosshairMarkerVisible: false,
    });
    smaSeries.setData(smaData);
  }

  // Set visible range
  const total = candleData.length;
  const visible = Math.min(INITIAL_VISIBLE_BARS, total);
  chart.timeScale().setVisibleLogicalRange({
    from: Math.max(0, total - visible),
    to: total - 1 + RIGHT_PADDING_BARS,
  });

  // Responsive resize
  const observer = new ResizeObserver(function (entries) {
    if (!entries[0]) return;
    const rect = entries[0].contentRect;
    chart.applyOptions({ width: rect.width, height: rect.height });
  });
  observer.observe(container);

  return { chart, candleSeries };
}

// ---------------------------------------------------------------------------
// Boot
// ---------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
  initChart();
});
