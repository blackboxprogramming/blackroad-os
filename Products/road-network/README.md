# road-network

`road-network` compiles BlackRoad's checked-in network canon into deterministic provider-neutral state and can now read live UniFi state before planning changes.

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

### Read the Dream Router without changing it

The UniFi adapter uses the official Network Integration API and sends the API key only in the `X-API-Key` request header. Keys are intentionally not accepted as command-line values, so they do not get sprayed into shell history.

```bash
export ROAD_UNIFI_URL='https://10.17.10.1'
export ROAD_UNIFI_API_KEY='...'

road-network --root ../.. discover --adapter unifi
road-network --root ../.. plan --adapter unifi
road-network --root ../.. apply --adapter unifi
```

A bare UniFi OS gateway origin is normalized to `/proxy/network/integration`. An explicit `.../integration` base is also accepted.

Optional selectors and TLS controls:

```bash
export ROAD_UNIFI_SITE_ID='...'
export ROAD_UNIFI_SITE_NAME='Default'
export ROAD_UNIFI_CA_FILE='/path/to/local-ca.pem'

road-network --root ../.. discover --adapter unifi --snapshot .road/network/unifi-observed.json
```

`--unifi-insecure` exists only for deliberate lab/recovery use. TLS verification is on by default.

Discovery reads:

- Network application version
- site identity
- networks/VLANs
- firewall zones
- firewall policies when the installed Network version exposes them
- adopted UniFi devices
- connected clients

The normal discovery output is a summary. `--full` emits the full observed payload. `--snapshot PATH` writes the full observation locally. Do not commit live snapshots containing client/network inventory to public repositories.

### Live planning

`plan --adapter unifi` compares canon against the observed router without mutating anything. It is deliberately conservative:

- an exact network name match is preferred
- an already-used VLAN with a different name becomes a blocker instead of an inferred rename
- unmanaged provider networks are reported but never auto-deleted
- destructive operations are never generated
- provider version gates are checked before a write plan is considered viable
- CIDR/gateway intent remains canon-only until the enrolled gateway's versioned API schema proves a safe writable mapping

`apply --adapter unifi` is therefore still a provider dry-run. `apply --adapter unifi --execute` blocks explicitly and reports `provider_mutated: false` until write/readback support is enabled and tested against the enrolled Dream Router. A tool must not report a network mutation it did not perform.

## Local compiled state

`apply --execute` with the default local adapter writes deterministic artifacts to `.road/network/`:

- `unifi.json` — provider-neutral UniFi network/zone intent
- `dns.json` — private DNS records
- `fleet.json` — compiled device homes
- `services.json` — service and control-plane addresses
- `bindings.json` — agent/device placement bindings
- `state.json` — deterministic desired-state snapshot used for future diffs
- `receipts/` — RoadChain local-apply receipts

## Exit codes

- `0` — valid / clean / successful read or compile
- `10` — plan contains changes or dry-run has work
- `20` — blocked, ambiguous, unreachable provider, or invalid canon

## Safety invariants

- inter-zone default is deny
- unknown devices stay in `road.lab`
- VLAN 1729 is `road.control`
- an IP is not an identity
- an agent/device binding grants no authority by itself
- physical actuation requires permission and a receipt
- the recovery plane remains independent
- public repositories do not receive credentials, secrets, serials, or private overlay material
- live provider state is read before any future write
- no guessed rename, delete, or destructive reconciliation

## `road network`

The Road CLI should route these subcommands directly to this package:

```text
road network validate   -> road-network validate
road network discover   -> road-network discover
road network plan       -> road-network plan
road network apply      -> road-network apply
```

That bridge stays thin. Network behavior belongs here, while Road remains the operator command surface.
