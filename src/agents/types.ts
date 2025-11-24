/**
 * Agent type definition for BlackRoad OS Genesis Agents
 */
export interface Agent {
  id: string;
  name: string;
  role: string;
  traits: string[];
  inputs: string[];
  outputs: string[];
  description: string;
  triggers: string[];
  inherits_from: string | null;
  active?: boolean;
}

/**
 * Agent validation result
 */
export interface AgentValidationResult {
  valid: boolean;
  errors: string[];
}
