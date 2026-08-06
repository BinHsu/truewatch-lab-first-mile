#!/usr/bin/env python3
"""Emit OTLP metric + span to local DataKit (v0.0.4).

Dual signal (ADR-0003):
  1) OTLP metrics HTTP protobuf → DataKit /otel/v1/metrics
  2) OTLP traces HTTP protobuf → DataKit /otel/v1/traces

DataKit accepts protobuf only on these routes (not JSON). Prefer Compose emit
image (pinned opentelemetry-proto).

Docs: docs/runbooks/otel-emit.md
Official: https://docs.truewatch.com/integrations/opentelemetry/
"""

from __future__ import annotations

import argparse
import os
import secrets
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from lab_path_values import default_value  # noqa: E402

try:
    from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import (
        ExportMetricsServiceRequest,
    )
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import (
        ExportTraceServiceRequest,
    )
    from opentelemetry.proto.common.v1 import common_pb2
    from opentelemetry.proto.metrics.v1 import metrics_pb2
    from opentelemetry.proto.resource.v1 import resource_pb2
    from opentelemetry.proto.trace.v1 import trace_pb2
except ImportError:  # pragma: no cover - host without pin
    ExportMetricsServiceRequest = None  # type: ignore
    ExportTraceServiceRequest = None  # type: ignore
    common_pb2 = None  # type: ignore
    metrics_pb2 = None  # type: ignore
    resource_pb2 = None  # type: ignore
    trace_pb2 = None  # type: ignore

SERVICE = "lab-emitter"
ENV_NAME = "lab"
PATH_TAG = "otel"
METRIC_NAME = "truewatch_lab_first_mile.ping"
SPAN_NAME = "lab.otel.ping"
INSTRUMENTATION = "truewatch-lab-first-mile"
VERSION = "0.0.4"
USER_AGENT = (
    f"truewatch-lab-first-mile/{VERSION} "
    "(+https://github.com/BinHsu/truewatch-lab-first-mile)"
)


def _datakit_http_base() -> str:
    return (os.environ.get("DATAKIT_URL") or "http://127.0.0.1:9529").rstrip("/")


def _kv_str(key: str, value: str) -> common_pb2.KeyValue:
    return common_pb2.KeyValue(
        key=key,
        value=common_pb2.AnyValue(string_value=value),
    )


def _resource() -> resource_pb2.Resource:
    return resource_pb2.Resource(
        attributes=[
            _kv_str("service.name", SERVICE),
            _kv_str("service.version", VERSION),
            _kv_str("deployment.environment", ENV_NAME),
            _kv_str("path", PATH_TAG),
            _kv_str("lab", "truewatch-lab-first-mile"),
            _kv_str("telemetry.sdk.language", "python"),
            _kv_str("telemetry.sdk.name", INSTRUMENTATION),
        ]
    )


def build_metrics_request(value: float, ts_ns: int) -> ExportMetricsServiceRequest:
    point = metrics_pb2.NumberDataPoint(
        attributes=[
            _kv_str("path", PATH_TAG),
            _kv_str("service", SERVICE),
            _kv_str("env", ENV_NAME),
            _kv_str("lab", "truewatch-lab-first-mile"),
        ],
        time_unix_nano=ts_ns,
        as_double=value,
    )
    metric = metrics_pb2.Metric(
        name=METRIC_NAME,
        description="Lab synthetic first-mile ping (OTLP)",
        unit="1",
        gauge=metrics_pb2.Gauge(data_points=[point]),
    )
    scope_metrics = metrics_pb2.ScopeMetrics(
        scope=common_pb2.InstrumentationScope(name=INSTRUMENTATION, version=VERSION),
        metrics=[metric],
    )
    resource_metrics = metrics_pb2.ResourceMetrics(
        resource=_resource(),
        scope_metrics=[scope_metrics],
    )
    return ExportMetricsServiceRequest(resource_metrics=[resource_metrics])


