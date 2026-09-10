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
