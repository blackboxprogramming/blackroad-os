# Routing — RoadSport

## Route here when the user wants to...
- Plan sports routes, movement paths, or choreography with physics constraints
- Run Monte Carlo simulations or collision/timing analysis
- Get practice feedback, video annotation, or formation analysis
- Work with football, marching band precision, or constrained movement intelligence

## Do not route here when...
- General interactive worldbuilding or games (RoadWorld)
- Creating visual diagrams without sports physics (BlackBoard)
- Human travel routing (Detour / RoundAbout)

## Common confusion boundaries

### RoadSport vs RoadWorld
RoadSport = constrained sports/movement physics, routes, collisions, practice feedback (football, marching band, athletics).
RoadWorld = broad creative worldbuilding, games, and simulations.
Handoff: RoadSport simulations can become training modules inside RoadWorld later.

### RoadSport vs BlackBoard
RoadSport = sports-specific diagrams, routes, and physics visuals.
BlackBoard = general visual media and animation.

### RoadSport vs Detour
RoadSport = athletic/sports movement simulation and analysis.
Detour = human travel/service route execution.

## Inbound handoffs
- RoadView for sports analysis search
- BlackBoard for diagrams that need physics overlay
- RoadTrip for agent-assisted simulation planning

## Outbound handoffs
- RoadChain for practice/proof logs
- RoadMap for team progress
- CarKeys for school/team permissions (especially minors/athletes)
- HighWay for video/compute workloads

## Example routing decisions

User says: "Simulate this football route with player weight, speed, and collision risk."
Route: RoadSport
Reason: Constrained movement physics and Monte Carlo analysis.
Receipt needed: yes
Permission needed: project_member or school permissions

User says: "Create a general historical battle simulation."
Route: RoadWorld
Reason: Broad worldbuilding vs sports-specific physics.

## Receipt events
- roadsport.route.planned
- roadsport.simulation.ran
- roadsport.athlete_data_permission_checked
- roadsport.practice_feedback.added

## Permission notes
- Creating private route plans: user_write
- Storing or analyzing athlete/minor/student data: strict review + CarKeys
- Public sharing or school exports: operator_approval_required

## Anti-drift
RoadSport must replace overpriced, limited sports-video tools with useful physics-based simulation and feedback. It must not claim guaranteed outcomes, ignore player safety, or expose minor/athlete data without strict permissions.