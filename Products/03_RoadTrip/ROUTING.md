# Routing — RoadTrip

## Route here when the user wants to...
- Work solo with multiple AIs, models, agents, or tools in one visible mission room
- Run parallel agent threads, compare models, or do research with visible reasoning
- Create handoff packets to other products
- Capture memory and summarize into RoadWire/RoadChain

## Do not route here when...
- Using the general workspace (RoadOS)
- Group collaboration with other humans (CarPool)
- Business/operational work (RoadWork)
- Creating or editing visual media (BlackBoard)

## Common confusion boundaries

### RoadTrip vs CarPool
RoadTrip = one human + many agents.
CarPool = multiple humans + agents.
Handoff: RoadTrip can promote a solo mission into a CarPool room when others join.

### RoadTrip vs RoadWire
RoadTrip = live work.
RoadWire = durable async records and notes.
Handoff: RoadTrip should automatically summarize important events into RoadWire.

### RoadTrip vs RoadCode
RoadTrip is for exploration and planning with agents.
RoadCode is for concrete build/execute actions with approvals.
Handoff: Research from RoadTrip can become a RoadCode patch plan.

## Inbound handoffs
- RoadOS command or workspace launch
- RoadView research queries
- RoadWork task that needs AI assistance

## Outbound handoffs
- RoadWire for durable notes
- RoadMap for task status
- RoadCode for build execution
- RoadChain for important decisions

## Example routing decisions

User says: "Research this topic with Claude and GPT and summarize the best approach."
Route: RoadTrip
Reason: Solo multi-agent research.
Receipt needed: yes
Permission needed: user_write

User says: "Build the feature we just researched."
Route: RoadCode (with handoff from RoadTrip)
Reason: Execution vs exploration.

## Receipt events
- roadtrip.room.created
- roadtrip.handoff.created
- roadtrip.summary.saved
- roadtrip.model.switched
- roadtrip.consent.updated

## Permission notes
- Creating/using room: user_write
- External tool or provider calls: operator_approval or CarKeys scoped grant
- Exporting memory: consent check + receipt

## Anti-drift
RoadTrip must remain solo. It must not become group chat or generic chat app. It must make agent work visible and produce clear handoff packets with receipts.