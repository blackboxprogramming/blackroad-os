# Routing — HighWay

## Route here when the user wants to...
- Manage infrastructure: compute, routing, cloud, fleet, nodes, domains, TLS, model serving, observability
- Check service health, routes, domains, or node/fleet status
- Plan or inspect deployments and infrastructure routes
- Bridge local hardware (Pi clusters, home servers) with cloud

## Do not route here when...
- Building the software itself (RoadCode)
- Human travel or service route execution (Detour)
- General workspace or file actions (RoadOS)

## Common confusion boundaries

### HighWay vs RoadCode
HighWay = run, route, observe, and scale the infrastructure.
RoadCode = build the software, produce deploy plans, and figure out the next technical step.
Handoff: RoadCode produces deploy plans that HighWay executes and observes.

### HighWay vs Detour
HighWay = infrastructure/system routing (servers, domains, APIs, model endpoints).
Detour = human/work travel routing (destination, ETA, alternate paths for people/services).

### HighWay vs RoadSport
HighWay = technical infrastructure.
RoadSport = sports/movement physics and simulation (can use HighWay for video/compute workloads).

## Inbound handoffs
- RoadCode deploy plans
- RoadTrip / CarPool when heavy compute or model serving is needed
- Any product needing service discovery or health checks

## Outbound handoffs
- RoadChain for deploy/route/incident receipts
- RoadMap for infrastructure status
- CarKeys for access control to services
- GloveBox for infrastructure capabilities

## Example routing decisions

User says: "Check the health of my services and show me any failing routes."
Route: HighWay
Reason: Infrastructure observability and routing.
Receipt needed: yes for incidents
Permission needed: appropriate scope

User says: "Deploy this and make sure the domain and TLS are set up."
Route: HighWay (with plan from RoadCode)

## Receipt events
- highway.route.checked
- highway.health.changed
- highway.incident.created
- highway.deploy.planned

## Permission notes
- Viewing public or own service health: user_read
- Making DNS, deployment, or exposure changes: operator_approval_required
- Accessing internal services or credentials: admin_only + CarKeys

## Anti-drift
HighWay must make infrastructure understandable and routable instead of overwhelming users with DevOps jargon. It must not expose internal services accidentally, publish secrets, or claim a service is live when only files exist.