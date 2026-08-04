#!/usr/bin/env python3
"""OpenTelemetry → DataKit path — NOT-IMPLEMENTED until release v0.0.4.

Planned (ADR-0003): emit BOTH
  1) a synthetic OTLP metric (/otel/v1/metrics or gRPC), and
  2) a synthetic OTLP span (/otel/v1/traces or gRPC :4317).
Prefer Compose with opentelemetry input (traces + metrics) enabled.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("emit_mode=otel")
    print("status=NOT-IMPLEMENTED")
    print("target_release=v0.0.4")
    print("planned_signals=metric+span")
    print(
        "hint: implement after v0.0.3; enable DataKit opentelemetry traces+metrics; "
        "see docs/ADR/0003-otel-trace-path.md and docs/observability-glossary.md"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
