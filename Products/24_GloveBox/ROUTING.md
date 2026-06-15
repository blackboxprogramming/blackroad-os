# Routing — GloveBox

## Route here when the user wants to...
- Discover what BlackRoad can do (capabilities, tools, features)
- Find available tools, open-source alternatives, or capability status
- Understand what permission or CarKeys grant is needed for a tool
- See REAL vs PLANNED vs MOCK status of capabilities

## Do not route here when...
- Checking or requesting actual access/permissions (CarKeys)
- Searching for information in the world (RoadView)
- General help (RoadSide)

## Common confusion boundaries

### GloveBox vs CarKeys
GloveBox = what capabilities/tools exist and what they need.
CarKeys = who can use them (access, grants, permissions).
Handoff: GloveBox lists the tool → CarKeys decides if it can be used.

### GloveBox vs RoadView
GloveBox = internal capability catalog.
RoadView = external search and discovery.
Handoff: RoadView may discover external tools; GloveBox records approved BlackRoad capabilities.

## Inbound handoffs
- RoadView capability discovery
- RoadTrip / CarPool when choosing tools for agents
- RoadCode when needing build tools
- Any product needing to know available capabilities

## Outbound handoffs
- CarKeys for permission checks
- RoadChain for capability status receipts
- RoadMap for capability roadmap

## Example routing decisions

User says: "What tools or capabilities does BlackRoad have for audio analysis?"
Route: GloveBox
Reason: Capability and tool discovery.
Receipt needed: no for discovery
Permission needed: public_read or user_read

User says: "Can I use this tool right now?"
Route: CarKeys (after GloveBox identifies it)

## Receipt events
- glovebox.capability.added
- glovebox.tool.status_changed
- glovebox.open_source_candidate_added

## Permission notes
- Browsing public capabilities: public_read
- Adding or changing capability status (REAL/PLANNED): operator_approval_required
- Marking commercial-safe: license review required

## Anti-drift
GloveBox must be the honest catalog of what BlackRoad can actually do. It must not store raw secrets, pretend planned tools are real, or let agents use tools without CarKeys permission.