# ROADCHAIN_OVER_MESH

**Status:** Design phase (v1, provenance specification)

**Owner:** Theodosia (Agent 23) / Records keeper

**Created:** 2026-06-19

## Overview

RoadChain Over Mesh is the **provenance layer** for BlackRoad OS. It creates immutable, cryptographically-signed proof trails of all significant events as they propagate across the LoRa + WireGuard mesh network.

**Key principle:** Every action (commit, sync, approval, decision) is recorded in an append-only ledger. Gateway stores canonical receipts; edges maintain local proof of participation.

## Why RoadChain?

| Property | Benefit |
|----------|---------|
| **Append-only** | History cannot be rewritten or deleted |
| **Signed** | Proof that Event X happened (cryptographic proof) |
| **Timestamped** | When it happened (with tolerance for clock skew) |
| **Distributed** | Copies on multiple nodes (resilient to single node loss) |
| **Auditable** | Full trail of who did what and when |

## Receipt Lifecycle

### 1. Event Occurs (on any node)

```
Node: Edge Device A
Event: User commits change to local repository
Time: 2026-06-19T11:15:23Z (local device clock, may be wrong)
Action: git commit -m "Update product config"
```

### 2. Receipt Created (locally)

```
Node creates receipt:
├─ Event description
├─ Timestamp (local + gateway if available)
├─ Node ID signature (prove this node created it)
├─ Hash of commit (cryptographic proof)
└─ RoadChain previous hash (chain link)

Receipt stored in: _receipts/RECEIPT-[date]-[node-id].md
```

### 3. Receipt Broadcast (when connected)

```
Edge Device:
  "I have receipt: RECEIPT-20260619-edge-device-a.md"
  (broadcast via LoRa or WireGuard)

Gateway hears broadcast:
  Requests receipt from Edge Device
  Receives full receipt + commit hash
  Verifies signature + hash
```

### 4. Canonical Receipt Created (at gateway)

```
Gateway creates canonical receipt:
├─ Copy of original receipt (prove it was created at time T)
├─ Gateway verification (prove gateway saw it)
├─ Gateway timestamp (authoritative clock)
├─ All participating nodes listed
└─ RoadChain chain continuation (link to previous receipt)

Canonical receipt stored in: Receipts/RECEIPT-[date]-[event].md
```

### 5. Receipt Propagates Back (to all nodes)

```
Gateway broadcasts:
  "New canonical receipt: [hash]"
  (via LoRa to all nodes)

All nodes eventually receive + store:
  _receipts/RECEIPT-[date]-[event]-canonical.md
```

## Receipt Format & Structure

### Local Receipt (created immediately on event)

```markdown
# Receipt: Local Event

**Date (Local):** 2026-06-19T11:15:23Z
**Node:** edge-device-a
**Node ID Hash:** 0x1a2b3c...
**Event Type:** git-commit

## What

User committed local changes to git repository.

## Proof

- **Commit hash:** abc123def456...
- **Commit signature:** [SSH key signature]
- **Files changed:** 3
- **Insertions:** 42
- **Deletions:** 7

## Chain Link

**Previous receipt:** RECEIPT-20260619-000042 (hash: xyz789...)
**Current receipt hash:** sha256(this_receipt) = abc...

## Metadata

- Node local time: 2026-06-19T11:15:23Z (may be wrong)
- Node sync status: offline
- Network available: none
- RoadChain version: v1

---

**Status:** unsigned (waiting for gateway verification)
**Receipt ID:** receipt_20260619_11_15_23_edge_a_001
```

### Canonical Receipt (created at gateway after verification)

```markdown
# Receipt: Canonical — Git Commit Event

**Date (Gateway):** 2026-06-19T14:30:15Z (authoritative time)
**Local Date:** 2026-06-19T11:15:23Z (edge device reported time)
**Node:** edge-device-a
**Event Type:** git-commit
**Receipt Status:** approved

## What

Edge Device A committed 3 file changes to local repository.
Gateway received and verified commit at [canonical time].

## Proof

- **Commit hash:** abc123def456...
- **Commit signature:** [verified ✓ with edge-device-a public key]
- **Node signature:** [verified ✓ with node registration key]
- **Gateway verification:** [verified ✓ with gateway key]
- **RoadChain chain hash:** def789...

## Event Chain

**Previous receipt:** RECEIPT-20260619-000042
  └─ Hash: xyz789abc123...
  └─ Verified ✓

**Current receipt hash:** sha256(this_receipt) = ghi012...

**Next receipt:** RECEIPT-20260619-000044 (follows in chain)

## Metadata

- **Local time delta:** +3 hours 15 minutes (edge clock ahead)
- **Sync latency:** 45 seconds (LoRa transmission time)
- **Sync path:** LoRa (via relay 2)
- **Conflict detection:** none
- **Files affected:** 3 (config.json, README.md, SCHEMA.md)
- **Git tree integrity:** verified ✓

## Signatures

- **Edge Device A:** [SSH signature, verifiable with public key]
- **Gateway:** [Gateway signature, verifiable with public cert]

---

**Status:** canonical ✓ approved
**Receipt ID:** receipt_20260619_14_30_15_edge_a_001_canonical
```

