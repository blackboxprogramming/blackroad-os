# Test suite

Dependency-free tests for the registry **validators** and **sync generators** in
`scripts/`, using Node's built-in test runner (`node:test`). No `npm install`,
no framework — the same "no external build tools" posture as the rest of the repo.

```bash
npm test                          # or:
node --test test/*.test.mjs
```

The shell expands the test-file pattern before Node runs, so Node 20 does not
need built-in glob support. CI invokes the same `npm test` command.

Requires Node 20+ (CI pins 20; developed against 22).

## Why these tests exist

Before this suite the validators only ever ran against the **real, already-valid**
registry. Their entire failure path — *does the validator actually reject bad
data?* — was never exercised, so a regression that silently neutered a check
would pass CI forever. These tests feed each validator deliberately-broken
registries and assert it exits non-zero with the right message, plus a golden
valid case that exits 0.

## How it works

Each script honours a `BLACKROAD_ROOT` environment override. `test/helpers.mjs`
copies the real `Registry/` (and `index.html` where needed) into a throwaway temp
directory, mutates one record, and runs the **real** script against the copy via
`BLACKROAD_ROOT`. So the tests exercise the actual CLI contract (exit code +
stderr), not a re-implementation of the validation logic.

| Test file | Covers |
|---|---|
| `validate-registry.test.mjs` | product schema, enums, patterns, `id==slug`, duplicates, count, contiguity |
| `validate-agents.test.mjs` | agent schema, `slug==name.toLowerCase()`, duplicates, count, `total_agents` |
| `validate-collections.test.mjs` | orgs/domains/lanes/carkeys counts, duplicates, canonical domain names, overlapping roots, per-file error attribution |
| `validate-agents-roster.test.mjs` | registry ↔ `index.html` roster drift, missing-array handling |
| `validate-references.test.mjs` | product and domain foreign keys, hostname boundaries, malformed link collections, org warnings |
| `sync-products.test.mjs` | `--check` drift detection, regenerate round-trip, missing-marker handling |

## Cross-registry references (`scripts/validate-references.mjs`)

New guard that resolves the foreign keys linking the registries:

- `product.agents[]` → `agents.json` (by name) — **error** on a dangling ref
- `product.domain` → `domains.json` (exact root or dot-delimited subdomain) — **error** on a malformed or foreign hostname
- `domain.products[]` → `products.json` (by name) — **error** on a dangling ref
- `domain.agents[]` → `agents.json` (by name) — **error** on a dangling ref
- `domain.nextRoads[]` → `domains.json` (exact root or dot-delimited subdomain) — **error** on a malformed or foreign hostname
- `product.org` → `orgs.json` (by name) — **warning** for now

`product.org` is a warning, not an error, because the registry already contains
org references that resolve to no org record — e.g. `BlackRoad-Agents`,
`BlackRoad-Knowledge`, `BlackRoad-Private` against the `BlackRoad-OS-*` org names.
Picking the correct org for each of those products is a canon call for the
operator, not something the script should guess. Once reconciled, set
`ORG_SEVERITY = "error"` in the validator (one line) to lock it down.

Domain names are canonical lowercase ASCII with valid 1–63 character labels and
at most 253 characters overall. Roots must be unique and non-overlapping. Input
is validated as stored; validators do not silently trim, lowercase, parse URLs,
or rewrite generated projections. These are offline namespace checks, not DNS
or public-suffix registration verification.
