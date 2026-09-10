#!/usr/bin/env node
/**
 * sync-product-folders.mjs
 *
 * Single source of truth = Registry/products.json.
 * Each Products/NN_Name/product.json is a *generated projection* of the matching
 * registry record — byte-for-byte the canon object, nothing more. This kills the
 * old per-folder schema (id:1, primary_agents, next_action, …) that had drifted
 * away from the registry, so there is exactly one product schema in the repo.
 *
 *   node scripts/sync-product-folders.mjs          # write every product.json
 *   node scripts/sync-product-folders.mjs --check   # exit 1 if any is missing/stale (CI)
 *
 * Every registry product has a Products/NN_Name/ folder (including HighWay/18).
 * Folders are matched by their NN_ prefix.
 */
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const PRODUCTS_DIR = join(root, "Products");
const REGISTRY = join(root, "Registry", "products.json");

const reg = JSON.parse(readFileSync(REGISTRY, "utf8"));

// number ("01") -> folder name ("01_RoadOS"), from the folders that exist on disk
const folderByNumber = new Map();
for (const name of readdirSync(PRODUCTS_DIR, { withFileTypes: true })) {
  if (!name.isDirectory()) continue;
  const m = /^(\d{2})_/.exec(name.name);
  if (m) folderByNumber.set(m[1], name.name);
}

const serialize = (record) => JSON.stringify(record, null, 2) + "\n";

const check = process.argv.includes("--check");
const stale = [];
const written = [];
const missing = [];

for (const p of reg.products) {
  const folder = folderByNumber.get(p.number);
  if (!folder) { missing.push(`Products/${p.number}_* (for ${p.name})`); continue; }
  const file = join(PRODUCTS_DIR, folder, "product.json");
  const want = serialize(p);
  const have = existsSync(file) ? readFileSync(file, "utf8") : null;
  if (have === want) continue;
  if (check) { stale.push(`Products/${folder}/product.json`); continue; }
  writeFileSync(file, want);
  written.push(`Products/${folder}/product.json`);
}

if (check) {
  if (stale.length || missing.length) {
    if (stale.length) {
      console.error(`✗ ${stale.length} per-folder product.json out of sync with the registry:`);
      for (const s of stale) console.error("  - " + s);
    }
    if (missing.length) {
      console.error(`✗ ${missing.length} registry product(s) with no Products/ folder (drift):`);
      for (const m of missing) console.error("  - " + m);
    }
    console.error("  Run: node scripts/sync-product-folders.mjs  then commit Products/.");
    process.exit(1);
  }
  console.log(`✓ All per-folder product.json are in sync with Registry/products.json (${reg.products.length}/${reg.products.length})`);
} else {
  console.log(`✓ Wrote ${written.length} product.json from the registry` +
    (written.length ? " (" + written.length + " updated)" : " (all already current)"));
}
