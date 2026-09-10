# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

**BlackRoad OS** is a browser-native operating environment with:
- 27 products (organized in `Products/` directory)
- 27 agents (registered in `Registry/agents.json`, folders in `Agents/`)
- 20 organizations and domains (in registries)
- 17 core commands (in `Commands/`)
- A single source of truth: the registry system

The rendered desktop UI is `index.html` (fully self-contained, open directly in browser).

## Critical Architecture: The Registry System

**The cardinal rule: `Registry/` is the single source of truth. Never hand-edit generated files.**

### How it works:
1. **Canonical data** lives in `Registry/*.json` files (validated against `Registry/schemas/*.schema.json`)
2. **Generated files** are projections of registry data:
   - `index.html` — contains `PRODUCTS`, `ORGS`, `DOMAINS`, `LANES`, `CARKEYS_LANES` arrays (between auto-generated markers)
   - `Products/NN_*/product.json` — byte-for-byte projection of each registry product record
   - Attempting to hand-edit these **will cause CI to fail**

### Registry Files:

| File | Purpose | Count | Array key | Validator |
|------|---------|-------|-----------|-----------|
| `products.json` | All 27 products | 27 | `products` | `validate-registry.mjs` |
| `agents.json` | All 27 agents | 27 | `agents` | `validate-agents.mjs` |
| `orgs.json` | Organizations | 20 | `organizations` | `validate-collections.mjs` |
| `domains.json` | Root domains | 20 | `domains` | `validate-collections.mjs` |
| `lanes.json` | RoadMap build-status lanes | 20 | `lanes` | `validate-collections.mjs` |
| `carkeys.json` | CarKeys permission lanes | 16 | `lanes` | `validate-collections.mjs` |

### Registry JSON shape (IMPORTANT):

Each registry file is a **wrapped object**, not a bare array. The records live
under a named key (see "Array key" column above), alongside metadata:

```jsonc
{
  "schema_version": "2.0",
  "last_updated": "2026-06-19",
  "note": "Single source of truth for the 27 products. ...",
  "products": [ /* the 27 records */ ]
}
```

So to query records you must go through the key — e.g. `.products[]`, not `.[]`.
When adding/removing records, keep the metadata block and update `last_updated`
(and `total_*` counts where present).

## Essential Commands

### Registry Synchronization & Validation

After editing any registry file in `Registry/`:

```bash
# Regenerate index.html PRODUCTS array from registry
node scripts/sync-products.mjs

# Regenerate all Products/NN_*/product.json from registry
node scripts/sync-product-folders.mjs

# Validate product registry
node scripts/validate-registry.mjs

# Validate agent registry
node scripts/validate-agents.mjs

# Check agent roster matches index.html
node scripts/validate-agents-roster.mjs

# Regenerate ORGS/DOMAINS/LANES/CARKEYS_LANES in index.html
node scripts/sync-collections.mjs

# Validate all org/domain/lane/carkeys registries
node scripts/validate-collections.mjs
```

### CI Mode (fail if drifted)

```bash
# Check if index.html is in sync without regenerating
node scripts/sync-products.mjs --check

# Check if Products/NN_*/product.json files are in sync
node scripts/sync-product-folders.mjs --check

# Check if index.html collections are in sync
node scripts/sync-collections.mjs --check
```

### Full Validation Suite

```bash
# Run everything the CI pipeline runs
node scripts/validate-registry.mjs && \
node scripts/validate-agents.mjs && \
node scripts/validate-agents-roster.mjs && \
node scripts/validate-collections.mjs && \
node scripts/sync-products.mjs --check && \
node scripts/sync-collections.mjs --check && \
node scripts/sync-product-folders.mjs --check
```

## Workflow: Editing Products

When you need to add, update, or remove products:

1. **Edit only** `Registry/products.json`
   - Required fields: `number`, `id`, `slug`, `name`, `role`, `status`, `meaning`, `does[]`, `org`, `domain`, `agents[]`, `receipts[]`, `carkeys[]`, `next`
   - Optional canon fields: `category`, `definition`, `boundary`, `mvp`, `implementation_status`, `risk_level`, `primary_handoff`, `core_promise`
   - Records go inside the `products` array of the wrapped object (see "Registry JSON shape" above)
   - Constraint: exactly 27 products numbered `01`–`27`; `id` must equal `slug`
   - Valid statuses: `active | next | planned | mvp-stub`

2. **Run sync commands** (in order):
   ```bash
   node scripts/sync-products.mjs
   node scripts/sync-product-folders.mjs
   node scripts/validate-registry.mjs
   ```

3. **Commit both files together:**
   - `Registry/products.json` (the source)
   - `index.html` (the generated output)
   - Always commit them together — they must stay in sync

