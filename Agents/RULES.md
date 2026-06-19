# Agents — RULES

Local rules for agent documentation and governance.

## Agent Folder Naming

Format: `NN_AgentName` (number + name, both required)

Examples: `01_Lucidia`, `02_Roadie`, `27_Olympia`

Each agent folder is self-contained and mirrors Registry/agents.json entry.

## Required Files Per Agent

| File | Purpose | Created | Status |
|------|---------|---------|--------|
| `README.md` | Overview + role | scaffold | ✓ |
| `INDEX.md` | Domain map | scaffold | ✓ |
| `STATUS.md` | Current state | scaffold | ✓ |
| `NEXT.md` | Next action | scaffold | ✓ |
| `RESPONSIBILITIES.md` | Product assignments | planned | — |
| `ACTIVITY.md` | Recent work + receipts | planned | — |
| `HANDOFF_PROTOCOL.md` | Context passing | planned | — |

## Required Subdirectories

| Directory | Purpose | Content |
|-----------|---------|---------|
| `_permissions/` | Access control | carkeys-matrix.md |
| `_handoffs/` | Context templates | TEMPLATE_*.md files |
| `_receipts/` | Activity proof trails | receipt files |

## RESPONSIBILITIES.md Format

```markdown
# Agent NN: Name — RESPONSIBILITIES

**Role:** [Role from Registry/agents.json]

## Primary Assignments

| Product | Domain | Status |
|---------|--------|--------|
| [Product] | [Domain] | active/planned |

## Support Assignments

| Product | Role | Status |
|---------|------|--------|
| [Product] | [Support type] | active/planned |

## Current Focus

- [Current project 1]
- [Current project 2]

## Handoff Points

| To Agent | Context | Template |
|----------|---------|----------|
| [Agent] | [What context] | _handoffs/TEMPLATE_*.md |

See HANDOFF_PROTOCOL.md for detailed patterns.
```

## HANDOFF_PROTOCOL.md Format

```markdown
# Agent NN: Name — HANDOFF PROTOCOL

## Incoming Handoffs

**When to hand off TO this agent:**
- [Trigger 1]
- [Trigger 2]

**Context required:**
- [Input 1]
- [Input 2]

**Template:** See _handoffs/HANDOFF_TO_[NAME].md

## Outgoing Handoffs

**When this agent hands off FROM:**
- [Scenario 1]
- [Scenario 2]

**Context provided:**
- [Output 1]
- [Output 2]

**Template:** See _handoffs/HANDOFF_FROM_[NAME].md

## Common Workflows

[Workflow 1] → [Agent sequence] → [Workflow outcome]
```

## Invariants

- Every agent must have a primary product assignment
- Every agent must have defined CarKeys permissions (can't request what not allowed)
- Every agent must have documented handoff protocols (how to pass context to/from)
- Agent folder structure must mirror Registry entry (number, name, role)
- No agent can work in isolation (all must have handoff points)

## Maintenance

- Lucidia (Agent 01) oversees agent coordination
- Octavia (Agent 12) supervises handoff protocols
- Theodosia (Agent 23) maintains activity records + receipts
- CarKeys permissions reviewed quarterly by Seraphina (Agent 19)

## Validation

CI script (planned): `scripts/validate-agents-folders.mjs`
- Check all 27 folders exist with required files
- Validate RESPONSIBILITIES links to actual products
- Validate handoff targets are valid agents
- Check _permissions/ files exist and are not empty
