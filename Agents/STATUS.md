# Agents — STATUS

**State:** roster registered; per-agent folders not yet created
**Implementation:** planned — agents are canon roles, not running workers
**Receipts:** none yet

## What exists
- `README.md` — purpose and boundary (agents request, Operator approves, CarKeys gates, RoadChain records)
- Canon roster: all 27 agents in `Registry/agents.json` (validated by `scripts/validate-agents.mjs`)
- Live agent roster also rendered in `index.html` (Agents window)

## Next
- Create per-agent folders (roles, handoffs, permissions, device assignments), each cross-linked to its `Registry/agents.json` record.
