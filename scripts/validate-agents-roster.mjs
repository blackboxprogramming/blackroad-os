#!/usr/bin/env node
/**
 * validate-agents-roster.mjs
 *
 * Anti-drift cross-check between the two places the agent roster appears:
 *   - Registry/agents.json (canon roster, single source of truth)
 *   - the inline AGENTS array rendered by index.html (richer UI fields)
 *
 * The desktop array carries extra UI/runtime fields (can/status/note/task/...)
 * and intentionally phrases roles differently, so this guard does NOT compare
 * role text — it only enforces that both list the *same 27 agent identities*.
 * Adding, removing, or renaming an agent in one place without the other fails.
 *
 *   node scripts/validate-agents-roster.mjs   # exit 1 on any mismatch
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "Registry", "agents.json"), "utf8"));
const html = readFileSync(join(root, "index.html"), "utf8");

const m = html.match(/const AGENTS = (\[[\s\S]*?\n {2}\]);/);
if (!m) {
  console.error("✗ could not locate the AGENTS array in index.html");
  process.exit(1);
}
const indexIds = Function(`"use strict";return (${m[1]});`)().map((a) => a.id);
const regSlugs = reg.agents.map((a) => a.slug);

const errors = [];
const setReg = new Set(regSlugs);
const setIdx = new Set(indexIds);
for (const slug of regSlugs) if (!setIdx.has(slug)) errors.push(`in Registry/agents.json but not index.html AGENTS: "${slug}"`);
for (const id of indexIds) if (!setReg.has(id)) errors.push(`in index.html AGENTS but not Registry/agents.json: "${id}"`);
if (indexIds.length !== regSlugs.length) {
  errors.push(`count mismatch: registry ${regSlugs.length} vs index ${indexIds.length}`);
}

if (errors.length) {
  console.error(`✗ agent roster out of sync between Registry/agents.json and index.html:`);
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log(`✓ Agent roster in sync — ${regSlugs.length} identities match across Registry/agents.json and index.html`);
