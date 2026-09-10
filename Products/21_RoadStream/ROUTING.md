# Routing — RoadStream

## Route here when the user wants to...
- Manage unified watchlists, continue-watching, and subscriptions across Netflix, Hulu, Disney+, etc.
- Remember where content lives and solve the “where was I watching that?” problem
- Search or organize streaming content in one surface
- Hand off curation to RoadShow when the user wants programming or playlists

## Do not route here when...
- Creating or curating shows/channels (RoadShow)
- Music-specific work (RoadBand)
- General social sharing (BackRoad)

## Common confusion boundaries

### RoadStream vs RoadShow
RoadStream = wrapper for streaming services and subscriptions (where content lives).
RoadShow = TV Guide / YouTube-style curation, channels, playlists, and public programming.
Handoff: RoadStream finds sources → RoadShow turns selections into programming.

### RoadStream vs RoadBand
RoadStream = video streaming services.
RoadBand = music creation, taste, and hosting.
Handoff: Music videos can cross over, but they are distinct.

## Inbound handoffs
- RoadView media search
- RoadShow when user wants to watch instead of curate
- RoadTrip for entertainment recommendations

## Outbound handoffs
- RoadShow for curated programming
- RoadWire for shared recommendations
- CarKeys for streaming account permissions
- OneWay for data portability if needed

## Example routing decisions

User says: "Where can I continue watching that show I started on Netflix?"
Route: RoadStream
Reason: Unified streaming wrapper and continue-watching.
Receipt needed: yes for watch history
Permission needed: streaming account permissions via CarKeys

User says: "Turn these shows into a curated playlist or channel."
Route: RoadShow (with sources from RoadStream)

## Receipt events
- roadstream.service.added
- roadstream.watchlist.item_added
- roadstream.roadshow.handoff_created

## Permission notes
- Basic watchlist and continue-watching: user_read / user_write
- Linking streaming accounts: CarKeys grant + consent
- Importing watch history: explicit consent + receipt

## Anti-drift
RoadStream must solve fragmentation without bypassing platform rights or becoming another confusing recommendation loop. It remembers where content lives.