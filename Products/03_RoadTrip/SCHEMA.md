# Schema — RoadTrip

## Core objects

### MissionRoom
Purpose: A solo workspace where one human works with multiple agents/models.
Fields:
- id: roadtrip.room.<uuid>
- title
- owner_id
- created_at
- status (active, archived)
- selected_models
- receipt_head

### AgentThread
Purpose: Conversation or work thread with a specific agent or model.
Fields:
- id
- room_id
- agent_id
- messages (array or reference)
- summary
- handoff_packet

### HandoffPacket
Purpose: Structured output meant to be passed to another product.
Fields:
- id
- room_id
- target_product
- content
- receipt_id

## Status values
- active
- paused
- completed
- archived

## IDs
roadtrip.room.<uuid>
roadtrip.thread.<uuid>
roadtrip.handoff.<uuid>

## Events
- roadtrip.room.created
- roadtrip.handoff.created
- roadtrip.summary.saved
- roadtrip.model.switched

## Permissions
- Creating/using rooms: user_write
- External tool calls or provider access: operator_approval or scoped CarKeys grant
- Exporting memory: consent + receipt

## Data retention
- Room summaries and handoff packets: keep with receipts
- Full message history: summarize after 30 days