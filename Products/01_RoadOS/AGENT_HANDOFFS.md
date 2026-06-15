# Agent Handoffs — RoadOS

## Primary agents
- Roadie (guide / action broker — appears inside workspace for intent clarification and safe routing)
- Lucidia (system orchestrator — manages workspace state, memory continuity, and cross-product handoffs)

## Supporting agents
- Any product-specific agent when routed (e.g., Sophia in PitStop, Elias in RoadCode)
- Cordelia for relay/continuity when moving between products

## Agent responsibilities

### Roadie
May do:
- Clarify ambiguous user intent
- Propose safe route options
- Explain why a route was chosen
- Draft simple commands or file actions

Must not do:
- Execute destructive actions without explicit user/operator approval
- Access secrets or provider credentials
- Act outside the current workspace scope

Needs approval for:
- Any file write, external exposure, or shell execution

Writes receipts for:
- Intent clarification and route proposals

Hands off to:
- Target product agent (e.g., RoadCode’s build agents) once route is approved

### Lucidia
May do:
- Maintain workspace memory map and context continuity
- Coordinate handoffs between products
- Surface relevant receipts and previous context
- Manage agent session lifecycle inside the workspace

Must not do:
- Override user decisions
- Expose private context without permission
- Perform actions that require operator approval

Needs approval for:
- Major layout or memory mutations that affect multiple products

Writes receipts for:
- Context saves, handoff events, session state changes

Hands off to:
- Specific product agents or RoadMap for status updates

## Human approval points
- Destructive file operations or shell commands
- External data exposure or provider connections
- Agent actions that touch secrets, location, or sensitive data
- Publishing or sharing workspace content

## Conflict handling
If agents disagree on route or action:
1. Surface options to user with clear trade-offs and receipt implications
2. Lucidia proposes safest default
3. User or operator (Alexa) makes final call
4. Record decision + reasoning in RoadChain

Default reviewers for conflicts: Lucidia (continuity), Portia (permissions), Atticus (documentation/proof).