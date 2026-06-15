# Routing — OneWay

## Route here when the user wants to...
- Move data into BlackRoad, map/rotate/encode it to BlackRoad identity/memory, then return it outward in the format external providers need
- Maintain data sovereignty and prevent external providers from owning the durable memory layer
- Create controlled import/export pipelines with consent and provenance

## Do not route here when...
- Managing identity, permissions, or grants (CarKeys)
- Recording proof/receipts (RoadChain)
- General file/workspace actions (RoadOS)

## Common confusion boundaries

### OneWay vs CarKeys
OneWay = data movement, rotation, mapping, and sovereignty after permission is granted.
CarKeys = identity, access, permissions, and grants.
Handoff: OneWay asks CarKeys who/what is allowed before moving data.

### OneWay vs RoadChain
OneWay = controlled data flow and transformation.
RoadChain = receipts and proof of what happened during the flow.
Handoff: OneWay writes RoadChain receipts for important data flows.

### OneWay vs RoadWork
OneWay = technical data sovereignty pipelines.
RoadWork = business/backend setup that may use those pipelines.

## Inbound handoffs
- RoadTrip / CarPool when external provider data is involved
- RoadCode when connecting APIs or external services
- Any product needing to bring data in or push data out while preserving ownership

## Outbound handoffs
- RoadChain for flow receipts and provenance
- CarKeys for permission checks before movement
- RoadWork for backend data setup

## Example routing decisions

User says: "Take this data from ChatGPT, map it to my BlackRoad identity, store it durably here, and give me a clean export."
Route: OneWay
Reason: Controlled data flow and sovereignty.
Receipt needed: yes
Permission needed: consent + CarKeys check

User says: "Connect my external account and sync data."
Route: CarKeys first (for permission/grant) → OneWay for the actual data movement.

## Receipt events
- oneway.flow.created
- oneway.consent.checked
- oneway.data.returned
- oneway.mapping.created

## Permission notes
- Basic flow planning: user_write
- Moving sensitive or provider data: operator_approval_required + explicit consent
- Storing raw payloads long-term: review required
- Exporting user data: consent + receipt

## Anti-drift
OneWay must prevent external providers from becoming the durable owner of the user’s data. It is not just “export” — it is controlled one-way-and-back transformation with ownership preserved. It must not silently take user data or train on it without permission.