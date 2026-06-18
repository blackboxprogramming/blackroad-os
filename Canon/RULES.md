# Canon — RULES

Local rules for canon documentation in this folder.

## Naming Conventions

- Product canon: `product-NN-slug.md` (e.g., `product-01-roadOS.md`)
- Agent canon: `agent-NN-slug.md` (e.g., `agent-01-lucidia.md`)
- Cross-reference index: `canon-products.md`, `canon-agents.md`
- Strategic docs: `strategic-<topic>.md` (e.g., `strategic-mesh-networking.md`)

## Canon Document Structure

Each canon document must include:

1. **Title** — entity name and number
2. **Role/Purpose** — what this product/agent is
3. **Boundary** — what it does and doesn't do
4. **Key Rules** — constraints or requirements specific to this entity
5. **Handoffs** — context passing to other products/agents
6. **Status** — current implementation state
7. **Receipts** — proof of completion/progress (links to `Receipts/`)

## Canon Invariants

- Statements must be falsifiable and backed by proof
- No aspirational claims — only documented truth
- Status of `active` or `real` requires receipt in `Receipts/`
- Interim statuses: `planned`, `next`, `mvp-stub`
- Cross-references must link to canonical sources (Registry/, root CANON.md, CONTRIBUTING.md)

## Maintenance

- Canon is append-only (superseded docs moved to `Archive/`)
- Updates synchronized with Registry/ via scripts/sync-* commands
- Changes require review by Lucidia (Agent 01) or Octavia (Agent 12)
