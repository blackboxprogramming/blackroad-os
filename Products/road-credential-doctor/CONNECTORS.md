# Connector assurance model

“Supported” is not allowed to mean “a provider name appears in a list.” Connector status uses four explicit evidence levels:

| Level | Meaning |
| --- | --- |
| `CORE_VERIFIED` | The metadata-only no-lockout state machine, redaction, approval, coverage, rollback, receipts, and recovery behavior passed adversarial tests. |
| `ADAPTER_VERIFIED` | A specific provider adapter passed its contract suite and a provider sandbox or bounded integration test. |
| `HOST_MANAGED` | Authentication is owned by the connector host. Local token extraction and rotation are prohibited; health and reauthorization are the available controls. |
| `UNVERIFIED` | A lifecycle can be represented, but provider-specific behavior has not been demonstrated. It must not be enabled for unattended healing. |

The core is `CORE_VERIFIED`. No provider adapter is bundled. An adapter becomes `ADAPTER_VERIFIED` only when its connector-host implementation exercises the real provider and consumer workflow without returning secret material.

## Connector classes

| Class | Default treatment | Revocation gate |
| --- | --- | --- |
| Connector-hosted OAuth | `HOST_MANAGED`; reauthorize through the host | Host confirms the new grant and the connector probe succeeds |
| Git and infrastructure control planes | Connector-hosted short-lived federation preferred; otherwise overlapping least-privilege tokens | Every repo, runner, mirror, deployer, host, and daemon verifies through connectors |
| Commerce and finance | Critical risk; provider-id rotation with independent authorization | Read-only and bounded-write probes succeed; webhook signing paths also verify |
| Compute, edge, DNS, and tunnels | Critical risk; canary by zone/project/device | Existing route health and replacement-authenticated change probe succeed |
| Data stores | Dual identity or alternate password | New sessions, old session continuity, replication, backup, and restore probes succeed |
| SSH and WireGuard | Overlapping keys | A fresh independent session succeeds before the old public key is removed |
| Webhook signing | Dual validation window | Old and new signatures are accepted during cutover; sender and receiver both prove new |
| TLS certificates | Certificate overlap | Served chain, hostname, expiry, and independent client validation succeed |
| Signing/encryption keys | Versioned key ring and migration | Recovery/re-encryption proof succeeds before retirement; automatic destructive cleanup is prohibited |

## BlackRoad rollout order

1. **CarKeys** — connector-held credential identities, scopes, ownership, risk, and authorization actions.
2. **RoadChain** — connector-side append-only receipts, health history, pending revocation state, and evidence export.
3. **RoundAbout / Detour** — route and dependency discovery so every external and self-hosted consumer is registered.
4. **GitHub / Forgejo / Gitea** — replace broad PAT usage with app or short-lived identities; cover actions, mirrors, local daemons, and deployers.
5. **Cloudflare / DigitalOcean / Tailscale** — canary edge, compute, DNS, tunnel, and fleet paths.
6. **Stripe and finance connectors** — isolate live/test identities and require critical approval plus transaction-safe probes.
7. **Application and collaboration connectors** — OpenAI, Hugging Face, Slack, Resend, PostHog, Supabase, Netlify, Vercel, Railway, package registries, and remaining adapters.

## Required adapter evidence

Before setting `auto_heal: true`, retain all of the following from the connector implementation:

- provider documentation and API/version identity;
- least-privilege create, validate, and revoke permissions;
- stable provider IDs for both old and new credentials;
- idempotency under the same `ROAD_ROTATION_ID`;
- a successful canary test;
- simulated create, validate, update, verify, store, restore, revoke, timeout, and crash failures;
- proof that connector output contains no credential material and unknown fields fail closed;
- a bounded recovery procedure for `pending_revocation`;
- owner, risk, expiry, and rollback responsibility.

High and critical connectors never qualify for unattended healing. Their connector authorization action is the CarKeys/Portia boundary.

## Placement rule

Provider adapters, secret-manager clients, rotation schedulers, and revocation workers run in the connector trust domain. They do not run on laptops, phones, Raspberry Pis, application servers, or developer workstations. Devices may scan read-only content and submit metadata-only requests; they never receive the old or replacement credential.
