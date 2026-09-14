from __future__ import annotations

from urllib.parse import quote


def _segment(value: str, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty Route segment")
    # RFC 3986 leaves dots unescaped, but a literal `.` or `..` path segment can
    # be normalized by intermediaries. Encode dots so identifiers stay data.
    return quote(value, safe="").replace(".", "%2E")


def rotation_route(
    *,
    runtime_id: str,
    connector_id: str,
    credential_id: str,
    rotation_id: str,
    consumer_id: str | None = None,
) -> str:
    """Return the canonical metadata-only Route for one Ramp operation."""
    route = (
        f"road://ramps/{_segment(runtime_id, 'runtime_id')}"
        f"/{_segment(connector_id, 'connector_id')}"
        f"/credentials/{_segment(credential_id, 'credential_id')}"
        f"/rotations/{_segment(rotation_id, 'rotation_id')}"
    )
    if consumer_id is not None:
        route += f"/consumers/{_segment(consumer_id, 'consumer_id')}"
    return route
