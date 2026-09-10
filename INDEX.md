# BlackRoad OS — Root INDEX

Map of the repository. Canon explains, Registry structures, Receipts prove.
See `CANON.md` for the canon and `CONTRIBUTING.md` for the source-of-truth rules.

## Top-level map

| Path | Purpose | State |
|------|---------|-------|
| `CANON.md` | Living canon (current shape + rules) | substantive |
| `NEXT.md` | Immediate next action | substantive |
| `CONTRIBUTING.md` | Source-of-truth + branch rules | substantive |
| `index.html` | Self-contained rendered "RoadOS" desktop (generated arrays) | substantive |
| `Registry/` | Single source of truth — products, agents, orgs, domains + schemas | substantive |
| `Products/` | 27 product folders (`product.json` generated from registry) | substantive |
| `Agents/` | 27-agent roster (registered in `Registry/agents.json`) | roster done, folders planned |
| `scripts/` | Validators + sync generators (registry → index.html / folders) | substantive |
| `Canon/` | Canon documents (currently held by root `CANON.md`) | scaffold |
| `Commands/` | Operator command surface (17 core commands) | scaffold |
| `Docs/` | Architecture, specs, research | scaffold |
| `Deployments/` | Runbooks, env maps, rollback plans | scaffold |
| `HighWay/` | Product 18 — infrastructure + hybrid mesh backbone | scaffold |
| `Receipts/` | RoadChain append-only proof trails | scaffold |
| `Assets/` | Brand / media / UI assets | scaffold |
| `Archive/` | Frozen, superseded history | scaffold (empty) |

Each scaffold folder carries a `STATUS.md` with its honest current state and next step.

## Registries (single source of truth)

| File | Count | Schema | Validator |
|------|-------|--------|-----------|
| `Registry/products.json` | 27 | `schemas/product.schema.json` | `scripts/validate-registry.mjs` |
| `Registry/agents.json` | 27 | `schemas/agent.schema.json` | `scripts/validate-agents.mjs` |
| `Registry/orgs.json` | 20 | `schemas/organization.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/domains.json` | 20 | `schemas/domain.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/lanes.json` | 20 | `schemas/lane.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/carkeys.json` | 16 | `schemas/carkeys-lane.schema.json` | `scripts/validate-collections.mjs` |

Generated-from-registry (never hand-edit): the `PRODUCTS` / `ORGS` / `DOMAINS` /
`LANES` / `CARKEYS_LANES` blocks in `index.html`, and every
`Products/NN_*/product.json`. CI (`.github/workflows/registry.yml`) fails on any
drift.
