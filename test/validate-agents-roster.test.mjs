import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox({ withIndexHtml: true }); });
afterEach(() => sandbox.cleanup());

test("passes when the roster matches index.html", () => {
  const { code, stdout } = sandbox.run("validate-agents-roster.mjs");
  assert.equal(code, 0);
  assert.match(stdout, /in sync/);
});

test("fails when an agent is renamed in the registry only", () => {
  sandbox.mutate("agents.json", (r) => {
    r.agents[0].slug = "renamed-agent";
    r.agents[0].name = "Renamed-Agent";
  });
  const { code, stderr } = sandbox.run("validate-agents-roster.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /out of sync/);
  assert.match(stderr, /renamed-agent/);
});

test("fails when the registry has an agent index.html lacks", () => {
  // Drop the AGENTS array's first entry from index.html so counts diverge.
  const html = sandbox.readRaw("index.html");
  const patched = html.replace(/const AGENTS = \[\s*\{[\s\S]*?\},/, "const AGENTS = [");
  assert.notEqual(patched, html, "expected to modify the AGENTS array");
  sandbox.writeRaw("index.html", patched);
  const { code, stderr } = sandbox.run("validate-agents-roster.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /out of sync/);
});

test("fails cleanly when the AGENTS array cannot be located", () => {
  const html = sandbox.readRaw("index.html");
  sandbox.writeRaw("index.html", html.replace("const AGENTS =", "const ROSTER ="));
  const { code, stderr } = sandbox.run("validate-agents-roster.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /could not locate the AGENTS array/);
});
