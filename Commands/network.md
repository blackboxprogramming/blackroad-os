# `road network`

Operator surface for BlackRoad network desired state.

## Routes

```text
road network validate
road network discover
road network plan
road network apply
```

Implementation: `Products/road-network`.

## Behavior

`validate` checks identity, address, VLAN, control-plane, binding, and quarantine invariants.

`discover` reads current UniFi Network state through the official Integration API. It is read-only. The API key must come from an environment variable, never a command-line argument.

`plan` compiles `Canon/Network/` and diffs it against either the last local compiled `state.json` or, with `--adapter unifi`, the live Dream Router observation.

`apply` is dry-run by default. `apply --execute` with the local adapter writes deterministic compiled state and a RoadChain receipt. UniFi provider write remains explicitly blocked until the enrolled Dream Router's versioned schema and write/readback sequence are proven.

## UniFi route

```text
Canon/Network
     |
     v
road network discover
     |
     v
observed UniFi state
     |
     v
road network plan --adapter unifi
     |
     +--> exact matches
     +--> safe creates/updates
     +--> blockers
     +--> unmanaged observations
     |
     v
future CarKeys-gated write/readback
```

## Laws

1. Canon precedes provider state.
2. Read provider state before planning a provider write.
3. Unknown devices enter `road.lab`.
4. VLAN 1729 is `road.control`.
5. An address is not identity.
6. Agent/device placement is a binding, not shared identity.
7. Default inter-zone posture is deny.
8. VLAN collisions block instead of triggering guessed renames.
9. Unmanaged provider resources are never silently deleted.
10. No provider mutation may be reported without verification and a receipt.
