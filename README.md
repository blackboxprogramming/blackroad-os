# BlackRoad OS

**Browser-native operating environment.** 27 products, 27 agents, a hybrid mesh
networking backbone, a Git-native data plane, and RoadChain provenance — with
context that hands off across one road.

This repository is the **canon and implementation foundation**: the single source
of truth from which the product surfaces, the agent roster, and the rendered
RoadOS desktop are generated.

> Canon explains. Registry structures. Receipts prove.

---

## Quick start

```bash
git clone https://github.com/blackboxprogramming/blackroad-os.git
cd blackroad-os

# Validate the source of truth
node scripts/validate-registry.mjs      # products.json
node scripts/validate-agents.mjs        # agents.json
node scripts/validate-collections.mjs   # orgs, domains, lanes, carkeys

# Check that generated artifacts are in sync
node scripts/sync-products.mjs --check
node scripts/sync-collections.mjs --check
node scripts/sync-product-folders.mjs --check
```

Open `index.html` in a browser to see the self-contained RoadOS desktop.
No build step, no server, no dependencies.

---

## How this repository works

Everything flows in one direction:

```
Registry/*.json  ──validate──>  schemas/  ──sync──>  index.html
   (truth)                                       └──>  Products/NN_*/product.json
```

`Registry/` is hand-edited. Everything downstream is **generated** — the
`PRODUCTS`, `ORGS`, `DOMAINS`, `LANES`, and `CARKEYS_LANES` blocks inside
`index.html`, and every `Products/NN_*/product.json`. CI
(`.github/workflows/registry.yml`) fails the build on any drift, so a
hand-edit to a generated file will not merge.

### Registries

| File | Count | Schema | Validator |
|------|-------|--------|-----------|
| `Registry/products.json` | 27 | `schemas/product.schema.json` | `scripts/validate-registry.mjs` |
| `Registry/agents.json` | 27 | `schemas/agent.schema.json` | `scripts/validate-agents.mjs` |
| `Registry/orgs.json` | 20 | `schemas/organization.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/domains.json` | 20 | `schemas/domain.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/lanes.json` | 20 | `schemas/lane.schema.json` | `scripts/validate-collections.mjs` |
| `Registry/carkeys.json` | 16 | `schemas/carkeys-lane.schema.json` | `scripts/validate-collections.mjs` |

---

## Repository map

| Path | Purpose | State |
|------|---------|-------|
| `CANON.md` | Living canon — current shape and rules | substantive |
| `NEXT.md` | Immediate next action | substantive |
| `CONTRIBUTING.md` | Source-of-truth and branch rules | substantive |
| `INDEX.md` | Full repository map | substantive |
| `index.html` | Self-contained rendered RoadOS desktop | substantive |
| `Registry/` | Single source of truth + JSON schemas | substantive |
| `Products/` | 27 product folders (`product.json` generated) | substantive |
| `Agents/` | 27-agent roster | roster done, folders planned |
| `scripts/` | Validators and sync generators | substantive |
| `Canon/` | Canon documents (currently held by root `CANON.md`) | scaffold |
| `Commands/` | Operator command surface (17 core commands) | scaffold |
| `Docs/` | Architecture, specs, research | scaffold |
| `Deployments/` | Runbooks, env maps, rollback plans | scaffold |
| `HighWay/` | Product 18 — infrastructure + hybrid mesh backbone | scaffold |
| `Receipts/` | RoadChain append-only proof trails | scaffold |
| `Assets/` | Brand, media, and UI assets | scaffold |
| `Archive/` | Frozen, superseded history | scaffold |

Every scaffold folder carries a `STATUS.md` stating its honest current state and
next step. Scaffold means *declared and reserved*, not *implemented* — the map is
deliberately honest about what does not exist yet.

---

## The 27 products

| # | Product | # | Product | # | Product |
|---|---------|---|---------|---|---------|
| 01 | RoadOS | 10 | RoadView | 19 | RoadSport |
| 02 | RoadCode | 11 | RoadChain | 20 | OfficeRoad |
| 03 | RoadTrip | 12 | RoadSide | 21 | RoadStream |
| 04 | PitStop | 13 | RoadCoin | 22 | RoadShow |
| 05 | RoadWork | 14 | CarPool | 23 | RoundAbout |
| 06 | BackRoad | 15 | BlackBoard | 24 | GloveBox |
| 07 | CarKeys | 16 | OneWay | 25 | RoadMap |
| 08 | RoadBook | 17 | RoadBand | 26 | RoadWire |
| 09 | RoadWorld | 18 | HighWay | 27 | Detour |

Each lives in `Products/NN_Name/` with a `README.md`, `ROUTING.md`, `SCHEMA.md`,
`UI_PLAN.md`, and a registry-generated `product.json`.

---

## Architecture

- **Hybrid mesh backbone** — Meshtastic for long-range low-bandwidth reach,
  Headscale/WireGuard for the encrypted overlay. Product 18, `HighWay/`.
- **Git-native data plane** — state is committed, diffable, and reviewable
  rather than hidden in a database.
- **RoadChain provenance** — append-only receipts in `Receipts/` and
  `06-ROADCHAIN-RECEIPTS/`, so any claim about what happened has a proof trail.
- **Context handoff** — agents pass working context across products so a task
  continues on one road instead of restarting at each boundary.

---

## Contributing

Read `CONTRIBUTING.md` first — it defines the source-of-truth and branch rules.
The short version:

1. Edit `Registry/*.json`, never a generated file.
2. Run the matching validator, then the `--check` sync scripts.
3. Regenerate rather than hand-patch `index.html` or `product.json`.
4. If a folder is a scaffold, update its `STATUS.md` honestly instead of
   implying work that has not been done.

---

## Related repositories

| Repository | Role |
|------------|------|
| [`blackroad-os`](https://github.com/blackboxprogramming/blackroad-os) | Canon and implementation foundation (this repo) |
| [`BlackRoad-OS-Live-Working-Version-Public`](https://github.com/blackboxprogramming/BlackRoad-OS-Live-Working-Version-Public) | Polished public live/demo surface |
| [`roadc`](https://github.com/blackboxprogramming/roadc) | RoadCode toolchain |
| [`Amundson-Mathematics`](https://github.com/blackboxprogramming/Amundson-Mathematics) | Mathematical framework |

---

## Links

- Website — [blackroad.io](https://blackroad.io)

---

*Remember the Road. Pave Tomorrow.*
