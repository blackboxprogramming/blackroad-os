# RoadChain Receipts — RoadOS

## Receipt philosophy
RoadOS is the persistent home base. Important state changes (routing decisions, context saves, file mutations, agent actions, workspace layout changes) should be receipt-backed so the user can always see what happened and why.

## Required receipt events
- roados.workspace.opened
- roados.command.routed (includes inferred_intent, chosen_route, safe_alternatives)
- roados.context.saved (memory map or active work snapshot)
- roados.file.viewed or mutated (with provenance if from RoadChain)
- roados.agent.session_started / ended
- roados.intent.inferred (with confidence and reasoning summary)
- roados.route.handoff (to another product)

## Optional receipt events
- roados.layout.customized
- roados.command.failed_safely (with explanation and suggested fix)

## Do not record
- Raw user file contents (store references + hash only)
- Full agent chain-of-thought (summary + receipt link is enough)
- Temporary UI state that has no lasting impact
- Any secrets, tokens, or credentials

## Example receipt
{
  "event": "roados.command.routed",
  "actor": "user | Roadie | Lucidia",
  "product": "roados",
  "timestamp": "ISO-8601",
  "summary": "User asked to open yesterday’s work. Routed to RoadOS workspace and restored last context.",
  "source": "command_dock or voice or agent suggestion",
  "previous_hash": "...",
  "hash": "computed_later",
  "details": {
    "inferred_intent": "...",
    "routed_to": "roados.workspace",
    "safe_next_actions": ["open file X", "ask RoadCode for build help"]
  }
}