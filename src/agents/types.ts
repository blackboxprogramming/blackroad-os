/**
 * Agent Type Definitions for Lucidia DSL Agent System
 * 
 * These types define the schema for agents that can be:
 * - Triggerable via emojis
 * - Linkable to issues and PRs
 * - Self-describing
 * - Able to spawn more agents
 */

export interface AgentTrigger {
  emoji: string;
  action: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  enabled: boolean;
}

export interface AgentMetadata {
  createdAt: string;
  createdBy: string;
  version: string;
  lastModified?: string;
}

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string;
  traits: string[];
  triggers: AgentTrigger[];
  capabilities: AgentCapability[];
  metadata: AgentMetadata;
  parentAgent?: string;
  childAgents?: string[];
}

export interface AgentTemplate {
  $schema?: string;
  templateVersion: string;
  defaults: Omit<Partial<Agent>, 'metadata'> & { metadata?: Partial<AgentMetadata> };
}

export type AgentRole = 
  | "scribe" 
  | "qa" 
  | "planner" 
  | "broadcast" 
  | "guardian" 
  | "digest" 
  | "archive" 
  | "support"
  | "custom";
