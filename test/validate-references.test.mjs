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

test("rejects malformed product hostnames before matching registered suffixes", () => {
  const original = sandbox.read("products.json");
  for (const domain of ["", null, 42, [], {}, "https://app.blackroad.io", "user@app.blackroad.io", ".blackroad.io", "bad..blackroad.io", "bad-.blackroad.io", "-bad.blackroad.io", "*.blackroad.io", "app.blackroad.io:443", " app.blackroad.io", "app.blackroad.io\n", "app\n.blackroad.io", "APP.blackroad.io", "app.blackroad.io.", "evilblackroad.io", "blackroad.io.example.com"]) {
    sandbox.write("products.json", original);
    sandbox.mutate("products.json", (r) => { r.products[0].domain = domain; });
    const { code, stderr } = sandbox.run("validate-references.mjs");
    assert.equal(code, 1, JSON.stringify(domain));
    assert.match(stderr, /canonical hostname|not under any registered root domain/);
    assert.doesNotMatch(stderr, /TypeError/);
  }
});

for (const [field, value, diagnostic] of [
  ["products", "MissingProduct", /unknown product "MissingProduct"/],
  ["agents", "MissingAgent", /unknown agent "MissingAgent"/],
  ["nextRoads", "external.example", /not under any registered root domain/]
]) {
  test(`rejects dangling domain ${field} references`, () => {
    sandbox.mutate("domains.json", (r) => { r.domains[0][field] = [value]; });
    const { code, stderr } = sandbox.run("validate-references.mjs");
    assert.equal(code, 1);
    assert.match(stderr, diagnostic);
    assert.match(stderr, /domain 01 \(blackroad.io\)/);
  });
}

test("accepts existing product/agent links and nested next-road hostnames", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[0].nextRoads = ["git.blackroad.systems", "nested.app.blackroad.io", "blackroad.network"]; });
  assert.equal(sandbox.run("validate-references.mjs").code, 0);
});

test("rejects URLs and malformed next-road hostnames", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[0].nextRoads = ["https://git.blackroad.systems", "bad..blackroad.io"]; });
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /nextRoads\[0\].*canonical hostname/);
  assert.match(stderr, /nextRoads\[1\].*canonical hostname/);
});

test("standalone reference checks report malformed domain link collections", () => {
  for (const field of ["products", "agents", "nextRoads"]) {
    for (const value of [null, "RoadOS", [null], [17], [{}]]) {
      const original = sandbox.read("domains.json");
      sandbox.mutate("domains.json", (r) => { r.domains[0][field] = value; });
      const { code, stderr } = sandbox.run("validate-references.mjs");
      assert.equal(code, 1, `${field} ${JSON.stringify(value)}`);
      assert.match(stderr, /must be an array|must be a string/);
      assert.doesNotMatch(stderr, /TypeError/);
      sandbox.write("domains.json", original);
    }
  }
});

test("standalone reference checks reject duplicate root identities", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[1].name = r.domains[0].name; });
  const { code, stderr } = sandbox.run("validate-references.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /duplicate domain name/);
});