## Clock Synchronization & Skew Handling

### The Clock Skew Problem

Edge devices may have inaccurate clocks (offline for days, no NTP). Gateway has accurate time (internet-synced). This creates challenges:

| Scenario | Problem | RoadChain Handling |
|----------|---------|-------------------|
| **Edge ahead:** Edge clock +3 hours | Timestamp looks future-dated | Gateway records both local + canonical time; human inspects if needed |
| **Edge behind:** Edge clock -1 day | Timestamp looks very old | Acceptable (just means offline long); chain continues |
| **Time jump:** Edge clock jumps +5 hours | Receipts become out-of-order | Gateway reorders using canonical time; flags anomaly for review |

### Tolerance Strategy

```
Maximum accepted clock skew: ±24 hours (configurable)
├─ Skew within tolerance → Accept, record both times
├─ Skew outside tolerance → Flag for manual review, accept anyway
└─ Consistent skew over time → Likely failed clock; recommend correction
```

### Receipt Ordering

Receipts are ordered by **gateway canonical time**, not local time:

```
Edge A (local time):           Edge B (local time):
2026-06-18T08:00:00            2026-06-19T12:00:00
       ↓                               ↓
Event A1 created              Event B1 created
       ↓                               ↓
   (both broadcast)
          ↓─ received by gateway ─↓

Gateway canonical time:
1. Event B1 at 2026-06-19T14:30:00 (received first)
2. Event A1 at 2026-06-19T14:30:45 (received second)

Chain order: [B1] → [A1] (not A1 → B1)
(Even though A1 happened "earlier" by local clocks)
```

## Event Types & Receipt Formats

### Git Commit Event

```
Type: git-commit
When: Local commit created
Proof: Commit hash + signature
Metadata: Files changed, lines added/removed
```

### Git Sync Event

```
Type: git-sync
When: Push or pull completed
Proof: Sync commit hash + push receipt
Metadata: Commits transferred, conflicts resolved, latency
```

### RoadChain Append Event

```
Type: roadchain-append
When: New receipt added to canonical ledger
Proof: Receipt hash + gateway signature
Metadata: Event type, node, timestamp
```

### Permission Grant/Revoke

```
Type: carkeys-permission
When: Permission granted or revoked
Proof: CarKeys signature + approval chain
Metadata: Permission type, target node/agent, approver
```

### Approval/Decision Event

```
Type: decision
When: Operator (Alexa) makes decision
Proof: Operator signature + scope
Metadata: Decision type, affected products/agents, rationale
```

## Chain Structure

### Linear Chain with Branches

```
Receipt 001 (git-commit by edge-a)
    ↓
Receipt 002 (git-sync by gateway)
    ↓
Receipt 003 (git-commit by edge-b)
    ├─ (concurrent to receipts 4-5)
    ↓
Receipt 006 (gateway merge + chain continuation)
    ↓
Receipt 007 (git-commit by edge-a)

(Receipts 004, 005 happen concurrently on edge-b and edge-c)
(Gateway orders them in canonical sequence at receipt 006)
```

### Hash Chain Link

Each receipt contains hash of previous + current:

```
Receipt 002 header:
  Previous hash: sha256(receipt_001) = abc...
  Current hash: sha256(receipt_002) = def...

Receipt 003 header:
  Previous hash: sha256(receipt_002) = def... (✓ match)
  Current hash: sha256(receipt_003) = ghi...

(If receipt 002 is tampered, hash chain breaks → tampering detected)
```

## Validation & Verification

### Node Can Verify Receipt

```bash
# Edge device wants to verify it participated in receipt 047
cat Receipts/RECEIPT-20260619-047.md | jq .proof
# Shows: "edge-device-a" listed in participating nodes
# Can check signature: gpg --verify signature (public key available)
```

### Gateway Can Audit Full Chain

```bash
# Verify chain integrity
node scripts/roadchain-verify.mjs Receipts/

Output:
✓ Receipt 001: valid signature, chain hash OK
✓ Receipt 002: valid signature, chain hash OK
  (previous = abc..., ✓ matches receipt 001)
✓ Receipt 003: valid signature, chain hash OK
  (previous = def..., ✓ matches receipt 002)
...
✓ All 1,000 receipts verified, chain is valid
```

### Third Party Can Audit

Anyone with public keys can verify chain:

```bash
# Public data: all receipts + public keys
# Verify signature on each receipt
# Verify chain hash linkage
# Conclusion: Receipts were created in this order; none were tampered
```

## Incentive Alignment: Why Nodes Can't Cheat

### Scenario 1: Rewriting Local Receipt

**Node tries:** Edit local receipt to claim "more work than actually done"

