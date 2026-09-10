import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox(); });
afterEach(() => sandbox.cleanup());

test("passes on the real registry (agents + domains resolve)", () => {
  const { code, stdout } = sandbox.run("validate-references.mjs");
  assert.equal(code, 0);
  assert.match(stdout, /references resolve/);
});

test("fails when a product references an unknown agent", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].agents = ["Nonexistent"]; });
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /unknown agent "Nonexistent"/);
});

test("fails when a product domain is under no registered root", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].domain = "example.com"; });
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /not under any registered root domain/);
});

test("accepts a subdomain of a registered root domain", () => {
  sandbox.mutate("products.json", (r) => { r.products[0].domain = "anything.blackroad.io"; });
  const { code } = sandbox.run("validate-references.mjs");
  assert.equal(code, 0);
});

test("surfaces unknown org names as non-fatal warnings", () => {
  // The real registry already carries org drift; assert it warns but exits 0.
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 0);
  assert.match(stderr, /org .* is not a registered organization name/);
});

test("a valid org name produces no warning for that product", () => {
  sandbox.mutate("products.json", (r) => {
    for (const p of r.products) p.org = "BlackRoad-OS-Primary";
  });
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 0);
  assert.doesNotMatch(stderr, /not a registered organization name/);
});
