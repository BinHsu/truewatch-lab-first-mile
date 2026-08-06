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
| **v0.0.3** | DDTrace → DataKit: **metric (StatsD/DogStatsD) + span**; `EMIT_MODE=ddtrace` ([ADR-0003](0003-otel-trace-path.md)) |
| **v0.0.4** | OTLP → DataKit: **metric + span**; `EMIT_MODE=otel` ([ADR-0003](0003-otel-trace-path.md)) |
| **v0.1.0** | Lab checkpoint: v0.0.1–v0.0.4 paths + portable payload UT in Docker + CI |
| **v0.1.1** | Docs close-out: forker README flow, `EMIT_MODE`-first examples |
| **v0.2.0** | Thin closed loop: Monitor + Dashboard + email notify via TF+JSON ([ADR-0004](0004-tf-json-closed-loop.md)) |
| **v0.3.0** | MCP OWL + Tobylike ([ADR-0004](0004-tf-json-closed-loop.md)) |

Unfinished modes must print `NOT-IMPLEMENTED` and exit **non-zero** (never fake OK).

### Select path

```bash
python3 scripts/emit.py --mode dataway
EMIT_MODE=dataway python3 scripts/emit.py
docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit
```

**Preferred for docs and cloud-shaped deploys:** `EMIT_MODE` (env).  
Optional CLI `--mode` still overrides when passed (local convenience).

Precedence when both appear: `--mode` > `EMIT_MODE` > default `dataway`.

### Runtime preference

1. **Docker Compose** — default recommendation for a clean host (especially
   DataKit / DDTrace / OTel in later tags).
2. **Host `python3`** — allowed for DataWay (stdlib only); useful when Docker is
   absent. This machine tagged v0.0.1 without a local Docker binary; Compose
   files are still the forker contract. Colima later verified for DataKit.

## Consequences

- Mode-specific scripts: `emit_dataway.py`, `emit_datakit.py`, `emit_ddtrace.py`,
  `emit_otel.py` (unified via `emit.py` + `EMIT_MODE`).
- `.env.example` documents `EMIT_MODE`.
- Later tags (closed-loop / MCP) do not change the `emit.py` UX.

## Addendum — 2026-08-04

Owner accepted **v0.0.4 OTel** and then required **metric + span** for **both**
v0.0.3 (DDTrace + StatsD) and v0.0.4 (OTLP traces + OTLP metrics). Canonical
detail: [ADR-0003](0003-otel-trace-path.md).

## Addendum — 2026-08-05

Owner verified OTel Console: two emit shots ~200ms apart looked like **one** metric
point (gauge value `1`) while APM showed two spans. Decision: unify **repeat
spacing** on `scripts/emit.py` for all modes:

| Knob | Default | Env |
|---|---|---|
| `--count` | `1` | `EMIT_COUNT` (only if `--count` not passed) |
| `--interval` | **`5` seconds** | `EMIT_INTERVAL_SEC` (only if `--interval` not passed) |

Precedence: CLI flag → env (if set) → default. Bad env values raise on cast.
Mode scripts stay single-shot. The dispatcher sleeps between shots (skipped on
`--dry-run`). Use `--count 2` (or higher) when proving Metrics Explorer shows
distinct points; protocol proof still works with `count=1`.

## Addendum — 2026-08-05 (v0.1.0 checkpoint)

Owner treated post-v0.0.4 work (payload contracts + Docker/CI, no host pip) as the
lab’s first summary release **v0.1.0**, not a retag of v0.0.4.

## Addendum — 2026-08-05 (EMIT_MODE-first; no fake --no-datakit flag)

Docs and Compose examples prefer **`EMIT_MODE=…`** over `--mode`. Keeping DataKit
off for DataWay is done by **not** passing `--profile datakit` (DataKit is
profile-gated; `emit` does not `depends_on` it). Do not document Compose
`--no-deps` as “no DataKit” — that flag is unrelated and confusing.

## Addendum — 2026-08-05 (v0.2.0 / v0.3.0 tags)

Owner accepted thin closed-loop + MCP tags. Canonical decision:
[ADR-0004](0004-tf-json-closed-loop.md).

## Addendum — 2026-08-06 (v0.2.0 cut)

**v0.2.0** tagged after id1 apply + four-path emit + N3 email verify (`mailGroup` → `acnt_…`).
See `CHANGELOG.md` and `docs/truewatch-tips.md`.

## Addendum — 2026-08-06 (v0.3.0 cut)

**v0.3.0** tagged after CLI smoke + OWL MCP + Tobylike MCP (`Endpoint=id2`) verify.
See `CHANGELOG.md`, `docs/runbooks/owl-mcp-cursor.md`, `docs/truewatch-tips.md`.

## Re-check trigger

Revisit if Compose cannot run DataKit cleanly on macOS arm64, or if Cloudflare /
DataWay blocks the container User-Agent the same way it blocks `Python-urllib`.
