# Deployments — INDEX

Map of deployment configurations, runbooks, and infrastructure documentation.

## Deployment Environments

| Environment | Purpose | Status |
|-------------|---------|--------|
| Local | Development laptop | scaffold |
| Testing | QA/staging environment | scaffold |
| Production | Live user deployment | scaffold |
| Edge | On-device deployment (LoRa mesh) | scaffold |

## Deployment Components

| Component | Purpose | Runbook |
|-----------|---------|---------|
| Database | Persistent storage | TBD |
| Sync | Git-native data plane sync | TBD |
| Mesh | Hybrid mesh network (LoRa + WireGuard) | TBD |
| Auth | CarKeys permission system | TBD |
| UI | Browser-native desktop | TBD |
| RoadChain | Proof trail + provenance | TBD |

## Deployment Phases

1. **Phase 1:** Local development setup
2. **Phase 2:** Staging environment validation
3. **Phase 3:** Edge device deployment (LoRa mesh nodes)
4. **Phase 4:** Production multi-region rollout

## Current Status

**Scaffold:** Deployment folder structure exists
**Planned:** Environment-specific configs + runbooks
**Research:** Mesh deployment topology (Meshtastic + Headscale)
