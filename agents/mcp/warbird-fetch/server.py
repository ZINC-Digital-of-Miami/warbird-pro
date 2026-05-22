#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Minimal stdio fetch MCP for Warbird: no local ports, no daemon."""

from __future__ import annotations

import ipaddress
import json
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

MAX_CHARS_DEFAULT = 20000

mcp = FastMCP(
    "warbird_fetch_mcp",
    instructions=(
        "HTTP/HTTPS fetch helper. Blocks localhost/private-network URLs unless "
        "explicitly allowed."
    ),
)


def _private_host(host: str) -> bool:
    if not host:
        return True
    if host.lower() in {"localhost", "local", "0.0.0.0"} or host.endswith(".local"):
        return True
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_multicast
            or ip.is_reserved
        ):
            return True
    return False


def _fmt(payload: dict[str, Any], response_format: Literal["json", "markdown"] = "markdown"):
    if response_format == "json":
        return payload
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```"


@mcp.tool()
def fetch_url(
    url: str,
    max_chars: int = MAX_CHARS_DEFAULT,
    allow_private: bool = False,
    response_format: Literal["json", "markdown"] = "markdown",
) -> str | dict[str, Any]:
    """Fetch an HTTP/HTTPS URL with private-network protection and bounded output."""
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return _fmt(
            {"ok": False, "error": "Only http/https URLs are allowed", "url": url},
            response_format,
        )
    if not allow_private and _private_host(parsed.hostname or ""):
        return _fmt(
            {
                "ok": False,
                "error": "Blocked private/localhost URL; set allow_private=true only for intentional local checks",
                "url": url,
            },
            response_format,
        )

    req = urllib.request.Request(url, headers={"User-Agent": "Warbird-Fetch/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            safe_max = max(1, min(max_chars, 100000))
            raw = response.read(safe_max + 1)
            text = raw[:safe_max].decode(
                response.headers.get_content_charset() or "utf-8", errors="replace"
            )
            payload = {
                "ok": True,
                "url": url,
                "status": getattr(response, "status", None),
                "content_type": response.headers.get("content-type"),
                "truncated": len(raw) > safe_max,
                "text": text,
            }
    except urllib.error.HTTPError as exc:
        body = exc.read(min(max_chars, 100000)).decode("utf-8", errors="replace")
        payload = {
            "ok": False,
            "url": url,
            "status": exc.code,
            "error": str(exc),
            "text": body,
        }
    except Exception as exc:
        payload = {"ok": False, "url": url, "error": repr(exc)}
    return _fmt(payload, response_format)


if __name__ == "__main__":
    mcp.run()
