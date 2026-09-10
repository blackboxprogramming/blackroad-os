# Routing — RoadWire

## Route here when the user wants to...
- Handle non-immediate, durable, email-like messaging and long-term records
- Create threads, drafts, or archives that need to be remembered
- Automatically capture important notes from RoadTrip or CarPool
- Manage outside communication and formal records

## Do not route here when...
- Live solo AI work (RoadTrip)
- Live group collaboration (CarPool)
- Social feeds (BackRoad)
- Immediate help (RoadSide)

## Common confusion boundaries

### RoadWire vs RoadTrip
RoadWire = durable async records and notes.
RoadTrip = live solo work (should summarize into RoadWire).
Handoff: RoadTrip automatically notes important events into RoadWire.

### RoadWire vs CarPool
RoadWire = non-immediate threaded records.
CarPool = live/shared collaboration (decisions should note into RoadWire).
Handoff: CarPool decisions and summaries should note into RoadWire.

### RoadWire vs BackRoad
RoadWire = messaging, threads, and formal records.
BackRoad = social feed and community.

## Inbound handoffs
- RoadTrip and CarPool for automatic note capture
- RoadWork for operational follow-up
- RoadSide for support threads
- RoadMap for status-linked communication

## Outbound handoffs
- RoadWork for action items
- RoadMap for status updates from threads
- RoadChain for important decision receipts
- CarKeys for contact permissions

## Example routing decisions

User says: "Create a thread for this project discussion and keep it as a long-term record."
Route: RoadWire
Reason: Durable async messaging and records.
Receipt needed: yes for important threads
Permission needed: user_write

User says: "Send this as an email to the client."
Route: RoadWire (with approval)

## Receipt events
- roadwire.thread.created
- roadwire.email.drafted
- roadwire.email.sent
- roadwire.thread.archived

## Permission notes
- Creating private threads: user_write
- Sending outside messages: operator_approval_required
- Archiving or deleting sensitive threads: review required
- External communication: consent and compliance checks

## Anti-drift
RoadWire must be the durable memory layer for non-immediate communication. It must not become noisy chat, lose important decisions, or duplicate live collaboration (RoadTrip/CarPool).