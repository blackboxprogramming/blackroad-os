# Rotation preflight hardening

This change adds engine-level gates before connector dispatch:

- Manual and automatic rotation require at least one declared consumer.
- Rotation requires a non-empty old provider ID, including direct engine calls.
- A pending revocation blocks a new rotation of the same credential while the state lock is held. Reconcile the pending operation first.

Verification: three regression tests failed on the previous implementation; all 31 package tests pass after the fix. Tests use a simulated dispatcher, not live provider accounts.

## Deployment status and limitations

This is an orchestration library, not a deployed connector service. The example `road-connectors` dispatcher is a contract placeholder; this package does not implement or authenticate it. A catalog entry is not an installed or verified provider adapter.

Connector-only placement is a deployment requirement, not something the local subprocess runner can independently prove. An `authority: connector` response is self-reported, not a cryptographic attestation. The runner receives response bytes before rejecting invalid fields; schema rejection cannot guarantee that a malicious dispatcher never sends secret bytes. The scanner necessarily reads source material that may contain leaks.

The response runner now enforces 64 KiB while reading stdout, retaining at most one extra byte to detect overflow. It concurrently writes stdin, applies a deadline across pipe I/O and process completion, and cleans up the dispatcher's POSIX process group. Dispatchers must not daemonize or escape that process group; independent durable jobs belong on the authenticated remote connector host. Non-POSIX dispatch fails closed. This bounds captured response data, not total interpreter or child-process memory.

Duplicate JSON fields, malformed UTF-8, whitespace-padded IDs, and parser recursion failures are rejected. Exact-limit valid output is accepted; one byte over is blocked.

Crash recovery between provider creation and durable pending-revocation state still requires connector-side idempotency and a durable transaction journal. This limitation remains unresolved.

No live credentials have been rotated or revoked by this change. Production enablement requires a real authenticated connector runtime, provider-specific tests, durable recovery, and independently verified consumer coverage.
