import { test } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

function fixture(t) {
  const sandbox = makeSandbox({ withIndexHtml: true });
  t.after(sandbox.cleanup);
  return sandbox;
}

test("window registry matches the desktop", (t) => {
  const result = fixture(t).run("validate-windows.mjs");
  assert.equal(result.code, 0, result.stdout + result.stderr);
});

test("window labels must be strings", (t) => {
  const sandbox = fixture(t);
  sandbox.mutate("windows.json", (registry) => { registry.windows[0].label = 42; });
  const result = sandbox.run("validate-windows.mjs");
  assert.equal(result.code, 1, result.stdout + result.stderr);
  assert.match(result.stderr, /label.*must be a string/);
});

for (const value of [null, {}, "windows"]) {
  test(`reports a non-array window collection: ${JSON.stringify(value)}`, (t) => {
    const sandbox = fixture(t);
    sandbox.mutate("windows.json", (registry) => { registry.windows = value; });
    const result = sandbox.run("validate-windows.mjs");
    assert.equal(result.code, 1);
    assert.match(result.stderr, /windows must be an array/);
    assert.doesNotMatch(result.stderr, /TypeError/);
  });
}

test("reports a non-object window entry", (t) => {
  const sandbox = fixture(t);
  sandbox.mutate("windows.json", (registry) => { registry.windows[0] = null; });
  const result = sandbox.run("validate-windows.mjs");
  assert.equal(result.code, 1);
  assert.match(result.stderr, /window\[0\].*must be an object/);
  assert.doesNotMatch(result.stderr, /TypeError/);
});

test("checks window drift read-only, then regenerates from the registry", (t) => {
  const sandbox = fixture(t);
  const before = sandbox.readRaw("index.html");
  sandbox.mutate("windows.json", (registry) => { registry.windows[0].label = "Updated home"; });
  const stale = sandbox.run("sync-windows.mjs", ["--check"]);
  assert.equal(stale.code, 1);
  assert.match(stale.stderr, /OUT OF SYNC/);
  assert.equal(sandbox.readRaw("index.html"), before);
  assert.equal(sandbox.run("sync-windows.mjs").code, 0);
  assert.equal(sandbox.run("sync-windows.mjs", ["--check"]).code, 0);
});
