# Agents MCP Registry

Portable read-only MCP servers under `agents/mcp/`.

These servers are intentionally read-only and platform-independent.

## Servers

- `warbird-status`: repo status and guardrail visibility helpers
- `warbird-fetch`: constrained HTTP/HTTPS fetch helper
- `warbird-filesystem`: read-only filesystem helper with secret-path denylist
- `warbird-github`: read-only GitHub REST helper
- `warbird-supabase-ro`: read-only Supabase REST select helper

Each server includes a `run.sh` launcher that uses project `.venv` when
available, then falls back to `python3`.