**Why it fails:**
- Receipt contains hash of actual git commit
- Git commit is immutable (content-addressed hash)
- Discrepancy between receipt + commit detected by gateway
- Tampering flagged in canonical receipt

### Scenario 2: Creating Fake Commit

**Node tries:** Forge commit with false changes

**Why it fails:**
- Commit must be signed with node's SSH key
- Gateway verifies signature against registered public key
- Forged key would need access to node's private key
- Theft of private key triggers CarKeys revocation

### Scenario 3: Reordering Receipts

**Node tries:** Rearrange receipts to claim work in different order

**Why it fails:**
- Chain hashes link receipts (tampering breaks chain)
- Gateway maintains authoritative sequence
- Other nodes can verify chain independently
- Tampering detected immediately

## Receipts & Proof of Work

### Product Implementation Claim

**Statement:** "Product 01 RoadOS is active"

**Proof required:**
- Receipt of first working build
- Receipts of successful tests
- Receipts of user feedback
- Receipt of launch decision by Operator

**RoadChain shows:**
```
[build receipt] → [test receipt 1] → [test receipt 2] → [launch receipt]
        ↓              ↓                   ↓                   ↓
     2026-06-15   2026-06-16         2026-06-17          2026-06-18
  (all canonical timestamps)
```

### Agent Assignment Claim

**Statement:** "Agent 05 (Sebastian) worked on Products A, B, C"

**Proof required:**
- Receipts of commits by Agent 05 to Products A, B, C repos
- Receipts of approval by Agent 06 (Elias) for code review
- Receipt of handoff from Agent 05 to next agent

**RoadChain shows:**
```
[commit by sebastian] → [review by elias] → [handoff to next]
         ↓                      ↓                    ↓
  agent work logged        work verified     context passed
```

## Operational Scenarios

### Scenario 1: Edge Device Goes Offline (1 week)

1. **Days 1-7:** Device works offline
   - Creates commits + local receipts
   - No network available
   - Receipts stored in local _receipts/
2. **Day 8:** Device reconnects
   - Syncs commits to gateway (git push)
   - Syncs receipts to gateway
   - Gateway creates canonical receipts
   - Device receives canonical receipts back
3. **Result:** Full proof trail from reconnection point forward

### Scenario 2: Node Compromised

1. **Compromise detected:** Attacker accessed node's private key
2. **Immediate action:** CarKeys revokes node's keys
3. **Receipt created:** "Node 05 keys revoked due to compromise"
4. **Consequences:**
   - Node cannot create new signed receipts
   - Previous receipts remain valid (immutable)
   - Any commits after revocation are unverifiable
   - Audit shows exactly when compromise was detected

### Scenario 3: Clock Skew Detected

1. **Edge device reports:** Timestamp 2026-06-25 (but actual is 2026-06-19)
2. **Gateway flags:** Anomalous clock detected (+6 days skew)
3. **Receipt created:** "Anomalous timestamp detected from edge-device-x"
4. **Theodosia (Agent 23) alerted:** May indicate clock failure
5. **Resolution:** Operator approves correction, device syncs time

## Integration with Products

Each product maintains receipts proving implementation:

```
Products/01_RoadOS/_receipts/
├── RECEIPT-build-2026-06-15.md
├── RECEIPT-test-ui-2026-06-16.md
├── RECEIPT-test-sync-2026-06-17.md
├── RECEIPT-launch-2026-06-18.md
└── RECEIPT-usage-metrics-weekly-*

(Cross-references to canonical Receipts/ for canonical timestamps)
```

## Validation & Auditing

### Weekly Audit

```bash
node scripts/roadchain-audit.mjs --week=2026-06-19
```

Output:
```
Week of 2026-06-19:
├─ Total receipts: 423
├─ By type:
│   ├─ git-commit: 128
│   ├─ git-sync: 87
│   ├─ carkeys: 34
│   └─ decision: 8
├─ Nodes active: 12
├─ Potential anomalies: 1
│   └─ Edge device clock skew (edge-device-a)
├─ Chain integrity: ✓ all receipts valid
└─ Status: CLEAN
```

### Quarterly Audit

```bash
node scripts/roadchain-audit.mjs --quarter=Q2 --year=2026
```

Output: Full chain verification, statistical analysis, compliance report

## Next Steps

1. **Implement RoadChain service** on gateway (receipt creation, signing, verification)
2. **Integrate with git-sync** (create receipts after every push/pull)
3. **Build audit tools** (chain verification, tampering detection)
4. **Test clock skew scenarios** (real-world offline tests)
5. **Create runbook** for operators (viewing receipts, detecting tampering)
6. **Integrate with products** (each product links receipts for its status)

---

**Related documents:**
- `/Docs/MESH_TOPOLOGY_DESIGN.md` (network layer)
- `/Docs/GIT_SYNC_OVER_MESH.md` (data plane layer)
- `/Products/11_RoadChain/` (product definition)
- `/Receipts/` (canonical receipt directory)
