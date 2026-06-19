# MESH_TOPOLOGY_DESIGN

**Status:** Design phase (v1, not yet built)

**Owner:** Gaia (Agent 08) / Infrastructure lead

**Created:** 2026-06-19

## Overview

BlackRoad OS uses a hybrid mesh topology combining:
- **LoRa (LoRaWAN-compatible)** for long-range, low-power, offline-first wireless
- **Headscale + WireGuard** for secure VPN overlay and internet connectivity
- **Git** as append-only data plane
- **RoadChain** for immutable proof trails

This creates a resilient, offline-capable system that works across remote, disconnected, and urban environments.

## Why Hybrid?

| Layer | Purpose | Strength | Weakness |
|-------|---------|----------|----------|
| **LoRa** | Offline-first mesh | 10+ km range, low power, no internet needed | Low bandwidth, high latency |
| **WireGuard** | Encrypted overlay | Fast, secure, modern crypto, VPN standard | Requires internet connectivity |
| **Git** | Append-only sync | Simple, distributed, proven, versioned | Eventual consistency |

**Hybrid approach:** LoRa for resilience + offline operation; WireGuard for throughput + encryption; Git for data consistency.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  Products (RoadOS, RoadCode, CarKeys, etc.) + Agents        │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                  RoadChain (Provenance)                      │
│  Immutable receipt trails + cryptographic signing            │
└────────────────┬────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────┐
│                  Git Data Plane                              │
│  Append-only repo sync (push/pull with conflict resolution)  │
└────────────────┬────────────────────────────────────────────┘
                 │
       ┌─────────┴─────────┐
       │                   │
┌──────▼──────┐      ┌─────▼─────────┐
│   LoRa Mesh │      │  WireGuard    │
│  (Offline)  │      │   VPN Layer   │
│             │      │  (Online)     │
├─────────────┤      ├───────────────┤
│ • RAK4631   │      │ • Headscale   │
│ • T-Beam    │      │ • Peer keys   │
│ • 900 MHz   │      │ • 10.100.0/16 │
│ • 10+ km    │      │ • Encrypted   │
└─────────────┘      └───────────────┘

      LoRa                 Internet/LAN
     (Physical)            (Tunneled)
```

## Node Roles

### 1. Gateway Node

**Function:** Hub that bridges LoRa mesh to internet. Runs VPN coordinator.

**Hardware:**
- Meshtastic device (RAK4631, always-on)
- Raspberry Pi 4 or mini-PC (compute)
- Ethernet + WiFi or cellular (WAN uplink)

**Software:**
- Meshtastic firmware (Router role)
- Headscale server (VPN coordinator)
- git daemon (sync repository)
- Linux OS

**Count:** 1-3 (1 primary, 1-2 standby for redundancy)

**Example location:** Office, data center, or always-on home server

### 2. Relay Node

**Function:** Extend LoRa range by rebroadcasting. No internet access needed.

**Hardware:**
- Meshtastic device (RAK4631, T-Beam)
- Optional: Raspberry Pi Zero or STM32 for local processing
- Solar panel + battery (for outdoor/remote deployment)

**Software:**
- Meshtastic firmware (Router + Power-on-Boot)
- Optional: local git client if compute available

**Count:** 3-10 (distributed around coverage area)

**Example location:** Rooftops, hills, remote areas

### 3. Edge Device

**Function:** User endpoint. Mobile, sporadic connectivity. Runs full app.

**Hardware:**
- Laptop, tablet, or phone with LoRa USB addon
- T-Beam Ultra, Seeed Studio S3, or LoRa hat
- WiFi or cellular uplink (when available)

**Software:**
- Any OS (Windows, macOS, Linux, iOS, Android)
- Meshtastic client (for LoRa)
- WireGuard VPN client (for internet)
- Git client (for sync)
- RoadOS application suite

**Count:** Variable (1-100+ users)

**Example location:** Anywhere (home, office, field, vehicle)

## Network Topology

### LoRa Physical Layer (Mesh)

- **Frequency:** 902-928 MHz (ISM band, North America) or 868 MHz (Europe)
- **Spreading factor:** 7 (configurable for range vs throughput)
- **Bandwidth:** 125 kHz
- **Transmission power:** 17 dBm
- **Range:** 10-20 km line-of-sight; 2-5 km urban
- **Channel:** Single shared channel (all nodes on same frequency)

**Topology:**
```
Edge Device A ──LoRa──┐
                      │
