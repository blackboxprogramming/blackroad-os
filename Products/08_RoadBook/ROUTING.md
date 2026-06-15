# Routing — RoadBook

## Route here when the user wants to...
- Create, edit, publish, or narrate digital books, audiobooks, research, essays, or notes
- Attach sources, provenance, authorship, and peer review
- Collaborate on knowledge work with comments and review layers
- Preserve ownership and economics for creators

## Do not route here when...
- Creating visual media or animation (BlackBoard)
- Social posting or community (BackRoad)
- Curating public shows (RoadShow)
- General search (RoadView)

## Common confusion boundaries

### RoadBook vs RoadView
RoadView = search, discovery, source routing.
RoadBook = saving, publishing, annotating, and preserving knowledge as durable artifacts.
Handoff: RoadView results can become RoadBook entries.

### RoadBook vs BlackBoard
RoadBook = text/audio knowledge publishing.
BlackBoard = visual/animation/video/infographic creation.
Handoff: BlackBoard visuals can illustrate RoadBook works.

### RoadBook vs RoadShow
RoadBook = the knowledge content.
RoadShow = programming it into shows/channels.
Handoff: RoadBook works can be curated into RoadShow.

## Inbound handoffs
- RoadView sourced research
- PitStop learning material
- RoadTrip research summaries
- BlackBoard visual assets

## Outbound handoffs
- RoadView for discovery
- RoadChain for provenance receipts
- RoadWire for author/narrator correspondence
- CarKeys for rights and permissions

## Example routing decisions

User says: "Turn this research into a published book with sources and narration."
Route: RoadBook
Reason: Digital-native publishing with provenance.
Receipt needed: yes
Permission needed: user_write + rights review for publishing

User says: "Find sources for my essay."
Route: RoadView first → RoadBook to save.

## Receipt events
- roadbook.work.created
- roadbook.source.attached
- roadbook.publish.status_changed
- roadbook.review.added
- roadbook.rights_review_needed

## Permission notes
- Creating drafts: user_write
- Publishing or changing royalties/rights: operator_approval_required + rights review
- Attaching copyrighted sources: consent + provenance receipt

## Anti-drift
RoadBook must make digital-native publishing easier with better creator economics and provenance. It must not become a PDF dump or trap authors in bad royalty systems. Physical-book assumptions should not limit it.