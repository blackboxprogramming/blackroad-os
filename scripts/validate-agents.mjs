#!/usr/bin/env node
/**
 * validate-agents.mjs
 *
 * Dependency-free guard for Registry/agents.json, mirroring validate-registry.mjs
 * for products. Enforces Registry/schemas/agent.schema.json plus cross-record
 * invariants: exactly 27 agents, contiguous numbers 01..27, unique id/slug/number,
 * and total_agents matching the array length.
 *
 *   node scripts/validate-agents.mjs   # exit 1 on any violation
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "Registry", "agents.json"), "utf8"));
const schema = JSON.parse(readFileSync(join(root, "Registry", "schemas", "agent.schema.json"), "utf8"));

const errors = [];
const fail = (msg) => errors.push(msg);

const agents = reg.agents;
if (!Array.isArray(agents)) fail("agents must be an array");
if (agents && agents.length !== 27) fail(`expected 27 agents, found ${agents?.length}`);
if (reg.total_agents !== undefined && reg.total_agents !== agents?.length) {
  fail(`total_agents (${reg.total_agents}) != agents.length (${agents?.length})`);
}

const seenId = new Set(), seenSlug = new Set(), seenNum = new Set();
for (const [i, a] of (agents ?? []).entries()) {
  const where = `agent[${i}] (${a?.name ?? a?.slug ?? "?"})`;
  if (a === null || typeof a !== "object" || Array.isArray(a)) {
    fail(`${where}: must be an object`);
    continue;
  }
  for (const req of schema.required) {
    if (a[req] === undefined) fail(`${where}: missing required field "${req}"`);
  }
  for (const [key, val] of Object.entries(a)) {
    const spec = schema.properties[key];
    if (!spec) { fail(`${where}: unknown field "${key}"`); continue; }
    if (spec.type === "integer" && !Number.isInteger(val)) fail(`${where}: "${key}" must be an integer`);
    if (spec.type === "string" && typeof val !== "string") fail(`${where}: "${key}" must be a string`);
    if (spec.type === "array") {
      if (!Array.isArray(val)) fail(`${where}: "${key}" must be an array`);
      else if (spec.items?.type === "string") {
        val.forEach((item, j) => {
          if (typeof item !== "string") fail(`${where}: "${key}[${j}]" must be a string`);
        });
      }
    }
  }
  if (a.number && !/^[0-9]{2}$/.test(a.number)) fail(`${where}: number "${a.number}" must be two digits`);
  if (a.slug && a.name && a.slug !== a.name.toLowerCase()) {
    fail(`${where}: slug "${a.slug}" != name.toLowerCase() "${a.name.toLowerCase()}"`);
  }
  if (a.id !== undefined) { if (seenId.has(a.id)) fail(`duplicate id "${a.id}"`); seenId.add(a.id); }
  if (a.slug) { if (seenSlug.has(a.slug)) fail(`duplicate slug "${a.slug}"`); seenSlug.add(a.slug); }
  if (a.number) { if (seenNum.has(a.number)) fail(`duplicate number "${a.number}"`); seenNum.add(a.number); }
}

for (let n = 1; n <= 27; n++) {
  const k = String(n).padStart(2, "0");
  if (!seenNum.has(k)) fail(`missing agent number "${k}"`);
}

if (errors.length) {
  console.error(`✗ Registry/agents.json invalid (${errors.length} error(s)):`);
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log(`✓ Registry/agents.json valid — 27 agents, schema + invariants OK`);
