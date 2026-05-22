#!/usr/bin/env python3
# pyright: reportMissingImports=false
"""Read-only filesystem MCP rooted to user/project volumes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

ROOTS = [Path("/Users/zincdigital").resolve(), Path("/Volumes/Satechi Hub").resolve()]
DENY_PARTS = {".ssh", ".gnupg", ".aws", ".1password", ".cache", ".npm", ".Trash"}
DENY_NAMES = {".env", "auth.json", "hosts.yml", "id_rsa", "id_ed25519"}
MAX_CHARS = 50000

mcp = FastMCP(
    "warbird_filesystem_mcp",
    instructions=(
        "Read-only filesystem MCP rooted at /Users/zincdigital and "
        "/Volumes/Satechi Hub. Secret-like paths are denied."
    ),
)


def _fmt(payload: dict[str, Any], response_format: Literal["json", "markdown"] = "markdown"):
    if response_format == "json":
        return payload
    return "```json\n" + json.dumps(payload, indent=2, sort_keys=True) + "\n```"


def _resolve(path: str) -> Path:
    return Path(path).expanduser().resolve()


def _check(path: str) -> tuple[bool, str, Path | None]:
    resolved = _resolve(path)
    if not any(resolved == root or root in resolved.parents for root in ROOTS):
        return False, "Path is outside allowed roots", None
    if (
        any(part in DENY_PARTS for part in resolved.parts)
        or resolved.name in DENY_NAMES
        or resolved.suffix.lower() in {".pem", ".key", ".p12"}
    ):
        return False, "Path is denied because it may contain secrets", None
    return True, "", resolved


@mcp.tool()
def fs_roots(response_format: Literal["json", "markdown"] = "markdown") -> str | dict[str, Any]:
    """Return allowed read-only roots."""
    return _fmt({"ok": True, "roots": [str(root) for root in ROOTS]}, response_format)


@mcp.tool()
def fs_list(
    path: str,
    limit: int = 200,
    response_format: Literal["json", "markdown"] = "markdown",
) -> str | dict[str, Any]:
    """List a directory under allowed roots."""
    ok, err, resolved = _check(path)
    if not ok:
        return _fmt({"ok": False, "error": err, "path": path}, response_format)
    if not resolved or not resolved.is_dir():
        return _fmt({"ok": False, "error": "Not a directory", "path": str(resolved)}, response_format)

    rows = []
    safe_limit = max(1, min(limit, 1000))
    for child in sorted(resolved.iterdir(), key=lambda item: (not item.is_dir(), item.name.lower()))[:safe_limit]:
        if child.name in DENY_NAMES:
            continue
        try:
            stat = child.stat()
        except OSError:
            continue
        rows.append(
            {
                "name": child.name,
                "path": str(child),
                "type": "dir" if child.is_dir() else "file",
                "size": stat.st_size,
            }
        )

    return _fmt({"ok": True, "path": str(resolved), "entries": rows}, response_format)


@mcp.tool()
def fs_read_text(
    path: str,
    max_chars: int = MAX_CHARS,
    response_format: Literal["json", "markdown"] = "markdown",
) -> str | dict[str, Any]:
    """Read a text file under allowed roots, bounded and secret-path protected."""
    ok, err, resolved = _check(path)
    if not ok:
        return _fmt({"ok": False, "error": err, "path": path}, response_format)
    if not resolved or not resolved.is_file():
        return _fmt({"ok": False, "error": "Not a file", "path": str(resolved)}, response_format)

    safe_max = max(1, min(max_chars, 200000))
    data = resolved.read_bytes()[: safe_max + 1]
    text = data[:safe_max].decode("utf-8", errors="replace")
    return _fmt(
        {
            "ok": True,
            "path": str(resolved),
            "truncated": len(data) > safe_max,
            "text": text,
        },
        response_format,
    )


if __name__ == "__main__":
    mcp.run()
