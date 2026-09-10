# Routing — Detour

## Route here when the user wants to...
- Handle actual route execution: destination, timing, ETA, alternate paths, reroutes
- Manage leave-by logic, fallback planning, and what happens when the plan changes
- Execute trips, service routes, or appointments

## Do not route here when...
- Preparation around the trip (RoundAbout)
- Infrastructure/system routing (HighWay)
- General mapping or navigation without BlackRoad context

## Common confusion boundaries

### Detour vs RoundAbout
Detour = actual route/timing/ETA/alternate path execution.
RoundAbout = preparation around the trip (before/after checklists, materials, readiness).
Handoff: RoundAbout finishes prep → Detour handles movement.

### Detour vs HighWay
Detour = human/work travel routing.
HighWay = infrastructure and system routing.

### Detour vs RoadSport
Detour = human travel and service routes.
RoadSport = athletic/sports movement simulation.

## Inbound handoffs
- RoundAbout when prep is complete
- RoadWork for service or field route tasks
- RoadMap for route-related status
- RoadWire for appointment/customer context

## Outbound handoffs
- RoadMap for arrival/status
- RoadChain for completion proof
- RoadWire for post-route notes
- CarKeys for location sharing permissions

## Example routing decisions

User says: "Get me to this appointment with the best route and ETA, and handle reroutes if needed."
Route: Detour
Reason: Actual route execution and fallback planning.
Receipt needed: yes for timing and completion
Permission needed: location permissions via CarKeys

User says: "First help me prepare what I need for this trip."
Route: RoundAbout first → Detour

## Receipt events
- detour.route.created
- detour.eta.calculated
- detour.location_permission_checked
- detour.arrival.recorded

## Permission notes
- Creating private route plans: user_write
- Sharing location or live tracking: explicit opt-in + CarKeys
- Customer or external route sharing: operator_approval_required

## Anti-drift
Detour must handle real route execution and fallback planning. It must not claim live traffic without integration, ignore prep dependencies from RoundAbout, or expose location without permission.