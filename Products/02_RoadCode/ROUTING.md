# Routing — RoadCode

## Route here when the user wants to...
- Build, debug, patch, test, host, deploy, or figure out the next technical step for code
- Inspect a repo and understand what exists vs what is missing
- Get a safe patch plan, test plan, or deploy readiness checklist
- Route technical work through the 172 process and 1,729 capabilities

## Do not route here when...
- Using the general workspace or command shell (RoadOS)
- Doing solo AI research or mission work (RoadTrip)
- Doing business/operational filings or compliance (RoadWork)
- Searching or discovering (RoadView)

## Common confusion boundaries

### RoadCode vs RoadOS
RoadCode is the builder.
RoadOS is the computer that launches and contains the build work.
Handoff: RoadOS routes build intents to RoadCode.

### RoadCode vs RoadTrip
RoadTrip is for exploration and agent conversation.
RoadCode is for concrete build/deploy actions with receipts.
Handoff: RoadTrip research can produce a plan that RoadCode executes.

### RoadCode vs HighWay
RoadCode builds the software.
HighWay runs, routes, observes, and scales the infrastructure.
Handoff: RoadCode produces deploy plans that HighWay executes.

## Inbound handoffs
- RoadOS command router
- RoadTrip research plans
- RoadView technical search results
- RoadWork backend/internal system tasks

## Outbound handoffs
- HighWay for deploy/infra
- RoadChain for every meaningful change
- RoadMap for status
- CarKeys for secrets/permissions during build

## Example routing decisions

User says: "Fix the bug in this repo and deploy it."
Route: RoadCode
Reason: Build + deploy work.
Receipt needed: yes (patch, test, deploy plan)
Permission needed: user_write + operator_approval for deploy

User says: "What should I build next?"
Route: RoadTrip first, then handoff to RoadCode
Reason: Exploration vs execution.

## Receipt events
- roadcode.repo.inspected
- roadcode.patch.planned
- roadcode.test.ran
- roadcode.deploy.planned
- roadcode.deploy.executed
- roadcode.risk.classified

## Permission notes
- Repo inspection: user_read
- Patch planning: user_write
- Applying patches, committing, pushing, deploying: operator_approval_required
- Accessing secrets/env: CarKeys scoped grant

## Anti-drift
RoadCode must not claim code is deployed when it is only written. It must surface missing pieces, risk, and require approval for destructive or external actions. No fake completion.