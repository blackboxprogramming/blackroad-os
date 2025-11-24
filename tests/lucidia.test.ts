import { describe, expect, it } from "vitest";
import { Lucidia, createLucidia } from "../src/lucidia";
import type { SpawnRulesConfig, Metrics } from "../src/lucidia/types";

const testConfig: SpawnRulesConfig = {
  version: "1.0.0",
  settings: {
    approval_required: true,
    approver: "@alexa",
    default_ttl: "72h",
    max_clones: 3,
    cooldown_period: "24h",
  },
  rules: [
    {
      id: "escalation-overflow",
      name: "Escalation Overflow Handler",
      if: {
        escalations_last_3_days: "> 15",
        agent_load: "> 85",
      },
      then: {
        spawn: "guardian-clone-vault",
        config: {
          role: "sentinel",
          ttl: "96h",
          inherits_from: "guardian-agent",
          description: "Temporary overflow clone",
        },
      },
    },
  ],
};

const baseMetrics: Metrics = {
  escalations_last_3_days: 0,
  agent_load: 0,
  blocked_prs: 0,
  avg_review_time: 0,
  unmapped_repos: 0,
  repo_activity_score: 0,
  open_issues: 0,
  avg_issue_age: 0,
  unowned_workflows: 0,
};

describe("Lucidia", () => {
  describe("createLucidia", () => {
    it("creates Lucidia instance from config", () => {
      const lucidia = createLucidia(testConfig);
      expect(lucidia).toBeInstanceOf(Lucidia);
    });
  });

  describe("getSettings", () => {
    it("returns configured settings", () => {
      const lucidia = new Lucidia(testConfig);
      const settings = lucidia.getSettings();

      expect(settings.approval_required).toBe(true);
      expect(settings.approver).toBe("@alexa");
      expect(settings.max_clones).toBe(3);
    });
  });

  describe("getRules", () => {
    it("returns configured rules", () => {
      const lucidia = new Lucidia(testConfig);
      const rules = lucidia.getRules();

      expect(rules).toHaveLength(1);
      expect(rules[0].id).toBe("escalation-overflow");
    });
  });

  describe("detect", () => {
    it("detects matching conditions", () => {
      const lucidia = new Lucidia(testConfig);
      const metrics: Metrics = {
        ...baseMetrics,
        escalations_last_3_days: 18,
        agent_load: 89,
      };

      const result = lucidia.detect(metrics);

      expect(result.matched).toBe(true);
      expect(result.rule?.id).toBe("escalation-overflow");
    });

    it("returns no match for normal conditions", () => {
      const lucidia = new Lucidia(testConfig);
      const result = lucidia.detect(baseMetrics);

      expect(result.matched).toBe(false);
      expect(result.rule).toBeNull();
    });
  });

  describe("write", () => {
    it("generates agent files", () => {
      const lucidia = new Lucidia(testConfig);
      const agent = lucidia.write(testConfig.rules[0]);

      expect(agent.spec.name).toBe("guardian-clone-vault");
      expect(agent.prompt).toBeDefined();
      expect(agent.workflow).toBeDefined();
      expect(agent.docs).toBeDefined();
    });
  });

  describe("propose", () => {
    it("creates PR proposal", () => {
      const lucidia = new Lucidia(testConfig);
      const agent = lucidia.write(testConfig.rules[0]);
      const pr = lucidia.propose(testConfig.rules[0], agent);

      expect(pr.title).toContain("guardian-clone-vault");
      expect(pr.files).toHaveLength(4);
    });
  });

  describe("spawn", () => {
    it("executes full spawn pipeline when conditions match", () => {
      const lucidia = new Lucidia(testConfig);
      const metrics: Metrics = {
        ...baseMetrics,
        escalations_last_3_days: 18,
        agent_load: 89,
      };

      const { result, agent, pr } = lucidia.spawn(metrics);

      expect(result.matched).toBe(true);
      expect(agent).toBeDefined();
      expect(agent?.spec.name).toBe("guardian-clone-vault");
      expect(pr).toBeDefined();
      expect(pr?.title).toContain("[spawn]");
    });

    it("returns only result when no match", () => {
      const lucidia = new Lucidia(testConfig);
      const { result, agent, pr } = lucidia.spawn(baseMetrics);

      expect(result.matched).toBe(false);
      expect(agent).toBeUndefined();
      expect(pr).toBeUndefined();
    });
  });
});
