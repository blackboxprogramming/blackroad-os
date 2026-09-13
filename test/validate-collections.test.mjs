import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox(); });
afterEach(() => sandbox.cleanup());

test("accepts the real, unmodified collections", () => {
  const { code, stdout } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 0);
  assert.match(stdout, /valid/);
});

test("rejects the wrong organization count", () => {
  sandbox.mutate("orgs.json", (r) => { r.organizations.pop(); });
  const { code, stderr } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /expected 20 organizations, found 19/);
});

test("rejects a duplicate domain num", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[1].num = r.domains[0].num; });
  const { code, stderr } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /duplicate num/);
});

test("rejects the wrong carkeys-lane count", () => {
  sandbox.mutate("carkeys.json", (r) => { r.lanes.pop(); });
  const { code, stderr } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /expected 20 carkeys lanes, found 19/);
});

test("rejects a missing required field in a lane", () => {
  sandbox.mutate("lanes.json", (r) => {
    const firstKey = Object.keys(r.lanes[0])[0];
    delete r.lanes[0][firstKey];
  });
  const { code } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
});

test("reports the offending file in the error output", () => {
  sandbox.mutate("orgs.json", (r) => { r.organizations.pop(); });
  const { stderr } = sandbox.run("validate-collections.mjs");
  assert.match(stderr, /Registry\/orgs\.json/);
});

test("rejects duplicate domain names even when IDs and numbers differ", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[1].name = r.domains[0].name; });
  const { code, stderr } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /duplicate domain name/);
});

test("rejects malformed and noncanonical domain names", () => {
  const original = sandbox.read("domains.json");
  for (const name of ["", "BLACKROAD.io", "https://blackroad.io", "blackroad.io.", ".blackroad.io", "bad..blackroad.io", "-bad.blackroad.io", "bad-.blackroad.io", "*.blackroad.io", "127.0.0.1", `${"a".repeat(64)}.io`, `${"a".repeat(63)}.${"b".repeat(63)}.${"c".repeat(63)}.${"d".repeat(63)}.io`]) {
    sandbox.write("domains.json", original);
    sandbox.mutate("domains.json", (r) => { r.domains[0].name = name; });
    const { code, stderr } = sandbox.run("validate-collections.mjs");
    assert.equal(code, 1, JSON.stringify(name));
    assert.match(stderr, /canonical hostname/);
  }
});

test("rejects a subdomain entered as a second root domain", () => {
  sandbox.mutate("domains.json", (r) => { r.domains[1].name = "app.blackroad.io"; });
  const { code, stderr } = sandbox.run("validate-collections.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /overlapping root domains/);
});

test("accepts a canonical hostname at the label and total length limits", () => {
  const name = `${"a".repeat(63)}.${"b".repeat(63)}.${"c".repeat(63)}.${"d".repeat(61)}`;
  assert.equal(name.length, 253);
  sandbox.mutate("domains.json", (r) => { r.domains[0].name = name; });
  assert.equal(sandbox.run("validate-collections.mjs").code, 0);
});
