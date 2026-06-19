# GIT_SYNC_OVER_MESH

**Status:** Design phase (v1, protocol specification)

**Owner:** Gaia (Agent 08) / Infrastructure lead

**Created:** 2026-06-19

## Overview

Git Sync Over Mesh is the **data plane** for BlackRoad OS. It enables append-only synchronization of state (products, configuration, user data) across the hybrid LoRa + WireGuard mesh network.

**Key principle:** Nodes work offline with local Git repositories. When connectivity available, push/pull with automatic conflict resolution (last-write-wins).

## Why Git?

| Property | Benefit |
|----------|---------|
| **Append-only** | Immutable history (RoadChain receipts) |
| **Distributed** | No single point of failure |
| **Proven** | Billions of lines use git daily |
| **Versioned** | Can revert or inspect historical state |
| **Standard** | Existing tools + libraries |

## Architecture

### Repository Structure

```
canonical-repo/
├── README.md                    # Public handbook
├── Registry/                    # Canonical products, agents, orgs, domains
│   ├── products.json
│   ├── agents.json
│   └── ...
├── Products/                    # Product state
│   ├── 01_RoadOS/
│   │   ├── product.json
│   │   ├── config.json          # Local overrides
│   │   └── ...
│   └── ...
├── Agents/                      # Agent assignments + state
├── Receipts/                    # RoadChain proof trails
│   ├── RECEIPT-001-*
│   └── ...
├── _local/                      # Not synced (gitignored)
│   ├── .env                     # Secrets, local config
│   └── temporary-files/
└── .gitignore                   # Exclude _local/

```

### Repository Topology

```
Edge Device A          Edge Device B          Gateway Node
  local repo             local repo            canonical repo
    (branch)              (branch)               (main)
      ↓                     ↓                      ↑
   commits by A         commits by B        upstream source
      │                     │                      ↑
      └─── LoRa push ──────→└─ WireGuard push ───→│
           (or WireGuard)       (internet)        │
                                                  │
                      Gateway pulls B commits    │
                      Merges, signs, broadcasts │
                                                  ↓
Edge Device A           Edge Device B          (via LoRa/WireGuard)
  git pull ←──────────────LoRa pull ←─────────────┤
  (eventually)
```

### Sync Workflow

1. **Offline local work:**
   ```bash
   git add .
   git commit -m "Local change: update config"
   # Stored locally; no network needed
   ```

2. **Push notification (optional):**
   ```
   Node broadcasts over LoRa: "I have new commits (hash: abc123)"
   Gateway hears it, adds to sync queue
   ```

3. **Push when possible:**
   ```bash
   # When edge connectivity available:
   git push origin main  # Push to gateway via LoRa or WireGuard
   ```

4. **Gateway receives & merges:**
   ```bash
   git fetch origin  # Receive Edge A's commits
   git merge        # Auto-merge (last-write-wins)
   git commit -m "Merge Edge A commits"
   ```

5. **Broadcast to other edges:**
   ```
   Gateway announces over LoRa: "New canonical state (hash: def456)"
   All edges receive notification
   ```

6. **Pull when possible:**
   ```bash
   # When edge wants latest state:
   git pull origin main  # Fetch from gateway via LoRa or WireGuard
   ```

### Push Protocol

```
Edge Device                           Gateway
    │                                   │
    │─── Announce readiness (LoRa) ───→│
    │     "I have commits to sync"     │
    │                                   │
    │←─── Gateway acks (LoRa) ─────────│
    │     "Ready to receive"            │
    │                                   │
    │─── git push (LoRa/WireGuard) ───→│
    │     commit objects + refs        │
    │                                   │
    │←─── Verify + ack (LoRa) ────────│
    │     "Commits received OK"        │
    │                                   │
    ├─ Gateway processes:              │
    │  ├─ Verify commit signatures    │
    │  ├─ Auto-merge if possible      │
    │  └─ Create RoadChain receipt    │
    │                                   │
    │←─── Broadcast new canonical ────│
    │     (via LoRa to all nodes)     │
```

### Pull Protocol

```
Edge Device                           Gateway
    │                                   │
    │─── Request latest (LoRa) ───────→│
    │     "Give me HEAD"                │
    │                                   │
    │←─── git pull (LoRa/WireGuard) ──│
    │     commit objects + refs        │
    │                                   │
    │─── Verify + ack ────────────────→│
    │     "Commits received OK"        │
    │                                   │
    ├─ Edge merges:                    │
    │  ├─ Verify signatures           │
    │  ├─ Local merge (if needed)     │
    │  └─ Resolve conflicts (automatic)
```

## Conflict Resolution: Last-Write-Wins

### Single LoRa Channel = No Conflicting Writes

Since all nodes share **one LoRa channel**, only one push can be active at a time (physical serialization). This means:

- Edge A pushes commits 1, 2, 3 (LoRa transmits A1 → A2 → A3)
- Edge B waits (LoRa busy)
- Edge B pushes commits 1, 2 (LoRa transmits B1 → B2)
- Result: Total order [A1, A2, A3, B1, B2]

**No true conflict.** Merge is trivial (just fast-forward).

### WireGuard Path (Internet) May Have Conflicts

