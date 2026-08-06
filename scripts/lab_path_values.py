"""Lab default metric values per ingest path (EMIT_MODE).

Distinct y-values so a multi-series dashboard does not stack four points on one
pixel when paths are emitted close together. Tag ``path`` remains the identity.

Monitor fault threshold is ``>= 900``; these defaults stay quiet.

Override any time with ``--value`` / fault inject ``--value 900``.
"""

from __future__ import annotations

# Keep in sync with README "Compare all four" / emit-dashboard-demo.sh.
DEFAULT_VALUE_BY_PATH: dict[str, float] = {
    "dataway": 1.0,
    "datakit": 2.0,
    "ddtrace": 3.0,
    "otel": 4.0,
}


def default_value(path: str) -> float:
    try:
        return DEFAULT_VALUE_BY_PATH[path]
    except KeyError as e:
        raise KeyError(
            f"unknown lab path {path!r}; expected one of "
            f"{sorted(DEFAULT_VALUE_BY_PATH)}"
        ) from e
