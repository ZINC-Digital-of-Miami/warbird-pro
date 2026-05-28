"""AI analysis card — OpenRouter GPT integration for trade commentary."""

from __future__ import annotations

import json
import logging
import time
from typing import Any

import httpx

from engine.config import AI_BASE_URL, AI_MODEL, get_ai_key

logger = logging.getLogger("warbird.ai")

_last_call_ts: float = 0.0
_MIN_INTERVAL_SEC: float = 30.0  # rate-limit: at most one call per 30s
_last_analysis: dict[str, Any] | None = None


SYSTEM_PROMPT = """You are Warbird AI, a concise ES/MES futures trading analyst embedded in a live trading dashboard. You receive real-time market context (price, fibs, pressure, volume, trigger signals) and provide brief, actionable commentary.

Rules:
- Be extremely concise: 2-4 sentences max.
- Focus on what matters RIGHT NOW for entries/exits.
- Reference specific levels, pressure direction, and volume conditions.
- If there's a trigger signal, explain why it's strong or weak.
- Use trading terminology naturally (fib retracement, golden zone, squeeze, delta).
- Never give financial advice disclaimers — this is a professional tool.
- Format: plain text, no markdown, no bullet points."""


def build_market_context(
    last_bar: dict | None,
    fibs: dict | None,
    trigger: dict | None,
    pressure: dict | None,
) -> str:
    parts = []

    if last_bar:
        parts.append(
            f"MES Price: {last_bar.get('close', '?')} "
            f"(O:{last_bar.get('open', '?')} H:{last_bar.get('high', '?')} "
            f"L:{last_bar.get('low', '?')} V:{last_bar.get('volume', '?')})"
        )

    if pressure:
        bull = pressure.get("bullPct", 50)
        bear = pressure.get("bearPct", 50)
        sq = "ON" if pressure.get("squeezeOn") else "OFF"
        mom = pressure.get("squeezeMomentum", 0)
        rsi = pressure.get("rsiValue", 50)
        parts.append(
            f"Pressure: {bull:.0f}% bull / {bear:.0f}% bear | "
            f"Squeeze {sq} (mom {mom:+.1f}) | RSI {rsi:.1f}"
        )

    if fibs and fibs.get("levels"):
        direction = "BULLISH" if fibs.get("isBullish") else "BEARISH"
        levels_str = ", ".join(
            f"{lv['label']}={lv['price']:.2f}"
            for lv in fibs["levels"]
            if not lv.get("isExtension")
        )
        parts.append(f"Fib Structure: {direction} | {levels_str}")

    if trigger:
        decision = trigger.get("decision", "NO_GO")
        score = trigger.get("score", 0)
        direction = trigger.get("direction", "?")
        parts.append(
            f"Trigger: {decision} ({direction}) score={score:.2f} | "
            f"rej_wick={trigger.get('rejectionWick', False)} "
            f"vol_spike={trigger.get('volumeSpike', False)} "
            f"squeeze={trigger.get('squeezeOn', False)} "
            f"engulf={trigger.get('engulfing', False)}"
        )

    return "\n".join(parts) if parts else "No market data available yet."


async def get_ai_analysis(
    last_bar: dict | None = None,
    fibs: dict | None = None,
    trigger: dict | None = None,
    pressure: dict | None = None,
    force: bool = False,
) -> dict[str, Any]:
    """Call OpenRouter for AI trade analysis. Rate-limited to 1 call per 30s."""
    global _last_call_ts, _last_analysis

    api_key = get_ai_key()
    if not api_key:
        return {"text": "AI analysis unavailable — no API key configured.", "model": "", "cached": False}

    now = time.time()
    if not force and _last_analysis and (now - _last_call_ts) < _MIN_INTERVAL_SEC:
        return {**_last_analysis, "cached": True}

    context = build_market_context(last_bar, fibs, trigger, pressure)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{AI_BASE_URL}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://warbird-pro.local",
                    "X-Title": "Warbird Pro Trading Dashboard",
                    "Content-Type": "application/json",
                },
                json={
                    "model": AI_MODEL,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": f"Current market state:\n{context}\n\nProvide brief trading analysis."},
                    ],
                    "max_tokens": 200,
                    "temperature": 0.3,
                },
            )

        if resp.status_code != 200:
            logger.warning("OpenRouter API error %d: %s", resp.status_code, resp.text[:200])
            return {"text": f"AI error ({resp.status_code})", "model": AI_MODEL, "cached": False}

        data = resp.json()
        choices = data.get("choices", [])
        if not choices:
            logger.warning("OpenRouter returned no choices: %s", json.dumps(data)[:300])
            return {"text": "AI returned empty response", "model": AI_MODEL, "cached": False}
        msg_obj = choices[0].get("message", {})
        text = msg_obj.get("content") or msg_obj.get("reasoning") or ""
        text = text.strip()
        model_used = data.get("model", AI_MODEL)

        _last_call_ts = now
        _last_analysis = {"text": text, "model": model_used, "cached": False}
        return _last_analysis

    except Exception as e:
        logger.warning("AI analysis failed: %s", e)
        return {"text": f"AI analysis error: {str(e)[:80]}", "model": AI_MODEL, "cached": False}
