# RoadChain Receipt: UniFi read-first adapter

Date: 2026-09-13
Repository: `blackboxprogramming/blackroad-os`
Component: `Products/road-network`

## Intent

Connect BlackRoad network canon to the Dream Router 7 through a read-first provider adapter without allowing provider state to become canonical authority.

## Changes

- added dependency-free official UniFi Network Integration API client
- added `road-network discover --adapter unifi`
- added live `road-network plan --adapter unifi`
- reads application version, site, networks, firewall zones, firewall policies when supported, adopted devices, and connected clients
- added API-version capability gates
- added exact-name network matching and VLAN-collision blockers
- reports unmanaged provider networks without deleting them
- keeps provider write disabled
- keeps destructive operation count at zero
- refuses command-line API-key values; API keys are sourced from environment variables
- keeps TLS verification enabled by default with explicit CA-file support
- added unit coverage for URL normalization, secret redaction, site disambiguation, idempotent planning, VLAN collision blocking, and old-version blocking
- documented `road network discover` operator route

## Provider authority

UniFi is a Ramp. `Canon/Network/` remains the desired-state authority.

## Safety result

Provider mutation: **NO**
Provider read capability: **IMPLEMENTED**
Provider live planning: **IMPLEMENTED**
Provider live write: **BLOCKED**
Destructive reconciliation: **NONE**

## Verification

GitHub Actions `road-network` run 8 completed successfully after the adapter, tests, package metadata, and documentation were installed.

No API keys, public/private credentials, client snapshots, router serials, or provider secrets were committed.
