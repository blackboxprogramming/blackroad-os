#!/usr/bin/env node
/**
 * sync-windows.mjs
 *
 * Single source of truth = Registry/windows.json.
 * Regenerates the WINDOW_REGISTRY array embedded in index.html (between the
 * AUTO-GENERATED:WINDOWS markers). The ACTION_TO_ROUTE and CLOSE_BY_WIN_ID
 * maps in index.html derive from WINDOW_REGISTRY at runtime, so this manifest
 * is the load-bearing list of every OS window.
 *
 *   node scripts/sync-windows.mjs          # write index.html in place
 *   node scripts/sync-windows.mjs --check  # exit 1 if out of sync (CI)
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const HTML = join(root, "index.html");
const REGISTRY = join(root, "Registry", "windows.json");

const START = "/* AUTO-GENERATED:WINDOWS:START";
const END = "/* AUTO-GENERATED:WINDOWS:END */";

const FIELDS = ["id", "label", "type", "kind", "status", "elementId", "openFn", "closeFn"];

function buildBlock() {
  const reg = JSON.parse(readFileSync(REGISTRY, "utf8"));
  const rows = reg.windows.map((w) => {
    const o = {};
    for (const f of FIELDS) o[f] = w[f];
    return o;
  });
  const body = JSON.stringify(rows, null, 2).split("\n").map((l) => "  " + l).join("\n");
  return `  const WINDOW_REGISTRY =\n${body};`;
}

function render(html) {
  const s = html.indexOf(START);
  const e = html.indexOf(END);
  if (s === -1 || e === -1) throw new Error("WINDOWS markers not found in index.html");
  const startLineEnd = html.indexOf("\n", s) + 1; // keep START marker line
  return html.slice(0, startLineEnd) + buildBlock() + "\n  " + html.slice(e);
}

const check = process.argv.includes("--check");
const current = readFileSync(HTML, "utf8");
const next = render(current);

if (current === next) {
  console.log("✓ index.html WINDOW_REGISTRY is in sync with Registry/windows.json");
  process.exit(0);
}
if (check) {
  console.error("✗ index.html WINDOW_REGISTRY is OUT OF SYNC with Registry/windows.json.");
  console.error("  Run: node scripts/sync-windows.mjs  then commit index.html");
  process.exit(1);
}
writeFileSync(HTML, next);
console.log("✓ Regenerated WINDOW_REGISTRY block in index.html from Registry/windows.json");
