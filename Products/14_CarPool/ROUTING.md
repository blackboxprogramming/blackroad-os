# Routing — CarPool

## Route here when the user wants to...
- Collaborate with other humans + agents in a shared project room
- Run meetings, share tasks/files, make group decisions
- Have live or async group work with automatic note capture
- Move from solo work (RoadTrip) into group mode

## Do not route here when...
- Solo AI/agent work (RoadTrip)
- Operational business steps (RoadWork)
- Durable long-term messaging (RoadWire)
- Visual office presence (OfficeRoad)

## Common confusion boundaries

### CarPool vs RoadTrip
CarPool = multiple humans + agents.
RoadTrip = one human + many agents.
Handoff: RoadTrip can promote into CarPool when others join.

### CarPool vs RoadWire
CarPool = live/shared collaboration and decisions.
RoadWire = durable async records and outside messages.
Handoff: CarPool decisions and summaries should note into RoadWire.

### CarPool vs RoadWork
CarPool = talking and working together.
RoadWork = executing the actual business/operational steps.
Handoff: CarPool discussion can create RoadWork tasks.

### CarPool vs OfficeRoad
CarPool = collaboration room/conversation.
OfficeRoad = visual spatial office with desks, presence, and coordination.
Handoff: CarPool can be launched from or linked inside OfficeRoad.

## Inbound handoffs
- RoadTrip solo missions that need group input
- RoadWork tasks that require discussion
- RoadMap items that need collaboration

## Outbound handoffs
- RoadWire for durable records
- RoadMap for status updates
- RoadWork for operational follow-up
- RoadChain for important decisions

## Example routing decisions

User says: "Let’s discuss this project with the team and agents and make decisions."
Route: CarPool
Reason: Human + AI group collaboration.
Receipt needed: yes for decisions
Permission needed: project_member permissions

User says: "Turn our discussion notes into tasks."
Route: RoadWork (with handoff from CarPool)

## Receipt events
- carpool.room.created
- carpool.member.invited
- carpool.decision.recorded
- carpool.roadwire.handoff

## Permission notes
- Creating or joining rooms: user_write
- Adding agents or external members: operator_approval_required
- Exporting shared files or decisions: scoped permissions + receipt

## Anti-drift
CarPool must support real human + AI collaboration without losing decisions. It must not become noisy chat, allow agents to join without permission, or replace durable records (RoadWire).