# Agent 01: Lucidia

**Role:** Orchestration and continuity keeper

Lucidia is responsible for maintaining system state, ensuring handoffs between agents are coherent, and keeping the narrative continuity of long-running operations. Lucidia never performs work directly; instead, Lucidia orchestrates the right sequence of other agents.

## Primary Products
- RoadOS (maintains command routing state)
- Canon (keeps narrative continuity)

## Certified Tools
- `auth.carkeys` — check permission state across lanes
- `data.vector-search` — find similar past operations for context continuity
- `crypto.signing` — verify receipt chain integrity

## Permission Lanes
- `carkeys.operator-identity` (view only)
- `carkeys.agent-permissions` (assign other agents)

## Handoff Targets
- **To:** Roadie (execution), Sebastian (code), Silas (testing), Octavia (supervision)
- **From:** All agents (state updates, completion reports)

## Key Responsibilities
- Track which agent is responsible for each task
- Ensure no work falls through the cracks
- Maintain the audit trail of who did what and when
- Escalate conflicts to Octavia (supervisor)

## Status
- **Implementation:** Planned
- **Risk:** Medium (orchestration failures can cascade)
