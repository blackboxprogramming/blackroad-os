# Docs — RULES

Local rules for documentation in this folder.

## Document Types and Structure

### Architecture Documents (ARCHITECTURE.md, *_ARCHITECTURE.md)

Required sections:
1. Overview — one sentence
2. Components — list with boundaries
3. Data flow — how data moves
4. Interfaces — APIs between components
5. Security — threat model + mitigations
6. Failure modes — what can break

### Specification Documents (*_SPEC.md)

Required sections:
1. Purpose — why this spec exists
2. Scope — what's included/excluded
3. Definitions — key terms
4. Requirements — functional + non-functional
5. Protocol — format, flow, error handling
6. Examples — realistic usage
7. Edge cases — boundary conditions

### Implementation Guides (*_GUIDE.md)

Required sections:
1. Prerequisites — what you need before starting
2. Steps — step-by-step procedure
3. Verification — how to test success
4. Troubleshooting — common issues + fixes
5. Rollback — how to undo if needed

## Naming Conventions

- Architecture: `ARCHITECTURE.md`, `COMPONENT-architecture.md`
- Specs: `COMPONENT-spec.md` (e.g., `mesh-networking-spec.md`)
- Guides: `COMPONENT-guide.md` (e.g., `deployment-guide.md`)
- Research: `research-TOPIC.md` (e.g., `research-meshtastic-devices.md`)

## Invariants

- Every doc must have a `Status` line (Draft/Review/Stable)
- Code examples must be realistic and runnable
- Architectural decisions must cite Canon + CONTRIBUTING.md rules
- Specs must not contradict Registry definitions
- Docs must cross-link to relevant products/agents

## Maintenance

- Docs reviewed by Ophelia (Agent 16) for clarity
- Technical accuracy reviewed by domain experts (Elias for arch, Sebastian for code, etc.)
- Archive superseded docs to Archive/ instead of deleting
