#!/usr/bin/env node

/**
 * spawn-agent CLI Tool
 * 
 * Creates a new agent with full spec, prompt, workflow, and docs.
 * 
 * Usage: node scripts/spawn-agent.js <agent-id>
 * Example: pnpm spawn-agent scribe-support
 */

const fs = require('fs');
const path = require('path');

// Configuration
const TEMPLATES_DIR = path.join(__dirname, '..', 'templates');
const AGENTS_DIR = path.join(__dirname, '..', 'agents');
const WORKFLOWS_DIR = path.join(__dirname, '..', '.github', 'workflows');
const DOCS_DIR = path.join(__dirname, '..', 'docs', 'agents');

/**
 * Convert agent ID to human-readable name
 * e.g., "scribe-support" -> "Scribe Support"
 */
function idToName(id) {
  return id
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

/**
 * Generate role based on agent naming conventions
 */
function inferRole(id) {
  const parts = id.toLowerCase().split('-');
  
  // Common role patterns
  const roleMap = {
    'scribe': 'Documentation and note-taking specialist',
    'support': 'User assistance and support handler',
    'review': 'Code review and quality assurance agent',
    'reviewer': 'Code review and quality assurance agent',
    'deploy': 'Deployment and release automation agent',
    'monitor': 'System monitoring and alerting agent',
    'test': 'Testing and validation agent',
    'security': 'Security scanning and vulnerability assessment agent',
    'data': 'Data processing and analysis agent',
    'notify': 'Notification and communication agent',
    'sync': 'Synchronization and integration agent',
    'build': 'Build and compilation agent',
    'clean': 'Cleanup and maintenance agent'
  };
  
  for (const part of parts) {
    if (roleMap[part]) {
      return roleMap[part];
    }
  }
  
  return `Specialized agent for ${idToName(id)} tasks`;
}

/**
 * Generate traits based on agent ID
 */
function inferTraits(id) {
  const baseTraits = ['autonomous', 'reliable'];
  const parts = id.toLowerCase().split('-');
  
  const traitMap = {
    'scribe': ['detailed', 'organized'],
    'support': ['helpful', 'responsive'],
    'review': ['thorough', 'analytical'],
    'reviewer': ['thorough', 'analytical'],
    'deploy': ['cautious', 'systematic'],
    'monitor': ['vigilant', 'proactive'],
    'test': ['meticulous', 'comprehensive'],
    'security': ['vigilant', 'strict'],
    'data': ['analytical', 'efficient'],
    'notify': ['timely', 'clear'],
    'sync': ['coordinated', 'accurate'],
    'build': ['efficient', 'robust'],
    'clean': ['systematic', 'thorough']
  };
  
  for (const part of parts) {
    if (traitMap[part]) {
      return [...baseTraits, ...traitMap[part]];
    }
  }
  
  return baseTraits;
}

/**
 * Generate tags based on agent ID
 */
function inferTags(id) {
  const baseTags = ['agent', 'blackroad-os'];
  const parts = id.toLowerCase().split('-');
  return [...baseTags, ...parts];
}

/**
 * Read template file
 */
function readTemplate(templateName) {
  const templatePath = path.join(TEMPLATES_DIR, templateName);
  return fs.readFileSync(templatePath, 'utf8');
}

/**
 * Replace all placeholders in template
 */
function processTemplate(template, replacements) {
  let result = template;
  for (const [key, value] of Object.entries(replacements)) {
    const regex = new RegExp(`{{${key}}}`, 'g');
    result = result.replace(regex, value);
  }
  return result;
}

/**
 * Ensure directory exists
 */
function ensureDir(dirPath) {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
  }
}

/**
 * Main spawn agent function
 */
