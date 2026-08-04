#!/usr/bin/env python3
"""Emit one synthetic metric (and optional log) to TrueWatch via DataWay.

Reads DATAWAY_URL + TRUEWATCH_WORKSPACE_TOKEN (or DK_DATAWAY) from the
environment. Never prints the token. Stdlib only.

Usage (from repo root):
  set -a && source .env && set +a
  python3 scripts/emit_dataway.py
  python3 scripts/emit_dataway.py --also-log
  python3 scripts/emit_dataway.py --dry-run
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
DEFAULT_TAGS = "path=dataway,service=lab-emitter,env=lab"
# id1-openway sits behind Cloudflare Browser Integrity Check; default
# Python-urllib User-Agent returns HTTP 403 / CF error 1010. Use a lab UA.
USER_AGENT = (
    "truewatch-lab-first-mile/0.0.1 "
    "(+https://github.com/BinHsu/truewatch-lab-first-mile)"
)


def _redact_url(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    if not parts.query:
        return url
    pairs = urllib.parse.parse_qsl(parts.query, keep_blank_values=True)
    redacted = [("token", "***") if k == "token" else (k, v) for k, v in pairs]
    # Keep *** literal (urlencode would turn * into %2A).
    new_query = "&".join(
        f"{urllib.parse.quote(k, safe='')}={v if v == '***' else urllib.parse.quote(v, safe='')}"
        for k, v in redacted
    )
    return urllib.parse.urlunsplit(
        (parts.scheme, parts.netloc, parts.path, new_query, parts.fragment)
    )


def resolve_write_url(category: str) -> str:
    """Build https://…/v1/write/<category>?token=… without echoing secrets."""
    dataway = (os.environ.get("DATAWAY_URL") or "").rstrip("/")
    token = os.environ.get("TRUEWATCH_WORKSPACE_TOKEN") or ""
    dk = os.environ.get("DK_DATAWAY") or ""

    if dataway and token:
        return f"{dataway}/v1/write/{category}?token={urllib.parse.quote(token, safe='')}"

    if dk:
        # DK_DATAWAY is https://host?token=… — insert /v1/write/<category>
        parts = urllib.parse.urlsplit(dk)
        if not parts.scheme or not parts.netloc:
            raise SystemExit("DK_DATAWAY is not a valid URL")
        path = f"/v1/write/{category}"
        return urllib.parse.urlunsplit(
            (parts.scheme, parts.netloc, path, parts.query, parts.fragment)
        )

    raise SystemExit(
        "Missing ingest env: set DATAWAY_URL + TRUEWATCH_WORKSPACE_TOKEN "
        "(or DK_DATAWAY). See docs/runbooks/owl-cli-credentials.md §5."
    )


def line_protocol_metric(value: float, ts_ns: int) -> str:
    # measurement,tags fields timestamp
    return f"{MEASUREMENT},{DEFAULT_TAGS} ping={value} {ts_ns}"


def line_protocol_log(message: str, ts_ns: int) -> str:
    # logging points commonly use status/message-style fields; keep synthetic & short
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print redacted URL + payload; do not POST",
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
    metric_url = resolve_write_url("metric")

    print(f"measurement={MEASUREMENT}")
    print(f"metric_url={_redact_url(metric_url)}")
    print(f"metric_body={metric_body}")

    if args.dry_run:
        if args.also_log:
            log_url = resolve_write_url("logging")
            log_body = line_protocol_log("lab dataway emit ok", ts_ns)
            print(f"logging_url={_redact_url(log_url)}")
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
        log_url = resolve_write_url("logging")
        log_body = line_protocol_log("lab dataway emit ok", ts_ns)
        print(f"logging_url={_redact_url(log_url)}")
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
        f"filter measurement={MEASUREMENT} or tag path=dataway "
        "(allow a short ingest delay)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
