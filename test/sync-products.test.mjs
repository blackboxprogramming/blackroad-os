import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox({ withIndexHtml: true }); });
afterEach(() => sandbox.cleanup());

test("--check passes when index.html is already in sync", () => {
  const { code, stdout } = sandbox.run("sync-products.mjs", ["--check"]);
  assert.equal(code, 0);
  assert.match(stdout, /in sync/);
});

test("--check fails after the registry changes underneath index.html", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].name = "Renamed Product"; });
  const { code, stderr } = sandbox.run("sync-products.mjs", ["--check"]);
  assert.equal(code, 1);
  assert.match(stderr, /OUT OF SYNC/);
});

test("regenerating then re-checking is a stable round-trip", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].name = "Renamed Product"; });
  const write = sandbox.run("sync-products.mjs");
  assert.equal(write.code, 0);
  const check = sandbox.run("sync-products.mjs", ["--check"]);
  assert.equal(check.code, 0, "index.html should be in sync after regeneration");
  assert.match(sandbox.readRaw("index.html"), /Renamed Product/);
});

test("throws clearly when the AUTO-GENERATED markers are missing", () => {
  const html = sandbox.readRaw("index.html");
  sandbox.writeRaw("index.html", html.replace("AUTO-GENERATED:PRODUCTS:START", "REMOVED-MARKER"));
  const { code, stderr } = sandbox.run("sync-products.mjs", ["--check"]);
  assert.notEqual(code, 0);
  assert.match(stderr, /markers not found/);
});
