# RoadChain Receipt: Road / RoadOS / Roadies Route + Handoff v1

Date: 2026-09-13
Scope: `blackboxprogramming/road`, `blackboxprogramming/RoadOS`, `blackboxprogramming/roadies`

## Intent

Turn the Road / RoadOS / Roadies naming model into an executable local collaboration contract without conflating identity, handoff, provider invocation, tool authority, code execution, or completion.

## Repository heads observed after integration

- `blackboxprogramming/road`: `c7e05580add8fb9245ec16efda963809cf0cd3be`
- `blackboxprogramming/RoadOS`: `e82d762bd1e9a0ea07c71adec63d0b2f7fe1f83c`
- `blackboxprogramming/roadies`: `eb9b841c03ba8c67a57f29535a2c2e10b93a2645`

These are observed repository heads at receipt-writing time, not permanent identity claims.

## Road

Added a versioned `road-route/v1` contract and example Route:

- `routes/road-route.schema.json`
- `routes/hello-blackroad.route.json`
- `ROUTES.md`

The Route carries intent, participant roles, declared permission scope, provider policy, and mandatory receipt policy. Participant names do not grant authority.

## RoadOS

Added:

- `route.py`: read-only planning plus dry-run-by-default local handoff dispatch
- `handoff.py`: deterministic, read-only Roadie inbox discovery and handoff verification
- `ROUTES.md`
- `HANDOFFS.md`
- `tests/test_route.py`
- `tests/test_handoff.py`
- `.github/workflows/tests.yml`

Route dispatch creates immutable `roadie-handoff/v1` envelopes and a content-hashed RoadOS dispatch receipt. Handoff IDs are derived from canonical content.

Inbox discovery revalidates the handoff identifier, Roadie route, canonical Road/project routes, pending status, SHA-256 provenance, and the absence of claimed provider/tool execution before surfacing work.

## Roadies

Added:

- `protocol/ROADIE_PROTOCOL.md`
- `protocol/HANDOFF.md`
- `protocol/INBOX.md`
- `schemas/roadie-manifest.schema.json`
- `schemas/roadie-handoff.schema.json`

The unbound Roadies catalog continues to separate BlackRoad identity from provider/model identity. Preferred Ramps are labels, not credentials.

## Authority boundaries

The implemented v1 path is:

```text
Road Route
  -> RoadOS plan
  -> receipted local handoff
  -> verified Roadie inbox
```

The following are deliberately **not** implied by that path:

- provider connection
- model invocation
- tool grant
- Road program execution
- Roadie acceptance
- task completion
- deployment authority

Those require later explicit evidence and grants.

## Verification

RoadOS GitHub Actions main push run `34806480075` completed successfully for head `e82d762bd1e9a0ea07c71adec63d0b2f7fe1f83c` after the Route and inbox surfaces, tests, documentation, and ecosystem manifest were present.

No provider credentials, API keys, model secrets, device secrets, or private runtime state were committed by this integration.

## Canon statement

Road expresses the work. RoadOS validates and carries the work. Roadies receive bounded work. Ramps are optional provider boundaries. Receipts prove which step actually happened.
