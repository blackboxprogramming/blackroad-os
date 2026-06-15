# Schema — RoadCode

## Core objects

### Project
Purpose: A codebase or technical project being built or maintained.
Fields:
- id: roadcode.project.<uuid>
- name
- repo_url or local_path
- language
- status (active, archived, needs_review)
- last_inspected
- receipt_head

### PatchPlan
Purpose: Proposed changes to a project.
Fields:
- id
- project_id
- description
- risk_level (low, medium, high)
- files_changed
- test_plan
- deploy_readiness
- approval_status
- receipt_id

### BuildStep
Purpose: A step in the build/test/deploy process.
Fields:
- id
- step_type (inspect, patch, test, deploy, etc.)
- status
- output_summary
- receipt_id

## Status values
- active
- needs_review
- blocked
- deployed

## IDs
roadcode.project.<uuid>
roadcode.patch_plan.<uuid>
roadcode.build_step.<uuid>

## Events
- roadcode.repo.inspected
- roadcode.patch.planned
- roadcode.test.ran
- roadcode.deploy.planned
- roadcode.risk.classified

## Permissions
- Repo inspection: user_read
- Creating patch plans: user_write
- Applying patches or deploying: operator_approval_required

## Data retention
- Project metadata and patch history: keep with receipts
- Sensitive environment details: never stored directly (use CarKeys references)