If two edges push simultaneously over WireGuard (faster internet):

```
Edge A commits (timestamp: 14:00:00)   Edge B commits (timestamp: 14:00:01)
    └─ git push over WireGuard ────→
                                Gateway receives both
                                    Merge strategy: Last-write-wins
                                    ↓ B's commit (later) overwrites A's
```

**Strategy:** Automatic merge script on gateway:

```javascript
// Pseudo-code
function mergeConflictingWrites(edgeACommit, edgeBCommit) {
  if (edgeBCommit.timestamp > edgeACommit.timestamp) {
    return edgeBCommit;  // B's write is newer
  } else {
    return edgeACommit;  // A's write is newer
  }
}
```

### Application-Level Conflict Detection

If application logic needs to detect conflicts:

```bash
git log --oneline | grep "Merge commit"  # Shows merge points
git show MERGE_COMMIT                     # Shows what was merged
```

Operators or Cordelia (Agent 26) can inspect history and decide if manual intervention needed.

## Bandwidth & Latency Characteristics

### LoRa Path

- **Bandwidth:** 50 bytes/sec (very slow)
- **Latency:** 100-500 ms per packet
- **Sync time for 1 MB:** ~20,000 seconds (5.5 hours)
- **Optimal:** Small frequent commits (100 KB max per sync)

**Implication:** Data must be structured for LoRa (small objects, compress before push)

### WireGuard Path

- **Bandwidth:** 1-10 Mbps (typical home internet)
- **Latency:** 10-50 ms
- **Sync time for 1 MB:** ~1 second
- **Optimal:** Large batch commits possible

## Retry & Backoff Strategy

### LoRa Retry

```
Attempt 1: Send message (wait 5 sec for ack)
├─ Success? → Done
└─ Timeout? → Backoff

Attempt 2: Send message (wait 10 sec)
├─ Success? → Done
└─ Timeout? → Backoff

Attempt 3: Send message (wait 20 sec)
├─ Success? → Done
└─ Timeout? → Backoff

Attempt 4: Send message (wait 40 sec)
├─ Success? → Done
└─ Timeout? → Attempt later (node stores in queue)
```

### WireGuard Retry

```
Attempt 1: git push (TCP timeout 30 sec)
├─ Success? → Done
└─ Timeout? → Backoff

Attempt 2: git push (wait 60 sec, retry)
├─ Success? → Done
└─ Network error? → Try LoRa as fallback
```

## Error Handling

### Common Errors

| Error | Cause | Recovery |
|-------|-------|----------|
| **Signature verification failed** | Commit not signed by valid key | Reject commit; alert CarKeys |
| **Merge conflict (app-level)** | Same file edited by two edges | Last-write-wins; log conflict receipt |
| **Network timeout** | LoRa/WireGuard unreachable | Retry with exponential backoff |
| **Out-of-space** | Edge device disk full | Alert operator; clear cache |
| **Corrupted git object** | Transmission error or disk failure | Fetch missing object from gateway |

### Corruption Recovery

```bash
# If git repo corrupted:
git fsck --full                # Check integrity
git gc --aggressive            # Optimize + repair
git push --force-with-lease    # Re-sync with gateway
```

## Offline-First Implications

### Working Offline

- All commits stored locally
- `git log` shows only local history (until next pull)
- `git status` shows uncommitted changes locally
- No network needed for local operations

### Rejoining Network

- `git pull` fetches gateway's canonical history
- Local history preserved (not overwritten)
- Automatic merge (fast-forward if no local divergence)
- New canonical HEAD replaces local
- `git log` now shows full history

### Data at Rest

- Unsynced commits on edge devices are temporary
- Think of them as "in-flight" work
- Gateway copy is the canonical record
- RoadChain receipt proves sync completed

## Schema for Sync Metadata

Each commit in the repository includes metadata:

```json
{
  "sync_metadata": {
    "node_id": "edge-device-a",
    "sync_timestamp": "2026-06-19T14:30:00Z",
    "sync_path": "lora",
    "sync_latency_ms": 450,
    "conflict_count": 0,
    "receipt_hash": "abc123def456"
  }
}
```

This allows auditing of sync history and correlation with RoadChain receipts.

## Validation Checklist

- [ ] All commits signed with valid SSH key
- [ ] Merge commits have parent lineage
- [ ] RoadChain receipts reference commit hashes
- [ ] Timestamps consistent with LoRa + WireGuard propagation
- [ ] No circular merges or history rewriting
- [ ] All objects reachable from HEAD

## Next Steps

1. **Prototype:** Test git sync over real LoRa + WireGuard
2. **Measure:** Quantify bandwidth, latency, reliability
3. **Optimize:** Compress strategies, batch sizing
4. **Integrate:** Connect to RoadChain for receipts
5. **Test:** Multi-node conflict scenarios
6. **Document:** Runbook for operators (sync procedures, troubleshooting)

---

**Related documents:**
- `/Docs/MESH_TOPOLOGY_DESIGN.md` (network layer)
- `/Docs/ROADCHAIN_OVER_MESH.md` (provenance layer) — planned
- `/Deployments/GIT_SYNC_GUIDE.md` (operational guide) — planned
