# Deployments — RULES

Local rules for deployment configuration and runbooks.

## Runbook Format

Every runbook must include:

1. **Prerequisites** — what must be true before starting (tools, access, state)
2. **Steps** — numbered, atomic steps; one logical action per step
3. **Verification** — how to confirm each step succeeded
4. **Troubleshooting** — common failure modes + recovery
5. **Rollback** — how to undo if anything fails
6. **Time estimate** — how long this should take
7. **Owner** — who maintains this runbook

## Environment Configuration

- Environment variables in `_registry/env-ENVIRONMENT.sh` (e.g., `env-local.sh`)
- Secrets in `.env.local` (gitignored) — template in `_registry/env-template.sh`
- Config files in `_registry/CONFIG-ENVIRONMENT.json` (e.g., `mesh-topology-local.json`)
- Docker/deployment files in per-environment subdirectories (local/, testing/, prod/)

## Naming Conventions

- Local setup: `LOCAL_SETUP.md`
- Testing: `TESTING_SETUP.md`
- Production: `PRODUCTION_DEPLOYMENT.md`
- Rollback: `ROLLBACK_PLAN.md`
- Monitoring: `MONITORING.md`
- Incident response: `INCIDENT_RESPONSE.md`

## Invariants

- Every runbook must be tested before commit
- Destructive operations must have a clear rollback
- All credentials/secrets go in `.env` files (never in docs/configs)
- Environment configs must version with the codebase
- Failed deployments must be logged (RoadChain receipt)

## Maintenance

- Runbooks reviewed by Gaia (Agent 08) for accuracy
- Infrastructure changes synchronized with HighWay/ product docs
- Incident reports filed in Receipts/ with lessons learned
