# Routing — RoadOS

## Route here when the user wants to...
- Open the one-tab browser computer/workspace
- Use command palette, file surface, terminal, memory map, or product launcher
- Route an intent/command to the right product, file, or action
- See active work, receipts, or context in one stable home base

## Do not route here when...
- Building/debugging/deploying code (RoadCode)
- Solo AI/agent mission work (RoadTrip)
- Group human+AI collaboration (CarPool)
- Searching or discovering (RoadView)
- Doing business/operational work steps (RoadWork)

## Common confusion boundaries

### RoadOS vs RoadCode
RoadOS is the computer/shell/workspace.
RoadCode is where you build, patch, test, deploy, and figure out "now what?" after code exists.
Handoff: RoadOS opens the workspace and routes the build task to RoadCode.

### RoadOS vs RoadTrip
RoadOS is the persistent home base.
RoadTrip is the solo operator + AI mission room that can live inside or be launched from RoadOS.
Handoff: RoadOS can open or hand off to a RoadTrip room.

### RoadOS vs RoadView
RoadOS is the surface.
RoadView is the search/discovery lens and visible agent browsing.
Handoff: RoadOS can embed or launch RoadView search.

## Inbound handoffs
- RoadView search results can open in RoadOS workspace
- RoadTrip/Carpool rooms can be launched from RoadOS
- RoadCode patches can be inspected in RoadOS file surface

## Outbound handoffs
- Command/intent routing to any product
- File/context handoff to RoadBook, RoadWork, RoadChain, etc.
- Agent work to RoadTrip

## Example routing decisions

User says: "Open my files and show me what I was working on yesterday."
Route: RoadOS
Reason: Persistent workspace and memory surface.
Receipt needed: yes (context loaded)
Permission needed: user_read

User says: "Build this feature."
Route: RoadCode (via RoadOS command router)
Reason: Build/deploy work.
Receipt needed: yes
Permission needed: user_write + operator_approval if deploy

User says: "Help me with this homework."
Route: PitStop (via RoadOS or RoadView)
Reason: Learning/tutoring intent.

## Receipt events
- roados.workspace.opened
- roados.command.routed
- roados.context.saved
- roados.file.viewed
- roados.intent.inferred

## Permission notes
- Reading workspace/files: user_read
- Routing commands that change state: user_write or operator_approval
- Exposing files externally: operator_approval_required
- Agent actions inside workspace: agent_write_limited + CarKeys scope

## Anti-drift
RoadOS must not become a decorative desktop skin or generic tab manager. It must actively route, remember context, and give safe next actions instead of "command not found" errors.