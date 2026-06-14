#!/usr/bin/env node
/**
 * validate-collections.mjs
 *
 * Dependency-free guard for the registry-backed collections that are NOT
 * products or agents — currently Registry/orgs.json and Registry/domains.json.
 * Enforces each record's schema plus cross-record invariants: exactly 20 entries,
 * contiguous numbers 01..20, unique id/num, and a matching total_* count.
 *
 *   node scripts/validate-collections.mjs   # exit 1 on any violation
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");

const COLLECTIONS = [
  { file: "Registry/orgs.json", schema: "Registry/schemas/organization.schema.json",
    key: "organizations", total: "total_organizations", count: 20, label: "organizations" },
  { file: "Registry/domains.json", schema: "Registry/schemas/domain.schema.json",
    key: "domains", total: "total_domains", count: 20, label: "root domains" },
];

const errors = [];
const load = (p) => JSON.parse(readFileSync(join(root, p), "utf8"));

for (const c of COLLECTIONS) {
  const fail = (msg) => errors.push(`[${c.file}] ${msg}`);
  const reg = load(c.file);
  const schema = load(c.schema);
  const rows = reg[c.key];

  if (!Array.isArray(rows)) { fail(`"${c.key}" must be an array`); continue; }
  if (rows.length !== c.count) fail(`expected ${c.count} ${c.label}, found ${rows.length}`);
  if (reg[c.total] !== undefined && reg[c.total] !== rows.length) {
    fail(`${c.total} (${reg[c.total]}) != ${c.key}.length (${rows.length})`);
  }

  const seenId = new Set(), seenNum = new Set();
  for (const [i, r] of rows.entries()) {
    const where = `${c.key}[${i}] (${r?.name ?? r?.id ?? "?"})`;
    for (const req of schema.required) {
      if (r[req] === undefined) fail(`${where}: missing required field "${req}"`);
    }
    for (const [key, val] of Object.entries(r)) {
      const spec = schema.properties[key];
      if (!spec) { fail(`${where}: unknown field "${key}"`); continue; }
      if (spec.enum && !spec.enum.includes(val)) fail(`${where}: "${key}"="${val}" not in [${spec.enum.join(", ")}]`);
      if (spec.type === "array" && !Array.isArray(val)) fail(`${where}: "${key}" must be an array`);
      if (spec.type === "string" && typeof val !== "string") fail(`${where}: "${key}" must be a string`);
      if (spec.type === "integer" && !Number.isInteger(val)) fail(`${where}: "${key}" must be an integer`);
      if (spec.pattern && typeof val === "string" && !new RegExp(spec.pattern).test(val)) {
        fail(`${where}: "${key}"="${val}" fails pattern ${spec.pattern}`);
      }
    }
    if (r.id) { if (seenId.has(r.id)) fail(`duplicate id "${r.id}"`); seenId.add(r.id); }
    if (r.num) { if (seenNum.has(r.num)) fail(`duplicate num "${r.num}"`); seenNum.add(r.num); }
  }
  for (let n = 1; n <= c.count; n++) {
    const k = String(n).padStart(2, "0");
    if (!seenNum.has(k)) fail(`missing num "${k}"`);
  }
}

if (errors.length) {
  console.error(`✗ collections invalid (${errors.length} error(s)):`);
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log("✓ Registry/orgs.json + domains.json valid — 20 + 20, schema + invariants OK");
