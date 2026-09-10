# Schema — RoadOS

## Core objects

### Workspace
Purpose: The persistent one-tab operating surface that holds files, terminal, agents, memory, command history, active routes, and context.
Fields:
- id (roados.workspace.<uuid>)
- owner
- created_at
- last_active_at
- layout (json: panels, command_dock, agent_rail)
- open_files[]
- active_route
- memory_map_ref
- receipt_chain_head

Relationships:
- has_many: files, commands, agent_sessions
- belongs_to: user

### Command
Purpose: User or agent intent that gets routed.
Fields:
- id
- timestamp
- raw_input
- inferred_intent
- routed_to (product_slug or lane)
- status (routed | executed | failed_safely)
- receipt_id

### FileReference
Purpose: Pointer to actual file content (local, git, or memory-backed).
Fields:
- path
- type (file | dir | memory)
- last_modified
- provenance (RoadChain ref if applicable)

### AgentSession
Purpose: Active agent presence inside the workspace.
Fields:
- agent_id
- role
- permissions_scope
- started_at
- last_message_at

## Status values
- active
- archived
- shared
- readonly

## IDs
roados.workspace.<uuid>
roados.command.<uuid>
roados.file.<path_hash>

## Events
- workspace.opened
- command.routed
- context.saved
- file.viewed
- agent.joined
- intent.inferred

## Permissions
- read: user_read or public_read (for shared workspaces)
- write: user_write (layout, notes) or operator_approval (destructive actions)
- agent actions: agent_write_limited + CarKeys scope

## Data retention
- Command history: summarized after 30 days unless receipt-linked
- Memory map: user-controlled retention
- Avoid storing raw secrets or large binary blobs directly