# Routing — OfficeRoad

## Route here when the user wants to...
- Work in a visual meta office with humans and AI teammates side-by-side
- See desks, rooms, agent presence, tasks, and documents spatially arranged
- Coordinate work visually instead of in chat boxes or hidden tabs
- Get a spatial view of who/what is working on what

## Do not route here when...
- Live group collaboration and conversation (CarPool)
- Status reporting and blockers (RoadMap)
- Operational task execution (RoadWork)
- General workspace (RoadOS)

## Common confusion boundaries

### OfficeRoad vs CarPool
OfficeRoad = visual spatial office environment and presence.
CarPool = live/shared collaboration room and conversation.
Handoff: CarPool can be launched from or linked inside OfficeRoad.

### OfficeRoad vs RoadMap
OfficeRoad = visual work presence and coordination.
RoadMap = structural status, blockers, and progress reporting.
Handoff: OfficeRoad shows work visually; RoadMap reports it structurally.

### OfficeRoad vs RoadWork
OfficeRoad = the place where work is visually arranged.
RoadWork = the actual operational steps and execution.

## Inbound handoffs
- RoadTrip solo work that needs visual team context
- CarPool rooms that benefit from spatial view
- RoadMap items that need visual coordination

## Outbound handoffs
- CarPool for live group work
- RoadWire for async records linked from the office
- RoadMap for status updates
- RoadWork for operational tasks
- RoadChain for receipts

## Example routing decisions

User says: "Show me the office and who is working on what right now."
Route: OfficeRoad
Reason: Visual meta office with agent presence.
Receipt needed: yes for presence/status changes
Permission needed: office membership permissions

User says: "Turn this visual coordination into actual tasks."
Route: RoadWork (with context from OfficeRoad)

## Receipt events
- officeroad.office.created
- officeroad.agent_presence.updated
- officeroad.task.linked
- officeroad.room.shared

## Permission notes
- Viewing own offices: user_read
- Creating or arranging personal offices: user_write
- Inviting members or assigning agents to sensitive rooms: operator_approval_required
- Exposing private documents through room views: strict permission check

## Anti-drift
OfficeRoad must make AI coworkers visible in a spatial work environment instead of hiding them in chat boxes. It must not become decorative office cosplay or show fake agent activity. It shows presence and coordination, not completed work.