Edge Device B ──LoRa──┼──→ Relay 1 ──LoRa──┐
                      │                      │
Edge Device C ──LoRa──┘                      ├──→ Relay 2 ──LoRa──┬──→ Gateway (internet)
                                             │                    │
Relay 3 ───────────────────────────────────┘────────────────────┘

(Mesh routing: each node can relay through any other reachable node)
```

### WireGuard VPN Layer (Logical Mesh)

- **VPN coordinator:** Headscale server on gateway
- **Peer network:** 10.100.0.0/16 (configurable)
- **Gateway address:** 10.100.1.1
- **Per-device address:** 10.100.x.x (static assignment)
- **Encryption:** Curve25519 (built-in to WireGuard)

**How it works:**
1. Each device has WireGuard private key + Headscale peer config
2. Devices can reach each other via WireGuard tunnel (encrypted)
3. Gateway routes traffic between LoRa nodes and internet
4. WireGuard provides path encryption even over LoRa (double encryption)

## Data Plane: Git Sync Over Mesh

### Offline-First Design

All nodes maintain a **local Git repository** with full history. Work proceeds offline. When connectivity available, sync with peers.

```
Node A (Offline)           Node B (Offline)        Gateway (Online)
┌──────────────────┐      ┌──────────────────┐    ┌──────────────────┐
│ git repo (HEAD)  │      │ git repo (HEAD)  │    │ git repo (HEAD)  │
│ Commit A1        │      │ Commit B1        │    │ Commit A1        │
│ Commit A2 ✓ new │      │ Commit B2 ✓ new │    │ Commit B1        │
└────────┬─────────┘      └────────┬─────────┘    └────────┬─────────┘
         │                         │                       │
         └────────LoRa request ───→├─ WireGuard push A2 ──┤
                                   │                       │
                       Gateway pulls B2 over internet ────→│
                              (eventually)
```

### Sync Protocol

1. **Local work:** Node creates commits locally (offline OK)
2. **Broadcast readiness:** Node announces "I have new commits" via LoRa
3. **Sync opportunity:** When edge connectivity available:
   - **Push:** Node sends new commits to gateway via LoRa or WireGuard
   - **Pull:** Node receives new commits from gateway (if any)
4. **Merge:** Automatic (last-write-wins on single LoRa channel)
5. **Receipt:** RoadChain creates signed proof of sync event

### Conflict Resolution

**Strategy:** Last-write-wins with RoadChain proof

- Both nodes write to same file → second write overwrites first
- RoadChain receipt shows which write "won" (timestamp + proof)
- Application layer can detect conflict in history (git log)
- Operator or Cordelia (Agent 26) resolves if critical

## RoadChain Integration: Provenance Over Mesh

### How Receipts Flow Across Mesh

1. **Local event:** Node creates event (commit, action, permission change)
2. **Local receipt:** Event stored in local RoadChain (LoRa node submits to gateway when connected)
3. **Gateway receipt:** Gateway receives receipt over LoRa or WireGuard
4. **Canonical record:** Receipt stored in central Receipts/ (authoritative copy)
5. **Sync back:** If needed, receipt propagates back to other nodes

### Clock Synchronization

- **Gateway node:** Authoritative time source (NTP-synced if online)
- **Edge nodes:** May be out-of-sync (hours or days if offline long)
- **RoadChain:** Tolerates clock skew; uses both local and gateway timestamps
- **Ordering:** Events ordered by local clock on each node, reconciled at gateway

### Receipt Format

```markdown
# Receipt: Mesh Sync Event

**Date:** 2026-06-19T14:30:00Z (gateway time)
**Local Date:** 2026-06-19T11:15:00Z (edge device clock)
**Node ID:** edge-device-a
**Event:** git push (5 commits)

## Evidence

- git refs: abc123...def456
- RoadChain hash: [proof hash]
- Signature: [cryptographic signature]

## Metadata

