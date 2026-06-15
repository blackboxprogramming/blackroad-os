# Routing — RoadWorld

## Route here when the user wants to...
- Build drag-and-drop games, simulations, worlds, or interactive experiences
- Create historical simulations, survival games, or "drop into any time period" scenarios
- Prototype mechanics, scenes, assets, and monetization
- Share or publish playable worlds with ownership

## Do not route here when...
- Creating static visual media or animation (BlackBoard)
- Sports/movement physics and practice (RoadSport)
- General 3D or game engine work without BlackRoad structure

## Common confusion boundaries

### RoadWorld vs BlackBoard
RoadWorld = interactive worlds, games, simulations, playable experiences.
BlackBoard = visual media, animation, infographics, video assets.
Handoff: BlackBoard creates assets that RoadWorld uses in interactive worlds.

### RoadWorld vs RoadSport
RoadWorld = broad creative worldbuilding and games.
RoadSport = constrained sports/movement physics, football routes, marching band precision, Monte Carlo simulation for athletics.
Handoff: RoadSport simulations can later become training modules inside RoadWorld.

### RoadWorld vs RoadShow
RoadWorld = the playable world.
RoadShow = curating/showcasing worlds or recordings of them.

## Inbound handoffs
- RoadView historical or game-related search
- BlackBoard visual assets
- RoadBook lore and source material
- RoadTrip agent-assisted world design

## Outbound handoffs
- RoadChain for world provenance and ownership
- RoadShow for showcasing
- CarPool for multiplayer collaboration
- HighWay for hosting

## Example routing decisions

User says: "Build a historical survival simulation set in 1920s New York."
Route: RoadWorld
Reason: Interactive worldbuilding and simulation.
Receipt needed: yes
Permission needed: user_write + rights review if publishing

User says: "Create a football route playbook with physics."
Route: RoadSport
Reason: Constrained athletic movement vs general worldbuilding.

## Receipt events
- roadworld.world.created
- roadworld.prototype.planned
- roadworld.monetization_review_needed
- roadworld.asset.added

## Permission notes
- Creating private worlds: user_write
- Publishing, monetization, or multiplayer: operator_approval_required + rights review
- Using external assets: provenance + rights check

## Anti-drift
RoadWorld must lower the barrier for people with game/world ideas without requiring them to become engine engineers. It must preserve creator ownership and not copy exploitative creator economics.