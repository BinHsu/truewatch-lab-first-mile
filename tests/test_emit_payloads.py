#!/usr/bin/env python3
"""Contract tests for emit payloads and credential redaction (in-process).

No network. Loads scripts/*.py via importlib.

Preferred run (clean host — ADR-0002): Docker emitter image, not host pip:

    bash scripts/run-emit-payload-tests.sh

Inside the image / CI image:

    python3 tests/test_emit_payloads.py -v
"""

from __future__ import annotations

import importlib.util
import io
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

REPO = Path(__file__).resolve().parent.parent
SCRIPTS = REPO / "scripts"
CANARY = "sekrit-canary-XYZ-do-not-leak"


def _load(name: str):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class TestLabPathValues(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.vals = _load("lab_path_values")

    def test_defaults_are_distinct_and_below_fault(self) -> None:
        d = self.vals.DEFAULT_VALUE_BY_PATH
        self.assertEqual(
            d,
            {"dataway": 1.0, "datakit": 2.0, "ddtrace": 3.0, "otel": 4.0},
        )
        self.assertEqual(len(set(d.values())), 4)
        for v in d.values():
            self.assertLess(v, 900.0)

    def test_emit_argparse_defaults(self) -> None:
        for name, path in (
            ("emit_dataway", "dataway"),
            ("emit_datakit", "datakit"),
            ("emit_ddtrace", "ddtrace"),
            ("emit_otel", "otel"),
        ):
            mod = _load(name)
            # Re-parse help path: call parser construction indirectly via default_value
            self.assertEqual(mod.default_value(path), self.vals.default_value(path))


class TestDatawayRedactAndBodies(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dw = _load("emit_dataway")

    def test_redact_url_masks_token(self) -> None:
        raw = f"https://example.invalid/v1/write/metric?token={CANARY}&x=1"
        out = self.dw._redact_url(raw)
        self.assertIn("token=***", out)
        self.assertNotIn(CANARY, out)
        self.assertIn("x=1", out)

    def test_line_protocol_metric_shape(self) -> None:
        body = self.dw.line_protocol_metric(1.0, 123)
        self.assertEqual(
            body,
            "truewatch_lab_first_mile,path=dataway,service=lab-emitter,env=lab "
            "ping=1.0 123",
        )

    def test_dry_run_stdout_hides_workspace_token(self) -> None:
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("DK_DATAWAY", "DATAWAY_URL", "TRUEWATCH_WORKSPACE_TOKEN")
        }
        env["DATAWAY_URL"] = "https://example.invalid"
        env["TRUEWATCH_WORKSPACE_TOKEN"] = CANARY
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True):
            with redirect_stdout(buf):
                code = self.dw.main(["--dry-run", "--value", "1.0"])
        self.assertEqual(code, 0)
        text = buf.getvalue()
        self.assertIn("dry_run=1", text)
        self.assertIn("metric_url=", text)
        self.assertIn("token=***", text)
        self.assertNotIn(CANARY, text)
        self.assertIn("path=dataway", text)

    def test_dry_run_stdout_hides_token_in_dk_dataway(self) -> None:
        env = {
            k: v
            for k, v in os.environ.items()
            if k not in ("DK_DATAWAY", "DATAWAY_URL", "TRUEWATCH_WORKSPACE_TOKEN")
        }
        env["DK_DATAWAY"] = f"https://example.invalid?token={CANARY}"
        buf = io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True):
            with redirect_stdout(buf):
                code = self.dw.main(["--dry-run"])
        self.assertEqual(code, 0)
        text = buf.getvalue()
        self.assertIn("token=***", text)
        self.assertNotIn(CANARY, text)
        self.assertIn("/v1/write/metric", text)


class TestDatakitBodies(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dk = _load("emit_datakit")

    def test_write_url_and_metric_body(self) -> None:
        with mock.patch.dict(os.environ, {"DATAKIT_URL": "http://127.0.0.1:9529"}):
            self.assertEqual(
                self.dk.write_url("metric"),
                "http://127.0.0.1:9529/v1/write/metric",
            )
        body = self.dk.line_protocol_metric(1.0, 99)
        self.assertIn("path=datakit", body)
        self.assertTrue(body.endswith(" ping=1.0 99"))


class TestDdtracePayloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.dd = _load("emit_ddtrace")

    def test_statsd_packet(self) -> None:
        pkt = self.dd.statsd_packet(1.0).decode("utf-8")
        self.assertEqual(
            pkt,
            "truewatch_lab_first_mile.ping:1.0|g|"
            "#path:ddtrace,service:lab-emitter,env:lab,lab:truewatch-lab-first-mile\n",
        )

    def test_build_span_and_msgpack_roundtrip(self) -> None:
        if self.dd.msgpack is None:
            self.skipTest("msgpack not installed")
        span = self.dd.build_span(1000, 5_000_000, 11, 22)
        self.assertEqual(span["service"], "lab-emitter")
        self.assertEqual(span["resource"], "lab.ddtrace.ping")
        self.assertEqual(span["meta"]["path"], "ddtrace")
        packed = self.dd.msgpack.packb([[span]], use_bin_type=True)
        back = self.dd.msgpack.unpackb(packed, raw=False)
        self.assertEqual(back[0][0]["trace_id"], 11)
        self.assertEqual(back[0][0]["span_id"], 22)


class TestOtelPayloads(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.otel = _load("emit_otel")

    def test_metrics_and_traces_protobuf(self) -> None:
        if self.otel.ExportMetricsServiceRequest is None:
            self.skipTest("opentelemetry-proto not installed")
        ts = 1_000_000_000
        mreq = self.otel.build_metrics_request(1.0, ts)
        self.assertGreater(len(mreq.SerializeToString()), 0)
        metric = mreq.resource_metrics[0].scope_metrics[0].metrics[0]
        self.assertEqual(metric.name, "truewatch_lab_first_mile.ping")
        attrs = {
            a.key: a.value.string_value
            for a in metric.gauge.data_points[0].attributes
        }
        self.assertEqual(attrs.get("path"), "otel")

        treq = self.otel.build_traces_request(
            ts - 5_000_000,
            ts,
            b"\x01" * 16,
            b"\x02" * 8,
        )
        self.assertGreater(len(treq.SerializeToString()), 0)
        span = treq.resource_spans[0].scope_spans[0].spans[0]
        self.assertEqual(span.name, "lab.otel.ping")
        res_attrs = {
            a.key: a.value.string_value
            for a in treq.resource_spans[0].resource.attributes
        }
        self.assertEqual(res_attrs.get("service.name"), "lab-emitter")
        self.assertEqual(res_attrs.get("path"), "otel")


class TestEmitDispatcherDefaults(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.emit = _load("emit")

    def test_count_and_interval_defaults(self) -> None:
        self.assertEqual(self.emit.DEFAULT_COUNT, 1)
        self.assertEqual(self.emit.DEFAULT_INTERVAL_SEC, 5.0)


if __name__ == "__main__":
    unittest.main()
