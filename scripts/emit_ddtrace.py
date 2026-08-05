#!/usr/bin/env python3
"""Emit StatsD metric + DDTrace span to local DataKit (v0.0.3).

Dual signal (ADR-0003):
  1) DogStatsD/StatsD UDP → DataKit :8125
  2) DDTrace agent msgpack → DataKit :9529/v0.4/traces

Prefer Compose emit image (pinned msgpack). Host needs:
  pip install -r requirements-emitter.txt

Docs: docs/runbooks/ddtrace-emit.md
"""

from __future__ import annotations

import argparse
import os
import secrets
import socket
import sys
import time
import urllib.error
import urllib.request

try:
    import msgpack
except ImportError:  # pragma: no cover - host without pin
    msgpack = None  # type: ignore

SERVICE = "lab-emitter"
ENV_NAME = "lab"
PATH_TAG = "ddtrace"
METRIC_NAME = "truewatch_lab_first_mile.ping"
SPAN_NAME = "lab.ddtrace.emit"
SPAN_RESOURCE = "lab.ddtrace.ping"
USER_AGENT = (
    "truewatch-lab-first-mile/0.0.3 "
    "(+https://github.com/BinHsu/truewatch-lab-first-mile)"
)


def _datakit_http_base() -> str:
    return (os.environ.get("DATAKIT_URL") or "http://127.0.0.1:9529").rstrip("/")


def _statsd_addr() -> tuple[str, int]:
    host = os.environ.get("STATSD_HOST") or "127.0.0.1"
    port = int(os.environ.get("STATSD_PORT") or "8125")
    return host, port


def statsd_packet(value: float = 1.0) -> bytes:
    # DogStatsD gauge with tags: name:value|g|#tag:val,...
    tags = f"path:{PATH_TAG},service:{SERVICE},env:{ENV_NAME},lab:truewatch-lab-first-mile"
    return f"{METRIC_NAME}:{value}|g|#{tags}\n".encode("utf-8")


def send_statsd(packet: bytes, timeout: float = 5.0) -> None:
    host, port = _statsd_addr()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.settimeout(timeout)
        sock.sendto(packet, (host, port))
    finally:
        sock.close()


def _u64() -> int:
    return secrets.randbits(64) or 1


def build_span(start_ns: int, duration_ns: int, trace_id: int, span_id: int) -> dict:
    return {
        "trace_id": trace_id,
        "span_id": span_id,
        "parent_id": 0,
        "name": SPAN_NAME,
        "resource": SPAN_RESOURCE,
        "service": SERVICE,
        "type": "custom",
        "start": start_ns,
        "duration": duration_ns,
        "error": 0,
        "meta": {
            "env": ENV_NAME,
            "path": PATH_TAG,
            "version": "0.0.3",
            "lab": "truewatch-lab-first-mile",
            "language": "python",
        },
        "metrics": {
            "_sampling_priority_v1": 1,
            "_dd.measured": 1,
        },
    }


def post_traces(payload: bytes, timeout: float = 30.0) -> tuple[int, str]:
    url = f"{_datakit_http_base()}/v0.4/traces"
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/msgpack",
            "User-Agent": USER_AGENT,
            "X-Datadog-Trace-Count": "1",
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
            f"Cannot reach DataKit traces at {url}: {e.reason}. "
            "Enable ddtrace input and publish :9529; see docs/runbooks/ddtrace-emit.md."
        ) from e


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print payloads; do not send")
    parser.add_argument(
        "--value",
        type=float,
        default=1.0,
        help="StatsD gauge value (default 1.0)",
    )
    parser.add_argument(
        "--skip-metric",
        action="store_true",
        help="Only send the DDTrace span",
    )
    parser.add_argument(
        "--skip-span",
        action="store_true",
        help="Only send the StatsD metric",
    )
    args = parser.parse_args()
    if args.skip_metric and args.skip_span:
        print("nothing to send (--skip-metric and --skip-span)", file=sys.stderr)
        return 2

    print("emit_mode=ddtrace")
    print(f"datakit_url={_datakit_http_base()}")
    sh, sp = _statsd_addr()
    print(f"statsd_addr={sh}:{sp}")

    packet = statsd_packet(args.value)
    print(f"statsd_packet={packet.decode('utf-8').rstrip()}")

    start_ns = time.time_ns()
    duration_ns = 5_000_000  # 5ms synthetic
    trace_id = _u64()
    span_id = _u64()
    span = build_span(start_ns, duration_ns, trace_id, span_id)
    traces = [[span]]
    print(f"trace_id={trace_id}")
    print(f"span_id={span_id}")
    print(f"span_service={SERVICE}")
    print(f"span_resource={SPAN_RESOURCE}")

    if msgpack is None and not args.skip_span:
        print(
            "status=MISSING-DEPENDENCY need msgpack "
            "(Compose image or: pip install -r requirements-emitter.txt)",
            file=sys.stderr,
        )
        return 2

    packed = b""
    if not args.skip_span:
        assert msgpack is not None
        packed = msgpack.packb(traces, use_bin_type=True)
        print(f"traces_endpoint={_datakit_http_base()}/v0.4/traces")
        print(f"traces_msgpack_bytes={len(packed)}")

    if args.dry_run:
        print("dry_run=1 (no send)")
        return 0

    metric_ok = True
    span_ok = True

    if not args.skip_metric:
        try:
            send_statsd(packet)
            print("statsd_send=OK")
        except OSError as e:
            print(f"statsd_send=FAIL err={e}", file=sys.stderr)
            metric_ok = False

    if not args.skip_span:
        code, raw = post_traces(packed)
        print(f"traces_http_status={code}")
        if raw.strip():
            print(f"traces_response_len={len(raw)}")
        if code < 200 or code >= 300:
            print("traces_post=FAIL", file=sys.stderr)
            span_ok = False
        else:
            print("traces_post=OK")

    if not metric_ok or not span_ok:
        return 1

    print(
        "next: OWL first — M for StatsD metric, T for service=lab-emitter; "
        "then console Metrics + APM (see docs/runbooks/ddtrace-emit.md)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