function spawnAgent(agentId, options = {}) {
  const {
    skipDocs = false,
    verbose = false
  } = options;

  // Validate agent ID
  if (!agentId || typeof agentId !== 'string') {
    throw new Error('Agent ID is required');
  }
  
  // Normalize agent ID
  const normalizedId = agentId.toLowerCase().replace(/[^a-z0-9-]/g, '-');
  
  // Generate agent metadata
  const agentName = idToName(normalizedId);
  const agentRole = inferRole(normalizedId);
  const agentTraits = inferTraits(normalizedId);
  const agentTags = inferTags(normalizedId);
  const createdAt = new Date().toISOString();
  const description = `${agentName} agent for the BlackRoad-OS ecosystem`;

  // Prepare replacements
  const replacements = {
    'AGENT_ID': normalizedId,
    'AGENT_NAME': agentName,
    'AGENT_ROLE': agentRole,
    'AGENT_DESCRIPTION': description,
    'AGENT_TRAITS': JSON.stringify(agentTraits),
    'AGENT_TRAITS_LIST': agentTraits.map(t => `- ${t}`).join('\n'),
    'AGENT_TRAITS_MDX': agentTraits.map(t => `- **${t}**`).join('\n'),
    'AGENT_TAGS': JSON.stringify(agentTags),
    'CREATED_AT': createdAt
  };

  // Ensure output directories exist
  ensureDir(AGENTS_DIR);
  ensureDir(WORKFLOWS_DIR);
  if (!skipDocs) {
    ensureDir(DOCS_DIR);
  }

  // Check if agent already exists
  const agentJsonPath = path.join(AGENTS_DIR, `${normalizedId}.agent.json`);
  if (fs.existsSync(agentJsonPath)) {
    throw new Error(`Agent '${normalizedId}' already exists at ${agentJsonPath}`);
  }

  // Process and write templates
  const outputs = [];

  // 1. Agent JSON spec
  const agentJson = processTemplate(readTemplate('base-agent.template.json'), replacements);
  fs.writeFileSync(agentJsonPath, agentJson);
  outputs.push(`agents/${normalizedId}.agent.json`);

  // 2. Agent prompt
  const promptPath = path.join(AGENTS_DIR, `${normalizedId}.prompt.txt`);
  const agentPrompt = processTemplate(readTemplate('base-agent.prompt.template.txt'), replacements);
  fs.writeFileSync(promptPath, agentPrompt);
  outputs.push(`agents/${normalizedId}.prompt.txt`);

  // 3. Workflow YAML
  const workflowPath = path.join(WORKFLOWS_DIR, `${normalizedId}.workflow.yml`);
  const agentWorkflow = processTemplate(readTemplate('base-agent.workflow.template.yml'), replacements);
  fs.writeFileSync(workflowPath, agentWorkflow);
  outputs.push(`.github/workflows/${normalizedId}.workflow.yml`);

  // 4. MDX docs (optional)
  if (!skipDocs) {
    const mdxPath = path.join(DOCS_DIR, `${normalizedId}.mdx`);
    const agentMdx = processTemplate(readTemplate('base-agent.mdx.template'), replacements);
    fs.writeFileSync(mdxPath, agentMdx);
    outputs.push(`docs/agents/${normalizedId}.mdx`);
  }

  return {
    agentId: normalizedId,
    agentName,
    outputs,
    metadata: {
      role: agentRole,
      traits: agentTraits,
      tags: agentTags,
      createdAt
    }
  };
}

/**
 * CLI entry point
 */
function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`
🛠️  spawn-agent – BlackRoad-OS Agent Generator

Usage:
  node scripts/spawn-agent.js <agent-id> [options]
  pnpm spawn-agent <agent-id> [options]

Arguments:
  agent-id     Unique identifier for the agent (e.g., scribe-support)

Options:
  --skip-docs  Skip generating MDX documentation
  --verbose    Show detailed output
  --help, -h   Show this help message

Examples:
  pnpm spawn-agent scribe-support
  pnpm spawn-agent code-reviewer --skip-docs
  pnpm spawn-agent deploy-bot --verbose
    `);
    process.exit(0);
  }

  const agentId = args[0];
  const skipDocs = args.includes('--skip-docs');
  const verbose = args.includes('--verbose');

  try {
    console.log(`\n🛠️  Spawning agent: ${agentId}\n`);
    
    const result = spawnAgent(agentId, { skipDocs, verbose });
    
    console.log(`✔ Created agent: ${result.agentName}`);
    result.outputs.forEach((output, index) => {
      const prefix = index === result.outputs.length - 1 ? '└─' : '├─';
      console.log(`${prefix} ${output}`);
    });
    
    if (verbose) {
      console.log('\n📋 Metadata:');
      console.log(`   Role: ${result.metadata.role}`);
      console.log(`   Traits: ${result.metadata.traits.join(', ')}`);
      console.log(`   Tags: ${result.metadata.tags.join(', ')}`);
      console.log(`   Created: ${result.metadata.createdAt}`);
    }
    
    console.log('\n💚 Agent spawned successfully!\n');
    
  } catch (error) {
    console.error(`\n❌ Error: ${error.message}\n`);
    process.exit(1);
  }
}

// Export for testing
module.exports = {
  spawnAgent,
  idToName,
  inferRole,
  inferTraits,
  inferTags,
  processTemplate
};

// Run CLI if executed directly
if (require.main === module) {
  main();
}
