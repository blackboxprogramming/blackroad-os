# Routing — RoadView

## Route here when the user wants to...
- Search, discover, or explore with the 17,290 master index
- Get source-backed results with provenance and citations
- See visible Agent RoadView browsing (agents working on-screen)
- Control consent for training or sharing search data
- Route results into the right product or lane

## Do not route here when...
- Publishing or saving knowledge long-term (RoadBook)
- General workspace actions (RoadOS)
- Creating content (BlackBoard, RoadBand, etc.)

## Common confusion boundaries

### RoadView vs RoadBook
RoadView = search, discovery, source routing, visible agent work.
RoadBook = saving, publishing, annotating, and preserving as durable artifacts.
Handoff: RoadView results can become RoadBook entries.

### RoadView vs GloveBox
RoadView searches the world/system.
GloveBox lists approved capabilities and tools.
Handoff: RoadView may discover external tools; GloveBox records approved ones.

### RoadView vs RoadTrip
RoadView can launch agent browsing sessions that continue in RoadTrip.
Handoff: Visible agent work in RoadView can move into a RoadTrip room.

## Inbound handoffs
- RoadOS command or search dock
- Any product needing sourced information
- RoadWork for business/process research

## Outbound handoffs
- RoadBook for knowledge capture
- RoadTrip for deeper agent research
- RoadCode for technical search
- RoadChain for source-backed claims
- Consent management stays inside RoadView

## Example routing decisions

User says: "Search for historical sources on 1920s New York and show me what agents find."
Route: RoadView
Reason: 17,290-indexed search + visible Agent RoadView.
Receipt needed: yes
Permission needed: consent for training/sharing

User says: "Save these sources into my research book."
Route: RoadBook (with handoff from RoadView)

## Receipt events
- roadview.query.created
- roadview.lane.matched
- roadview.source.result
- roadview.training_consent.updated
- roadview.agent_view.started

## Permission notes
- Basic search: public_read or user_read
- Saving results or training consent: user_write
- Sharing query data with BlackRoad or external: explicit consent + receipt
- Agent browsing visibility: user-controlled

## Anti-drift
RoadView must make search routed, source-backed, consent-aware, and visible (not opaque ranking or silent training). It must ask plainly about privacy and training instead of using giant terms-and-conditions walls.