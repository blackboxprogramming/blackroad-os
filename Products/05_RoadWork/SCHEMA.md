# Schema — RoadWork

## Core objects

### WorkItem
Purpose: A business, operational, compliance, or task item.
Fields:
- id: roadwork.item.<uuid>
- title
- type (formation, filing, compliance, operational, etc.)
- checklist
- deadlines
- status
- proof_requirements
- receipt_id

### Obligation
Purpose: A required step with proof.
Fields:
- id
- work_item_id
- description
- due_date
- completed
- receipt_id

## Status values
- not_started
- in_progress
- blocked
- completed
- needs_approval

## IDs
roadwork.item.<uuid>
roadwork.obligation.<uuid>

## Events
- roadwork.work_item.created
- roadwork.compliance_review_needed
- roadwork.task.completed
- roadwork.proof.attached

## Permissions
- Creating/editing own work items: user_write
- Official filings or sensitive actions: operator_approval_required
- Viewing team/org items: appropriate scope

## Data retention
Work items and obligations kept with receipts. Sensitive compliance data minimized.