# BlackRoad OS Architecture

## Overview

BlackRoad OS is a browser-native operating environment with 27 interconnected products, 27 specialized agents, and 1,729 catalogued capabilities. It is organized around a single source of truth: the Registry system.

## The Registry System

All system state lives in `Registry/` as JSON files validated against schemas:

| File | Purpose | Count | Validator |
|------|---------|-------|-----------|
| `products.json` | 27 products | 27 | `validate-registry.mjs` |
| `agents.json` | 27 agents | 27 | `validate-agents.mjs` |
| `glovebox-tools.json` | Tool registry | 1,729 | `validate-glovebox.mjs` |
| `roadchain-receipts.json` | Immutable ledger | n/a | `validate-roadchain.mjs` |
| `carkeys.json` | Permission lanes | 20 | `validate-collections.mjs` |
| `orgs.json` | Organizations | 20 | `validate-collections.mjs` |
| `domains.json` | Root domains | 20 | `validate-collections.mjs` |
| `lanes.json` | Index lanes | 17+ | `validate-collections.mjs` |

## The Five Implementation Batches

### Batch 1: Operating & Build Spine (Apps 01–05)

**Products:**
- **01. RoadOS** — Browser computer with shell, window management, app routing
- **02. RoadCode** — Build, test, deploy engine with Qwen reasoning
- **03. RoadTrip** — Solo operator + AI workspace for long tasks
- **04. PitStop** — Homework portal with incremental tutoring
- **05. RoadWork** — Business/compliance operations and workflow engine

**Key Tools:**
- `os.shell`, `os.file-nav` — OS capabilities
- `model.qwen`, `model.gemma` — Local LLM inference
- `exec.sandbox` — Safe code execution
- `storage.workspace`, `storage.indexeddb` — Persistence

**Key Agents:**
- Lucidia (orchestration), Roadie (operator support), Sebastian (code), Silas (testing)

**CarKeys Lanes:**
- `carkeys.operator-identity` — Who controls the system
- `carkeys.agent-permissions` — Which agents can do what

---

### Batch 2: Social, Identity, Publishing, Worlds, & Search (Apps 06–10)

**Products:**
- **06. BackRoad** — Social feed aggregator + ActivityPub interface
- **07. CarKeys** — Cryptographic identity & permission gates
- **08. RoadBook** — Digital-native publishing with annotations
- **09. RoadWorld** — Playable worldbuilding & simulations
- **10. RoadView** — 17,290 master indexed search with visible workflows

**Key Tools:**
- `auth.carkeys`, `auth.oauth` — Identity and auth
- `data.vector-search` — Semantic search
- `api.http` — External service integration
- `media.canvas` — Visual rendering

**Key Agents:**
- Seraphina (security), Alice (files), Ophelia (research), Thalia (teaching)

**CarKeys Lanes:**
- `carkeys.external-api` — External service access
- `carkeys.model-execution` — LLM token limits

---

### Batch 3: Verification, Support, Credits, & Collaboration (Apps 11–15)

**Products:**
- **11. RoadChain** — Immutable append-only receipt ledger
- **12. RoadSide** — Embedded help widget + support routing
- **13. RoadCoin** — Internal compute accounting (not an asset platform)
- **14. CarPool** — Multi-operator team workspaces
- **15. BlackBoard** — Visual canvas, storyboards, animations

**Key Tools:**
- `crypto.signing` — Receipt signing & verification
- `media.canvas` — Drawing and visualization
- `storage.indexeddb` — Ledger persistence

**Key Agents:**
- Octavia (supervision), Valeria (risk/finance), Celeste (planning), Sapphira (visual)

**CarKeys Lanes:**
- `carkeys.operator-deploy` — Who can deploy
- `carkeys.vcs-deployment` — Who can push code

---

### Batch 4: Sovereignty, Networks, & Spatial Meta-Office (Apps 16–20)

**Products:**
- **16. OneWay** — Controlled data pipelines with identity stripping
- **17. RoadBand** — Audio taste profiling & music preference
- **18. HighWay** — Core infrastructure registry (domains, SSL, networking)
- **19. RoadSport** — Physics simulation & route choreography
- **20. OfficeRoad** — Spatial coordination workspace with active tasks

**Key Tools:**
- `network.proxy` — Request routing and credential masking
- `api.http` — External APIs
- `media.canvas` — Visual workspace

**Key Agents:**
- Gaia (systems), Lyra (music), Seraphina (security), Cordelia (care)

**CarKeys Lanes:**
- `carkeys.network-admin` — Network configuration
- `carkeys.data-export` — Data pipeline control

---

### Batch 5: Curation, Capability Indexes, & Active Routing Tasks (Apps 21–27)

