# Deployments — NEXT

**Immediate next action:** Create LOCAL_SETUP.md runbook for development environment.

**Current state:**
- Deployments/ folder scaffold exists
- No runbooks or environment configs yet
- Infrastructure assumed but not documented

**Next steps:**
1. Write LOCAL_SETUP.md covering:
   - Prerequisites (Node.js 20+, git, browser)
   - Repo checkout + branch setup
   - Registry validation + sync
   - Running validation suite
   - Opening index.html locally
   - Troubleshooting common issues
2. Write TESTING_SETUP.md for staging environment
3. Write MESH_DEPLOYMENT.md for LoRa + Headscale setup
4. Write ROLLBACK_PLAN.md for incident response
5. Create environment variables template (_registry/env-template.sh)

**Owner:** Gaia (Agent 08) / Infrastructure lead

**Status:** Setup phase — local development runbook needed