4. **Push to your feature branch** (e.g., `claude/<task>-<id>`)

5. **CI validates** on push/PR — it will fail if:
   - Registry JSON is invalid
   - Schema validation fails
   - `index.html` is out of sync with registry
   - Per-product `product.json` files are out of sync

## Workflow: Editing Products (Alternative: Direct Edits)

If you need to bulk-edit multiple registry files:

```bash
# Edit Registry/products.json, Registry/agents.json, etc.
# Then run the complete sync + validate pipeline:
node scripts/sync-products.mjs && \
node scripts/sync-product-folders.mjs && \
node scripts/validate-registry.mjs && \
node scripts/validate-agents.mjs && \
node scripts/validate-collections.mjs && \
node scripts/sync-collections.mjs
```

## Directory Structure

```
blackroad-os/
├── CANON.md                     # Living canon: current shape + rules
├── CONTRIBUTING.md              # Source-of-truth rules & branch workflow
├── INDEX.md                     # Repository map
├── NEXT.md                      # Immediate next actions
├── README.md                    # Short repo intro
├── Registry/                    # Single source of truth (ALL registries + schemas)
│   ├── products.json            #   27 products   (records under `products`)
│   ├── agents.json              #   27 agents     (records under `agents`)
│   ├── orgs.json                #   20 orgs       (records under `organizations`)
│   ├── domains.json             #   20 domains    (records under `domains`)
│   ├── lanes.json               #   20 lanes      (records under `lanes`)
│   ├── carkeys.json             #   16 lanes      (records under `lanes`)
│   ├── README.md
│   └── schemas/                 # JSON schemas for validation
├── Products/                    # 27 product folders (product.json auto-generated)
│   ├── 01_RoadOS/ … 27_Detour/  #   27 numbered folders
│   ├── INDEX.md
│   └── PRODUCT_STATUS.json
├── Agents/                      # Agent roster (README + STATUS; per-agent folders planned)
├── scripts/                     # Validators & sync generators (Node.js, .mjs)
│   ├── validate-registry.mjs    #   validates products.json
│   ├── validate-agents.mjs      #   validates agents.json
│   ├── validate-agents-roster.mjs  # checks roster matches index.html
│   ├── validate-collections.mjs #   validates orgs/domains/lanes/carkeys
│   ├── sync-products.mjs         #  regenerates PRODUCTS in index.html
│   ├── sync-product-folders.mjs  #  regenerates Products/NN_*/product.json
│   └── sync-collections.mjs      #  regenerates ORGS/DOMAINS/LANES/CARKEYS_LANES
├── Canon/                       # Canon documents (scaffold)
├── Commands/                    # Operator command surface (17 core commands)
├── Docs/                        # Architecture, specs, research (README + STATUS)
├── docs/                        # Claude working notes / product batch reports
├── Deployments/                 # Runbooks, env maps, rollback plans
├── HighWay/                     # Product 18: hybrid mesh backbone
├── Receipts/                    # RoadChain append-only proof trails
├── 06-ROADCHAIN-RECEIPTS/       # Claude handoff receipts (product batches)
├── Archive/ · Assets/           # Scaffold folders (README + STATUS)
├── .github/workflows/           # CI pipeline
│   └── registry.yml             #   runs all validators + sync checks
├── index.html                   # Self-contained desktop UI (~30k lines, generated/auto-synced)
└── BlackRoadOS_RoadOS_Index.html # Standalone hand-written RoadOS prototype (NOT generated)
```

> **Two HTML files, different roles.** `index.html` is the large, generated
> desktop UI (its `PRODUCTS`/`ORGS`/`DOMAINS`/`LANES`/`CARKEYS_LANES` arrays are
> auto-synced from `Registry/` — never hand-edit them). `BlackRoadOS_RoadOS_Index.html`
> is a small, standalone RoadOS prototype built by hand and is **not** part of the
> registry sync/validation pipeline.
>
> **`Docs/` vs `docs/`.** `Docs/` (capital D) holds architecture/specs scaffolding;
> `docs/` (lowercase) holds Claude working notes and product batch reports. They are
> distinct directories — check case when referencing.

## Branch & Commit Workflow

1. **Create a feature branch** for your task: `claude/<task>-<id>` or similar
   - Never push directly to `main`
   - One branch per agent/task keeps parallel work reviewable

2. **Scope commits to one concern**
   - Commit messages should describe the change, not dump files
   - If editing registry: commit registry file + generated output together (e.g., `products.json` + `index.html`)

3. **Open a PR into `main`**
   - CI runs automatically (`.github/workflows/registry.yml`)
   - CI must pass (validates all registries, checks sync, runs validators)
   - Merge after green

