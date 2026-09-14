# RoadOS credential Routes

Road Credential Doctor maps the current BlackRoad canon onto a narrow security boundary:

| Canon name | Responsibility here |
| --- | --- |
| RoadOS | Presents or submits reviewed credential-health work. It does not hold provider credentials. |
| Roadies | Coordinate requests within granted risk and approval limits. They do not receive credential values. |
| Roadie | May orchestrate eligible Roadies, approvals, and recovery while preserving the same boundary. |
| Road | Expresses intent and policy; this Python package is not claimed to be implemented in Road. |
| Routes | Give each metadata-only rotation or consumer operation one deterministic address. |
| Ramps | External provider connections whose connector runtimes perform every mutating action. |

## Route shape

Each connector request schema 2 contains one Route:

```text
road://ramps/{runtime}/{connector}/credentials/{credential}/rotations/{rotation}
road://ramps/{runtime}/{connector}/credentials/{credential}/rotations/{rotation}/consumers/{consumer}
```

Every identifier is percent-encoded as a single path segment. Dots are encoded too,
so `.` and `..` cannot be interpreted as path traversal by an intermediary. The Route
contains identifiers only. It must never contain a key, token, password, or other
credential value.

The Route is an address and correlation key, not authorization. A connector runtime
must authenticate its caller, enforce CarKeys approval and provider scope, validate
the request fields independently, and return a non-secret execution receipt ID.

## Execution boundary

RoadOS and Roadies may discover, plan, approve, or observe work. Creation, validation,
consumer mutation, activation, rollback, and revocation remain on the authenticated
Ramp connector host. An endpoint device must not become a provider adapter merely
because it can parse a Route.
