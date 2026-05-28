/* Warbird Pro — Trading Command Center (frontend) */

(function () {
  "use strict";

  const WS_URL = `ws://${location.host}/ws`;
  const RECONNECT_DELAY = 2000;

  /* ── State ── */
  let ws = null;
  let chart = null;
  let candleSeries = null;
  let volumeSeries = null;
  let activeTf = "5m";
  let barsByTf = {};     // { tf: [{time, open, high, low, close, volume}] }
  let latestFibs = null;
  let latestTrigger = null;
  let fibLines = [];     // lightweight-charts price line objects
  let markersPrimitive = null; // LWC v5 SeriesMarkers primitive

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
        rightOffset: 5,
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
    updateTopbar(bars[bars.length - 1]);
  }

  /* ── Fib Lines ── */
  function renderFibLines() {
    // Remove old lines.
    for (const line of fibLines) {
      try { candleSeries.removePriceLine(line); } catch (e) {}
    }
    fibLines = [];

    if (!latestFibs || !latestFibs.levels) return;

    const ratioColors = {
      "0": "rgba(255,255,255,0.08)",
      ".236": "rgba(255,255,255,0.12)",
      ".382": "#26C6DA",
      "Pivot": "#FF9800",
      ".618": "#26C6DA",
      ".786": "rgba(255,255,255,0.12)",
      "1": "rgba(255,255,255,0.08)",
      "TP1": "rgba(0,230,118,0.3)",
      "TP2": "rgba(0,230,118,0.2)",
      "TP3": "rgba(0,230,118,0.15)",
    };

    for (const lv of latestFibs.levels) {
      const color = ratioColors[lv.label] || "rgba(255,255,255,0.06)";
      const line = candleSeries.createPriceLine({
        price: lv.price,
        color: color,
        lineWidth: lv.label === ".382" || lv.label === ".618" ? 1 : 1,
        lineStyle: lv.isExtension ? 2 : 0,
        axisLabelVisible: true,
        title: lv.label,
        lineVisible: true,
      });
      fibLines.push(line);
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

    const sqDot = document.getElementById("squeeze-dot");
    const sqText = document.getElementById("squeeze-text");
    if (t.squeezeOn) {
      sqDot.style.display = "inline-block";
      sqText.textContent = "ON";
      sqText.style.color = "#FF9800";
    } else {
      sqDot.style.display = "none";
      sqText.textContent = "OFF";
      sqText.style.color = "rgba(255,255,255,0.2)";
    }

    const momEl = document.getElementById("momentum-text");
    const mom = t.squeezeMomentum;
    momEl.textContent = (mom > 0 ? "+" : "") + mom.toFixed(1) + (mom > 0 ? " ▲" : " ▼");
    momEl.style.color = mom > 0 ? "#26C6DA" : "#F23645";
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
      .map(lv => `
        <div class="fib-row">
          <span class="fib-ratio">${lv.label}</span>
          <span class="fib-price" style="color:${lv.label === '.382' || lv.label === '.618' ? '#26C6DA' : 'rgba(255,255,255,0.5)'}">${lv.price.toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
        </div>
      `).join("");
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
        renderChart();
        updateSignalCard();
        updateConvictionCard();
        updatePressureBar();
        updateVolumeCard();
        updateFibCard();
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
          updatePressureBar();
          renderTriggerMarker();
        }
      }
    };
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
  connect();

  // Periodic system status update.
  setInterval(updateSystemCard, 5000);
})();
