#!/usr/bin/env python3
"""Unified ingest emitter — select path via --mode or EMIT_MODE.

Modes (ADR-0001 / ADR-0002 / ADR-0003):
  dataway  — direct DataWay write (v0.0.1); default value 1.0
  datakit  — via local/container DataKit metrics (v0.0.2); default value 2.0
  ddtrace  — DDTrace span + StatsD metric → DataKit (v0.0.3); default value 3.0
  otel     — OTLP span + OTLP metric → DataKit (v0.0.4); default value 4.0

Defaults live in scripts/lab_path_values.py (chart separation; tag path= is identity).

Repeat / spacing (all modes):
  --count N       emit N times (default 1; env EMIT_COUNT overrides if set)
  --interval SEC  sleep between repeats (default 5; env EMIT_INTERVAL_SEC if set)
  Skips sleep on --dry-run and after the last shot.

Usage:
  set -a && source .env && set +a
  python3 scripts/emit.py --mode dataway
  python3 scripts/emit.py --mode otel --count 2
  EMIT_MODE=otel EMIT_COUNT=2 python3 scripts/emit.py
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent

MODE_SCRIPTS = {
    "dataway": "emit_dataway.py",
    "datakit": "emit_datakit.py",
    "ddtrace": "emit_ddtrace.py",
    "otel": "emit_otel.py",
}

# Lab convention: Metrics Explorer often buckets by second; sub-second repeats
# collapse visually. Five seconds separates shots.
DEFAULT_INTERVAL_SEC = 5.0
DEFAULT_COUNT = 1


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
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_COUNT,
        help=f"How many emit shots (default: {DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_INTERVAL_SEC,
        metavar="SEC",
        help=(
            "Seconds between shots when count>1 "
            f"(default: {DEFAULT_INTERVAL_SEC:g})"
        ),
    )
    argv_list = list(argv) if argv is not None else sys.argv[1:]
    args, passthrough = parser.parse_known_args(argv_list)

    mode = (args.mode or os.environ.get("EMIT_MODE") or "dataway").strip().lower()
    if mode not in MODE_SCRIPTS:
        print(
            f"emit_mode=INVALID value={mode!r} "
            f"allowed={','.join(sorted(MODE_SCRIPTS))}",
            file=sys.stderr,
        )
        return 2

    # CLI > env > argparse default. Env only when the CLI flag is absent.
    # Missing env → keep default. Bad env string → int()/float() raise.
    count = args.count
    interval = args.interval
    if "EMIT_COUNT" in os.environ and "--count" not in argv_list:
        count = int(os.environ["EMIT_COUNT"].strip())
    if "EMIT_INTERVAL_SEC" in os.environ and "--interval" not in argv_list:
        interval = float(os.environ["EMIT_INTERVAL_SEC"].strip())

    if count < 1:
        print("emit_count must be >= 1", file=sys.stderr)
        return 2
    if interval < 0:
        print("emit_interval_sec must be >= 0", file=sys.stderr)
        return 2

    dry_run = "--dry-run" in passthrough
    script = SCRIPTS / MODE_SCRIPTS[mode]
    print(f"emit_mode={mode}", flush=True)
    print(f"emit_script={script.name}", flush=True)
    print(f"emit_count={count}", flush=True)
    print(f"emit_interval_sec={interval}", flush=True)

    cmd = [sys.executable, str(script), *passthrough]
    last_code = 0
    for i in range(1, count + 1):
        print(f"emit_shot={i}/{count}", flush=True)
        last_code = subprocess.call(cmd)
        if last_code != 0:
            return last_code
        if i < count and not dry_run and interval > 0:
            print(f"emit_sleep_sec={interval}", flush=True)
            time.sleep(interval)

    return last_code


if __name__ == "__main__":
    raise SystemExit(main())
