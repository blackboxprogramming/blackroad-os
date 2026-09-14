# Durable Ramp operation recovery

Credential rotation crosses several systems that cannot share one database transaction:
the Ramp connector, provider, consumer secret stores, workloads, and the Road Credential
Doctor state file. Recovery therefore uses a write-ahead intent plus idempotent connector
actions. It does not claim distributed atomicity.

## Durable states

| Stage | Durable evidence | Safe recovery behavior |
| --- | --- | --- |
| `create_pending` | Rotation identity, old provider ID, connector ID, findings | Repeat create with the same rotation ID. |
| `created` | Distinct replacement provider ID | Revalidate the replacement. |
| `validated` | Replacement previously passed validation | Revalidate, then replay consumer updates. |
| `updating_consumers` | IDs of consumers whose update and verification completed | Revalidate and replay every consumer update and verification. |
| `activated` | Activation previously returned success | Revalidate consumers and repeat activation before queuing revocation. |
| pending revocation | Active replacement and old provider ID are committed together | Revalidate replacement and consumers, then retry old-key revocation. |

The worker records `create_pending` after healthy baselines and before calling the
creation action. It writes the complete JSON to a temporary owner-only file, fsyncs the
file, atomically replaces the state file, and fsyncs the containing directory.

Every checkpoint records identifiers and evidence metadata only:

- credential, connector, and rotation IDs;
- old and replacement provider handles;
- proven stage and verified consumer IDs;
- SHA-256 finding fingerprints;
- timestamps and a bounded internal recovery error description.

No credential value belongs in this journal.

## Idempotency contract

For one rotation ID, a Ramp adapter must provide these semantics:

- create returns the same replacement provider ID after any successful prior create;
- validate tests the specified replacement and cannot silently fall back to the old key;
- consumer update converges the named consumer on the specified replacement;
- consumer verify proves that named consumer can authenticate using the replacement;
- activate converges the connector's active pointer on the replacement;
- restore converges the active pointer on the old provider ID;
- replacement revocation resolves by rotation ID when the response containing its
  provider ID was lost;
- old revocation is safe to repeat and reports success when already revoked.

A provider lacking those semantics needs an adapter-owned idempotency table inside the
authenticated Ramp trust domain. The table should bind tenant, connector, credential,
rotation, action, target provider ID, result provider ID, completion state, and receipt
ID. The Road Credential Doctor does not implement that remote table.

## Recovery sequence

1. Acquire the exclusive state lock.
2. Validate the complete state schema and reject ambiguity.
3. Match the pending operation to exactly one configured credential and connector.
4. Reauthorize high- or critical-risk recovery through its configured action.
5. If replacement creation is not proven, repeat creation with the original rotation ID.
6. Require a non-empty replacement provider ID distinct from the old provider ID.
7. Revalidate the replacement.
8. Replay each declared consumer update and verify it immediately.
9. Repeat activation.
10. Atomically record the replacement as active and queue old-key revocation.
11. Remove the operation journal record in the same state write.
12. Revalidate replacement access and consumers before retrying revocation.
13. Retire leak fingerprints only after old-key revocation succeeds.

Failures retain the last proven checkpoint and emit a hash-chained local receipt. They
do not revoke the old credential or claim access is retained unless the replacement and
every declared consumer were freshly verified.

`road-credentials --json status` provides a read-only queue view without scanning the
repository. It omits both old and replacement provider handles and returns canonical
Routes, stages, verified consumer IDs, timestamps, counts, and receipt-chain head.

## Process-exit scenarios

| Exit point | What may have happened remotely | Next action |
| --- | --- | --- |
| Before create dispatch | Nothing | Repeat create using the recorded intent. |
| During or after create | Replacement may exist while its ID response was lost | Repeat idempotent create by rotation ID. |
| During consumer update | A consumer may already use the replacement | Replay update and verify for every consumer. |
| During activation | Active pointer may already have moved | Revalidate all consumers and repeat activation. |
| After activation checkpoint | Replacement is proven but revocation is not queued | Rebuild the pending-revocation record. |
| During revocation | Old credential may already be revoked | Revalidate access, then repeat idempotent revocation. |

## Fail-closed state validation

The state loader rejects unsupported schemas, unknown fields, missing required fields,
invalid types, blank identifiers, invalid stages, replacement IDs equal to old IDs,
duplicate queue entries, and a rotation appearing in both operation and revocation
queues. Execution also blocks when a pending entry references an unconfigured
credential.

This strictness is intentional. Operators should preserve the invalid file as incident
evidence and repair it through a reviewed migration rather than deleting or guessing at
in-flight state.

## Remaining boundary

The local journal is meaningful only when it runs on the connector worker described in
the deployment model. Installing the mutating worker on a laptop, phone, Raspberry Pi,
or application server violates the design. RoadOS and Roadies may submit, approve, and
observe Route-addressed metadata, but provider credentials and adapter idempotency stay
inside authenticated Ramps.

No local journal can prove that a remote provider durably committed an operation. That
proof must come from provider-specific queries and connector-side receipts. Production
qualification therefore requires kill-point integration tests against each real adapter,
including lost responses, repeated actions, delayed consistency, partial consumer
rollouts, and already-revoked credentials.
