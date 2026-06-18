# Receipts — INDEX

Map of RoadChain proof trails, project status, and completion records.

**Purpose:** Receipts are the append-only evidence that backs up all implementation claims. Status must be backed by proof (receipt). No fake "done" — only documented completion.

## Receipt Types

| Type | Purpose | File pattern |
|------|---------|--------------|
| Completion | Product/feature shipped | `RECEIPT-NN-productname-date.md` |
| Milestone | Project checkpoint reached | `MILESTONE-PROJECT-date.md` |
| Decision | Major decision documented | `DECISION-TOPIC-date.md` |
| Incident | Issue occurred + resolved | `INCIDENT-TOPIC-date.md` |
| Review | Security/code/design review | `REVIEW-TYPE-date.md` |
| Test | Testing campaign results | `TEST-COMPONENT-date.md` |

## Receipt Structure

Every receipt must include:

1. **Date** — when this was completed/decided
2. **Owner** — who is responsible (agent + human contact)
3. **What** — what was done or decided
4. **Why** — why this matters to BlackRoad OS
5. **Evidence** — links to commits, test results, approvals
6. **Status** — completed/approved/pending/rejected
7. **Next** — what this enables or blocks

## Current Status

**Structure:** Receipts folder scaffold exists
**Receipts:** None yet
**Next:** First receipt = CLAUDE.md documentation work (this session)

## Receiving Receipts

To create a new receipt:

1. Copy receipt template from `_registry/RECEIPT_TEMPLATE.md`
2. Fill in all required fields
3. Add git commit references or test result links
4. Commit to Receipts/ with naming convention
5. Cross-reference in the relevant product/agent's NEXT.md

## Querying Receipts

Current status queries (planned):
- `node scripts/receipt-status.mjs products/NN` — product NN completion
- `node scripts/receipt-status.mjs agents/NN` — agent NN activity
- `node scripts/receipt-status.mjs all` — all receipts, grouped by type

See RULES.md for receipt management practices.
