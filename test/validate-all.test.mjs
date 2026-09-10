import { test } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

function fixture(t) {
  const sandbox = makeSandbox({ withIndexHtml: true, withProducts: true });
  t.after(sandbox.cleanup);
  return sandbox;
}

test("full suite accepts synchronized registries and projections", (t) => {
  const result = fixture(t).run("validate-all.mjs");
  assert.equal(result.code, 0, result.stdout + result.stderr);
});

test("full suite rejects stale domain projections without rewriting the desktop", (t) => {
  const sandbox = fixture(t);
  const before = sandbox.readRaw("index.html");
  sandbox.mutate("domains.json", (registry) => {
    registry.domains[0].board = "Changed domain board";
  });
  const result = sandbox.run("validate-all.mjs");
  assert.equal(result.code, 1, result.stdout + result.stderr);
  assert.match(result.stdout + result.stderr, /Generated Collections/);
  assert.match(result.stdout + result.stderr, /OUT OF SYNC|out of sync/);
  assert.equal(sandbox.readRaw("index.html"), before);
});

test("full suite retains the newer cross-registry reference guard", (t) => {
  const sandbox = fixture(t);
  sandbox.mutate("products.json", (registry) => {
    registry.products[0].domain = "unknown.invalid";
  });
  assert.equal(sandbox.run("sync-products.mjs").code, 0);
  assert.equal(sandbox.run("sync-product-folders.mjs").code, 0);
  const result = sandbox.run("validate-all.mjs");
  assert.equal(result.code, 1, result.stdout + result.stderr);
  assert.match(result.stdout + result.stderr, /Cross-Registry References/);
  assert.match(result.stdout + result.stderr, /unknown\.invalid/);
});
