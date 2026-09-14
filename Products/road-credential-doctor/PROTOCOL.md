# Ramp connector request protocol

Road Credential Doctor request schema 2 is a closed, metadata-only protocol. The
dispatcher validates it before creating a connector client process. Invalid requests
return an internal protocol failure and cross no process boundary.

## Exact request fields

| Field | Type | Rule |
| --- | --- | --- |
| `schema_version` | integer | Exactly `2`; booleans and strings are rejected. |
| `route` | string | Must exactly equal the canonical Route derived from the identifiers. |
| `connector_runtime_id` | string | Must match the separately configured runtime identity. |
| `connector` | string | Trimmed, non-empty, at most 1,024 characters. |
| `credential_id` | string | Trimmed, non-empty, at most 1,024 characters. |
| `rotation_id` | string | Trimmed, non-empty, at most 1,024 characters at the protocol boundary. |
| `phase` | string | One value from the fixed lifecycle phase allowlist. |
| `action` | string | A configured opaque action name, at most 256 characters. |
| `risk` | string | `low`, `medium`, `high`, or `critical`. |
| `approved_risk` | string | Same vocabulary and at least the requested risk. |
| `old_provider_id` | string | Required opaque provider handle; never a credential value. |
| `new_provider_id` | string or null | Required only after replacement creation is proven. |
| `consumer_id` | string or null | Required only for a consumer-specific phase. |

Every field is required, including nullable fields. Unknown and missing fields fail
closed. This prevents a caller from adding an undocumented `token`, command, URL,
environment, payload, or provider-credential field.

## Phase rules

| Phase | Consumer | Replacement provider ID |
| --- | --- | --- |
| `authorize_rotation` | forbidden | forbidden |
| `baseline_consumer` | required | forbidden |
| `create_new` | forbidden | forbidden |
| `validate_new` | forbidden | required |
| `update_consumer` | required | required |
| `verify_consumer` | required | required |
| `activate_connector_version` | forbidden | required |
| `rollback_consumer` | required | required |
| `restore_connector_active_version` | forbidden | required |
| `revoke_unused_replacement` | forbidden | optional for lost create responses |
| `revoke_old` | forbidden | required |
| `authorize_revocation_retry` | forbidden | forbidden |
| `retry_revoke_old` | forbidden | required |
| `authorize_operation_recovery` | forbidden | optional |
| `recover_create_new` | forbidden | forbidden |
| `recover_validate_new` | forbidden | required |
| `recover_update_consumer` | required | required |
| `recover_verify_consumer` | required | required |
| `recover_activate_connector_version` | forbidden | required |

The replacement handle must differ from the old provider handle whenever present.
Lifecycle actions are names, not executable command fragments. Their syntax is limited
to alphanumerics followed by alphanumerics, dot, underscore, colon, slash, or hyphen.

## Route binding

The protocol reconstructs the expected Route from runtime, connector, credential,
rotation, and optional consumer IDs. Byte-for-byte mismatch is rejected. A caller
therefore cannot submit one set of identifiers while addressing another Route.

Route binding is not identity proof. The production transport must authenticate the
workload and bind that authenticated identity to the configured runtime, tenant,
provider, allowed actions, and CarKeys approval. The subprocess placeholder in this
package does not provide that proof.

## Request size

Identifiers are individually capped at 1,024 characters and action names at 256.
The Route is deterministically derived from those bounded identifiers. This places an
implicit small bound on serialized requests before pipe I/O begins. Arbitrary caller
payloads and extensions are not supported.

## Response boundary

The response is also closed and contains only:

- `ok` as a JSON boolean;
- `execution_id` as a trimmed non-empty string of at most 1,024 characters;
- `authority` exactly equal to `connector`;
- `secret_material` exactly equal to `false`;
- optional `provider_id` as a trimmed non-empty string of at most 1,024 characters.

Unknown or duplicate fields, malformed JSON or UTF-8, excessive nesting, nonzero exit,
timeout, and output beyond 64 KiB fail closed. Stderr is discarded and response bytes
are never copied into receipts.

Local receipt verification separately rejects symlinks, non-regular files, files over
16 MiB, duplicate keys, malformed encoding or JSON, and broken hashes or chain links.

The `authority` and `secret_material` values remain self-assertions until an
authenticated connector transport independently proves the peer. Likewise, a malicious
adapter could place credential material in an allowed opaque identifier field. Schema
validation limits structure and size; it cannot prove the semantic meaning of a string.

## Environment and process boundary

The connector client receives only a small environment allowlist plus the configured
runtime and transport markers. Ambient credential variables are omitted. On POSIX, the
runner streams input and bounded output concurrently, applies one deadline to I/O and
completion, and kills the dispatcher's process group during cleanup.

Dispatchers must not daemonize or escape their process group. Long-running durable work
belongs behind the authenticated Ramp endpoint, keyed by rotation ID, rather than in a
child process on the caller.
