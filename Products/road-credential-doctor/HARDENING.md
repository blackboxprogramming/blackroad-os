# Rotation preflight hardening

This change adds engine-level gates before connector dispatch:

- Manual and automatic rotation require at least one declared consumer.
- Rotation requires a non-empty old provider ID, including direct engine calls.
- A pending revocation blocks a new rotation of the same credential while the state lock is held. Reconcile the pending operation first.

Verification: three regression tests failed on the previous implementation; all 31 package tests pass after the fix. Tests use a simulated dispatcher, not live provider accounts.

## Deployment status and limitations

This is an orchestration library, not a deployed connector service. The example `road-connectors` dispatcher is a contract placeholder; this package does not implement or authenticate it. A catalog entry is not an installed or verified provider adapter.

Connector-only placement is a deployment requirement, not something the local subprocess runner can independently prove. An `authority: connector` response is self-reported, not a cryptographic attestation. The runner receives response bytes before rejecting invalid fields; schema rejection cannot guarantee that a malicious dispatcher never sends secret bytes. The scanner necessarily reads source material that may contain leaks.

The existing 64 KiB response check happens after subprocess output is captured, so it is not a streaming memory limit. Crash recovery between provider creation and durable pending-revocation state still requires connector-side idempotency and a durable transaction journal. These limitations remain unresolved by this preflight patch.

No live credentials have been rotated or revoked by this change. Production enablement requires a real authenticated connector runtime, provider-specific tests, durable recovery, and independently verified consumer coverage.
