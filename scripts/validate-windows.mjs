#!/usr/bin/env node
/**
 * validate-windows.mjs
 *
 * Dependency-free guard for Registry/windows.json. Enforces the schema AND
 * cross-checks the manifest against index.html so the registry can never claim
 * a window that doesn't exist (or miss one that does):
 *   - every window's elementId exists as id="...Window" in index.html
 *   - every window's openFn and closeFn are declared in index.html
 *   - every real window element in index.html (those wired with a close handler)
 *     is present in the registry — no orphans
 *
 *   node scripts/validate-windows.mjs   # exit 1 on any violation
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const reg = JSON.parse(readFileSync(join(root, "Registry", "windows.json"), "utf8"));
const schema = JSON.parse(readFileSync(join(root, "Registry", "schemas", "window.schema.json"), "utf8"));
const html = readFileSync(join(root, "index.html"), "utf8");

const errors = [];
const fail = (m) => errors.push(m);
const windows = reg.windows;

if (!Array.isArray(windows)) fail("windows must be an array");

const seenId = new Set(), seenEl = new Set();
for (const [i, w] of (windows ?? []).entries()) {
  const where = `window[${i}] (${w?.id ?? "?"})`;
  for (const req of schema.required) {
    if (w[req] === undefined) fail(`${where}: missing required field "${req}"`);
  }
  for (const [key, val] of Object.entries(w)) {
    const spec = schema.properties[key];
    if (!spec) { fail(`${where}: unknown field "${key}"`); continue; }
    if (spec.enum && !spec.enum.includes(val)) fail(`${where}: "${key}"="${val}" not in [${spec.enum.join(", ")}]`);
    if (spec.pattern && !new RegExp(spec.pattern).test(String(val))) fail(`${where}: "${key}"="${val}" fails ${spec.pattern}`);
  }
  if (w.id) { if (seenId.has(w.id)) fail(`duplicate id "${w.id}"`); seenId.add(w.id); }
  if (w.elementId) { if (seenEl.has(w.elementId)) fail(`duplicate elementId "${w.elementId}"`); seenEl.add(w.elementId); }

  // cross-check against index.html
  if (w.elementId && !html.includes(`id="${w.elementId}"`)) fail(`${where}: id="${w.elementId}" not found in index.html`);
  if (w.openFn && !new RegExp(`function ${w.openFn}\\b`).test(html)) fail(`${where}: function ${w.openFn}() not declared in index.html`);
  if (w.closeFn && !new RegExp(`function ${w.closeFn}\\b`).test(html)) fail(`${where}: function ${w.closeFn}() not declared in index.html`);
}

// No orphans: every element wired with a closeXxx handler should be registered.
// Source of truth for "is a real window" = `function close<Name>()` declarations
// whose <name>Window element exists.
const declaredClose = [...html.matchAll(/function (close[A-Za-z]+)\s*\(\s*\)/g)].map((m) => m[1]);
for (const fn of declaredClose) {
  const base = fn.slice("close".length);
  const elementId = base[0].toLowerCase() + base.slice(1) + "Window";
  if (html.includes(`id="${elementId}"`) && !seenEl.has(elementId)) {
    fail(`orphan window "${elementId}" (has ${fn}) is not in Registry/windows.json`);
  }
}

if (errors.length) {
  console.error(`✗ Registry/windows.json invalid (${errors.length} error(s)):`);
  for (const e of errors) console.error("  - " + e);
  process.exit(1);
}
console.log(`✓ Registry/windows.json valid — ${windows.length} windows, schema + DOM cross-check OK`);
