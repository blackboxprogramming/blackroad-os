# Routing — RoadChain

## Route here when the user wants to...
- Record, verify, or view receipts, provenance, audit trails, or hash-chain events
- Prove that something important happened, changed, deployed, or was decided
- Check chain integrity or rollback references
- Get inspectable memory/proof without overclaiming legal compliance

## Do not route here when...
- General data movement or sovereignty (OneWay)
- Business compliance filings (RoadWork)
- Creating content (RoadBook, BlackBoard, etc.)

## Common confusion boundaries

### RoadChain vs OneWay
OneWay = controlled data flow and transformation.
RoadChain = receipts and proof of what happened.
Handoff: OneWay writes RoadChain receipts for important flows.

### RoadChain vs RoadWork
RoadWork = doing the operational/compliance work.
RoadChain = proving that the work happened with receipts.
Handoff: RoadWork actions that matter get RoadChain receipts.

### RoadChain vs RoadMap
RoadMap = status and progress view.
RoadChain = the underlying proof layer that RoadMap can reference.

## Inbound handoffs
- Every product that performs meaningful actions (especially RoadCode, RoadWork, CarKeys, deployments)
- RoadView for source-backed claims
- RoadBook for publishing provenance

## Outbound handoffs
- RoadMap for status that needs proof
- RoadWire for long-term records that need receipts
- Any product needing audit or rollback

## Example routing decisions

User says: "Show me proof that this deployment happened and what changed."
Route: RoadChain
Reason: Receipt and provenance layer.
Receipt needed: yes (verification)
Permission needed: user_read or appropriate scope

User says: "I need to file compliance paperwork."
Route: RoadWork first → RoadChain for proof of steps taken.

## Receipt events
- roadchain.receipt.created
- roadchain.receipt.verified
- roadchain.chain.verification_failed
- roadchain.provenance.linked
- roadchain.rollback.requested

## Permission notes
- Reading public receipts: public_read
- Writing receipts (via products): user_write or agent_write_limited
- Viewing sensitive audit data or exporting chains: operator_approval_required
- Superseding or reverting important receipts: admin_only

## Anti-drift
RoadChain must stay honest. It can say “receipt-backed,” “auditable,” and “provenance record.” It must not overclaim “legal proof,” “financial compliance,” or “blockchain guarantee” unless the implementation truly supports it. No fake immutability claims.