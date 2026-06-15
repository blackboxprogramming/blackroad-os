# Routing — RoundAbout

## Route here when the user wants to...
- Prepare for trips, service calls, appointments, or routes (before/after checklists, materials, people, context)
- Handle route-adjacent planning and readiness
- Get ready before handing off to actual route execution

## Do not route here when...
- Actual route execution, timing, ETA, or rerouting (Detour)
- General travel mapping or navigation
- Business operational workflows (RoadWork)

## Common confusion boundaries

### RoundAbout vs Detour
RoundAbout = preparation around the trip/service route (before/after checklists, materials, readiness).
Detour = actual route/timing/ETA/alternate path execution.
Handoff: RoundAbout finishes prep → Detour handles movement.

### RoundAbout vs RoadWork
RoundAbout = route/service prep and readiness.
RoadWork = broader business and operational execution.

### RoundAbout vs OfficeRoad
RoundAbout = specific trip/service preparation.
OfficeRoad = general visual work coordination.

## Inbound handoffs
- RoadWork service or field work tasks
- RoadMap items that involve travel or appointments
- RoadWire appointment notes

## Outbound handoffs
- Detour for actual route execution
- RoadWire for customer/appointment messaging
- RoadMap for status
- CarKeys for location permissions

## Example routing decisions

User says: "Help me prepare for this client visit — what do I need to bring and do before/after?"
Route: RoundAbout
Reason: Route-adjacent preparation and readiness.
Receipt needed: yes
Permission needed: user_write

User says: "Now actually get me there and handle timing."
Route: Detour (with prep from RoundAbout)

## Receipt events
- roundabout.trip_context.created
- roundabout.readiness.updated
- roundabout.detour.handoff_created

## Permission notes
- Creating private prep checklists: user_write
- Sharing location or customer context: operator_approval_required
- External notifications: scoped permissions

## Anti-drift
RoundAbout must handle everything that needs to be ready around the trip. It must not become a generic map app or ignore before/after tasks and dependencies.