def build_traces_request(
    start_ns: int,
    end_ns: int,
    trace_id: bytes,
    span_id: bytes,
) -> ExportTraceServiceRequest:
    span = trace_pb2.Span(
        trace_id=trace_id,
        span_id=span_id,
        name=SPAN_NAME,
        kind=trace_pb2.Span.SPAN_KIND_INTERNAL,
        start_time_unix_nano=start_ns,
        end_time_unix_nano=end_ns,
        attributes=[
            _kv_str("path", PATH_TAG),
            _kv_str("lab", "truewatch-lab-first-mile"),
            _kv_str("env", ENV_NAME),
        ],
        status=trace_pb2.Status(code=trace_pb2.Status.STATUS_CODE_OK),
    )
    scope_spans = trace_pb2.ScopeSpans(
        scope=common_pb2.InstrumentationScope(name=INSTRUMENTATION, version=VERSION),
        spans=[span],
    )
    resource_spans = trace_pb2.ResourceSpans(
        resource=_resource(),
        scope_spans=[scope_spans],
    )
    return ExportTraceServiceRequest(resource_spans=[resource_spans])


def _post_protobuf(url: str, body: bytes, timeout: float = 30.0) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/x-protobuf",
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
            f"Cannot reach DataKit OTLP at {url}: {e.reason}. "
            "Enable opentelemetry input on :9529; see docs/runbooks/otel-emit.md."
        ) from e


def _trace_id_hex(trace_id: bytes) -> str:
    return trace_id.hex()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print payloads; do not POST")
    parser.add_argument(
        "--value",
        type=float,
        default=default_value("otel"),
        help=f"OTLP gauge value (default {default_value('otel'):g})",
    )
    parser.add_argument(
        "--skip-metric",
        action="store_true",
        help="Only send the OTLP span",
    )
    parser.add_argument(
        "--skip-span",
        action="store_true",
        help="Only send the OTLP metric",
    )
    args = parser.parse_args()
    if args.skip_metric and args.skip_span:
        print("nothing to send (--skip-metric and --skip-span)", file=sys.stderr)
        return 2

    if ExportMetricsServiceRequest is None or ExportTraceServiceRequest is None:
        print(
            "status=MISSING-DEPENDENCY need opentelemetry-proto "
            "(Compose image or: pip install -r requirements-emitter.txt)",
            file=sys.stderr,
        )
        return 2

    base = _datakit_http_base()
    metrics_url = f"{base}/otel/v1/metrics"
    traces_url = f"{base}/otel/v1/traces"

    now_ns = time.time_ns()
    start_ns = now_ns - 5_000_000
    end_ns = now_ns
    trace_id = secrets.token_bytes(16)
    span_id = secrets.token_bytes(8)

    print("emit_mode=otel")
    print(f"datakit_url={base}")
    print(f"metrics_url={metrics_url}")
    print(f"traces_url={traces_url}")
    print(f"metric_name={METRIC_NAME}")
    print(f"span_name={SPAN_NAME}")
    print(f"service={SERVICE}")
    print(f"path_tag={PATH_TAG}")
    print(f"trace_id_hex={_trace_id_hex(trace_id)}")

    metrics_body = b""
    traces_body = b""
    if not args.skip_metric:
        metrics_req = build_metrics_request(args.value, now_ns)
        metrics_body = metrics_req.SerializeToString()
        print(f"metrics_protobuf_bytes={len(metrics_body)}")
    if not args.skip_span:
        traces_req = build_traces_request(start_ns, end_ns, trace_id, span_id)
        traces_body = traces_req.SerializeToString()
        print(f"traces_protobuf_bytes={len(traces_body)}")

    if args.dry_run:
        print("dry_run=1 (no POST)")
        return 0

    metric_ok = True
    span_ok = True

    if not args.skip_metric:
        code, raw = _post_protobuf(metrics_url, metrics_body)
        print(f"metrics_http_status={code}")
        if raw.strip():
            print(f"metrics_response_len={len(raw)}")
        if code < 200 or code >= 300:
            print("metrics_post=FAIL", file=sys.stderr)
            metric_ok = False
        else:
            print("metrics_post=OK")

    if not args.skip_span:
        code, raw = _post_protobuf(traces_url, traces_body)
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
        "next: OWL first — M for OTLP metric (path=otel / measurement may vary), "
        "T for service=lab-emitter; then console Metrics + APM "
        "(see docs/runbooks/otel-emit.md)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
