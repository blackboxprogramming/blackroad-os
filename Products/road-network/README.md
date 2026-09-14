# road-network

`road-network` compiles BlackRoad's checked-in network canon into deterministic provider-neutral state.

The source of truth is `Canon/Network/`. UniFi, Dream Router 7, DNS systems, overlays, and cloud networks are Ramps. They implement desired state; they do not own it.

## Commands

```bash
cd Products/road-network
python3 -m pip install -e .

road-network --root ../.. validate
road-network --root ../.. plan
road-network --root ../.. apply
road-network --root ../.. apply --execute
```

`apply` is dry-run unless `--execute` is supplied. The current implementation writes compiled local artifacts only. It deliberately refuses `--adapter unifi` because the Dream Router has not been enrolled and there is no authenticated provider session yet. A tool must not report a network mutation it did not perform.

Compiled output defaults to `.road/network/` and includes:

- `unifi.json` — provider-neutral UniFi network/zone intent
- `dns.json` — private DNS records
- `fleet.json` — compiled device homes
- `services.json` — service and control-plane addresses
- `bindings.json` — agent/device placement bindings
- `state.json` — deterministic desired-state snapshot used for future diffs
- `receipts/` — RoadChain local-apply receipts

## Exit codes

- `0` — valid / clean / successfully compiled
- `10` — plan contains changes or dry-run has work
- `20` — blocked or invalid canon

## Safety invariants

- inter-zone default is deny
- unknown devices stay in `road.lab`
- VLAN 1729 is `road.control`
- an IP is not an identity
- an agent/device binding grants no authority by itself
- physical actuation requires permission and a receipt
- the recovery plane remains independent
- public repositories do not receive credentials, secrets, serials, or private overlay material

## `road network`

The Road CLI should route these subcommands directly to this package:

```text
road network validate  -> road-network validate
road network plan      -> road-network plan
road network apply     -> road-network apply
```

That bridge is intentionally thin. Network behavior belongs here, while Road remains the operator command surface.
