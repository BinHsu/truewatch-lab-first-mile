# Runbook — DDTrace + StatsD emit (ADR-0003 / v0.0.3)

Prove DataKit converts **DogStatsD metrics** and **DDTrace spans** into TrueWatch
Metrics + APM. Companion to [`datakit-emit.md`](datakit-emit.md) (line protocol)
and [`dataway-emit.md`](dataway-emit.md).

**Never paste** tokens or full `DK_DATAWAY` into chat/git.

Official refs:
- DDTrace: https://docs.truewatch.com/integrations/ddtrace/
- StatsD: https://docs.truewatch.com/integrations/statsd/

---

## Prerequisites

1. `.env` with `DK_DATAWAY` (credentials runbook §5).
2. **Docker Compose** (Colima / Docker OK). Preferred path is the **emit image**
   (pins `msgpack` via `requirements-emitter.txt`) — IaC-friendly; host Python is
   optional and needs `pip install -r requirements-emitter.txt` for spans.
3. DataKit profile with inputs `dk,ddtrace,statsd` (see `docker-compose.yml`).

---

## Steps (Compose)

### 1. Start / recreate DataKit

```bash
cd /path/to/truewatch-lab-first-mile
set -a && source .env && set +a
docker compose --profile datakit --env-file .env up -d --force-recreate datakit
docker compose --profile datakit --env-file .env ps
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9529/v1/ping   # expect 200
```

Ports: **9529** (HTTP / traces / LP), **8125/udp** (StatsD).

### 2. Dry-run

```bash
docker compose --env-file .env build emit
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit --dry-run
```

Expect `emit_mode=ddtrace`, a StatsD packet with `path:ddtrace`, and a printed
`trace_id` / `span_id` (no send).

### 3. Live emit

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit
# Distinct Metrics points: --count 2 (default 5s gap; see ADR-0002)
```

Expect `statsd_send=OK` and `traces_post=OK` (`traces_http_status` in 2xx).

Host alternative (after `pip install -r requirements-emitter.txt`):

```bash
STATSD_HOST=127.0.0.1 STATSD_PORT=8125 DATAKIT_URL=http://127.0.0.1:9529 \
  EMIT_MODE=ddtrace python3 scripts/emit.py
```

---

## Verify — OWL CLI **first** (required before Console)

Group A gate. Do **not** treat the slice as done until these succeed.

```bash
set -a && source .env && set +a
export PATH="$HOME/.local/bin:$PATH"
END=$(python3 -c 'import time; print(int(time.time()*1000))')
START=$(python3 -c 'import time; print(int((time.time()-2*3600)*1000))')

# StatsD maps truewatch_lab_first_mile.ping → measurement truewatch, field lab_first_mile_ping
owl exec owl.data.query -p "{\"dql_namespace\":\"M\",\"start_time\":$START,\"end_time\":$END,\"query_text\":\"M::truewatch:(last(lab_first_mile_ping), count(lab_first_mile_ping)) { path = 'ddtrace' } [2h]\"}"

# Hyphenated service must be quoted; prefer raw rows or count(trace_id)
owl exec owl.data.query -p "{\"dql_namespace\":\"T\",\"start_time\":$START,\"end_time\":$END,\"query_text\":\"T::'lab-emitter':(trace_id, span_id, resource, service, duration) [2h] LIMIT 5\"}"
```

Pass criteria:

- **Metrics (`M`)**: `M::truewatch` field `lab_first_mile_ping`, tag `path=ddtrace`, `last=1` (or similar).
- **Traces (`T`)**: rows for `service=lab-emitter` with **`trace_id`**, resource `lab.ddtrace.ping`.

`[VERIFIED]` example (2026-08-05 id1): metric `count(lab_first_mile_ping)=2` /
`last=1` with `path=ddtrace`; trace `trace_id=974926597694416500`,
`resource=lab.ddtrace.ping`.

Record command outputs (redacted) and absolute times in
[`../handoff/CURRENT.md`](../handoff/CURRENT.md) with `[VERIFIED]`.

---

## Verify — TrueWatch Web Console (after OWL)

| Signal | Where | What to look for |
|---|---|---|
| Metric | **Metrics** → Explorer / Metric Analysis | Measurement **`truewatch`**, field **`lab_first_mile_ping`**, filter **`path=ddtrace`** |
| Span | **APM** → Traces | `service=lab-emitter`, resource `lab.ddtrace.ping`, open detail → **`trace_id`** |

Widen time range 15–30 minutes if empty. If OWL passed but Console empty, wait for
ingest lag then refresh — do not invert the order (OWL first). Four-path console map
(and why LP paths need **`by path`**):
[`README.md`](../../README.md#compare-all-four-in-the-web-console).

---

## What gets sent

| Signal | Wire format | Target |
|---|---|---|
| Metric | DogStatsD: `truewatch_lab_first_mile.ping:1\|g\|#path:ddtrace,…` → after DataKit mapping often **`M::truewatch`** field **`lab_first_mile_ping`** | UDP `:8125` |
| Span | DDTrace msgpack `/v0.4/traces` | HTTP `:9529` |

Not line-protocol `/v1/write/metric` (that is v0.0.1/v0.0.2).

---

## Env vars

| Var | Default (host / Compose) |
|---|---|
| `DATAKIT_URL` | `http://127.0.0.1:9529` / `http://datakit:9529` |
| `STATSD_HOST` | `127.0.0.1` / `datakit` |
| `STATSD_PORT` | `8125` |
| `EMIT_MODE` | `ddtrace` |

---

## Failure triage

| Symptom | Likely cause |
|---|---|
| `MISSING-DEPENDENCY need msgpack` | Host without pin — use Compose emit or `pip install -r requirements-emitter.txt` |
| `statsd_send=FAIL` | Port 8125/udp not published or `statsd` input not enabled |
| `traces_post=FAIL` / connection error | `ddtrace` not in `ENV_DEFAULT_ENABLED_INPUTS`; recreate container |
| OWL `M` empty | StatsD flush interval; wait ~10–30s and widen window; check measurement name via `owl.metric.list` |
| OWL `T` empty | Wrong service name; confirm `traces_post=OK`; check DataKit logs (redact tokens) |

---

## Related

- DataKit LP: [`datakit-emit.md`](datakit-emit.md)
- Glossary / console map: [`../observability-glossary.md`](../observability-glossary.md)
- ADR: [`../ADR/0003-otel-trace-path.md`](../ADR/0003-otel-trace-path.md)
- Status: [`../handoff/CURRENT.md`](../handoff/CURRENT.md)