4. **No fake implementation claims**
   - Product `status` of `active` or `real` must be backed by a receipt in `Receipts/`
   - Interim statuses: `planned`, `next`, `mvp-stub`

## Key Rules

### Unbreakable

- **Registry is truth.** `Registry/` is the single source of truth; all generated files are projections
- **Never hand-edit generated files.** `index.html` arrays and `Products/NN_*/product.json` are auto-generated (between markers or entirely)
- **Sync after registry edits.** Always run sync scripts after changing any `Registry/*.json`
- **Commit sync outputs together.** When you edit `Registry/products.json`, commit `Registry/products.json` AND `index.html` in the same commit
- **Validate before push.** Run validators locally; CI will fail if validation fails

### Product Semantics

- Every product must hand off context (no user silo traps)
- `Roadie` is an agent only, never a product
- `PitStop` is the homework/learning portal
- `GloveBox` is capabilities/meta-info/tools
- `RoadChain` is receipts/provenance (honest scope — no overclaiming legal compliance)

### Honesty of Status (no fake-done)

- Product `status` of `active` must be backed by a receipt in `Receipts/`; otherwise use `planned`, `next`, or `mvp-stub`
- RoadMap lanes (`Registry/lanes.json`) use `status = done | fake_done | next | planned`
- **`fake_done` is deliberate:** it flags a claim that *looks* finished but is **not** yet backed by a receipt. Never quietly upgrade `fake_done` → `done` — a lane only becomes `done` once a real receipt exists

### Agent Semantics

- Agents request; Operator (Alexa/Alexandria) approves
- CarKeys gates access
- RoadChain records provenance
- Current state: roster registered in `Registry/agents.json`; per-agent folders planned

## Common Patterns

### Viewing the Desktop

```bash
# Open in browser (no build server needed)
open index.html  # macOS
xdg-open index.html  # Linux
# Or double-click in file manager
```

### Checking a Specific Product

```bash
# Read the registry entry (records live under the `products` key)
cat Registry/products.json | jq '.products[] | select(.number == "01")'

# Read the generated folder projection
cat Products/01_RoadOS/product.json
```

### Checking the Agent Roster

```bash
# View canonical agent list (records live under the `agents` key)
cat Registry/agents.json | jq '.agents[] | {id, name, role}'

# Validate it
node scripts/validate-agents.mjs
```

### Fixing a Drift Error

If CI fails with "index.html is out of sync":

```bash
# Regenerate and commit
node scripts/sync-products.mjs
git add index.html
git commit -m "Sync index.html with Registry/products.json"
git push
```

If CI fails with "per-folder product.json drifted":

```bash
node scripts/sync-product-folders.mjs
git add Products/
git commit -m "Sync Products/*/product.json with Registry/products.json"
git push
```

## CI/CD Pipeline

CI runs on every push and PR (`.github/workflows/registry.yml`):

1. **Validate** `Registry/products.json` against schema
2. **Validate** `Registry/agents.json` against schema
3. **Check** agent roster matches `index.html`
4. **Validate** `Registry/orgs.json` + `domains.json` + `lanes.json` + `carkeys.json`
5. **Sync-check** `index.html` against registry (fails if drifted)
6. **Sync-check** collections arrays in `index.html`
7. **Sync-check** `Products/NN_*/product.json` against registry

**All must pass for merge.**

## Node.js Environment

- Node.js 20+ required
- All scripts are `.mjs` (ES modules)
- Validators use JSON schema validation (schemas in `Registry/schemas/`)
- No external build tools or server required for viewing `index.html`

## Anti-Patterns to Avoid

- ❌ Hand-editing the `PRODUCTS` array in `index.html`
- ❌ Hand-editing any `Products/NN_*/product.json` file
- ❌ Pushing `Registry/*.json` changes without running sync scripts
- ❌ Committing `Registry/*.json` without committing generated files (`index.html`, `Products/*/product.json`)
- ❌ Claiming a product is `active` without a proof receipt in `Receipts/`
- ❌ Creating feature branches directly from `main` and not using `-u origin <branch>` on first push
- ❌ Editing registry files without validating (CI will catch it, but better to catch locally)

## For Future Development

See `NEXT.md` for immediate roadmap:
- Full folder skeleton matching BLACKROAD UNIVERSAL FILESYSTEM v1
- 27 product folders with canon content
- 27 agent folders (roles, handoffs, permissions, device assignments)
- Hybrid mesh integration plan (Meshtastic + Headscale/WireGuard) in `HighWay/`

See `Agents/STATUS.md` and `INDEX.md` for folder-by-folder status.
