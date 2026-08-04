#!/usr/bin/env python3
"""Emit one synthetic metric (and optional log) via local DataKit HTTP API.

DataKit accepts line protocol on :9529 and forwards to DataWay using its own
ENV_DATAWAY / DK_DATAWAY. Prefer Docker Compose (ADR-0002). Stdlib only.

Usage (from repo root, DataKit listening on DATAKIT_URL):
  set -a && source .env && set +a
  python3 scripts/emit_datakit.py --dry-run
  python3 scripts/emit_datakit.py
  python3 scripts/emit.py --mode datakit --also-log

Docs: docs/runbooks/datakit-emit.md
Official API: https://docs.truewatch.com/datakit/apis/
"""

from __future__ import annotations

import argparse
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

MEASUREMENT = "truewatch_lab_first_mile"
DEFAULT_TAGS = "path=datakit,service=lab-emitter,env=lab"
DEFAULT_DATAKIT_URL = "http://127.0.0.1:9529"
USER_AGENT = (
    "truewatch-lab-first-mile/0.0.2 "
    "(+https://github.com/BinHsu/truewatch-lab-first-mile)"
)


def resolve_datakit_base() -> str:
    base = (os.environ.get("DATAKIT_URL") or DEFAULT_DATAKIT_URL).rstrip("/")
    parts = urllib.parse.urlsplit(base)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        raise SystemExit(
            f"DATAKIT_URL must be http(s)://host[:port], got {base!r}. "
            "See docs/runbooks/datakit-emit.md."
        )
    return base


def write_url(category: str) -> str:
    return f"{resolve_datakit_base()}/v1/write/{category}"


def line_protocol_metric(value: float, ts_ns: int) -> str:
    return f"{MEASUREMENT},{DEFAULT_TAGS} ping={value} {ts_ns}"


def line_protocol_log(message: str, ts_ns: int) -> str:
    safe = message.replace(" ", "\\ ").replace(",", "\\,")
    return (
        f"{MEASUREMENT},{DEFAULT_TAGS},status=info "
        f'message="{safe}" {ts_ns}'
    )


def post_lp(url: str, body: str, timeout: float = 30.0) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        method="POST",
        headers={
            "Content-Type": "text/plain; charset=utf-8",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            return resp.getcode() or 0, raw
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return e.code, raw
    except urllib.error.URLError as e:
        raise SystemExit(
            f"Cannot reach DataKit at {url}: {e.reason}. "
            "Start Compose `datakit` or a host DataKit on :9529; "
            "see docs/runbooks/datakit-emit.md."
        ) from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print URL + payload; do not POST",
    )
    parser.add_argument(
        "--also-log",
        action="store_true",
        help="Also POST one synthetic logging point",
    )
    parser.add_argument(
        "--value",
        type=float,
        default=1.0,
        help="Metric field ping= (default 1.0)",
    )
    args = parser.parse_args()

    ts_ns = time.time_ns()
    metric_body = line_protocol_metric(args.value, ts_ns)
    metric_url = write_url("metric")

    print("emit_mode=datakit")
    print(f"datakit_url={resolve_datakit_base()}")
    print(f"measurement={MEASUREMENT}")
    print(f"metric_url={metric_url}")
    print(f"metric_body={metric_body}")

    if args.dry_run:
        if args.also_log:
            log_url = write_url("logging")
            log_body = line_protocol_log("lab datakit emit ok", ts_ns)
            print(f"logging_url={log_url}")
            print(f"logging_body={log_body}")
        print("dry_run=1 (no POST)")
        return 0

    code, raw = post_lp(metric_url, metric_body)
    print(f"metric_http_status={code}")
    if raw.strip():
        print(f"metric_response_len={len(raw)}")
    if code < 200 or code >= 300:
        print("metric_post=FAIL", file=sys.stderr)
        return 1
    print("metric_post=OK")

    if args.also_log:
        log_url = write_url("logging")
        log_body = line_protocol_log("lab datakit emit ok", ts_ns)
        print(f"logging_url={log_url}")
        code2, raw2 = post_lp(log_url, log_body)
        print(f"logging_http_status={code2}")
        if raw2.strip():
            print(f"logging_response_len={len(raw2)}")
        if code2 < 200 or code2 >= 300:
            print("logging_post=FAIL", file=sys.stderr)
            return 1
        print("logging_post=OK")

    print(
        "next: in TrueWatch console open Metrics / Explorer; "
        f"filter measurement={MEASUREMENT} or tag path=datakit "
        "(allow a short ingest delay)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
