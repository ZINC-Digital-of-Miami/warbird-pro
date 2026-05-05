from __future__ import annotations

from pathlib import Path

from scripts.ag import tv_connection_doctor as doctor


def test_load_codex_path_missing_config(tmp_path: Path) -> None:
    missing = tmp_path / "missing.toml"
    path, msg = doctor._load_codex_tradingview_server_path(missing)
    assert path is None
    assert "missing config" in msg


def test_load_codex_path_valid_config(tmp_path: Path) -> None:
    cfg = tmp_path / "config.toml"
    cfg.write_text(
        """
[mcp_servers.tradingview]
command = "/opt/homebrew/bin/node"
args = ["/tmp/tradingview-mcp/src/server.js"]
""".strip()
    )
    path, msg = doctor._load_codex_tradingview_server_path(cfg)
    assert msg == "ok"
    assert path == "/tmp/tradingview-mcp/src/server.js"


def test_run_diagnostics_ready(monkeypatch, tmp_path: Path) -> None:
    codex_cfg = tmp_path / "config.toml"
    mcp_root = tmp_path / "tradingview-mcp"
    server_js = mcp_root / "src" / "server.js"
    cli_js = mcp_root / "src" / "cli" / "index.js"
    server_js.parent.mkdir(parents=True)
    cli_js.parent.mkdir(parents=True)
    server_js.write_text("// server")
    cli_js.write_text("// cli")
    codex_cfg.write_text(
        f"""
[mcp_servers.tradingview]
args = ["{server_js}"]
""".strip()
    )

    def fake_http_json(url: str, timeout: float):
        if url.endswith("/json/version"):
            return True, "ok", {"Browser": "TradingView"}
        if url.endswith("/json/list"):
            return True, "ok", [{"type": "page", "url": "https://www.tradingview.com/chart/"}]
        return False, "unexpected", None

    def fake_run_cmd(args: list[str], timeout: float = 3.0):
        cmd = " ".join(args)
        if cmd == "pgrep -fal TradingView":
            return 0, "123 /Applications/TradingView.app/Contents/MacOS/TradingView", ""
        if cmd.startswith("node ") and cmd.endswith(" status"):
            return 0, '{"success":true,"cdp_connected":true}', ""
        if cmd == "pgrep -fal tradingview-mcp/src/server.js":
            return 0, "456 node /tmp/tradingview-mcp/src/server.js", ""
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(doctor, "_http_json", fake_http_json)
    monkeypatch.setattr(doctor, "_run_cmd", fake_run_cmd)

    report = doctor.run_diagnostics(
        host="localhost",
        port=9222,
        timeout=1.0,
        codex_config=codex_cfg,
        mcp_root=mcp_root,
    )
    assert report["ready"] is True


def test_run_diagnostics_not_ready_when_cdp_down(monkeypatch, tmp_path: Path) -> None:
    codex_cfg = tmp_path / "config.toml"
    mcp_root = tmp_path / "tradingview-mcp"
    server_js = mcp_root / "src" / "server.js"
    cli_js = mcp_root / "src" / "cli" / "index.js"
    server_js.parent.mkdir(parents=True)
    cli_js.parent.mkdir(parents=True)
    server_js.write_text("// server")
    cli_js.write_text("// cli")
    codex_cfg.write_text(
        f"""
[mcp_servers.tradingview]
args = ["{server_js}"]
""".strip()
    )

    def fake_http_json(url: str, timeout: float):
        return False, "connection refused", None

    def fake_run_cmd(args: list[str], timeout: float = 3.0):
        cmd = " ".join(args)
        if cmd == "pgrep -fal TradingView":
            return 0, "123 /Applications/TradingView.app/Contents/MacOS/TradingView", ""
        if cmd.startswith("node ") and cmd.endswith(" status"):
            return 2, "", '{"success":false,"error":"CDP connection failed after 5 attempts: fetch failed"}'
        if cmd == "pgrep -fal tradingview-mcp/src/server.js":
            return 0, "456 node /tmp/tradingview-mcp/src/server.js", ""
        raise AssertionError(f"Unexpected command: {cmd}")

    monkeypatch.setattr(doctor, "_http_json", fake_http_json)
    monkeypatch.setattr(doctor, "_run_cmd", fake_run_cmd)

    report = doctor.run_diagnostics(
        host="localhost",
        port=9222,
        timeout=1.0,
        codex_config=codex_cfg,
        mcp_root=mcp_root,
    )
    assert report["ready"] is False
    failing = {ch["name"] for ch in report["checks"] if not ch["ok"]}
    assert "cdp_endpoint" in failing
    assert "mcp_status_cli" in failing
