import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox(); });
afterEach(() => sandbox.cleanup());

test("accepts the real, unmodified product registry", () => {
  const { code, stdout } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 0, "expected exit 0 on valid registry");
  assert.match(stdout, /valid/);
});

test("rejects a product with a missing required field", () => {
  sandbox.mutate("products.json", (r) => { delete r.products[0].role; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /missing required field "role"/);
});

test("rejects a product with an unknown field", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].bogus = "x"; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /unknown field "bogus"/);
});

test("rejects an invalid status enum value", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].status = "shipped"; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /"status"="shipped" not in/);
});

test("rejects a number that fails the two-digit pattern", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].number = "1"; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /fails pattern/);
});

test("rejects id != slug", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].slug = r.products[0].id + "x"; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /id .* != slug/);
});

test("rejects a duplicate product number", () => {
  sandbox.mutate("products.json", (r) => { r.products[1].number = r.products[0].number; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /duplicate number/);
});

test("rejects the wrong product count", () => {
  sandbox.mutate("products.json", (r) => { r.products.pop(); });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /expected 27 products, found 26/);
});

test("rejects a non-string item inside a string array field", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].does = ["ok", 42]; });
  const { code, stderr } = sandbox.run("validate-registry.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /must be a string/);
});
