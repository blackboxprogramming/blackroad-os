import { test, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";
import { makeSandbox } from "./helpers.mjs";

let sandbox;
beforeEach(() => { sandbox = makeSandbox(); });
afterEach(() => sandbox.cleanup());

test("accepts the real, unmodified agent registry", () => {
  const { code, stdout } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 0);
  assert.match(stdout, /valid/);
});

test("rejects the wrong agent count", () => {
  sandbox.mutate("agents.json", (r) => { r.agents.pop(); });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /expected 27 agents/);
});

test("rejects total_agents that disagrees with the array length", () => {
  sandbox.mutate("agents.json", (r) => { r.total_agents = 99; });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /total_agents/);
});

test("rejects slug that is not name.toLowerCase()", () => {
  sandbox.mutate("agents.json", (r) => { r.agents[0].slug = "not-the-name"; });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /slug .* != name\.toLowerCase/);
});

test("rejects a duplicate slug", () => {
  sandbox.mutate("agents.json", (r) => {
    r.agents[1].slug = r.agents[0].slug;
    r.agents[1].name = r.agents[0].name; // keep slug==name.toLowerCase invariant
  });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /duplicate slug/);
});

test("rejects a non-contiguous agent number set", () => {
  sandbox.mutate("agents.json", (r) => { r.agents[0].number = "99"; });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /missing agent number "01"/);
});

test("rejects a missing required field", () => {
  sandbox.mutate("agents.json", (r) => { delete r.agents[0].role; });
  const { code, stderr } = sandbox.run("validate-agents.mjs");
  assert.equal(code, 1);
  assert.match(stderr, /missing required field "role"/);
});
