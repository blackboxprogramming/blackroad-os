# RoadChain Receipt — road-network compiler

Date: 2026-09-13 (operator local date)
Repository: `blackboxprogramming/blackroad-os`
Scope: Network canon compiler and operator command surface

## Intent

Turn `Canon/Network/` into executable, testable desired state without making UniFi or any provider the source of truth.

## Added

- `Products/road-network/pyproject.toml`
- `Products/road-network/src/road_network/__init__.py`
- `Products/road-network/src/road_network/yamlmini.py`
- `Products/road-network/src/road_network/compiler.py`
- `Products/road-network/src/road_network/cli.py`
- `Products/road-network/tests/test_network.py`
- `Products/road-network/README.md`
- `Commands/network.md`
- `.github/workflows/road-network.yml`

## Updated

- `Commands/README.md`

## Behavior

The compiler now supports:

- `road-network validate`
- `road-network plan`
- `road-network apply`
- deterministic desired-state digests
- idempotent local compiled state
- DNS, fleet, service, binding, and UniFi-intent artifacts
- RoadChain local-apply receipts
- explicit blocking of live UniFi mutation until an authenticated router adapter exists

The package has no runtime dependencies outside the Python standard library. Its small YAML parser intentionally supports only the subset used by `Canon/Network/`.

## Validation gates

The validator checks:

- unique network IDs and VLANs
- valid CIDRs and gateways
- VLAN 1729 for `road.control`
- device IP membership
- target-network membership
- unresolved devices remain in `road.lab`
- service addresses belong to the correct service/control subnet
- agent bindings reference known devices
- deny-by-default inter-zone policy
- unknown-device quarantine policy

## CI

Workflow: `road-network`
Run: `34804378927`
Result: **success**

The first CI attempt correctly exposed an over-broad test that treated the legitimate service name `secrets.control.road.home.arpa` as secret material. The test was corrected to inspect credential-bearing field names rather than substrings, and the second run passed.

Validated sequence:

1. package install
2. canon validation
3. unit tests
4. local compile
5. idempotent re-plan

## Safety

No router, DNS provider, firewall, or external network was mutated by this work. `--adapter unifi` is intentionally blocked until the Dream Router is enrolled with a verified authenticated adapter.

No credentials, tokens, private keys, serials, or private overlay credentials were added.

## Result

`Canon/Network/` is now machine-readable desired state with a working validator/planner/compiler and green CI. The next provider step is an authenticated UniFi adapter that performs read-first discovery, computes a diff, requires explicit execution permission, verifies the result, and emits a provider mutation receipt.
