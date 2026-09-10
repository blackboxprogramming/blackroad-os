# Routing — RoadShow

## Route here when the user wants to...
- Create channels, shows, playlists, or programming blocks
- Curate media into intentional viewing experiences or public shows
- Program content from BlackBoard, RoadBook, RoadBand, or RoadStream into shows
- Share curated media worlds publicly

## Do not route here when...
- Managing personal streaming subscriptions and watchlists (RoadStream)
- Creating the visual media itself (BlackBoard)
- Social posting (BackRoad)

## Common confusion boundaries

### RoadShow vs RoadStream
RoadShow = curation, programming, channels, and public shows.
RoadStream = unified wrapper for existing streaming services.
Handoff: RoadStream provides sources → RoadShow curates them into programming.

### RoadShow vs BlackBoard
RoadShow = program and present the media.
BlackBoard = create the visual media and assets.
Handoff: BlackBoard exports → RoadShow for programming.

### RoadShow vs BackRoad
RoadShow = curated public shows and programming.
BackRoad = social feed and community distribution.

## Inbound handoffs
- BlackBoard visual creations
- RoadStream sources
- RoadBand music
- RoadBook knowledge content
- RoadView media discovery

## Outbound handoffs
- BackRoad for social distribution of shows
- RoadChain for provenance of curated content
- CarKeys for rights and publishing permissions
- RoadWire for shared programming notes

## Example routing decisions

User says: "Turn these videos and clips into a themed show or playlist."
Route: RoadShow
Reason: Curation and programming.
Receipt needed: yes for public programming
Permission needed: rights review + publishing approval

User says: "Just show me my subscriptions and where I left off."
Route: RoadStream

## Receipt events
- roadshow.show.created
- roadshow.programming_block.created
- roadshow.publication_review_needed

## Permission notes
- Creating private playlists: user_write
- Publishing public shows or channels: operator_approval_required + rights review
- Using third-party media: provenance and rights check

## Anti-drift
RoadShow must enable intentional curation and programming without becoming a rights-violating scraper or trapping creators in bad economics. It turns chaos into shows.