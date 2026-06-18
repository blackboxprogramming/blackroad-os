# Receipts — NEXT

**Immediate next action:** Create RECEIPT_TEMPLATE.md and first completion receipt for CLAUDE.md documentation work.

**Current state:**
- Receipts/ folder scaffold exists
- RoadChain (Product 11) provides provenance mechanism
- No receipts created yet

**Next steps:**
1. Write RECEIPT_TEMPLATE.md with:
   - Standard receipt header format
   - Required fields (date, owner, what, why, evidence, status, next)
   - Examples of each receipt type
   - Git commit reference format
2. Create first receipt:
   - RECEIPT-CLAUDE-2026-06-18.md (CLAUDE.md documentation work)
   - Owner: Claude (Agent + Session)
   - Evidence: git commit hash, CLAUDE.md file location
   - Status: completed
3. Create receipt query script `scripts/receipt-status.mjs`
4. Create receipt aggregation script `scripts/receipt-summary.mjs`
5. Update each product/agent's NEXT.md to cross-reference receipts

**Owner:** Theodosia (Agent 23) / Records keeper

**Status:** Setup phase — templates + first receipt needed
