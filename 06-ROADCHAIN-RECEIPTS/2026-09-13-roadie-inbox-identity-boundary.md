# RoadChain Receipt: Roadie Inbox + Identity-Only Planning Boundary

Date: 2026-09-13
Scope: Road / RoadOS / Roadies collaboration path

## Change

Extended the v1 Route/handoff integration with two additional safeguards:

1. RoadOS now provides `handoff.py`, a deterministic local Roadie inbox reader that validates handoff content identity and provenance before surfacing pending work.
2. `route.py` now rejects Roadies catalogs that bind a `brain_id` or grant `allowed_tools`, keeping the catalog an identity surface rather than an authority surface.

## Roadies protocol

Added `protocol/INBOX.md` and tracked it in the Roadies ecosystem manifest. Inbox discovery grants no authority and does not prove provider connection, tool execution, Roadie acceptance, or task completion.

## RoadOS implementation

Added:

- `handoff.py`
- `HANDOFFS.md`
- `tests/test_handoff.py`
- `tests/test_route_catalog_boundary.py`

The inbox validates:

- content-derived handoff IDs
- Roadie identity/route agreement
- canonical Road/project Routes
- pending status
- permission uniqueness
- provider policy
- Route/project/catalog SHA-256 provenance
- `provider_connection = not-requested`
- `tool_execution = not-requested`

Invalid handoff files are reported and not promoted into inbox items. Strict mode fails if any invalid handoff is present.

## Verification

RoadOS GitHub Actions main push run `34806669611` completed successfully for head `8c72f46ad0af311186b164c1be03ba0af320d16b`.

No provider connection, tool execution, model invocation, deployment, or external action was performed by this change.
