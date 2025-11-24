import * as fs from "fs";
import * as path from "path";
import type { Agent, AgentValidationResult } from "./types";

const AGENTS_DIR = path.join(__dirname, "../../agents");

/**
 * Validates an agent object against the expected schema
 */
export function validateAgent(agent: unknown): AgentValidationResult {
  const errors: string[] = [];

  if (typeof agent !== "object" || agent === null) {
    return { valid: false, errors: ["Agent must be an object"] };
  }

  const obj = agent as Record<string, unknown>;

  if (typeof obj.id !== "string" || obj.id.length === 0) {
    errors.push("Agent must have a non-empty string 'id'");
  }

  if (typeof obj.name !== "string" || obj.name.length === 0) {
    errors.push("Agent must have a non-empty string 'name'");
  }

  if (typeof obj.role !== "string" || obj.role.length === 0) {
    errors.push("Agent must have a non-empty string 'role'");
  }

  if (!Array.isArray(obj.traits)) {
    errors.push("Agent must have an array 'traits'");
  }

  if (!Array.isArray(obj.inputs)) {
    errors.push("Agent must have an array 'inputs'");
  }

  if (!Array.isArray(obj.outputs)) {
    errors.push("Agent must have an array 'outputs'");
  }

  if (typeof obj.description !== "string") {
    errors.push("Agent must have a string 'description'");
  }

  if (!Array.isArray(obj.triggers)) {
    errors.push("Agent must have an array 'triggers'");
  }

  if (obj.inherits_from !== null && typeof obj.inherits_from !== "string") {
    errors.push("Agent 'inherits_from' must be null or a string");
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Loads an agent from a JSON file
 */
export function loadAgent(filename: string): Agent {
  const filepath = path.join(AGENTS_DIR, filename);
  const content = fs.readFileSync(filepath, "utf8");
  const agent = JSON.parse(content);

  const validation = validateAgent(agent);
  if (!validation.valid) {
    throw new Error(`Invalid agent '${filename}': ${validation.errors.join(", ")}`);
  }

  return agent as Agent;
}

/**
 * Loads all agent definitions from the agents directory
 */
export function loadAllAgents(): Agent[] {
  const files = fs.readdirSync(AGENTS_DIR).filter((f) => f.endsWith(".json"));
  return files.map((file) => loadAgent(file));
}

/**
 * Gets the base agent template
 */
export function getBaseTemplate(): Agent {
  return loadAgent("base-agent.template.json");
}

/**
 * Creates a new agent from the base template
 */
export function createAgentFromTemplate(
  id: string,
  name: string,
  role: string,
  overrides: Partial<Agent> = {}
): Agent {
  const base = getBaseTemplate();
  return {
    ...base,
    id,
    name,
    role,
    ...overrides,
    inherits_from: "base-agent",
  };
}

/**
 * Gets an agent by its ID
 */
export function getAgentById(id: string): Agent | undefined {
  const agents = loadAllAgents();
  return agents.find((agent) => agent.id === id);
}

/**
 * Lists all available agent IDs
 */
export function listAgentIds(): string[] {
  return loadAllAgents().map((agent) => agent.id);
}
