# ADR-0002 — Release tags + selectable emit mode (Docker-first)

- **Status:** Accepted
- **Date:** 2026-08-04
- **Deciders:** Owner

## Context

ADR-0001 requires three ingest paths. Shipping them in one drop mixes unfinished
paths with a proven DataWay slice. The owner also prefers Docker for a clean lab
host, while still allowing host Python for the lightest DataWay check. Forkers
need one entrypoint that selects the push path by flag or environment variable.

## Decision

### Release tags

| Tag | Scope |
|---|---|
| **v0.0.1** | DataWay path working (`EMIT_MODE=dataway`); unified `scripts/emit.py`; Compose emitter image; credentials + DataWay runbooks |
| **v0.0.2** | DataKit path (prefer Compose); `EMIT_MODE=datakit` implemented |
| **v0.0.3** | DDTrace → DataKit; `EMIT_MODE=ddtrace` implemented |

Unfinished modes must print `NOT-IMPLEMENTED` and exit **non-zero** (never fake OK).

### Select path

```bash
python3 scripts/emit.py --mode dataway
EMIT_MODE=dataway python3 scripts/emit.py
docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit
```

Precedence: `--mode` > `EMIT_MODE` > default `dataway`.

### Runtime preference

1. **Docker Compose** — default recommendation for a clean host (especially
   DataKit / DDTrace in later tags).
2. **Host `python3`** — allowed for DataWay (stdlib only); useful when Docker is
   absent. This machine tagged v0.0.1 without a local Docker binary; Compose
   files are still the forker contract.

## Consequences

- Mode-specific scripts remain: `emit_dataway.py`, stubs for datakit/ddtrace.
- `.env.example` documents `EMIT_MODE`.
- Later tags supersede stubs without changing the `emit.py` UX.

## Re-check trigger

Revisit if Compose cannot run DataKit cleanly on macOS arm64, or if Cloudflare /
DataWay blocks the container User-Agent the same way it blocks `Python-urllib`.
