# HighWay — RULES

Local rules for hybrid mesh backbone design and documentation.

## Infrastructure Documentation Standards

### Topology Documents (*_DESIGN.md)

Required sections:
1. Overview — one-sentence summary
2. Components — hardware + software pieces
3. Diagram — ASCII art or referential (e.g., "See sketch in _registry/")
4. Configuration — how nodes are configured
5. Addressing — IP/channel assignment scheme
6. Routing — how packets flow
7. Failover — redundancy + recovery
8. Capacity — expected throughput/latency/range
9. Scaling — how to add nodes

### Integration Documents (*_OVER_MESH.md)

Required sections:
1. Purpose — why this layer sits on the mesh
2. Protocol — message format + handshake
3. Guarantees — ordering, delivery, consistency
4. Failure modes — what breaks with mesh failure
5. Recovery — how to restore consistency
6. Examples — typical traffic flows
7. Performance — bandwidth/latency impact

## Configuration Format

Mesh configurations stored in `_registry/` as JSON:

```json
{
  "version": "1.0",
  "topology": "type",
  "nodes": [
    {
      "id": "device-id",
      "name": "node-name",
      "type": "meshtastic-device-type",
      "region": "geographic-region",
      "role": "router|edge|gateway"
    }
  ],
  "links": [
    {
      "from": "node-a",
      "to": "node-b",
      "protocol": "lora|wireguard",
      "redundancy": "primary|backup"
    }
  ]
}
```

## Naming Conventions

- Topology design: `MESH_TOPOLOGY_DESIGN.md`, `*_TOPOLOGY.md`
- Integration: `*_OVER_MESH.md` (e.g., `GIT_SYNC_OVER_MESH.md`)
- Security: `SECURITY_MODEL.md`, `ENCRYPTION.md`
- Configuration: `_registry/mesh-*.json`, `_registry/topology-*.json`

## Invariants

- No topology doc can be merged without architecture review (Elias + Gaia)
- All devices must have power budget calculations
- Security model must address mesh-level threats (node compromise, packet sniffing)
- Configuration changes must be tracked in RoadChain
- Offline-first operation must be explicitly stated in sync docs

## Maintenance

- Topology reviewed by Gaia (Agent 08) for feasibility
- Security reviewed by Seraphina (Agent 19) for threat coverage
- Integration reviewed by Elias (Agent 06) for system consistency
