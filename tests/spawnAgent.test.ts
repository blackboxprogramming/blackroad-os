import { describe, it, expect, beforeEach, afterEach } from "vitest";
import * as fs from "fs";
import * as path from "path";
import { spawnAgent, saveAgent } from "../src/agents/spawn-agent";
import { AgentBuilder, AgentRegistry, createAgent } from "../src/agents/lucidia-agent-builder";
import type { Agent } from "../src/agents/types";

const TEST_AGENTS_DIR = path.join(__dirname, "../src/agents");
const TEST_OUTPUT_DIR = "/tmp/test-agents";

describe("spawn-agent", () => {
  beforeEach(() => {
    // Create test output directory
    if (!fs.existsSync(TEST_OUTPUT_DIR)) {
      fs.mkdirSync(TEST_OUTPUT_DIR, { recursive: true });
    }
  });

  afterEach(() => {
    // Clean up test files
    if (fs.existsSync(TEST_OUTPUT_DIR)) {
      const files = fs.readdirSync(TEST_OUTPUT_DIR);
      for (const file of files) {
        fs.unlinkSync(path.join(TEST_OUTPUT_DIR, file));
      }
      fs.rmdirSync(TEST_OUTPUT_DIR);
    }
  });

  describe("spawnAgent", () => {
    it("should create an agent with correct ID from name", () => {
      const agent = spawnAgent("Test Agent");
      expect(agent.id).toBe("test-agent");
      expect(agent.name).toBe("Test Agent");
    });

    it("should infer scribe role from name", () => {
      const agent = spawnAgent("scribe-support");
      expect(agent.role).toBe("scribe");
    });

    it("should infer qa role from name", () => {
      const agent = spawnAgent("qa-validator");
      expect(agent.role).toBe("qa");
    });

    it("should infer archive role from name", () => {
      const agent = spawnAgent("archive-manager");
      expect(agent.role).toBe("archive");
    });

    it("should use custom role when specified", () => {
      const agent = spawnAgent("my-agent", { role: "guardian" });
      expect(agent.role).toBe("guardian");
    });

    it("should use custom description when provided", () => {
      const agent = spawnAgent("my-agent", { description: "Custom description" });
      expect(agent.description).toBe("Custom description");
    });

    it("should include parent agent reference", () => {
      const agent = spawnAgent("child-agent", { parent: "parent-agent" });
      expect(agent.parentAgent).toBe("parent-agent");
      expect(agent.metadata.createdBy).toContain("spawned-by");
    });

    it("should include custom traits", () => {
      const agent = spawnAgent("my-agent", { traits: ["fast", "reliable"] });
      expect(agent.traits).toContain("fast");
      expect(agent.traits).toContain("reliable");
    });

    it("should include base capabilities", () => {
      const agent = spawnAgent("my-agent");
      const capabilityNames = agent.capabilities.map(c => c.name);
      expect(capabilityNames).toContain("self-describe");
      expect(capabilityNames).toContain("issue-link");
      expect(capabilityNames).toContain("pr-link");
    });

    it("should include role-specific triggers", () => {
      const agent = spawnAgent("scribe-agent");
      const triggerEmojis = agent.triggers.map(t => t.emoji);
      expect(triggerEmojis).toContain("📝");
    });

    it("should include custom emoji trigger", () => {
      const agent = spawnAgent("my-agent", { emoji: "🔮" });
      const triggerEmojis = agent.triggers.map(t => t.emoji);
      expect(triggerEmojis).toContain("🔮");
    });

    it("should include metadata with timestamp", () => {
      const agent = spawnAgent("my-agent");
      expect(agent.metadata.createdAt).toBeDefined();
      expect(agent.metadata.version).toBe("1.0.0");
    });
  });

  describe("saveAgent", () => {
    it("should save agent to JSON file", () => {
      const agent = spawnAgent("test-save-agent");
      const filePath = saveAgent(agent, TEST_OUTPUT_DIR);
      
      expect(fs.existsSync(filePath)).toBe(true);
      
      const content = fs.readFileSync(filePath, "utf-8");
      const savedAgent = JSON.parse(content);
      expect(savedAgent.id).toBe("test-save-agent");
    });
  });
});

describe("AgentBuilder", () => {
  it("should build agent with fluent API", () => {
    const agent = createAgent("Custom Agent")
      .withRole("guardian")
      .withDescription("A custom guardian agent")
      .withTraits("vigilant", "protective")
      .withTrigger("🛡️", "protect")
      .withCapability("monitoring", "Monitors the system", true)
      .build();

    expect(agent.id).toBe("custom-agent");
    expect(agent.name).toBe("Custom Agent");
    expect(agent.role).toBe("guardian");
    expect(agent.description).toBe("A custom guardian agent");
    expect(agent.traits).toContain("vigilant");
    expect(agent.triggers.some(t => t.emoji === "🛡️")).toBe(true);
    expect(agent.capabilities.some(c => c.name === "monitoring")).toBe(true);
  });

  it("should set parent agent", () => {
    const agent = createAgent("Child Agent")
      .withRole("support")
      .withParent("parent-id")
      .build();

    expect(agent.parentAgent).toBe("parent-id");
  });

  it("should add default capabilities if none provided", () => {
    const agent = createAgent("Simple Agent")
      .withRole("custom")
      .build();

    const capabilityNames = agent.capabilities.map(c => c.name);
    expect(capabilityNames).toContain("self-describe");
  });
});

describe("AgentRegistry", () => {
  it("should load existing agents", () => {
    const registry = new AgentRegistry(TEST_AGENTS_DIR);
    const agents = registry.loadAll();
    
    expect(agents.length).toBeGreaterThan(0);
    
    // Should have loaded the predefined agents
    const agentIds = agents.map(a => a.id);
    expect(agentIds).toContain("scribe-agent");
    expect(agentIds).toContain("qa-agent");
    expect(agentIds).toContain("guardian-agent");
  });

  it("should get agent by ID", () => {
    const registry = new AgentRegistry(TEST_AGENTS_DIR);
    const agent = registry.get("scribe-agent");
    
    expect(agent).toBeDefined();
    expect(agent?.role).toBe("scribe");
  });

  it("should find agents by role", () => {
    const registry = new AgentRegistry(TEST_AGENTS_DIR);
    registry.loadAll();
    const qaAgents = registry.findByRole("qa");
    
    expect(qaAgents.length).toBeGreaterThan(0);
    expect(qaAgents[0].role).toBe("qa");
  });

  it("should find agents by trigger emoji", () => {
    const registry = new AgentRegistry(TEST_AGENTS_DIR);
    registry.loadAll();
    const agents = registry.findByTrigger("📝");
    
    expect(agents.length).toBeGreaterThan(0);
  });

  it("should list all agent IDs", () => {
    const registry = new AgentRegistry(TEST_AGENTS_DIR);
    const ids = registry.list();
    
    expect(ids.length).toBeGreaterThan(0);
    expect(ids).toContain("scribe-agent");
  });
});
