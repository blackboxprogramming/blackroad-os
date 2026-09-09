# Road Credential Doctor

Road Credential Doctor detects leaked credential material and asks a trusted connector runtime to perform a no-lockout rotation:

`baseline every consumer → create → validate → update+verify each canary → activate → revoke old`

Version 0.3 has a hard execution-plane boundary: provider credentials, replacement values, secret-manager writes, consumer updates, and revocation all stay inside connectors. The doctor sends only credential IDs, provider IDs, action names, approvals, and rotation IDs. It has no API that accepts secret bytes.

The practical command remains:

```bash
road-credentials heal --all --execute --ack-keep-access
```

Without `--execute`, it produces a dry plan only.

## Implemented controls and deployment requirements

- Rotation requests use provider IDs, not credential values. The scanner still reads potentially leaked source material.
- Exactly one configured connector dispatcher is allowed to perform lifecycle actions.
- Dispatcher requests contain metadata and opaque provider handles only.
- Connector responses must attest `authority: connector` and `secret_material: false`.
- Unknown connector response fields are rejected without being persisted. This cannot prevent a malicious dispatcher from sending bytes to the process in the first place.
- The old provider ID is revoked only after connector-side validation, consumer canaries, and activation succeed.
- Failed rotations request connector-side rollback; failed revocation is durably queued by provider ID.
- Unknown secret names, duplicate ownership, and undeclared consumer paths block live rotation.
- High and critical credentials require explicit approval and a connector authorization action.
- Receipts are hash-chained and contain connector execution IDs, never credential values.
- Git history is detected but never rewritten automatically.

The local scanner may inspect a checked-out repository, but it is detection-only. It cannot mutate a provider, secret store, deployment, or consumer directly. Production scheduling belongs on the connector worker, not a laptop, phone, Raspberry Pi, or application host.

## Install

Python 3.11 or later is the only package dependency.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
cp examples/credentials.example.json credentials.json
```

Configure `connector_runtime.dispatch` with the connector host's approved metadata-only client, then run:

```bash
road-credentials doctor --repair
road-credentials inventory
road-credentials scan --git-history
road-credentials heal --all
road-credentials heal --all --execute --ack-keep-access --approve-risk critical
```

For connector-worker scheduling, adapt `services/road-credential-doctor.service.example`. Do not install an executing watcher on an endpoint device.

## Connector runtime contract

Version 0.3 requires `schema_version: 3` and refuses older registries. One connector dispatcher is declared at the top level:

```json
{
  "connector_runtime": {
    "id": "blackroad-connectors-production",
    "transport": "connector_rpc",
    "dispatch": ["road-connectors", "invoke", "--json-stdin"]
  }
}
```

The dispatcher receives one JSON request on stdin. It contains:

- connector runtime, connector, credential, rotation, and consumer IDs;
- connector action and transaction phase;
- old and new non-secret provider IDs;
- configured risk and approved risk.

It must execute the named action inside the connector trust domain and return only:

```json
{
  "ok": true,
  "execution_id": "connector-receipt-reference",
  "authority": "connector",
  "secret_material": false,
  "provider_id": "new-provider-id-only-for-create"
}
```

`provider_id` is optional except for creation. Output is capped at 64 KiB during streaming reads on POSIX workers. Duplicate fields, unknown fields, invalid declarations, malformed JSON or UTF-8, timeout, nonzero exit, missing execution IDs, missing new provider IDs, and returned secret fields fail closed. The authority declaration is self-reported, not cryptographic proof. See [HARDENING.md](HARDENING.md) for deployment status and unresolved limitations.

Connector actions are opaque names rather than commands:

- lifecycle: `authorize_action`, `create_action`, `validate_action`, `activate_action`, `restore_action`, `revoke_old_action`, `revoke_new_action`;
- consumer: `update_action`, `verify_action`, `rollback_action`.

The dispatcher itself is a connector transport client, not a provider adapter. It must never implement provider credential logic or secret custody on the calling endpoint.

## Credential and consumer inventory

Each credential declares:

- `connector`: one user-managed connector ID from `road-credentials connectors`;
- `risk`: `low`, `medium`, `high`, or `critical`;
- `provider_id`: the current provider's non-secret credential identifier;
- `detect`: scanner kinds, canonical secret names, path scopes, and optional SHA-256 fingerprints;
- `lifecycle`: connector action names;
- `consumers`: owned paths plus connector update, verification, and rollback actions;
- `auto_heal`: eligibility for unattended low/medium-risk connector rotation.

`road-credentials inventory` detects secret-like references across shell, GitHub Actions, JavaScript, Python, Go, Rust, Ruby, environment definitions, and orchestrator configuration. Every reference must have exactly one credential owner and at least one declared consumer path.

## Connector coverage

```bash
road-credentials --json connectors
```

The catalog classifies 69 connector-hosted integrations and 37 user-managed credential families across nine rotation strategies. Connector-hosted OAuth grants remain host-owned and cannot be extracted. User-managed credentials may rotate only through a connector adapter that has passed its provider contract and bounded integration tests.

See [CONNECTORS.md](CONNECTORS.md) for assurance levels and [SECURITY.md](SECURITY.md) for the trust boundary.

## Commands and exit codes

```text
road-credentials scan [--git-history]
road-credentials inventory
road-credentials connectors
road-credentials doctor [--git-history] [--repair]
road-credentials heal (--all | --credential ID) [--force] [--execute --ack-keep-access] [--approve-risk LEVEL]
road-credentials reconcile --execute --ack-keep-access [--approve-risk LEVEL]
road-credentials watch [--execute --ack-keep-access] [--interval 300]
```

| Exit | Meaning |
| --- | --- |
| `0` | Healthy or completed |
| `10` | Active findings or dry-run work remains |
| `20` | Configuration, mapping, connector, or safety gate blocked execution |
| `30` | Connector rotation or pending revocation needs intervention |
