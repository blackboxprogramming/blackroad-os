# Routing — RoadMap

## Route here when the user wants to...
- See overall progress, status, blockers, milestones, and what needs attention
- Get dashboards and reports across products, tasks, and initiatives
- Understand continuation points and “oh my God, this needs attention” items

## Do not route here when...
- Doing the actual operational work (RoadWork)
- Live collaboration (CarPool)
- Visual spatial coordination (OfficeRoad)
- Creating content

## Common confusion boundaries

### RoadMap vs RoadWork
RoadMap = seeing the work (status, blockers, reports).
RoadWork = doing the work (operational execution).
Handoff: RoadWork tasks update RoadMap; RoadMap blockers route back to RoadWork.

### RoadMap vs OfficeRoad
RoadMap = structural status and reporting.
OfficeRoad = visual spatial presence and coordination.
Handoff: OfficeRoad shows work visually; RoadMap reports it structurally.

### RoadMap vs RoadWire
RoadMap = progress and status.
RoadWire = durable communication records that can feed into status.

## Inbound handoffs
- Every product that produces tasks, blockers, or status
- CarPool and RoadTrip for work updates
- RoadWork for operational progress

## Outbound handoffs
- RoadWork for action on blockers
- RoadWire for communication linked to status
- RoadChain for proof-linked reports

## Example routing decisions

User says: "Show me everything that’s blocked or needs attention right now."
Route: RoadMap
Reason: Progress dashboard and blocker visibility.
Receipt needed: yes for major status changes
Permission needed: appropriate scope

User says: "Update the status on this initiative."
Route: RoadMap (with source from the owning product)

## Receipt events
- roadmap.status.updated
- roadmap.blocker.added
- roadmap.next_action.updated

## Permission notes
- Viewing personal or project status: user_read or project_member
- Marking major work complete or changing priorities: operator_approval_required
- Publishing status externally: review required

## Anti-drift
RoadMap must show real operational truth with proof links. It must not show fake green status, hide blockers, or become generic project management sludge.