#!/usr/bin/env node
/**
 * validate-references.mjs
 *
 * Cross-registry referential-integrity guard. The per-file validators
 * (validate-registry, validate-agents, validate-collections) each check a
 * single registry in isolation — they confirm a record is well-formed, but
 * NOT that the ids it points at actually exist elsewhere. This closes that
 * gap: it resolves the foreign keys that link the registries together, so a
 * typo or a rename in one file can no longer silently dangle.
 *
 * Foreign keys checked (product record -> target registry):
 *   - product.agents[]  ->  Registry/agents.json   (by agent name)      [ERROR]
 *   - product.domain    ->  Registry/domains.json  (by registrable root) [ERROR]
 *   - product.org       ->  Registry/orgs.json     (by org name)         [WARN]
 *
 * Why org is WARN, not ERROR: the current registry already contains org
 * references that resolve to no org record (e.g. "BlackRoad-Agents",
 * "BlackRoad-Knowledge", "BlackRoad-Private" vs the "BlackRoad-OS-*" org
 * names). Deciding the correct org for each product is a canon call for the
 * operator, not something this script should guess. So org mismatches are
 * surfaced loudly but do not fail CI yet. Once the canon is reconciled,
 * flip ORG_SEVERITY to "error" (one line) to lock it down.
 *
 *   node scripts/validate-references.mjs   # exit 1 on any ERROR-level dangling ref
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = process.env.BLACKROAD_ROOT || join(dirname(fileURLToPath(import.meta.url)), "..");
const load = (p) => JSON.parse(readFileSync(join(root, p), "utf8"));

// Flip to "error" once org references are reconciled with Registry/orgs.json.
const ORG_SEVERITY = "warn";

const products = load("Registry/products.json").products;
const agentNames = new Set(load("Registry/agents.json").agents.map((a) => a.name));
const orgNames = new Set(load("Registry/orgs.json").organizations.map((o) => o.name));
const rootDomains = load("Registry/domains.json").domains.map((d) => d.name);

// A product domain "carkeys.blackroad.io" is valid if it equals, or is a
// subdomain of, a registered root domain "blackroad.io".
const domainIsRegistered = (d) =>
  rootDomains.some((r) => d === r || d.endsWith("." + r));

const errors = [];
const warnings = [];
const note = (sev, msg) => (sev === "error" ? errors : warnings).push(msg);

for (const p of products) {
  const where = `product ${p.number} (${p.name})`;

  for (const agent of p.agents ?? []) {
    if (!agentNames.has(agent)) {
      note("error", `${where}: agents[] references unknown agent "${agent}"`);
    }
  }

  if (p.domain && !domainIsRegistered(p.domain)) {
    note("error", `${where}: domain "${p.domain}" is not under any registered root domain`);
  }

  if (p.org && !orgNames.has(p.org)) {
    note(ORG_SEVERITY, `${where}: org "${p.org}" is not a registered organization name`);
  }
}

if (warnings.length) {
  console.warn(`⚠ ${warnings.length} referential warning(s) (non-fatal):`);
  for (const w of warnings) console.warn("  - " + w);
}

if (errors.length) {
  console.error(`✗ ${errors.length} dangling cross-registry reference(s):`);
  for (const e of errors) console.error("  - " + e);
  console.error("  Fix the reference in Registry/products.json to match the target registry.");
  process.exit(1);
}

console.log(
  `✓ Cross-registry references resolve — ${products.length} products checked against ` +
  `agents/domains/orgs` + (warnings.length ? ` (${warnings.length} org warning(s), non-fatal)` : "")
);
