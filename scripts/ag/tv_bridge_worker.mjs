#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { pathToFileURL } from "node:url";

if (process.env.WB_ALLOW_LEGACY_TV_BRIDGE !== "1") {
  console.error(
    "[blocked] tv_bridge_worker.mjs is a legacy MCP bridge path and is disabled by default.\n" +
      "Use direct CDP flow via scripts/ag/tv_auto_tune.py instead."
  );
  process.exit(2);
}

function resolveTradingviewMcpRoot() {
  const fromEnv = process.env.WB_TRADINGVIEW_MCP_ROOT;
  const candidates = [
    fromEnv,
    path.resolve(process.cwd(), ".tradingview-mcp"),
    "/Users/zincdigital/tradingview-mcp",
  ].filter(Boolean);

  for (const root of candidates) {
    const connectionPath = path.join(root, "src", "connection.js");
    if (fs.existsSync(connectionPath)) {
      return { root, connectionPath };
    }
  }
  throw new Error(
    "Legacy bridge could not locate tradingview-mcp connection.js. " +
      "Set WB_TRADINGVIEW_MCP_ROOT or restore a valid tradingview-mcp checkout."
  );
}

const { connectionPath } = resolveTradingviewMcpRoot();
const { evaluate, getTargetInfo } = await import(pathToFileURL(connectionPath).href);

function normalizeResult(result) {
  if (result && typeof result === "object") {
    if (result.result && Object.prototype.hasOwnProperty.call(result.result, "value")) {
      return result.result.value;
    }
    if (Object.prototype.hasOwnProperty.call(result, "value")) {
      return result.value;
    }
  }
  return result;
}

async function handle(msg) {
  if (!msg || typeof msg !== "object") {
    return { ok: false, error: "Invalid message payload" };
  }

  if (msg.cmd === "health") {
    const target = await getTargetInfo();
    return { ok: true, target };
  }

  if (msg.cmd === "eval") {
    if (typeof msg.expr !== "string" || msg.expr.length === 0) {
      return { ok: false, error: "eval requires non-empty expr" };
    }
    const raw = await evaluate(msg.expr, msg.opts && typeof msg.opts === "object" ? msg.opts : {});
    return { ok: true, value: normalizeResult(raw) };
  }

  if (msg.cmd === "close") {
    return { ok: true, closing: true };
  }

  return { ok: false, error: `Unknown cmd: ${msg.cmd}` };
}

const rl = readline.createInterface({
  input: process.stdin,
  crlfDelay: Infinity,
});

for await (const line of rl) {
  const trimmed = line.trim();
  if (!trimmed) {
    continue;
  }

  let msg;
  try {
    msg = JSON.parse(trimmed);
  } catch (err) {
    process.stdout.write(JSON.stringify({ ok: false, error: `Invalid JSON: ${err.message}` }) + "\n");
    continue;
  }

  try {
    const out = await handle(msg);
    process.stdout.write(JSON.stringify({ id: msg.id ?? null, ...out }) + "\n");
    if (out.closing) {
      break;
    }
  } catch (err) {
    process.stdout.write(
      JSON.stringify({
        id: msg.id ?? null,
        ok: false,
        error: err instanceof Error ? err.message : String(err),
      }) + "\n"
    );
  }
}
