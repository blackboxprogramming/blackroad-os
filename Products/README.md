# Products/

The 27 BlackRoad products.

Every product must hand off context instead of trapping the user in another silo.

See individual product folders for full canon definitions.

## Structure
Each product folder contains:
- README.md (meaning, boundary, MVP, integrations)
- product.json (machine-readable — **generated** from `Registry/products.json`, do not hand-edit)
- routing.md
- schema.md (if applicable)
- status.md
- next.md
- _receipts/
- _registry/

## Status
Canon-ready (Level 4). Implementation planned.

Primary handoff rule: RoadOS is the shell. Products route through RoadOS command dock and agent rail.