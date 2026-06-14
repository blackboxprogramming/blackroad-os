# 07. CarKeys

**CarKeys** is the identity, permission, grants, login, and key layer.

The design standard is simple: if a user has to manually paste passwords or API keys, the system failed. CarKeys should make access feel as easy as logging into Google, but with BlackRoad’s own receipt-backed permissions and revocation.

CarKeys should handle:
- identity management
- permission grants and scopes
- key rotation and revocation
- login flows
- provider connections
- CarKeys/Portia permission checks

It must integrate tightly with RoadTrip, RoadCode, HighWay, and all products that need scoped access.

**Primary integrations:**
- RoadOS command dock
- RoadTrip agent permissions
- RoadCode secret handling
- HighWay node access
- RoadChain receipt of grants/revocations

**Core promise:**
Access that just works, with proof and easy revocation.

**Status:** Canon-ready (Level 4). Implementation planned.
**Risk:** High — identity and permission systems require careful review (Portia, Atticus, operator).