- Sync path: Edge → LoRa → Gateway
- Latency: 45 seconds
- Conflicts: None
```

## Security Model

### LoRa Mesh Security

- **Shared channel key:** All nodes on same frequency (radio can be observed)
- **Device-level encryption:** AES-128 (Meshtastic firmware)
- **No authentication:** Any compatible device can join frequency (open mesh assumption)

### WireGuard Security

- **Peer authentication:** Private/public key pairs (pre-shared during setup)
- **Encryption:** Curve25519 (mathematically proven, no backdoors)
- **Forward secrecy:** Per-packet encryption keys

### Git Commit Signing

- **SSH keys:** Each device signs commits with private key
- **Public key verification:** Gateway verifies signature before accepting commit
- **Revocation:** CarKeys can revoke device keys

### RoadChain Proof Signing

- **Asymmetric signature:** Receipts signed by creating node's key
- **Verification:** Gateway + other nodes verify signature
- **Timestamp:** Signed timestamp proves when event occurred

### Threat Model & Mitigations

| Threat | Impact | Mitigation |
|--------|--------|-----------|
| **Node compromise** | Attacker reads local data, forges commits | Disk encryption, SSH key protection, CarKeys revocation |
| **Eavesdropping (LoRa)** | Attacker reads wireless traffic | WireGuard encryption overlay, app-level encryption |
| **Eavesdropping (internet)** | Attacker reads internet traffic | WireGuard encryption, HTTPS over VPN |
| **Replay attacks** | Attacker re-broadcasts old messages | Git commit hashes prevent replay; RoadChain detects duplicates |
| **Man-in-the-middle** | Attacker intercepts sync | WireGuard peer authentication, git signature verification |

## Performance Expectations

| Metric | Offline LoRa | Online WireGuard | Notes |
|--------|------------|-----------------|-------|
| **Bandwidth** | 50 bytes/sec (1.5 kbps) | 1-10 Mbps | LoRa very slow; WireGuard limited by ISP/radio uplink |
| **Latency** | 100-500 ms | 10-50 ms | LoRa variable; WireGuard consistent |
| **Range** | 10-20 km line-of-sight | Unlimited (internet) | LoRa degrades in urban |
| **Power** | 100 mW LoRa device | 500 mW+ compute | LoRa very efficient; gateway always-on |
| **Reliability** | Best effort (no ACK per hop) | TCP reliable | LoRa packet loss 5-20%; WireGuard 0% (internet) |

## Deployment Readiness Checklist

- [ ] Hardware procurement (Meshtastic devices, Raspberry Pi, solar panels)
- [ ] Site survey (determine gateway + relay locations for coverage)
- [ ] LoRa channel allocation (request ISM band registration if needed)
- [ ] Headscale setup (install server, generate peer configs)
- [ ] Git repository initialization (create canonical repo structure)
- [ ] RoadChain integration (proof trail mechanism)
- [ ] Test LoRa range (walk test to validate coverage map)
- [ ] Test git sync (manual push/pull over LoRa)
- [ ] Test RoadChain receipts (verify signature and timestamps)
- [ ] Security audit (key rotation, encryption verification)
- [ ] Failover test (gateway offline, relays work)
- [ ] Load test (simultaneous sync from 10+ devices)

## Open Decisions Needed

1. **Device selection:** Which Meshtastic device for each role?
   - Gateway: RAK4631 or RAK Wisblock stack?
   - Relay: T-Beam or RAK4631?
   - Edge: USB addon or full board?

2. **Channel strategy:**
   - Single channel (simpler, lower bandwidth)?
   - Multi-channel (parallel, more complex)?

3. **Headscale regions:**
   - Centralized (all traffic through one server)?
   - Distributed (regional Headscale instances)?

4. **Clock skew tolerance:**
   - Allow 1 hour skew? 1 day? Unbounded?

5. **Redundancy:**
   - Active-passive (standby gateway)?
   - Active-active (distributed gateways)?

## Next Steps

**Phase 1 (2 weeks):** Research + prototyping
- Order Meshtastic devices
- Deploy test LoRa mesh (1 gateway, 2 relays, 3 edges)
- Validate range + throughput
- Document findings

**Phase 2 (4 weeks):** Integration
- Set up Headscale + WireGuard
- Integrate git sync layer
- Test RoadChain receipts
- Document sync protocol

**Phase 3 (4 weeks):** Product integration
- Test with actual products (RoadCode, RoadTrip, etc.)
- Test agent handoffs over mesh
- Performance testing + optimization

**Phase 4 (2 weeks):** Launch readiness
- Security audit
- Incident response planning
- Documentation for operators
- Runbook creation

See `/HighWay/NEXT.md` for detailed roadmap.

---

**Related documents:**
- `/Docs/ARCHITECTURE.md` (system overview)
- `/HighWay/_registry/MESH_TOPOLOGY_v1.json` (technical specification)
- `/Docs/GIT_SYNC_OVER_MESH.md` (data plane protocol) — planned
- `/Docs/ROADCHAIN_OVER_MESH.md` (provenance mechanism) — planned
