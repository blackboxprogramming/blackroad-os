# Contributing to BlackRoad OS

This repo is the **canon + registry + scaffold** for BlackRoad OS, plus the
rendered desktop (`index.html`). Multiple agents (Claude, Grok, …) and the
Operator all work here, so the rules below exist to keep fast, parallel work
from turning into drift. They restate `CANON.md`: *structured truth, then
docs, then receipts — no fake implementation claims.*

## The one rule that matters most

**`Registry/` is the single source of truth. `index.html` is generated from it.**

- Product data lives in `Registry/products.json` only.
- The `PRODUCTS` array in `index.html` is **generated** — it sits between
  `AUTO-GENERATED:PRODUCTS:START` / `END` markers. **Never hand-edit it.**
- After changing `Registry/products.json`, run the sync and commit both files:

  ```bash
  node scripts/sync-products.mjs         # regenerate the block in index.html
  node scripts/sync-product-folders.mjs  # regenerate each Products/NN_*/product.json
  node scripts/validate-registry.mjs     # check schema + invariants
  ```

- Each `Products/NN_*/product.json` is **also generated** — it is a byte-for-byte
  projection of the matching registry record. **Never hand-edit it.** This keeps
  one product schema in the repo instead of a second, drifting copy.

CI (`.github/workflows/registry.yml`) runs both on every push/PR and **fails
if the registry is invalid or `index.html` has drifted** from it. That is what
prevents two copies of the truth from diverging.

## Branch & commit workflow

1. **One branch per agent/task.** Never push directly to `main`. Each worker
   gets its own branch (e.g. `claude/<task>`, `grok/<task>`), then opens a PR.
   This is what keeps "50 commits in 2 seconds" reviewable instead of chaotic.
2. **Scope commits to one concern.** A commit message should describe a change,
   not a file dump.
3. **Open a PR into `main`.** Let CI run. Merge after it's green.
4. **No fake "done".** A `status` of `active` / `real` must be backed by a
   receipt in `Receipts/` (per `CANON.md`). Intent is `planned` / `next`.

## Editing products

`Registry/products.json` holds 27 products validated against
`Registry/schemas/product.schema.json`.

- **Required** fields (used by the UI): `number`, `id`, `slug`, `name`, `role`,
  `status`, `meaning`, `does[]`, `org`, `domain`, `agents[]`, `receipts[]`,
  `carkeys[]`, `next`.
- **Optional** canon fields: `category`, `definition`, `boundary`, `mvp`,
  `implementation_status`, `risk_level`, `primary_handoff`.
- `status` ∈ `active | next | planned | mvp-stub`. `id` must equal `slug`.
  There must be exactly 27 products numbered `01`–`27`.

To add/change a product: edit the JSON → `node scripts/sync-products.mjs` →
`node scripts/validate-registry.mjs` → commit `Registry/products.json` **and**
`index.html` together.

## Viewing the desktop

`index.html` is fully self-contained — open it directly in a browser
(double-click / `file://`). No build server or network is required to view it.

## Quick reference

| Task | Command |
|------|---------|
| Regenerate `index.html` from registry | `node scripts/sync-products.mjs` |
| Fail if `index.html` drifted (CI mode) | `node scripts/sync-products.mjs --check` |
| Regenerate every `Products/NN_*/product.json` | `node scripts/sync-product-folders.mjs` |
| Fail if a folder `product.json` drifted (CI mode) | `node scripts/sync-product-folders.mjs --check` |
| Validate the product registry | `node scripts/validate-registry.mjs` |
| Validate the agent registry | `node scripts/validate-agents.mjs` |
| Check agent roster matches `index.html` | `node scripts/validate-agents-roster.mjs` |
| Regenerate `index.html` ORGS + DOMAINS | `node scripts/sync-collections.mjs` |
| Fail if ORGS/DOMAINS drifted (CI mode) | `node scripts/sync-collections.mjs --check` |
| Validate the org + domain registries | `node scripts/validate-collections.mjs` |
