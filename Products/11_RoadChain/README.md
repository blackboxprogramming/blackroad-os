# 11. RoadChain

**RoadChain** is the receipt layer: provenance, memory proof, hashes, audit trails, rollback references, and evidence.

It should not overclaim legal compliance, but it should make BlackRoad inspectable. If something important happened, changed, moved, deployed, or got decided, RoadChain should know enough to prove the road.

The canon docs warn against unsafe overclaims around RoadChain — this is the right guardrail.

RoadChain is the proof surface for the entire operating system.

**Primary integrations:**
- Every product that changes state
- RoadMap for status + proof
- CarKeys for permission receipts
- HighWay for deployment and infra proofs
- Detour for recovery proofs

**Core promise:**
If it mattered, there’s proof. If there’s proof, you can see the road.

**Status:** Canon-ready (Level 4). Implementation planned.
**Risk:** Medium — must stay honest about scope (no fake blockchain claims).