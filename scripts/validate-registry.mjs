#!/usr/bin/env node
/**
 * validate-registry.mjs
 *
 * Dependency-free guard for Registry/products.json. Enforces the contract in
 * Registry/schemas/product.schema.json plus cross-record invariants, so no
 * agent (Claude, Grok, anyone) can merge malformed canon.
 *
 *   node scripts/validate-registry.mjs   # exit 1 on any violation
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "Registry", "products.json"), "utf8"));
const schema = JSON.parse(readFileSync(join(root, "Registry", "schemas", "product.schema.json"), "utf8"));

const errors = [];
const fail = (msg) => errors.push(msg);

const products = reg.products;
if (!Array.isArray(products)) fail("products must be an array");
if (products.length !== 27) fail(`expected 27 products, found ${products?.length}`);

const seenId = new Set(), seenNum = new Set();
for (const [i, p] of (products ?? []).entries()) {
  const where = `product[${i}] (${p?.name ?? p?.id ?? "?"})`;

  for (const req of schema.required) {
    if (p[req] === undefined) fail(`${where}: missing required field "${req}"`);
  }
  for (const [key, val] of Object.entries(p)) {
    const spec = schema.properties[key];
    if (!spec) { fail(`${where}: unknown field "${key}"`); continue; }
    if (spec.enum && !spec.enum.includes(val)) {
      fail(`${where}: "${key}"="${val}" not in [${spec.enum.join(", ")}]`);
    }
    if (spec.type === "array" && !Array.isArray(val)) fail(`${where}: "${key}" must be an array`);
    if (spec.type === "string" && typeof val !== "string") fail(`${where}: "${key}" must be a string`);
    if (spec.pattern && typeof val === "string" && !new RegExp(spec.pattern).test(val)) {
      fail(`${where}: "${key}"="${val}" fails pattern ${spec.pattern}`);
    }
  }
  if (p.id && p.slug && p.id !== p.slug) fail(`${where}: id "${p.id}" != slug "${p.slug}"`);
  if (p.id) { if (seenId.has(p.id)) fail(`duplicate id "${p.id}"`); seenId.add(p.id); }
  if (p.number) { if (seenNum.has(p.number)) fail(`duplicate number "${p.number}"`); seenNum.add(p.number); }
}

// numbers must be the contiguous set 01..27
for (let n = 1; n <= 27; n++) {
  const k = String(n).padStart(2, "0");
  if (!seenNum.has(k)) fail(`missing product number "${k}"`);
}

if (errors.length) {
  console.error(`✗ Registry/products.json invalid (${errors.length} error(s)):`);
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log(`✓ Registry/products.json valid — 27 products, schema + invariants OK`);
