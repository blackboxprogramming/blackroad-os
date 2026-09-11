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
 * Foreign keys checked (record -> target registry):
 *   - product.agents[]  ->  Registry/agents.json   (by agent name)      [ERROR]
 *   - product.domain    ->  Registry/domains.json  (exact root/subdomain) [ERROR]
 *   - product.org       ->  Registry/orgs.json     (by org name)         [WARN]
 *   - domain.products[] ->  Registry/products.json (by product name)     [ERROR]
 *   - domain.agents[]   ->  Registry/agents.json   (by agent name)       [ERROR]
 *   - domain.nextRoads[] -> Registry/domains.json  (exact root/subdomain) [ERROR]
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
import { domainIdentityErrors, isCanonicalHostname, registeredRoot } from "./lib/domains.mjs";

const root = process.env.BLACKROAD_ROOT || join(dirname(fileURLToPath(import.meta.url)), "..");
const load = (p) => JSON.parse(readFileSync(join(root, p), "utf8"));

// Flip to "error" once org references are reconciled with Registry/orgs.json.
const ORG_SEVERITY = "warn";

const products = load("Registry/products.json").products;
const domains = load("Registry/domains.json").domains;
const productNames = new Set(products.map((p) => p.name));
const agentNames = new Set(load("Registry/agents.json").agents.map((a) => a.name));
const orgNames = new Set(load("Registry/orgs.json").organizations.map((o) => o.name));
const rootDomains = Array.isArray(domains) ? domains.map((d) => d?.name) : [];

const errors = domainIdentityErrors(rootDomains).map((error) => `[Registry/domains.json] ${error}`);
if (!Array.isArray(domains)) errors.push('[Registry/domains.json] "domains" must be an array');
const warnings = [];
const note = (sev, msg) => (sev === "error" ? errors : warnings).push(msg);

function checkHostname(value, where) {
  if (!isCanonicalHostname(value)) {
    note("error", `${where}: must be a canonical hostname (lowercase ASCII, valid labels, no URL or trailing dot)`);
  } else if (registeredRoot(value, rootDomains) === null) {
    note("error", `${where}: domain "${value}" is not under any registered root domain (exactly one root required)`);
  }
}

function checkLinks(values, where, check) {
  if (values === undefined) return; // Domain links are optional in the schema.
  if (!Array.isArray(values)) { note("error", `${where}: must be an array`); return; }
  for (const [index, value] of values.entries()) {
    if (typeof value !== "string") note("error", `${where}[${index}]: must be a string`);
    else check(value, `${where}[${index}]`);
  }
}

function checkAgent(agent, where) {
  if (!agentNames.has(agent)) note("error", `${where}: references unknown agent "${agent}"`);
}

for (const p of products) {
  const where = `product ${p.number} (${p.name})`;

  checkLinks(p.agents, `${where}: agents`, checkAgent);
  checkHostname(p.domain, `${where}: domain`);

  if (p.org && !orgNames.has(p.org)) {
    note(ORG_SEVERITY, `${where}: org "${p.org}" is not a registered organization name`);
  }
}

for (const [index, domain] of (Array.isArray(domains) ? domains : []).entries()) {
  if (!domain || typeof domain !== "object" || Array.isArray(domain)) {
    note("error", `domains[${index}]: must be an object`);
    continue;
  }
  const where = `domain ${domain.num} (${domain.name})`;
  checkLinks(domain.products, `${where}: products`, (product, link) => {
    if (!productNames.has(product)) note("error", `${link}: references unknown product "${product}"`);
  });
  checkLinks(domain.agents, `${where}: agents`, checkAgent);
  checkLinks(domain.nextRoads, `${where}: nextRoads`, checkHostname);
}

if (warnings.length) {
  console.warn(`⚠ ${warnings.length} referential warning(s) (non-fatal):`);
  for (const w of warnings) console.warn("  - " + w);
}

if (errors.length) {
  console.error(`✗ ${errors.length} invalid cross-registry reference(s):`);
  for (const e of errors) console.error("  - " + e);
  console.error("  Fix the indicated source record in Registry/products.json or Registry/domains.json to match its target registry.");
  process.exit(1);
}

console.log(
  `✓ Cross-registry references resolve — ${products.length} products and ${domains.length} domains checked against ` +
  `agents/domains/orgs` + (warnings.length ? ` (${warnings.length} org warning(s), non-fatal)` : "")
);
