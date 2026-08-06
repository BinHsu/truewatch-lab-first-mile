# Runbook — OTLP metric + span emit (ADR-0003 / v0.0.4)

Synthetic dual-signal via DataKit OpenTelemetry input:

1. **OTLP metrics** → `POST /otel/v1/metrics` (protobuf)
2. **OTLP traces** → `POST /otel/v1/traces` (protobuf)

Official: https://docs.truewatch.com/integrations/opentelemetry/

DataKit HTTP OTLP handlers parse **protobuf only** (not JSON). Prefer Compose
emit image (`opentelemetry-proto` pinned in `requirements-emitter.txt`).

---

## Prerequisites

1. `.env` with `DK_DATAWAY` (owl-cli-credentials §5).
2. Colima / Docker Compose working.
3. DataKit profile with `opentelemetry` in `ENV_DEFAULT_ENABLED_INPUTS`
   (see `docker-compose.yml`).
4. OWL CLI + `OWL_TOKEN` for verify (same as other paths).

---

## 1. Recreate DataKit (enable OTel)

```bash
cd /path/to/truewatch-lab-first-mile
docker compose --profile datakit --env-file .env up -d --force-recreate datakit
docker compose --profile datakit --env-file .env ps
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:9529/v1/ping
```

Expect ping `200`.

---

## 2. Dry-run

```bash
docker compose --env-file .env build emit
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --dry-run
```

Expect `emit_mode=otel`, `metrics_url=…/otel/v1/metrics`,
`traces_url=…/otel/v1/traces`, non-zero `*_protobuf_bytes`, `dry_run=1`.

Host (optional):

```bash
pip install -r requirements-emitter.txt
DATAKIT_URL=http://127.0.0.1:9529 EMIT_MODE=otel python3 scripts/emit.py --dry-run
```

---

## 3. Live emit

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit
# Console-friendly: two metric points ≥5s apart (ADR-0002 addendum 2026-08-05)
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --count 2
```

Expect `metrics_post=OK` and `traces_post=OK` (HTTP 200 or 202).

---

## 4. OWL verify first (Group A)

Widen window if needed. Service name has a hyphen — quote it.

```bash
set -a && source .env && set +a
# OWL expects 13-digit unix ms (not ISO strings)
START=$(($(date +%s)*1000 - 7200000))
END=$(($(date +%s)*1000))

# Discovery: OTLP gauges often land in measurement otel_service
owl exec owl.metric.list -p '{}'
owl exec owl.metric.list -p '{"mode":"field","source":"otel_service"}'

# Metrics — field name keeps the OTLP metric name (including dots); quote it in DQL
owl exec owl.data.query -p "{\"dql_namespace\":\"M\",\"start_time\":$START,\"end_time\":$END,\"query_text\":\"M::otel_service:(last(\\\"truewatch_lab_first_mile.ping\\\"), count(\\\"truewatch_lab_first_mile.ping\\\")) { path = 'otel' } [2h]\"}"

# Traces — filter by resource (OTel may not populate operation like DDTrace)
owl exec owl.data.query -p "{\"dql_namespace\":\"T\",\"start_time\":$START,\"end_time\":$END,\"query_text\":\"T::'lab-emitter':(trace_id, span_id, resource, service, duration, source) { resource = 'lab.otel.ping' } [2h] LIMIT 5\"}"
```

Pass when:

- **Metrics (`M`)**: `M::otel_service` field **`truewatch_lab_first_mile.ping`**, tag `path=otel`, `last=1` (or similar).
- **Traces (`T`)**: `service=lab-emitter`, `resource=lab.otel.ping`, `source=opentelemetry`, with a `trace_id`.

`[VERIFIED]` example (2026-08-05 ~02:47–02:48 UTC): metric `count=2` / `last=1`;
traces `trace_id=31f5553f98c1c2a641b5dbcb63b79362` and `bc637a8d69523ceda08afaa3bf1c4e8e`.

---

## 5. Console (Group B) — after OWL

| Signal | Console | What to find |
|---|---|---|
| Metric | **Metrics** → Explorer | Measurement **`otel_service`**, field **`truewatch_lab_first_mile.ping`**, filter **`path=otel`** |
| Span | **APM** → Traces | `service=lab-emitter`, open → **`trace_id`** |

OWL first, then Console (same rule as ddtrace runbook). Four-path console map:
[`README.md`](../../README.md#compare-all-four-in-the-web-console).

---

## What gets sent

| Signal | Wire format | Target |
|---|---|---|
| Metric | OTLP gauge → after DataKit often **`M::otel_service`** field **`truewatch_lab_first_mile.ping`** (dots kept), tag `path=otel` | `POST :9529/otel/v1/metrics` |
| Span | OTLP span name/resource `lab.otel.ping`, `service.name=lab-emitter`, `source=opentelemetry` | `POST :9529/otel/v1/traces` |

Not line-protocol `/v1/write/metric` and not DDTrace `/v0.4/traces`.

---

## Env vars

| Var | Default (host / Compose) |
|---|---|
| `DATAKIT_URL` | `http://127.0.0.1:9529` / `http://datakit:9529` |
| `EMIT_MODE` | `otel` |

---

## Failure triage

| Symptom | Likely cause |
|---|---|
| `MISSING-DEPENDENCY need opentelemetry-proto` | Host without pin — use Compose emit |
| `metrics_post=FAIL` / 404 | `opentelemetry` not in enabled inputs; recreate DataKit |
| HTTP 400 | Wrong Content-Type or JSON body — must be `application/x-protobuf` |
| OWL `M` empty | Wrong measurement — use `owl.metric.list`; expect **`otel_service`**, not LP measurement names |
| OWL `T` empty | Confirm `traces_post=OK`; filter `resource='lab.otel.ping'` / `source='opentelemetry'`; quote `lab-emitter` |

---

## Next

Four-path ingest through v0.0.4 is shipped. Continue with:

- Closed loop: [`monitor-dashboard-tf.md`](monitor-dashboard-tf.md) (v0.2.0)
- MCP dual clients: [`owl-mcp-cursor.md`](owl-mcp-cursor.md) (v0.3.0)
- Payload tests (already in CI): `bash scripts/run-emit-payload-tests.sh`

Status: `docs/handoff/CURRENT.md`.
