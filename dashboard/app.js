/* Warbird Pro — Trading Command Center (frontend) */

(function () {
  "use strict";

  const WS_URL = `ws://${location.host}/ws`;
  const RECONNECT_DELAY = 2000;

  // Bar period in seconds for each TF (used for fib line extension).
  const TF_SECONDS = { "1m": 60, "3m": 180, "5m": 300, "15m": 900, "1h": 3600, "4h": 14400 };

  // V10 fib line styles matching the indicator settings panel.
  const FIB_STYLES = {
    "0":     { color: "rgba(255,255,255,0.35)", width: 1, lineStyle: 1 },  // dotted
    ".236":  { color: "rgba(255,255,255,0.35)", width: 1, lineStyle: 0 },  // solid gray
    ".382":  { color: "#cc0000",                width: 2, lineStyle: 0 },  // RED solid
    "Pivot": { color: "rgba(255,255,255,0.55)", width: 1, lineStyle: 2 },  // dashed white
    ".618":  { color: "#cc0000",                width: 2, lineStyle: 0 },  // RED solid
    ".786":  { color: "rgba(255,255,255,0.35)", width: 1, lineStyle: 0 },  // solid gray
    "1":     { color: "rgba(255,255,255,0.6)",  width: 2, lineStyle: 1 },  // dotted white
    "TP1":   { color: "#cc0000",                width: 2, lineStyle: 2 },  // RED dashed
    "TP2":   { color: "#cc0000",                width: 2, lineStyle: 2 },  // RED dashed
    "TP3":   { color: "#cc0000",                width: 2, lineStyle: 2 },  // RED dashed
  };

  /* ── State ── */
  let ws = null;
  let chart = null;
  let candleSeries = null;
  let volumeSeries = null;
  let activeTf = "5m";
  let barsByTf = {};     // { tf: [{time, open, high, low, close, volume}] }
  let latestFibs = null;
  let latestTrigger = null;
  let latestPressure = null;
  let latestNexus = null; // full nexus series [{time, osc, signal, vf}]
  let latestAi = null; // AI analysis text
  let fibSeriesList = []; // LWC LineSeries objects for bounded fib lines
  let markersPrimitive = null; // LWC v5 SeriesMarkers primitive

  // Nexus sub-chart state.
  let nexusChart = null;
  let nexusOscSeries = null;
  let nexusSigSeries = null;
  let nexusVfSeries = null;
  let nexusObLine = null;
  let nexusOsLine = null;
  let nexusMidLine = null;

  /* ── Chart Init ── */
  function initChart() {
    const container = document.getElementById("chart-container");
    chart = LightweightCharts.createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
      layout: {
        background: { type: "solid", color: "#131722" },
        textColor: "rgba(255,255,255,0.45)",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 10,
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.03)" },
        horzLines: { color: "rgba(255,255,255,0.03)" },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: { color: "rgba(255,255,255,0.1)", style: 3 },
        horzLine: { color: "rgba(255,255,255,0.1)", style: 3 },
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.06)",
        scaleMargins: { top: 0.05, bottom: 0.15 },
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.06)",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 8,
      },
    });

    candleSeries = chart.addSeries(LightweightCharts.CandlestickSeries, {
      upColor: "#26C6DA",
      downColor: "#F23645",
      borderUpColor: "#26C6DA",
      borderDownColor: "#F23645",
      wickUpColor: "#26C6DA",
      wickDownColor: "#F23645",
    });

    volumeSeries = chart.addSeries(LightweightCharts.HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "volume",
    });

    chart.priceScale("volume").applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    window.addEventListener("resize", () => {
      chart.applyOptions({
        width: container.clientWidth,
        height: container.clientHeight,
      });
      if (nexusChart) {
        const nc = document.getElementById("nexus-container");
        nexusChart.applyOptions({ width: nc.clientWidth, height: nc.clientHeight });
      }
    });
  }

  /* ── Nexus Sub-Chart Init ── */
  function initNexusChart() {
    const container = document.getElementById("nexus-container");
    if (!container) return;

    nexusChart = LightweightCharts.createChart(container, {
      width: container.clientWidth,
      height: container.clientHeight,
      layout: {
        background: { type: "solid", color: "#0d0d14" },
        textColor: "rgba(255,255,255,0.35)",
        fontFamily: "'JetBrains Mono', monospace",
        fontSize: 9,
      },
      grid: {
        vertLines: { color: "rgba(255,255,255,0.02)" },
        horzLines: { color: "rgba(255,255,255,0.02)" },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: { color: "rgba(255,255,255,0.08)", style: 3 },
        horzLine: { color: "rgba(255,255,255,0.08)", style: 3 },
      },
      rightPriceScale: {
        borderColor: "rgba(255,255,255,0.04)",
        scaleMargins: { top: 0.05, bottom: 0.05 },
      },
      timeScale: {
        borderColor: "rgba(255,255,255,0.04)",
        timeVisible: true,
        secondsVisible: false,
        rightOffset: 8,
        visible: false,
      },
    });

    // Volume flow histogram (behind osc line).
    nexusVfSeries = nexusChart.addSeries(LightweightCharts.HistogramSeries, {
      priceScaleId: "nexus",
      priceFormat: { type: "price", precision: 1, minMove: 0.1 },
      lastValueVisible: false,
      priceLineVisible: false,
    });

    // Oscillator line.
    nexusOscSeries = nexusChart.addSeries(LightweightCharts.LineSeries, {
      color: "#26C6DA",
      lineWidth: 2,
      priceScaleId: "nexus",
      priceFormat: { type: "price", precision: 1, minMove: 0.1 },
      lastValueVisible: true,
      priceLineVisible: false,
    });

    // Signal line.
    nexusSigSeries = nexusChart.addSeries(LightweightCharts.LineSeries, {
      color: "rgba(255,255,255,0.25)",
      lineWidth: 1,
      lineStyle: 2,
      priceScaleId: "nexus",
      priceFormat: { type: "price", precision: 1, minMove: 0.1 },
      lastValueVisible: false,
      priceLineVisible: false,
    });

    nexusChart.priceScale("nexus").applyOptions({
      scaleMargins: { top: 0.05, bottom: 0.05 },
      autoScale: false,
    });

    // OB/OS/mid reference lines.
    nexusObLine = nexusOscSeries.createPriceLine({
      price: 71.84, color: "rgba(204,0,0,0.25)", lineWidth: 1, lineStyle: 2,
      axisLabelVisible: true, title: "OB",
    });
    nexusOsLine = nexusOscSeries.createPriceLine({
      price: 19.59, color: "rgba(38,198,218,0.25)", lineWidth: 1, lineStyle: 2,
      axisLabelVisible: true, title: "OS",
    });
    nexusMidLine = nexusOscSeries.createPriceLine({
      price: 50, color: "rgba(255,255,255,0.08)", lineWidth: 1, lineStyle: 1,
      axisLabelVisible: false, title: "",
    });

    // Sync time scales between main chart and nexus.
    chart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
      if (range && nexusChart) {
        nexusChart.timeScale().setVisibleLogicalRange(range);
      }
    });
    nexusChart.timeScale().subscribeVisibleLogicalRangeChange((range) => {
      if (range && chart) {
        chart.timeScale().setVisibleLogicalRange(range);
      }
    });
  }

  /* ── Render Chart ── */
  function renderChart() {
    const bars = barsByTf[activeTf] || [];
    if (!bars.length) return;

    candleSeries.setData(bars.map(b => ({
      time: b.time,
      open: b.open,
      high: b.high,
      low: b.low,
      close: b.close,
    })));

    volumeSeries.setData(bars.map(b => ({
      time: b.time,
      value: b.volume,
      color: b.close >= b.open
        ? "rgba(38,198,218,0.15)"
        : "rgba(242,54,69,0.15)",
    })));

    renderFibLines();
    renderTriggerMarker();
    renderNexus();
    updateTopbar(bars[bars.length - 1]);
  }

  /* ── Fib Lines (bounded LineSeries matching V10 styles) ── */
  function renderFibLines() {
    // Remove old fib series.
    for (const fs of fibSeriesList) {
      try { chart.removeSeries(fs); } catch (e) {}
    }
    fibSeriesList = [];

    if (!latestFibs || !latestFibs.levels) return;

    const bars = barsByTf[activeTf] || [];
    if (!bars.length) return;

    const lastBarTime = bars[bars.length - 1].time;
    const barPeriod = TF_SECONDS[activeTf] || 300;
    const endTime = lastBarTime + 8 * barPeriod;

    // Anchor start = earlier of the high/low swing point.
    const anchorHighTime = latestFibs.anchorHighTime || bars[0].time;
    const anchorLowTime = latestFibs.anchorLowTime || bars[0].time;
    const startTime = Math.min(anchorHighTime, anchorLowTime);

    for (const lv of latestFibs.levels) {
      const style = FIB_STYLES[lv.label] || { color: "rgba(255,255,255,0.1)", width: 1, lineStyle: 0 };

      const series = chart.addSeries(LightweightCharts.LineSeries, {
        color: style.color,
        lineWidth: style.width,
        lineStyle: style.lineStyle,
        lastValueVisible: true,
        priceLineVisible: false,
        crosshairMarkerVisible: false,
        priceFormat: {
          type: "custom",
          formatter: function(price) { return lv.label + " " + price.toFixed(2); },
        },
      });

      series.setData([
        { time: startTime, value: lv.price },
        { time: endTime, value: lv.price },
      ]);

      fibSeriesList.push(series);
    }
  }

  /* ── Entry Markers (LWC v5 SeriesMarkers primitive) ── */
  function renderTriggerMarker() {
    if (markersPrimitive) {
      markersPrimitive.setMarkers([]);
    }

    if (!latestTrigger || latestTrigger.decision === "NO_GO") {
      return;
    }
    const bars = barsByTf[activeTf] || [];
    if (!bars.length) return;
    const lastBar = bars[bars.length - 1];

    const isLong = latestTrigger.direction === "LONG";
    const markers = [{
      time: lastBar.time,
      position: isLong ? "belowBar" : "aboveBar",
      color: latestTrigger.decision === "GO" ? "#00E676" : "#FF9800",
      shape: isLong ? "arrowUp" : "arrowDown",
      text: `${latestTrigger.direction} ${latestTrigger.score.toFixed(2)}`,
    }];

    if (!markersPrimitive) {
      markersPrimitive = LightweightCharts.createSeriesMarkers(candleSeries, markers);
    } else {
      markersPrimitive.setMarkers(markers);
    }
  }

  /* ── Render Nexus Oscillator ── */
  function renderNexus() {
    if (!nexusChart || !latestNexus || !latestNexus.length) return;

    nexusOscSeries.setData(latestNexus.map(p => ({
      time: p.time,
      value: p.osc,
    })));

    nexusSigSeries.setData(latestNexus.map(p => ({
      time: p.time,
      value: p.signal,
    })));

    nexusVfSeries.setData(latestNexus.map(p => ({
      time: p.time,
      value: p.vf - 50, // center around 0
      color: p.vf >= 50 ? "rgba(38,198,218,0.12)" : "rgba(204,0,0,0.12)",
    })));
  }

  /* ── Update UI Elements ── */
  function updateTopbar(bar) {
    if (!bar) return;
    const priceEl = document.getElementById("top-price");
    priceEl.textContent = bar.close.toLocaleString("en-US", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  }

  function updateSignalCard() {
    const decisionEl = document.getElementById("signal-decision");
    const scoreEl = document.getElementById("signal-score");
    const metaEl = document.getElementById("signal-meta");
    const shapEl = document.getElementById("shap-bars");

    if (!latestTrigger || latestTrigger.decision === "NO_GO") {
      decisionEl.textContent = "—";
      decisionEl.style.color = "rgba(255,255,255,0.15)";
      scoreEl.textContent = "Waiting for setup…";
      scoreEl.style.color = "rgba(255,255,255,0.2)";
      metaEl.innerHTML = "";
      shapEl.innerHTML = "";
      return;
    }

    const t = latestTrigger;
    const colors = { GO: "#00E676", WAIT: "#FF9800", NO_GO: "#555" };
    decisionEl.textContent = t.decision;
    decisionEl.style.color = colors[t.decision];
    scoreEl.textContent = `Score: ${t.score.toFixed(2)} / 1.00`;
    scoreEl.style.color = "rgba(255,255,255,0.6)";

    metaEl.innerHTML = `
      <div class="signal-meta-item"><span class="signal-meta-label">Direction</span><span class="signal-meta-value" style="color:${t.direction === 'LONG' ? '#26C6DA' : '#F23645'}">${t.direction}</span></div>
      <div class="signal-meta-item"><span class="signal-meta-label">Fib Level</span><span class="signal-meta-value">${t.fibRatio || '—'}</span></div>
      <div class="signal-meta-item"><span class="signal-meta-label">Entry</span><span class="signal-meta-value">${t.entryPrice ? t.entryPrice.toLocaleString() : '—'}</span></div>
      <div class="signal-meta-item"><span class="signal-meta-label">R:R</span><span class="signal-meta-value">${t.rr ? '1:' + t.rr : '—'}</span></div>
    `;

    // SHAP-style breakdown bars.
    const features = [
      { label: "Rej Wick", active: t.rejectionWick, val: t.rejectionWick ? 0.20 : 0 },
      { label: "Vol Spike", active: t.volumeSpike, val: t.volumeSpike ? 0.15 : t.volumeRatio >= 1.2 ? 0.08 : 0 },
      { label: "Engulfing", active: t.engulfing, val: t.engulfing ? 0.05 : 0 },
      { label: "Squeeze", active: t.squeezeOn, val: t.squeezeOn ? 0.20 : 0 },
      { label: "RSI", active: true, val: t.rsiValue < 35 || t.rsiValue > 65 ? 0.15 : t.rsiValue < 45 || t.rsiValue > 55 ? 0.08 : 0 },
    ];

    shapEl.innerHTML = `<div style="font-size:8px; font-weight:600; color:rgba(255,255,255,0.2); letter-spacing:0.12em; margin-bottom:4px; text-transform:uppercase">WHY THIS ENTRY</div>` +
      features.filter(f => f.val > 0).map(f => `
        <div class="shap-row">
          <span class="shap-label">${f.label}</span>
          <div class="shap-track"><div class="shap-fill" style="width:${Math.min(f.val / 0.25 * 100, 100)}%; background:${f.val >= 0.15 ? '#26C6DA' : '#FF9800'}"></div></div>
          <span class="shap-val" style="color:${f.val >= 0.15 ? '#26C6DA' : '#FF9800'}">+${f.val.toFixed(2)}</span>
        </div>
      `).join("");
  }

  function updateConvictionCard() {
    const levelEl = document.getElementById("conviction-level");
    const badgeEl = document.getElementById("conviction-badge");
    const layersEl = document.getElementById("conviction-layers");

    if (!latestFibs || !latestTrigger) {
      levelEl.textContent = "—";
      levelEl.style.color = "rgba(255,255,255,0.15)";
      badgeEl.textContent = "—";
      badgeEl.style.background = "rgba(255,255,255,0.06)";
      badgeEl.style.color = "rgba(255,255,255,0.3)";
      layersEl.innerHTML = "";
      return;
    }

    const t = latestTrigger;
    const isBull = t.direction === "LONG";
    const dir = isBull ? "BULL" : "BEAR";
    const color = isBull ? "#26C6DA" : "#F23645";

    let level = "LOW";
    if (t.score >= 0.75) level = "MAXIMUM";
    else if (t.score >= 0.6) level = "HIGH";
    else if (t.score >= 0.45) level = "MODERATE";

    levelEl.textContent = level;
    levelEl.style.color = color;

    if (t.score >= 0.6) {
      badgeEl.textContent = "ALIGNED";
      badgeEl.style.background = "rgba(0,230,118,0.15)";
      badgeEl.style.color = "#00E676";
    } else {
      badgeEl.textContent = "MIXED";
      badgeEl.style.background = "rgba(255,152,0,0.15)";
      badgeEl.style.color = "#FF9800";
    }

    layersEl.innerHTML = `
      <div class="conviction-layer"><div class="conviction-dot" style="background:${color}"></div><span style="font-size:9px; color:rgba(255,255,255,0.4)">1H</span><span style="font-size:9px; font-weight:600; color:${color}">${dir}</span></div>
      <div class="conviction-layer"><div class="conviction-dot" style="background:${color}"></div><span style="font-size:9px; color:rgba(255,255,255,0.4)">15m</span><span style="font-size:9px; font-weight:600; color:${color}">${dir}</span></div>
    `;
  }

  function updatePressureBar() {
    // Use real pressure data from the server if available.
    if (latestPressure) {
      const p = latestPressure;
      const bullPct = Math.round(p.bullPct);
      const bearPct = Math.round(p.bearPct);

      document.getElementById("pressure-bull").style.width = bullPct + "%";
      document.getElementById("pressure-bear").style.width = bearPct + "%";

      const pctEl = document.getElementById("pressure-pct");
      if (bullPct > bearPct) {
        pctEl.textContent = bullPct + "% BULL";
        pctEl.style.color = "#26C6DA";
      } else {
        pctEl.textContent = bearPct + "% BEAR";
        pctEl.style.color = "#F23645";
      }

      const sqDot = document.getElementById("squeeze-dot");
      const sqText = document.getElementById("squeeze-text");
      if (p.squeezeOn) {
        sqDot.style.display = "inline-block";
        sqText.textContent = "ON";
        sqText.style.color = "#FF9800";
      } else {
        sqDot.style.display = "none";
        sqText.textContent = "OFF";
        sqText.style.color = "rgba(255,255,255,0.2)";
      }

      const momEl = document.getElementById("momentum-text");
      const mom = p.squeezeMomentum;
      momEl.textContent = (mom > 0 ? "+" : "") + mom.toFixed(1) + (mom > 0 ? " ▲" : " ▼");
      momEl.style.color = mom > 0 ? "#26C6DA" : "#F23645";

      // RSI value display.
      const rsiEl = document.getElementById("rsi-text");
      if (rsiEl) {
        rsiEl.textContent = p.rsiValue.toFixed(1);
        rsiEl.style.color = p.rsiValue > 60 ? "#26C6DA" : p.rsiValue < 40 ? "#F23645" : "rgba(255,255,255,0.5)";
      }
      return;
    }

    // Fallback: derive from trigger if no pressure data yet.
    if (!latestTrigger) return;
    const t = latestTrigger;
    const bullPct = t.direction === "LONG" ? Math.round(50 + t.score * 30) : Math.round(50 - t.score * 30);
    const bearPct = 100 - bullPct;

    document.getElementById("pressure-bull").style.width = bullPct + "%";
    document.getElementById("pressure-bear").style.width = bearPct + "%";

    const pctEl = document.getElementById("pressure-pct");
    if (bullPct > bearPct) {
      pctEl.textContent = bullPct + "% BULL";
      pctEl.style.color = "#26C6DA";
    } else {
      pctEl.textContent = bearPct + "% BEAR";
      pctEl.style.color = "#F23645";
    }
  }

  function updateVolumeCard() {
    const bars = barsByTf[activeTf] || [];
    if (!bars.length) return;

    const last = bars[bars.length - 1];
    document.getElementById("vol-last").textContent = last.volume.toLocaleString();

    const recent = bars.slice(-20);
    const avgVol = recent.reduce((s, b) => s + b.volume, 0) / recent.length;
    document.getElementById("vol-avg").textContent = Math.round(avgVol).toLocaleString();

    const ratio = avgVol > 0 ? (last.volume / avgVol) : 0;
    const ratioEl = document.getElementById("vol-ratio");
    ratioEl.textContent = ratio.toFixed(2) + "x";
    ratioEl.style.color = ratio >= 1.5 ? "#00E676" : ratio >= 1.2 ? "#FF9800" : "rgba(255,255,255,0.6)";
  }

  function updateFibCard() {
    const dirEl = document.getElementById("fib-direction");
    const levelsEl = document.getElementById("fib-levels");

    if (!latestFibs || !latestFibs.levels) {
      dirEl.textContent = "—";
      levelsEl.innerHTML = '<div style="font-size:10px; color:rgba(255,255,255,0.2)">Waiting for 1H data…</div>';
      return;
    }

    const dir = latestFibs.isBullish ? "BULL" : "BEAR";
    const color = latestFibs.isBullish ? "#26C6DA" : "#F23645";
    dirEl.textContent = dir;
    dirEl.style.background = latestFibs.isBullish ? "rgba(38,198,218,0.15)" : "rgba(242,54,69,0.15)";
    dirEl.style.color = color;

    levelsEl.innerHTML = latestFibs.levels
      .filter(lv => !lv.isExtension)
      .reverse()
      .map(lv => {
        const fibStyle = FIB_STYLES[lv.label];
        const lvColor = fibStyle ? fibStyle.color : "rgba(255,255,255,0.5)";
        return `
          <div class="fib-row">
            <span class="fib-ratio">${lv.label}</span>
            <span class="fib-price" style="color:${lvColor}">${lv.price.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
          </div>
        `;
      }).join("");
  }

  function updateSystemCard() {
    document.getElementById("sys-update").textContent = new Date().toLocaleTimeString();
    const bars1m = barsByTf["1m"] || [];
    document.getElementById("sys-bars").textContent = bars1m.length.toString();
    document.getElementById("sys-feed").textContent = ws && ws.readyState === WebSocket.OPEN ? "Connected" : "Disconnected";
    document.getElementById("sys-feed").style.color = ws && ws.readyState === WebSocket.OPEN ? "#00E676" : "#F23645";
  }

  /* ── WebSocket ── */
  function connect() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      document.getElementById("status-dot").classList.add("connected");
      document.getElementById("status-text").textContent = "LIVE · Databento";
      updateSystemCard();
    };

    ws.onclose = () => {
      document.getElementById("status-dot").classList.remove("connected");
      document.getElementById("status-text").textContent = "RECONNECTING…";
      updateSystemCard();
      setTimeout(connect, RECONNECT_DELAY);
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "snapshot") {
        barsByTf = msg.bars || {};
        if (msg.fibs) latestFibs = msg.fibs;
        if (msg.trigger) latestTrigger = msg.trigger;
        if (msg.pressure) latestPressure = msg.pressure;
        if (msg.nexus) latestNexus = msg.nexus;
        if (msg.ai) { latestAi = msg.ai; updateAiCard(); }
        renderChart();
        updateSignalCard();
        updateConvictionCard();
        updatePressureBar();
        updateVolumeCard();
        updateFibCard();
        updateAiCard();
        updateSystemCard();
        return;
      }

      if (msg.type === "bar") {
        const tf = msg.tf;
        if (!barsByTf[tf]) barsByTf[tf] = [];
        barsByTf[tf].push(msg.bar);
        // Keep buffer bounded.
        if (barsByTf[tf].length > 5000) barsByTf[tf] = barsByTf[tf].slice(-4500);

        if (tf === activeTf) {
          candleSeries.update({
            time: msg.bar.time,
            open: msg.bar.open,
            high: msg.bar.high,
            low: msg.bar.low,
            close: msg.bar.close,
          });
          volumeSeries.update({
            time: msg.bar.time,
            value: msg.bar.volume,
            color: msg.bar.close >= msg.bar.open
              ? "rgba(38,198,218,0.15)"
              : "rgba(242,54,69,0.15)",
          });
          updateTopbar(msg.bar);
          updateVolumeCard();
          updateSystemCard();
        }

        if (msg.fibs) {
          latestFibs = msg.fibs;
          renderFibLines();
          updateFibCard();
        }

        if (msg.trigger) {
          latestTrigger = msg.trigger;
          updateSignalCard();
          updateConvictionCard();
          renderTriggerMarker();
        }

        if (msg.pressure) {
          latestPressure = msg.pressure;
          updatePressureBar();
        }

        if (msg.pressure) {
          latestPressure = msg.pressure;
          updatePressureBar();
        }

        if (msg.nexus && msg.nexus.length) {
          if (!latestNexus) latestNexus = [];
          for (const pt of msg.nexus) {
            latestNexus.push(pt);
          }
          // Keep bounded.
          if (latestNexus.length > 5000) latestNexus = latestNexus.slice(-4500);

          // Update nexus sub-chart incrementally.
          if (nexusOscSeries) {
            const last = msg.nexus[msg.nexus.length - 1];
            nexusOscSeries.update({ time: last.time, value: last.osc });
            nexusSigSeries.update({ time: last.time, value: last.signal });
            nexusVfSeries.update({
              time: last.time,
              value: last.vf - 50,
              color: last.vf >= 50 ? "rgba(38,198,218,0.12)" : "rgba(204,0,0,0.12)",
            });
          }
        }
      if (msg.type === "ai") {
        latestAi = msg.analysis;
        updateAiCard();
      }
    };
  }

  function updateAiCard() {
    const textEl = document.getElementById("ai-text");
    const metaEl = document.getElementById("ai-meta");
    const badgeEl = document.getElementById("ai-badge");
    if (!textEl) return;

    if (!latestAi || !latestAi.text) {
      textEl.textContent = "Waiting for analysis…";
      textEl.style.color = "rgba(255,255,255,0.2)";
      return;
    }

    textEl.textContent = latestAi.text;
    textEl.style.color = "rgba(255,255,255,0.7)";

    if (metaEl && latestAi.model) {
      const cached = latestAi.cached ? " (cached)" : "";
      metaEl.textContent = latestAi.model + cached;
    }

    if (badgeEl && latestAi.cached) {
      badgeEl.style.opacity = "0.5";
    } else if (badgeEl) {
      badgeEl.style.opacity = "1";
    }
  }

  /* ── TF Buttons ── */
  document.getElementById("tf-buttons").addEventListener("click", (e) => {
    if (e.target.tagName !== "BUTTON") return;
    const tf = e.target.dataset.tf;
    if (tf === activeTf) return;

    document.querySelectorAll(".topbar-tf button").forEach(b => b.classList.remove("active"));
    e.target.classList.add("active");
    activeTf = tf;
    renderChart();
  });

  /* ── Boot ── */
  initChart();
  initNexusChart();
  connect();

  // Periodic system status update.
  setInterval(updateSystemCard, 5000);
})();
