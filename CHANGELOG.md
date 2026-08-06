# Changelog

## v0.3.0 — 2026-08-06 (OWL MCP + Tobylike MCP)

Dual MCP showcase (ADR-0004) plus CLI replay twin — wiring face, not new ingest/TF features:

- Cursor template: `.cursor/mcp.json.example` (OWL Bearer on id1 + Tobylike `Endpoint=id2`)
- Runbook: `docs/runbooks/owl-mcp-cursor.md` (intent→tool map for both clients)
- Smokes: `scripts/owl-readonly-smoke.sh` (CLI); `scripts/mcp-dual-smoke.py` (OWL + Tobylike HTTP)
- Tips: MCP uses `owl.data.simple_query` (not `owl.data.query`); Tobylike global host + SITE_KEY
- Design note: `docs/design/mcp-dual-verify.md`

Dashboard create remains **not** via MCP (CLI / Terraform / console).

## v0.2.0 — 2026-08-06 (TF+JSON closed loop + N3 email)

Monitor + Dashboard + email notify on site **id1**, verified end-to-end:

- Terraform closed loop: notify (`mailGroup`) → alert policy → four path monitors → dashboard
- Dashboard `is_public=1`; console compare docs (`by path`); demo emit stagger script
- Path default metric values **1/2/3/4** (`scripts/lab_path_values.py`)
- mailGroup binds workspace **member UUID** (`LAB_ALERT_MEMBER_UUID` / `acnt_…`) — tip sheet
- Fault inject `--value 900` → critical event → email `[VERIFIED]`
- `docs/truewatch-tips.md` + agent duty in `AGENTS.md` to append lab-verified gotchas

Local `terraform.tfstate` stays gitignored; forkers choose their own backend (ADR-0004).

## v0.1.1 — 2026-08-05 (Docs close-out)

Forker-facing close-out after v0.1.0:

- README: four-path ingest flow, live verify cmds, `--dry-run` for all modes
- Docs prefer **`EMIT_MODE`** (Compose/cloud-style); optional `--mode` remains in code
- DataWay skips DataKit by omitting `--profile datakit` (no `--no-deps` as “no DataKit”)
- ADR-0002 addenda for EMIT_MODE-first documentation

## v0.1.0 — 2026-08-05 (First-mile lab checkpoint)

Lab summary tag: all four ingest paths are shipped (v0.0.1–v0.0.4), plus portable
payload contracts.

- Ingest complete: DataWay LP, DataKit LP, DDTrace (StatsD + span), OTel (OTLP metric + span)
- Spaced repeats on `emit.py` (`--count` / `--interval`, default 5s)
- `tests/test_emit_payloads.py` — in-process LP/StatsD/OTLP shapes + DataWay token redact
- `scripts/run-emit-payload-tests.sh` — run those tests **inside** the emitter image (no host pip)
- CI: `security-checks.yml` runs the Docker payload suite
- Portable default: Git + Docker/Colima; pins stay in the image (ADR-0002)

## v0.0.4 — 2026-08-05 (OpenTelemetry → DataKit)

- `EMIT_MODE=otel`: OTLP protobuf **metric + span** (`/otel/v1/metrics`, `/otel/v1/traces`)
- Compose: enable `opentelemetry` (+ existing `dk,ddtrace,statsd`); `ENV_INPUT_OTEL_HTTP`
- Emitter pins `opentelemetry-proto==1.34.1`
- Runbook: `docs/runbooks/otel-emit.md` (OWL-first, then Console)
- `emit.py`: `--count` / `--interval` (default **5s**) for spaced repeats across all modes (ADR-0002)

## v0.0.3 — 2026-08-05 (DDTrace + StatsD)

- `EMIT_MODE=ddtrace`: DogStatsD metric + DDTrace `/v0.4/traces` span
- Compose: `ENV_DEFAULT_ENABLED_INPUTS=dk,ddtrace,statsd`; UDP `8125`
- Emitter image pins `msgpack` (`requirements-emitter.txt`)
- Runbook: `docs/runbooks/ddtrace-emit.md` (OWL-first, then Console)

## v0.0.2 — 2026-08-04 (DataKit)

- `scripts/emit_datakit.py`: POST line protocol to local DataKit `/v1/write/{metric|logging}`
- Compose: `datakit` service (profile `datakit`), image `pubrepo.truewatch.com/truewatch/datakit:2.7.1`
- Runbook: `docs/runbooks/datakit-emit.md`
- `.env.example`: `DATAKIT_URL` / `EMIT_MODE=datakit`

## v0.0.1 — 2026-08-04 (DataWay)

- Unified emitter: `scripts/emit.py` with `--mode` / `EMIT_MODE`
- DataWay path: `scripts/emit_dataway.py` (HTTP 200 verified on id1)
- Stubs (exit 2, `NOT-IMPLEMENTED`): `emit_datakit.py`, `emit_ddtrace.py`
- Docker: `docker/Dockerfile.emitter`, `docker-compose.yml` service `emit`
- Runbooks: OWL credentials, DataWay emit; ADR-0001 / ADR-0002
