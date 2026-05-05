#!/usr/bin/env python3
"""
Read-only TradingView connection doctor for Warbird tuning flows.

This script does not launch, kill, restart, or modify TradingView.
It reports whether the local environment is ready for CDP-based tools.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen


DEFAULT_HOST = "localhost"
DEFAULT_PORT = 9222
DEFAULT_TIMEOUT = 1.5
DEFAULT_CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
DEFAULT_MCP_ROOT = Path("/Users/zincdigital/tradingview-mcp")


@dataclass
class CheckResult:
    name: str
    ok: bool
    detail: str
    hint: str = ""


def _cap_lines(lines: list[str], max_lines: int = 12) -> list[str]:
    normalized = [
        (line if len(line) <= 220 else f"{line[:217]}...")
        for line in lines
    ]
    if len(normalized) <= max_lines:
        return normalized
    extra = len(normalized) - max_lines
    return [*normalized[:max_lines], f"... truncated {extra} line(s)"]


def _http_json(url: str, timeout: float) -> tuple[bool, str, Any | None]:
    try:
        with urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
        return True, "ok", json.loads(body)
    except (URLError, TimeoutError, OSError) as exc:
        return False, str(exc), None
    except json.JSONDecodeError as exc:
        return False, f"invalid_json: {exc}", None


def _run_cmd(args: list[str], timeout: float = 3.0) -> tuple[int, str, str]:
    try:
        proc = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return 124, stdout.strip(), (stderr.strip() or f"timeout after {timeout}s")


def _load_codex_tradingview_server_path(config_path: Path) -> tuple[str | None, str]:
    if not config_path.exists():
        return None, f"missing config: {config_path}"
    try:
        data = tomllib.loads(config_path.read_text())
    except Exception as exc:  # pragma: no cover - defensive
        return None, f"failed to parse TOML: {exc}"

    try:
        server = data["mcp_servers"]["tradingview"]
    except Exception:
        return None, "mcp_servers.tradingview not configured"

    args = server.get("args")
    if not isinstance(args, list) or not args:
        return None, "mcp_servers.tradingview.args missing/empty"
    script_path = str(args[0])
    return script_path, "ok"


def run_diagnostics(
    *,
    host: str,
    port: int,
    timeout: float,
    codex_config: Path,
    mcp_root: Path,
) -> dict[str, Any]:
    checks: list[CheckResult] = []

    tv_code, tv_out, _tv_err = _run_cmd(["pgrep", "-fal", "TradingView"])
    tv_running = tv_code == 0 and bool(tv_out)
    checks.append(
        CheckResult(
            name="tradingview_process",
            ok=tv_running,
            detail="running" if tv_running else "no TradingView process found",
            hint="" if tv_running else "Launch TradingView manually before MCP checks.",
        )
    )

    version_url = f"http://{host}:{port}/json/version"
    cdp_ok, cdp_msg, cdp_payload = _http_json(version_url, timeout=timeout)
    checks.append(
        CheckResult(
            name="cdp_endpoint",
            ok=cdp_ok,
            detail=version_url if cdp_ok else f"{version_url} unreachable: {cdp_msg}",
            hint="" if cdp_ok else "TradingView is open but CDP is not active on this port.",
        )
    )

    list_url = f"http://{host}:{port}/json/list"
    list_ok, list_msg, list_payload = _http_json(list_url, timeout=timeout)
    page_count = 0
    if list_ok and isinstance(list_payload, list):
        page_count = sum(1 for row in list_payload if row.get("type") == "page")
    checks.append(
        CheckResult(
            name="cdp_targets",
            ok=list_ok and page_count > 0,
            detail=(
                f"{page_count} page target(s)"
                if list_ok
                else f"{list_url} unavailable: {list_msg}"
            ),
            hint="" if list_ok else "No CDP targets available to attach.",
        )
    )

    server_path, server_msg = _load_codex_tradingview_server_path(codex_config)
    server_exists = bool(server_path) and Path(server_path).exists()
    checks.append(
        CheckResult(
            name="codex_mcp_server_path",
            ok=server_exists,
            detail=server_path or server_msg,
            hint=(
                ""
                if server_exists
                else "Update ~/.codex/config.toml mcp_servers.tradingview.args[0] to a real server.js path."
            ),
        )
    )

    mcp_server_path = mcp_root / "src" / "server.js"
    mcp_cli_path = mcp_root / "src" / "cli" / "index.js"
    checks.append(
        CheckResult(
            name="local_tradingview_mcp_install",
            ok=mcp_server_path.exists() and mcp_cli_path.exists(),
            detail=f"server={mcp_server_path} cli={mcp_cli_path}",
            hint=(
                ""
                if (mcp_server_path.exists() and mcp_cli_path.exists())
                else "Install/restore /Users/zincdigital/tradingview-mcp."
            ),
        )
    )

    status_ok = False
    status_detail = "skipped"
    status_hint = ""
    if mcp_cli_path.exists():
        rc, out, err = _run_cmd(["node", str(mcp_cli_path), "status"], timeout=10.0)
        if rc == 0:
            status_ok = True
            status_detail = out or "status returned success"
        else:
            status_detail = err or out or f"exit {rc}"
            status_hint = "MCP status fails when CDP is unavailable or server path/config is stale."
    checks.append(
        CheckResult(
            name="mcp_status_cli",
            ok=status_ok,
            detail=status_detail,
            hint=status_hint,
        )
    )

    mcp_rc, mcp_out, _mcp_err = _run_cmd(["pgrep", "-fal", "tradingview-mcp/src/server.js"])
    mcp_proc_count = len(mcp_out.splitlines()) if mcp_rc == 0 and mcp_out else 0
    checks.append(
        CheckResult(
            name="mcp_server_process_count",
            ok=mcp_proc_count <= 1,
            detail=f"{mcp_proc_count} process(es)",
            hint=(
                ""
                if mcp_proc_count <= 1
                else "Multiple server processes can create session confusion across agents."
            ),
        )
    )

    hard_fail_checks = {"cdp_endpoint", "cdp_targets", "codex_mcp_server_path", "mcp_status_cli"}
    ready = all(ch.ok for ch in checks if ch.name in hard_fail_checks)
    return {
        "ready": ready,
        "host": host,
        "port": port,
        "checks": [asdict(ch) for ch in checks],
        "process_snapshot": {
            "tradingview": _cap_lines(tv_out.splitlines()) if tv_out else [],
            "tradingview_mcp": _cap_lines(mcp_out.splitlines()) if mcp_out else [],
        },
        "notes": [
            "Doctor is read-only: no launch/restart/kill actions are performed.",
            "Readiness requires both CDP endpoint and MCP status to be green.",
        ],
    }


def _print_human(report: dict[str, Any]) -> None:
    print(f"TradingView CDP Doctor: READY={report['ready']}")
    for ch in report["checks"]:
        status = "PASS" if ch["ok"] else "FAIL"
        print(f"- {status} {ch['name']}: {ch['detail']}")
        if ch.get("hint") and not ch["ok"]:
            print(f"  hint: {ch['hint']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument(
        "--codex-config",
        default=str(DEFAULT_CODEX_CONFIG),
        help="Path to Codex config.toml.",
    )
    parser.add_argument(
        "--mcp-root",
        default=str(DEFAULT_MCP_ROOT),
        help="Path to local tradingview-mcp checkout root.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    report = run_diagnostics(
        host=args.host,
        port=args.port,
        timeout=args.timeout,
        codex_config=Path(args.codex_config),
        mcp_root=Path(args.mcp_root),
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0 if report["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
