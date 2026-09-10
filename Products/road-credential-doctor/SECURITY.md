# Security model

## Trust boundary

Credential custody and every mutating lifecycle action belong to authenticated connectors. Endpoint devices are not credential vaults, provider adapters, rotation workers, or revocation authorities.

The doctor has two roles:

1. detection and consumer-reference inventory;
2. metadata-only orchestration through one connector dispatcher.

The dispatcher receives no credential bytes. It receives opaque provider IDs, action names, scope identifiers, the rotation ID, and the approved risk. Provider API calls, credential generation, validation, storage, distribution, rollback, and revocation occur beyond that boundary in the connector runtime.

Run continuous execution only on the connector worker. A device may perform a read-only scan or submit a reviewed rotation request, but it must not host lifecycle adapters.

## Connector response boundary

The dispatcher response schema is deliberately tiny: `ok`, `execution_id`, `authority`, `secret_material`, and optional `provider_id`. The doctor rejects every unknown field. It also requires:

- `authority` equal to `connector`;
- `secret_material` equal to `false`;
- a non-empty connector execution ID;
- a non-empty new provider ID after creation;
- a response no larger than 64 KiB.

Dispatcher stderr is discarded. Connector response text is parsed in memory and never written into receipts. Receipts retain only the connector execution ID and phase outcome.

The connector client process receives a minimal environment allowlist. Ambient token, password, API-key, and credential variables are not inherited.

## No-lockout invariant

The connector may revoke the old provider ID only after all of these facts are true:

1. Every declared consumer had a healthy connector-side baseline.
2. A distinct replacement provider ID exists.
3. The connector validates the replacement.
4. Each consumer is updated and independently verified as a canary.
5. The connector activates its replacement version.
6. Pending revocation state is durably recorded.

Failures before revocation request connector-side rollback. A failed rollback is reported without claiming retained access. A failed revocation leaves a provider-ID-only pending record for safe connector retry.

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
