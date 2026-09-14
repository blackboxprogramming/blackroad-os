# RoadChain Receipt — Network Canon v1

Date: 2026-09-13
Repository: `blackboxprogramming/blackroad-os`
Branch: `main`

## Intent

Install a canonical BlackRoad network source of truth for the Dream Router 7 migration and the existing device fleet.

## Changes

Created:

- `Canon/Network/README.md`
- `Canon/Network/networks.yaml`
- `Canon/Network/devices.yaml`
- `Canon/Network/services.yaml`
- `Canon/Network/bindings.yaml`
- `Canon/Network/policy.yaml`

Updated:

- `Canon/README.md`

## Commit receipts

- `fa526df45f85f0fc950a22d24d2f1aab0feb3b51` — network canon overview
- `50aec7c0ce7ac34a31b66f0ccd23e8335ec2b05c` — VLAN/CIDR plan
- `a6e09123befac8ccc73978ed7b1e43b4ac8905f8` — fleet homes
- `5a545630c0d2b90edb8eb12ab133dd28efb838cc` — services/control addresses
- `7cf0ae504f2324f7fdd6a2e4bf353a66b87c5bad` — agent/device bindings
- `62ec239e63644a058da600ba8dcc82dc73a9ffda` — deny-first policy
- `d5d10a3e696fc50da1f6f159a89926c394325c05` — Canon index update

## Safety / publication boundary

This public repository intentionally excludes credentials, secrets, serial numbers, private overlay credentials, and public infrastructure IP addresses.

## State

`CANON_INSTALLED`

Provider state has not yet been applied. The Dream Router 7 is represented as ordered; UniFi configuration remains pending physical arrival and enrollment.
