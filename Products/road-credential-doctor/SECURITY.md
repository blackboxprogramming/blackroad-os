# Security model

## Trust boundary

Credential custody and every mutating lifecycle action belong to authenticated connectors. Endpoint devices are not credential vaults, provider adapters, rotation workers, or revocation authorities.

The doctor has two roles:

1. detection and consumer-reference inventory;
2. metadata-only orchestration through one connector dispatcher.

The dispatcher receives no credential bytes. It receives opaque provider IDs, action names, scope identifiers, the rotation ID, and the approved risk. Provider API calls, credential generation, validation, storage, distribution, rollback, and revocation occur beyond that boundary in the connector runtime.

Request schema 2 also carries a deterministic `road://ramps/...` Route. Route
segments are percent-encoded identifiers and contain no credential values. The Route
is not an authority token: the connector must authenticate and authorize every request.

Run continuous execution only on the connector worker. A device may perform a read-only scan or submit a reviewed rotation request, but it must not host lifecycle adapters.

## Configuration and request boundary

Configuration schema 3 rejects duplicate JSON keys, unknown fields at every nesting
level, ambiguous booleans, invalid sizes and types, invalid UTF-8, and files over 4 MiB.
The dispatcher independently validates the exact request schema, phase-specific fields,
risk approval, bounded identifiers, and canonical Route before starting a process.

Opaque provider handles are structurally allowed and semantically expected to be
non-secret. The package cannot prove that a malicious or incorrectly configured adapter
has not mislabeled credential material as an identifier.

## Connector response boundary

The dispatcher response schema is deliberately tiny: `ok`, `execution_id`, `authority`, `secret_material`, and optional `provider_id`. The doctor rejects every unknown field. It also requires:

- `authority` equal to `connector`;
- `secret_material` equal to `false`;
- a non-empty connector execution ID;
- a non-empty new provider ID after creation;
- a response no larger than 64 KiB.

Dispatcher stderr is discarded. Connector response text is parsed in memory and never written into receipts. Receipts retain only the connector execution ID and phase outcome.

Receipt verification opens regular files without following symlinks, caps each file at
16 MiB, rejects duplicate keys, invalid UTF-8, malformed or excessively nested JSON,
and non-object roots, then verifies both the receipt hash and chain link. Receipt
filenames accept only bounded safe rotation IDs and UTC timestamps.

The connector client process receives a minimal environment allowlist. Ambient token, password, API-key, and credential variables are not inherited.

## No-lockout invariant

The connector may revoke the old provider ID only after all of these facts are true:

1. A metadata-only operation intent was durably recorded before creation.
2. Every declared consumer had a healthy connector-side baseline.
3. A distinct replacement provider ID exists.
4. The connector validates the replacement.
5. Each consumer is updated and independently verified as a canary.
6. The connector activates its replacement version.
7. Pending revocation state is durably recorded.

Failures before revocation request connector-side rollback. A failed rollback is reported without claiming retained access. A failed revocation leaves a provider-ID-only pending record for safe connector retry.

An unhandled process exit leaves `pending_operations` on the connector worker. A
reviewed reconciliation reuses the same rotation ID, replays idempotent actions,
and checkpoints forward. Recovery never infers success from a recorded attempt.

## Connector implementation rules

- Keep provider credentials inside the connector's secret manager or provider-native vault.
- Never return, log, or embed credential material in an execution response.
- Resolve provider IDs to secrets only inside the connector trust domain.
- Authenticate the dispatcher with workload identity, connector-host OAuth, or mutually authenticated transport; do not use a device-resident long-lived API key.
- Make create, update, activate, rollback, and revoke idempotent for the same rotation ID.
- Scope connector control identities to one provider, tenant, and lifecycle where possible.
- Verify real access paths rather than checking only that a secret record exists.
- Store connector receipts independently and expose only their non-secret execution IDs.
- Require CarKeys/Portia authorization for high and critical actions.
- Never enable unattended rotation for high or critical credentials.

## What the tool does not claim

- A provider name in the catalog does not make its adapter verified.
- Local repository scans cannot find every remote consumer; register remote paths explicitly.
- Scanner signatures cannot identify every custom credential format.
- Revocation neutralizes a leaked value but does not erase Git objects, forks, logs, caches, backups, chat history, or third-party indexes.
- A connector attestation is only as trustworthy as the connector host, dispatcher authentication, and provider adapter implementation.
- The local non-secret state and receipt mirror are not substitutes for connector-side source-of-truth receipts.

## Emergency containment

Active exploitation can justify immediate provider-side revocation before consumer migration. That intentionally breaks the no-lockout sequence. Perform it through the connector incident workflow, isolate affected systems, restore access with a clean connector-held credential, and preserve incident evidence.
