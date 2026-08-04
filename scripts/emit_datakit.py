#!/usr/bin/env python3
"""DataKit ingest path — NOT-IMPLEMENTED until release v0.0.2.

Planned: POST synthetic points to local DataKit HTTP API (default :9529),
with DataKit forwarding to DataWay. Prefer Docker Compose for a clean host.
"""

from __future__ import annotations

import sys


def main() -> int:
    print("emit_mode=datakit")
    print("status=NOT-IMPLEMENTED")
    print("target_release=v0.0.2")
    print(
        "hint: use EMIT_MODE=dataway (v0.0.1) until DataKit compose lands; "
        "see docs/ADR/0002-release-tags-and-emit-mode.md"
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
