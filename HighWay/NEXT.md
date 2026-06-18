# HighWay — NEXT

**Immediate next action:** Create MESH_TOPOLOGY_DESIGN.md with Meshtastic + Headscale/WireGuard architecture.

**Current state:**
- HighWay/ scaffold exists (README.md, STATUS.md)
- Products/18_HighWay/ has product definition
- No technical integration docs yet

**Next steps:**
1. Write MESH_TOPOLOGY_DESIGN.md covering:
   - Meshtastic network design (device types, placement, channels)
   - Headscale/WireGuard VPN topology (peers, regions, routing)
   - Hybrid integration (LoRa + WireGuard fallback)
   - Network diagram (ASCII or Markdown)
2. Write GIT_SYNC_OVER_MESH.md covering:
   - Append-only Git sync across mesh edges
   - Conflict resolution strategy
   - Retry + backoff for unreliable links
   - Offline-first operation
3. Write ROADCHAIN_OVER_MESH.md covering:
   - Event ordering guarantees on delayed edges
   - Clock skew handling
   - Proof trail replication
4. Write SECURITY_MODEL.md covering:
   - Mesh node authentication (CarKeys)
   - End-to-end encryption
   - Permission propagation
5. Create _registry/mesh-topology-template.json with device definitions

**Owner:** Gaia (Agent 08) / Infrastructure lead; Seraphina (Agent 19) / Security

**Status:** Design phase — architecture docs needed before implementation
