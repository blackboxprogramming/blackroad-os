# Routing — BackRoad

## Route here when the user wants to...
- View or post in social/community feeds (native BackRoad or aggregated external social)
- Manage creator/community profiles and social graph
- Engage socially without algorithmic addiction or ownership loss
- Route social/campaign work into RoadWork when it becomes business execution

## Do not route here when...
- Doing marketing campaigns, analytics, or business operations (RoadWork)
- Creating visual media (BlackBoard)
- Publishing long-form knowledge (RoadBook)
- Curating shows/playlists (RoadShow)

## Common confusion boundaries

### BackRoad vs RoadWork
BackRoad = social viewing, posting, community.
RoadWork = when social becomes campaign execution, reporting, or business operations.
Handoff: BackRoad content/campaign signals → RoadWork tasks.

### BackRoad vs RoadShow
BackRoad = social feed and native community.
RoadShow = curated programming, channels, playlists, public shows.
Handoff: BackRoad posts can feed into RoadShow curation.

### BackRoad vs RoadWire
BackRoad = live social/community surface.
RoadWire = durable async messaging and records.
Handoff: Important community interactions can be noted into RoadWire.

## Inbound handoffs
- RoadView social search results
- RoadShow public shows shared socially
- RoadBook published work shared to community

## Outbound handoffs
- RoadWork for business/campaign execution
- RoadWire for long-term community records
- RoadChain for provenance of important posts
- CarKeys for identity and permissions

## Example routing decisions

User says: "Show me what my community is posting and let me reply."
Route: BackRoad
Reason: Social feed and native community.
Receipt needed: yes for important interactions
Permission needed: user_write

User says: "Turn this social post into a marketing campaign."
Route: RoadWork (with context from BackRoad)
Reason: Social → business execution.

## Receipt events
- backroad.post.created
- backroad.feed.source_added
- backroad.campaign_handoff.roadwork
- backroad.profile.updated

## Permission notes
- Viewing public feeds: public_read
- Posting or replying: user_write
- Linking external social accounts: operator_approval or CarKeys grant
- Moderation actions: admin_only

## Anti-drift
BackRoad must help users regain ownership from algorithmic platforms. It must not become another addictive feed or hide why users see content. When social work becomes business work, it must route to RoadWork.