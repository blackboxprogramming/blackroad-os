#!/usr/bin/env node
/**
 * sync-products.mjs
 *
 * Single source of truth = Registry/products.json.
 * This regenerates the PRODUCTS array embedded in index.html (between the
 * AUTO-GENERATED:PRODUCTS markers) so the rendered desktop can never drift
 * from canon. index.html stays a self-contained, double-click-able file.
 *
 *   node scripts/sync-products.mjs          # write index.html in place
 *   node scripts/sync-products.mjs --check  # exit 1 if out of sync (CI)
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const HTML = join(root, "index.html");
const REGISTRY = join(root, "Registry", "products.json");

const START = "/* AUTO-GENERATED:PRODUCTS:START";
const END = "/* AUTO-GENERATED:PRODUCTS:END */";

// Fields the index.html UI actually consumes, in render order.
const UI_FIELDS = ["number", "id", "name", "role", "status", "meaning",
  "does", "org", "domain", "agents", "receipts", "carkeys", "next"];

function buildBlock() {
  const reg = JSON.parse(readFileSync(REGISTRY, "utf8"));
  const ui = reg.products.map((p) => {
    const o = {};
    for (const f of UI_FIELDS) {
      // index.html names the canon "number" field "num"
      o[f === "number" ? "num" : f] = p[f];
    }
    return o;
  });
  const body = JSON.stringify(ui, null, 2)
    .split("\n").map((l) => "  " + l).join("\n");
  return `  const PRODUCTS =\n${body};`;
}

function render(html) {
  const s = html.indexOf(START);
  const e = html.indexOf(END);
  if (s === -1 || e === -1) {
    throw new Error("PRODUCTS markers not found in index.html");
  }
  const startLineEnd = html.indexOf("\n", s) + 1; // keep START marker line
  const block = buildBlock();
  return html.slice(0, startLineEnd) + block + "\n  " + html.slice(e);
}

const check = process.argv.includes("--check");
const current = readFileSync(HTML, "utf8");
const next = render(current);

if (current === next) {
  console.log("✓ index.html PRODUCTS is in sync with Registry/products.json");
  process.exit(0);
}
if (check) {
  console.error("✗ index.html PRODUCTS is OUT OF SYNC with Registry/products.json.");
  console.error("  Run: node scripts/sync-products.mjs  then commit index.html");
  process.exit(1);
}
writeFileSync(HTML, next);
console.log("✓ Regenerated PRODUCTS block in index.html from Registry/products.json");
