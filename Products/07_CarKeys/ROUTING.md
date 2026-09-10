# Routing — CarKeys

## Route here when the user wants to...
- Log in, manage identity, sessions, or permissions
- Request, approve, or revoke grants/scopes for tools, agents, or providers
- Connect external accounts or APIs with proper consent and revocation
- Check what a user or agent is allowed to do

## Do not route here when...
- Managing capabilities or tools themselves (GloveBox)
- Moving or transforming data between systems (OneWay)
- General workspace actions (RoadOS)

## Common confusion boundaries

### CarKeys vs GloveBox
CarKeys = who has access and what scopes/grants exist.
GloveBox = what capabilities/tools/features exist to unlock.
Handoff: GloveBox lists the tool → CarKeys decides if it can be used.

### CarKeys vs OneWay
CarKeys = identity, permission, grants.
OneWay = controlled data flow and sovereignty after permission is granted.
Handoff: OneWay asks CarKeys for permission before moving data.

### CarKeys vs RoadTrip / CarPool
CarKeys gates agent and tool access inside rooms.
Handoff: Rooms request scoped grants via CarKeys.

## Inbound handoffs
- Any product requesting tool/agent access
- RoadTrip / CarPool when agents need capabilities
- RoadCode when deploying or connecting providers

## Outbound handoffs
- GloveBox for capability discovery
- RoadChain for grant/permission receipts
- OneWay after permission is granted

## Example routing decisions

User says: "Connect my GitHub account so agents can read repos."
Route: CarKeys
Reason: Grant + scoped permission for external provider.
Receipt needed: yes
Permission needed: operator_approval or user consent

User says: "What tools can I use here?"
Route: GloveBox first, then CarKeys for access check.

## Receipt events
- carkeys.grant.requested
- carkeys.grant.approved
- carkeys.grant.revoked
- carkeys.permission.checked
- carkeys.session.created

## Permission notes
- Basic login and own grants: user_write
- Approving sensitive or broad grants: operator_approval_required
- Provider connections and secret handling: admin_only + CarKeys scoped
- Agent actions: must have explicit scope

## Anti-drift
CarKeys must make access feel as easy as logging into Google while keeping BlackRoad-owned consent, scoped permissions, revocation, and receipts. It must never expose raw secrets or allow unscoped agent actions.