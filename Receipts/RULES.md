# Receipts — RULES

Local rules for receipt creation, maintenance, and RoadChain provenance.

## Receipt File Naming

Format: `RECEIPT-TYPE-DESCRIPTOR-DATE.md` or `TYPE-DESCRIPTOR-DATE.md`

Examples:
- `RECEIPT-01-roadOS-launch-2026-06-20.md` — Product 01 launch
- `COMPLETION-MESH-TOPOLOGY-2026-06-18.md` — Mesh topology design complete
- `INCIDENT-REGISTRY-DRIFT-2026-06-17.md` — Registry sync incident
- `REVIEW-SECURITY-CARKEYS-2026-06-16.md` — Security review of CarKeys

**Invariants:**
- Date is ISO format (YYYY-MM-DD)
- Type is CAPITALIZED, descriptive
- Filename should be self-explanatory (no "TODO-date.md")
- Sorted by date in directory listing

## Required Receipt Fields

```markdown
# Receipt: [Type] — [Descriptor]

**Date:** YYYY-MM-DD
**Owner:** [Agent Name] ([Agent Number]) / [Responsible Person if external]
**Status:** completed | approved | pending | rejected

## What

[One sentence: what was completed/decided]

[2-3 sentences: context and details]

## Why

[Why this matters to BlackRoad OS: unlocks next steps, reduces risk, validates assumption, etc.]

## Evidence

- Git commit: `[hash]` (link or reference)
- Test results: [link to test output/artifact]
- Approval: [sign-off from reviewer]
- Documentation: [link to resulting docs/PRs]

## Next

[What this enables or blocks for subsequent work]

---

**Receipt ID:** [YYYYMMDDnnn format for tracking, e.g., 20260618001]
```

## Receipt Lifecycle

1. **Created** — When work is completed, create receipt with status `completed`
2. **Reviewed** — Agent/owner reviews, approves → status `approved`
3. **Indexed** — Theodosia (Agent 23) adds to INDEX and receipt queries
4. **Archived** — Superseded receipts moved to Archive/ with link in NEXT.md

## Status Values

- `completed` — work done, awaiting approval
- `approved` — work done and signed off
- `pending` — in progress, work not finished
- `rejected` — work abandoned or reverted
- `archived` — superseded by newer receipt

## Invariants

- **No implementation claim without receipt** — status `active` or `real` must be backed by approved receipt
- **Receipts are append-only** — never delete or edit historical receipts (create new one if correction needed)
- **Date never lies** — receipt date must match actual completion (not backdated)
- **Evidence must link** — all evidence should be accessible (committed to repo, not expired links)
- **Cross-reference** — product/agent NEXT.md should reference receipt for status claims

## Maintenance

- Receipts reviewed by Theodosia (Agent 23) for completeness
- Receipts archived by Theodosia on quarterly basis (move to Archive/, leave cross-ref link)
- Summary queries run by Theodosia (or `receipt-summary.mjs` script) weekly
- RoadChain product (Product 11) ensures receipt immutability

## Example: First Receipt (CLAUDE.md Work)

See `_registry/RECEIPT_EXAMPLE.md` for worked example of CLAUDE.md documentation receipt.
