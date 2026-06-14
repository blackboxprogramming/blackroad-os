#!/usr/bin/env node
/**
 * sync-collections.mjs
 *
 * Generic version of sync-products.mjs for the other registry-backed arrays
 * embedded in index.html. Each block between AUTO-GENERATED:<NAME>:START / END
 * markers is regenerated from its registry file so the rendered desktop can
 * never drift from canon. index.html stays a self-contained, double-clickable file.
 *
 *   node scripts/sync-collections.mjs          # write index.html in place
 *   node scripts/sync-collections.mjs --check  # exit 1 if out of sync (CI)
 */
import { readFileSync, writeFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const HTML = join(root, "index.html");

const TARGETS = [
  { name: "ORGS", file: "Registry/orgs.json", key: "organizations" },
  { name: "DOMAINS", file: "Registry/domains.json", key: "domains" },
];

function buildBlock(t) {
  const reg = JSON.parse(readFileSync(join(root, t.file), "utf8"));
  const body = JSON.stringify(reg[t.key], null, 2)
    .split("\n").map((l) => "  " + l).join("\n");
  return `  const ${t.name} =\n${body};`;
}

function renderOne(html, t) {
  const START = `/* AUTO-GENERATED:${t.name}:START`;
  const END = `/* AUTO-GENERATED:${t.name}:END */`;
  const s = html.indexOf(START);
  const e = html.indexOf(END);
  if (s === -1 || e === -1) throw new Error(`${t.name} markers not found in index.html`);
  const startLineEnd = html.indexOf("\n", s) + 1; // keep START marker line
  return html.slice(0, startLineEnd) + buildBlock(t) + "\n  " + html.slice(e);
}

const check = process.argv.includes("--check");
const current = readFileSync(HTML, "utf8");
let next = current;
for (const t of TARGETS) next = renderOne(next, t);

if (current === next) {
  console.log("✓ index.html ORGS + DOMAINS are in sync with their registries");
  process.exit(0);
}
if (check) {
  console.error("✗ index.html ORGS/DOMAINS are OUT OF SYNC with Registry/orgs.json|domains.json.");
  console.error("  Run: node scripts/sync-collections.mjs  then commit index.html");
  process.exit(1);
}
writeFileSync(HTML, next);
console.log("✓ Regenerated ORGS + DOMAINS blocks in index.html from their registries");
