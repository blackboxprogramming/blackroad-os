# `road network`

Operator surface for BlackRoad network desired state.

## Routes

```text
road network validate
road network plan
road network apply
```

Implementation: `Products/road-network`.

## Behavior

`validate` checks identity, address, VLAN, control-plane, binding, and quarantine invariants.

`plan` compiles `Canon/Network/` and diffs it against the last compiled `state.json` without mutating a provider.

`apply` is dry-run by default. `apply --execute` writes deterministic local compiled state and a RoadChain receipt. Live UniFi mutation remains blocked until an authenticated Dream Router adapter is enrolled and verified.

## Laws

1. Canon precedes provider state.
2. Unknown devices enter `road.lab`.
3. VLAN 1729 is `road.control`.
4. An address is not identity.
5. Agent/device placement is a binding, not shared identity.
6. Default inter-zone posture is deny.
7. No provider mutation may be reported without verification and a receipt.
