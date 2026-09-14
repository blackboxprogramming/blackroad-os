# BlackRoad Network Canon

This directory is the source of truth for BlackRoad network intent.

UniFi, routers, switches, overlays, DNS providers, and cloud networks are **Ramps**: implementations of the desired state recorded here. They are not the canonical authority.

## Rules

- Default inter-zone posture is deny.
- Unknown devices enter `road.lab` before promotion.
- An IP address is an assignment, not an identity.
- Agent identity and device identity are separate; placement is represented by a binding.
- `road.control` / VLAN 1729 is an authority plane, not a general LAN.
- Recovery infrastructure remains operationally independent from the systems it may need to rescue.
- Physical actuation requires scoped permission and a receipt.
- Public IPs, credentials, secrets, device serials, and private overlay credentials do not belong in this public repository.
- Significant topology or policy changes require RoadChain receipts.

## Files

- `networks.yaml` — VLANs, CIDRs, gateways, and trust classes.
- `devices.yaml` — desired homes for known physical devices.
- `services.yaml` — stable service names and virtual addresses.
- `bindings.yaml` — agent-to-device placement bindings.
- `policy.yaml` — network security invariants and zone intent.

## Canonical flow

```text
BlackRoad canon
      |
      v
network compiler
      |
      +--> UniFi / Dream Router 7
      +--> DNS
      +--> RoadOS fleet registry
      +--> WireGuard / overlay adapters
      +--> receipts
```

The desired state lives here. Provider configuration is derived from it.
