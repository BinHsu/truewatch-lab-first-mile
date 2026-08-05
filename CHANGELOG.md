# Changelog

## v0.0.1 — 2026-08-04 (DataWay)

- Unified emitter: `scripts/emit.py` with `--mode` / `EMIT_MODE`
- DataWay path: `scripts/emit_dataway.py` (HTTP 200 verified on id1)
- Stubs (exit 2, `NOT-IMPLEMENTED`): `emit_datakit.py`, `emit_ddtrace.py`
- Docker: `docker/Dockerfile.emitter`, `docker-compose.yml` service `emit`
- Runbooks: OWL credentials, DataWay emit; ADR-0001 / ADR-0002

## v0.0.2 — 2026-08-04 (DataKit)

- `scripts/emit_datakit.py`: POST line protocol to local DataKit `/v1/write/{metric|logging}`
- Compose: `datakit` service (profile `datakit`), image `pubrepo.truewatch.com/truewatch/datakit:2.7.1`
- Runbook: `docs/runbooks/datakit-emit.md`
- `.env.example`: `DATAKIT_URL` / `EMIT_MODE=datakit`

## v0.0.3 — 2026-08-05 (DDTrace + StatsD)

- `EMIT_MODE=ddtrace`: DogStatsD metric + DDTrace `/v0.4/traces` span
- Compose: `ENV_DEFAULT_ENABLED_INPUTS=dk,ddtrace,statsd`; UDP `8125`
- Emitter image pins `msgpack` (`requirements-emitter.txt`)
- Runbook: `docs/runbooks/ddtrace-emit.md` (OWL-first, then Console)

## v0.0.4 — 2026-08-05 (OpenTelemetry → DataKit)

- `EMIT_MODE=otel`: OTLP protobuf **metric + span** (`/otel/v1/metrics`, `/otel/v1/traces`)
- Compose: enable `opentelemetry` (+ existing `dk,ddtrace,statsd`); `ENV_INPUT_OTEL_HTTP`
- Emitter pins `opentelemetry-proto==1.34.1`
- Runbook: `docs/runbooks/otel-emit.md` (OWL-first, then Console)
- `emit.py`: `--count` / `--interval` (default **5s**) for spaced repeats across all modes (ADR-0002)
- Deferred: `tests/test_emit_payloads.py` + GHA until owner Console verify
