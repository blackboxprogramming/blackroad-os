# API Plan — RoadOS

## Status
canon_status: canon_ready
implementation_status: planned
source: Products.txt + canon templates

## Read endpoints
GET /api/roados/status
  - Returns canon maturity, implementation status, risk, next action
GET /api/roados/workspaces/:id
  - Workspace layout, open files, active route, memory summary
GET /api/roados/commands/recent
  - Last N routed commands with status and receipt links
GET /api/roados/receipts
  - Recent receipts for this workspace

## Write endpoints
POST /api/roados/command/route
  - Body: { raw_input, context }
  - Infers intent, returns route options + safe next actions
  - Requires: user_write or agent_write_limited + scope
  - Writes receipt on successful route

POST /api/roados/workspace/save
  - Body: { layout?, notes?, active_route? }
  - Updates workspace state
  - Requires: user_write
  - Writes receipt if state changed

PATCH /api/roados/workspace/:id
  - Partial updates to layout or context

## Permissions
- public_read: status, public help docs
- user_read: own workspaces, command history summaries
- user_write: route commands, save workspace state, personal notes
- agent_write_limited: suggest routes, update agent session state (scoped)
- operator_approval_required: destructive file ops, external exposure, shell execution that changes system
- admin_only: global workspace policies

## Receipts
- roados.command.routed (always for routing actions)
- roados.workspace.saved
- roados.context.updated
- roados.agent.session_started

## Errors
- 400: invalid intent or missing context
- 401: unauthenticated for private workspace
- 403: insufficient permission or scope
- 404: workspace not found
- 422: unsafe route blocked (needs approval)

## Mock vs real
All routes currently PLANNED. Mock responses will return static safe examples until real implementation.

## External integrations
None in MVP. Later: git providers, local file system bridges, agent tool gateways (all gated by CarKeys).