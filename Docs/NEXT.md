# Docs — NEXT

**Immediate next action:** Create ARCHITECTURE.md as foundation for all other specs.

**Current state:**
- Docs/ folder scaffold exists (README.md, STATUS.md)
- No architecture or specification docs yet
- Some architecture knowledge in Products/18_HighWay/ and scattered across product folders

**Next steps:**
1. Write ARCHITECTURE.md covering:
   - System components (products, agents, registry, mesh, Git)
   - Data flow (input → processing → output)
   - Network topology (hybrid mesh)
   - Security model (CarKeys, RoadChain)
2. Follow with MESH_NETWORKING.md (LoRa + WireGuard design)
3. Then GIT_NATIVE_DATAPLANE.md (append-only sync)
4. Then ROADCHAIN_SPEC.md (proof trails)
5. API and deployment docs follow

**Owner:** Elias (Agent 06) / Architecture lead

**Status:** Architecture phase — foundation needed