**Products:**
- **21. RoadStream** — Subscriptions & media collections
- **22. RoadShow** — Programming blocks & broadcast curation
- **23. RoundAbout** — Pre-trip configuration & readiness
- **24. GloveBox** — Master 1,729 capability index
- **25. RoadMap** — Coherent status dashboard
- **26. RoadWire** — Long-term async communication threads
- **27. Detour** — Real-time transit orchestration & rerouting

**Key Tools:**
- `glovebox` system itself (GloveBox is a product AND a tool registry)
- `storage.indexeddb` — Caching tool manifests
- All other tools (GloveBox is the master of tools)

**Key Agents:**
- Calliope (publishing), Theodosia (records), Cicero (writing), Olympia (final review)

**CarKeys Lanes:**
- `carkeys.physical-devices` — Camera, mic, location access
- `carkeys.payment` — Payment and financial gating

---

## Files Architecture

Each of the 27 products has a folder:

```
Products/NN_ProductName/
├── product.json         (auto-synced from Registry/products.json)
├── tools.json           (which GloveBox tools this product uses)
├── handoffs.json        (where this product hands work to)
├── capabilities.json    (what this product actually does, tied to tools)
├── README.md            (product overview and status)
└── STATUS.md            (implementation progress)
```

Each of the 27 agents has a folder:

```
Agents/NN_AgentName/
├── README.md            (role, primary products, key responsibilities)
├── permissions.json     (which CarKeys lanes this agent can access)
├── handoffs.json        (which agents this agent works with)
├── tools.json           (which GloveBox tools this agent can use)
└── STATUS.md            (implementation progress)
```

## Key Architecture Rules

1. **Registry is truth.** Generated files are projections; never hand-edit them.
2. **Tools describe capabilities.** GloveBox is the single catalog of what BlackRoad can do.
3. **Receipts are immutable.** RoadChain logs every significant action, forever.
4. **Permissions are gated.** CarKeys is the only gate; no silent access elevation.
5. **Handoffs are explicit.** Every agent-to-agent or product-to-product transition is logged.
6. **Agents never conflict.** Lucidia orchestrates to ensure coherent sequential work.

## Validation Pipeline

All scripts in `scripts/`:

```bash
# Validate individual registries
node scripts/validate-registry.mjs          # products.json
node scripts/validate-agents.mjs            # agents.json
node scripts/validate-glovebox.mjs          # glovebox-tools.json
node scripts/validate-roadchain.mjs         # roadchain-receipts.json
node scripts/validate-collections.mjs       # carkeys, orgs, domains, lanes

# Sync generated files from registry
node scripts/sync-products.mjs              # index.html PRODUCTS array
node scripts/sync-product-folders.mjs       # Products/NN_*/product.json
node scripts/sync-collections.mjs           # index.html ORGS/DOMAINS/LANES arrays

# Check sync without regenerating (CI mode)
node scripts/sync-products.mjs --check      # Fail if drifted
node scripts/sync-collections.mjs --check
node scripts/sync-product-folders.mjs --check

# Full suite
node scripts/validate-all.mjs                # Run everything
```

## Workflow: Adding a New Tool

1. Edit `Registry/glovebox-tools.json`: add entry to `tools[]` array
2. Run `node scripts/validate-glovebox.mjs` — validates schema
3. For each product that uses this tool, update `Products/NN_*/tools.json` to reference it
4. Commit together: `Registry/glovebox-tools.json` + updated `Products/*/tools.json`

## Workflow: Adding a Receipt

1. RoadChain receives an action (e.g., product deploy, agent assignment)
2. Create receipt object with required fields, link to prior receipt
3. Sign receipt with `crypto.signing` tool
4. Append to `Registry/roadchain-receipts.json` (never modify prior receipts)
5. Run `node scripts/validate-roadchain.mjs`

## Workflow: Granting Agent Permissions

1. Operator (Alexandria / Alexa) approves grant
2. Create grant entry in appropriate `Registry/carkeys.json` lane
3. CarKeys product queries grant, checks `crypto.signing` signature
4. Agent receives confirmation, logged to RoadChain
5. Agent can now use gated tool/product

---

## Implementation Status

### Completed ✅
- Registry schema files
- GloveBox tool registry (seed: 15 tools, expandable to 1,729)
- RoadChain receipt ledger with genesis block
- CarKeys expanded to 20 lanes (including device/payment gates)
- Agent folder structure (01 Lucidia, 02 Roadie, 05 Sebastian as templates)
- Product tool manifests (RoadOS, RoadCode, CarKeys, RoadChain, GloveBox)
- Product capability manifests
- Validators for GloveBox and RoadChain
- Architecture documentation

### In Progress 🔄
- Remaining 24 agent detailed README files
- Sync scripts for GloveBox and RoadChain
- Product tools.json for all 27 products
- Product capabilities.json for all 27 products

### Planned 📋
- Agent tools.json for all 27 agents
- Full 1,729 tool enumeration in GloveBox
- Receipt types catalog
- Capability tier system implementation
- Frontend wireframes (index.html enhancements)
