# Routing — RoadBand

## Route here when the user wants to...
- Compare sounds, build a taste profile, or get music recommendations
- Create or guide music production from taste/mood references
- Host songs/stems or unify music libraries across platforms
- Work with car-first listening and better recommendations than current platforms

## Do not route here when...
- Creating visual media for music videos (BlackBoard)
- Curating shows or programming (RoadShow)
- General streaming service management (RoadStream)
- Social sharing of music (BackRoad)

## Common confusion boundaries

### RoadBand vs RoadStream
RoadBand = music creation, taste profiling, production, hosting, and recommendation.
RoadStream = wrapper for video streaming services and watchlists.
Handoff: RoadBand media can appear in RoadShow; RoadStream is mainly video.

### RoadBand vs RoadShow
RoadBand = create and host the music.
RoadShow = program/curate music into shows, playlists, or channels.
Handoff: RoadBand creations can be curated in RoadShow.

### RoadBand vs BlackBoard
RoadBand = audio/music focus.
BlackBoard = visual assets and video that can accompany music.

## Inbound handoffs
- RoadView music-related search
- RoadTrip agent-assisted production ideas
- BlackBoard for music video visuals

## Outbound handoffs
- RoadShow for music programming
- BackRoad for social sharing
- RoadBook for lyrics/liner notes
- RoadChain for provenance and rights
- CarKeys for rights and hosting permissions

## Example routing decisions

User says: "Help me compare sounds and build a taste profile, then suggest production direction."
Route: RoadBand
Reason: Music taste profiling and production guidance.
Receipt needed: yes for taste profile and briefs
Permission needed: user_write

User says: "Host this track and make it available across platforms."
Route: RoadBand (with rights review)

## Receipt events
- roadband.taste_profile.created
- roadband.production_brief.created
- roadband.rights_review_needed
- roadband.track.hosted

## Permission notes
- Creating private taste profiles and briefs: user_write
- Hosting or publishing tracks: operator_approval_required + rights review
- Using external music accounts or AI generation disclosure: consent + provenance

## Anti-drift
RoadBand must help people with good ears make music without needing to master a full DAW. It must preserve rights/provenance and avoid trapping artists in bad royalty economics. AI-generated music must be disclosed when relevant.