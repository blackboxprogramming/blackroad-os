# Routing — RoadSide

## Route here when the user wants to...
- Get help, support, onboarding, or concierge routing
- Ask a question and be routed to the right product, agent, or human
- Use an embeddable help surface on websites or inside BlackRoad
- Escalate from chatbot to human or deeper agent work

## Do not route here when...
- Doing deep solo AI work (RoadTrip)
- Group collaboration (CarPool)
- General workspace commands (RoadOS)

## Common confusion boundaries

### RoadSide vs RoadTrip
RoadSide = front-door help, support, concierge, and routing interface.
RoadTrip = solo operator + AI mission room (deeper work after escalation).
Handoff: RoadSide can escalate into a RoadTrip room for complex tasks.

### RoadSide vs CarPool
RoadSide = support and routing.
CarPool = live group collaboration and project rooms.
Handoff: Support threads can become CarPool rooms if collaboration is needed.

### RoadSide vs Roadie
RoadSide = the product (embeddable help surface).
Roadie = an agent that can appear inside RoadSide, RoadOS, RoadTrip, etc.
Never treat Roadie as the product.

## Inbound handoffs
- Any product’s help links or “need assistance” buttons
- RoadOS command failures or confusion
- External websites embedding the concierge

## Outbound handoffs
- RoadWire for long-form support records
- RoadWork for operational tickets
- RoadTrip for complex internal agent work after escalation
- CarKeys for login/access issues

## Example routing decisions

User says: "I’m stuck, can you help me connect my account?"
Route: RoadSide
Reason: Front-door support and routing.
Receipt needed: yes for the thread
Permission needed: user_read / CarKeys check

User says: "This is too complicated for chat, I need to work with agents on it."
Route: RoadTrip (escalated from RoadSide)

## Receipt events
- roadside.session.created
- roadside.route.suggested
- roadside.escalation.created
- roadside.roadwire.handoff

## Permission notes
- Basic help and public knowledge: public_read
- Account-specific or sensitive help: user_read + CarKeys
- Making security or account changes: operator_approval_required via CarKeys
- Escalating to internal systems: scoped agent permissions

## Anti-drift
RoadSide must be a simple, honest front-door. It must not trap users in chatbot loops, pretend to know what it doesn’t know, or replace human escalation when needed. It routes — it does not try to solve everything itself.