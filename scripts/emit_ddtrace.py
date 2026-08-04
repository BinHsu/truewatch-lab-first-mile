#!/usr/bin/env python3
"""DDTrace → DataKit path — NOT-IMPLEMENTED until release v0.0.3.

Planned (ADR-0003): emit BOTH
  1) a synthetic DogStatsD/StatsD metric to DataKit (:8125 typical), and
  2) a synthetic DDTrace span to DataKit ddtrace receiver (:9529).
Not Datadog Agent → DataKit. Docker Compose preferred.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("emit_mode=ddtrace")
    print("status=NOT-IMPLEMENTED")
    print("target_release=v0.0.3")
    print("planned_signals=metric+span")
    print(
        "hint: enable DataKit ddtrace + statsd inputs; "
        "see docs/ADR/0003-otel-trace-path.md"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
