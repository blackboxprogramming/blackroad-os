# 27. Detour

**Detour** is the route execution and fallback layer.

RoundAbout prepares around where someone is going; Detour handles going there and when.

It manages destination, timing, ETA, alternate paths, reroutes, degraded modes, and “the plan changed, now what?”

**Primary integrations:**
- RoadOS for execution surface
- RoundAbout for preparation handoff
- HighWay for route intelligence (including hybrid mesh)
- RoadChain for execution receipts and proof
- RoadMap for live status

**Core promise:**
Execute the plan and recover gracefully when things change.

**Status:** Canon-ready (Level 4). Implementation planned.
**Note:** HighWay + Detour together form the hybrid mesh + resilient routing backbone.