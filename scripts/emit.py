#!/usr/bin/env python3
"""Unified ingest emitter — select path via --mode or EMIT_MODE.

Modes (ADR-0001 / ADR-0002):
  dataway  — direct DataWay write (implemented at v0.0.1)
  datakit  — via local/container DataKit (target v0.0.2)
  ddtrace  — DDTrace protocol → DataKit (target v0.0.3)

Usage:
  set -a && source .env && set +a
  python3 scripts/emit.py --mode dataway
  EMIT_MODE=dataway python3 scripts/emit.py --dry-run
  python3 scripts/emit.py --mode datakit   # NOT-IMPLEMENTED until v0.0.2
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

MODE_SCRIPTS = {
    "dataway": "emit_dataway.py",
    "datakit": "emit_datakit.py",
    "ddtrace": "emit_ddtrace.py",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit synthetic lab telemetry via a selectable ingest path.",
    )
    parser.add_argument(
        "--mode",
        choices=sorted(MODE_SCRIPTS),
        default=None,
        help="Ingest path (default: env EMIT_MODE, else dataway)",
    )
    args, passthrough = parser.parse_known_args(argv)

    mode = (args.mode or os.environ.get("EMIT_MODE") or "dataway").strip().lower()
    if mode not in MODE_SCRIPTS:
        print(
            f"emit_mode=INVALID value={mode!r} "
            f"allowed={','.join(sorted(MODE_SCRIPTS))}",
            file=sys.stderr,
        )
        return 2

    script = SCRIPTS / MODE_SCRIPTS[mode]
    print(f"emit_mode={mode}", flush=True)
    print(f"emit_script={script.name}", flush=True)
    cmd = [sys.executable, str(script), *passthrough]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
