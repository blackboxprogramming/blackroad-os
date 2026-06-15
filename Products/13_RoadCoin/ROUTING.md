# Routing — RoadCoin

## Route here when the user wants to...
- View usage, compute, contribution, or credit balances
- Record internal usage or contribution events
- Understand what a task or action cost in credits/compute
- Request or review internal credit grants (non-financial)

## Do not route here when...
- Actual money, payments, banking, or investment (use proper financial systems after review)
- Business billing or invoicing (RoadWork)
- Speculative crypto or token mechanics

## Common confusion boundaries

### RoadCoin vs RoadWork
RoadCoin = internal utility credits and usage accounting.
RoadWork = the actual business, compliance, and operational work (including any billing setup).
Handoff: RoadWork can use RoadCoin data for internal reporting.

### RoadCoin vs RoadChain
RoadCoin records usage/credit movement.
RoadChain provides the receipt/proof layer for those events.
Handoff: Important credit events write RoadChain receipts.

## Inbound handoffs
- HighWay for compute metering
- RoadCode / RoadTrip for usage tracking
- Any product that consumes resources

## Outbound handoffs
- RoadChain for credit event receipts
- RoadMap for usage dashboards
- RoadWork for any billing/admin workflows

## Example routing decisions

User says: "How much compute did my agents use this week?"
Route: RoadCoin
Reason: Usage and credit accounting.
Receipt needed: yes
Permission needed: user_read

User says: "I want to earn credits by contributing compute."
Route: RoadCoin (with review)
Reason: Contribution accounting.

## Receipt events
- roadcoin.credit.granted
- roadcoin.credit.used
- roadcoin.usage.recorded
- roadcoin.compliance_review_needed

## Permission notes
- Viewing own usage/credits: user_read
- Granting credits or changing policy: operator_approval_required + compliance review
- Any language around payouts, exchange, or value: must go through review

## Anti-drift
RoadCoin must stay strictly internal utility credits, usage, compute, and contribution accounting. It must never use investment, yield, token sale, profit, tradable asset, security, or banking language. All public or creator-facing language requires compliance review.