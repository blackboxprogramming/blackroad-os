# HighWay — INDEX

Map of hybrid mesh backbone infrastructure and integration planning for BlackRoad OS.

**Note:** HighWay is **Product 18** — see `Products/18_HighWay/` for the product definition. This folder holds the infrastructure + technical integration planning.

## Infrastructure Components

| Component | Purpose | Status |
|-----------|---------|--------|
| LoRa Mesh | Long-range wireless (Meshtastic) | research |
| VPN Backbone | WireGuard overlay for secure tunneling | research |
| Git Sync | Append-only Git data plane | research |
| RoadChain | Proof trail + event log | research |
| Registry Sync | Cross-mesh registry synchronization | research |

## Integration Areas

| Area | Purpose | Owner | Status |
|------|---------|-------|--------|
| Network topology | Mesh node placement + routing | Gaia (Agent 08) | design |
| Data sync | Git push/pull across mesh edges | Gaia (Agent 08) | design |
| Permissions | CarKeys access control over mesh | Seraphina (Agent 19) | design |
| Failover | Offline-first + eventual consistency | Aria (Agent 18) | design |
| Monitoring | Mesh health + sync status | Theodosia (Agent 23) | design |

## Current Design Phase

- Meshtastic device evaluation (LoRa range, bandwidth, power)
- Headscale/WireGuard topology design
- Git sync conflict resolution strategy
- RoadChain event ordering across delayed edges
- Security model for mesh node authentication

## Key Decisions Needed

1. Which Meshtastic device variant(s) to deploy?
2. Single-tier or multi-tier mesh backbone?
3. Headscale region strategy (edge vs. central)?
4. Git sync retry + backoff strategy?
5. RoadChain ordering guarantees on out-of-order edges?

See NEXT.md for immediate roadmap.
