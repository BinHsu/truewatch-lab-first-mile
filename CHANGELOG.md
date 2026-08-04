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

## v0.0.3 — planned (DDTrace → DataKit)

- `EMIT_MODE=ddtrace`: **StatsD/DogStatsD metric + DDTrace span** (DataKit converts both)
- See ADR-0003

## v0.0.4 — planned (OpenTelemetry → DataKit)

- `EMIT_MODE=otel`: **OTLP metrics + OTLP traces** (DataKit converts both)
- Glossary: `docs/observability-glossary.md`
- See ADR-0003
