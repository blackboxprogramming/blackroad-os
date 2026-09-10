# Routing — BlackBoard

## Route here when the user wants to...
- Create visual media: animation, videos, infographics, explainers, graphics, storyboards, canvases
- Do drag-and-drop visual creation and layout
- Turn ideas into visual artifacts with timelines and assets
- Export visuals for use in other products

## Do not route here when...
- Publishing or curating shows (RoadShow)
- Social distribution (BackRoad)
- Interactive worlds/games (RoadWorld)
- Text/audio publishing (RoadBook)

## Common confusion boundaries

### BlackBoard vs RoadShow
BlackBoard = create the visual media.
RoadShow = program, curate, playlist, and present shows/channels.
Handoff: BlackBoard exports → RoadShow for programming.

### BlackBoard vs BackRoad
BlackBoard = create the media.
BackRoad = social/community distribution of media.
Handoff: BlackBoard creations can be posted to BackRoad.

### BlackBoard vs RoadWorld
BlackBoard = visual media, animation, video assets.
RoadWorld = interactive playable worlds and games (uses BlackBoard assets).
Handoff: BlackBoard assets feed into RoadWorld worlds.

### BlackBoard vs RoadSport
BlackBoard = general visual creation.
RoadSport = sports-specific diagrams, routes, physics simulation visuals.

## Inbound handoffs
- RoadTrip / CarPool research that needs visuals
- RoadBook for illustrated knowledge
- PitStop for visual learning material
- RoadView for visual discovery

## Outbound handoffs
- RoadShow for shows and programming
- BackRoad for social sharing
- RoadBook for illustrated content
- RoadChain for asset provenance
- CarKeys for rights and permissions

## Example routing decisions

User says: "Create an explainer video and infographic for this concept."
Route: BlackBoard
Reason: Visual creation studio.
Receipt needed: yes for assets and exports
Permission needed: user_write + rights review if using external assets

User says: "Turn this into a public show."
Route: RoadShow (with media from BlackBoard)

## Receipt events
- blackboard.canvas.created
- blackboard.asset.added
- blackboard.export.created
- blackboard.rights_review_needed

## Permission notes
- Creating private canvases: user_write
- Publishing or exporting with rights implications: operator_approval_required + rights review
- Using copyrighted or AI-generated assets: provenance + disclosure

## Anti-drift
BlackBoard must be a true drag-and-drop visual creation studio (Dreamweaver/Canva/animation class reimagined). It must not become analytics, generic dashboards, or trap users in expensive design-tool complexity. Creator ownership and asset provenance must be preserved.