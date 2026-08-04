#!/usr/bin/env python3
"""DDTrace → DataKit path — NOT-IMPLEMENTED until release v0.0.3.

Planned: small instrumented stub sending Datadog-trace protocol to DataKit
ddtrace receiver (:9529). Not Datadog Agent → DataKit. Docker Compose preferred.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("emit_mode=ddtrace")
    print("status=NOT-IMPLEMENTED")
    print("target_release=v0.0.3")
    print(
        "hint: requires v0.0.2 DataKit with ddtrace enabled; "
        "see docs/ADR/0002-release-tags-and-emit-mode.md"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
