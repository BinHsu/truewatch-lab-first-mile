# truewatch-lab-first-mile

Public **PDSA lab**: prove a synthetic **first-mile** loop into TrueWatch —

**emit → DataKit and/or DataWay → Metrics / APM (Explorer or OWL) → optional alert/dashboard.**

Checkpoint tags: **[v0.1.0](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.1.0)** (paths + UT/CI),
**[v0.1.1](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.1.1)** (forker docs),
**[v0.2.0](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.2.0)** (TF closed loop + N3 email).

**Status and next action live only in [`docs/handoff/CURRENT.md`](docs/handoff/CURRENT.md)** — not here.

---

## What you need

- Git + **Docker** (or Colima) — preferred; keeps the host pip-clean ([ADR-0002](docs/ADR/0002-release-tags-and-emit-mode.md))
- A TrueWatch workspace (lab uses site **id1** patterns in runbooks)
- Copy `.env.example` → `.env` (never commit `.env`)

```bash
git clone https://github.com/BinHsu/truewatch-lab-first-mile.git
cd truewatch-lab-first-mile
git config core.hooksPath .githooks
cp .env.example .env   # then fill credentials — see runbook below
```

Credentials: [`docs/runbooks/owl-cli-credentials.md`](docs/runbooks/owl-cli-credentials.md)  
(OWL API key ≠ Workspace Token ≠ RUM Client Token.)

---

## Four ingest paths (the lab’s core)

One emitter entrypoint: `scripts/emit.py`. Prefer **`EMIT_MODE`** (env) — same shape as
Compose / cloud. Optional `--mode` still overrides if you pass it.
Modes are **not** four ways to send the same LP `ping` — wire formats differ.

```text
                    ┌─────────────────────────────────────────┐
  lab emitter       │  EMIT_MODE = dataway | datakit |        │
  (Compose `emit`   │               ddtrace | otel            │
   or host python)  └────────────┬────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
   ┌───────────┐          ┌────────────┐          ┌────────────┐
   │ DataWay   │          │  DataKit   │          │  DataKit   │
   │ openway   │          │  :9529     │          │  + inputs  │
   │ /v1/write │          │  /v1/write │          │  ddtrace / │
   │  (LP)     │          │  (LP)      │          │  statsd /  │
   └─────┬─────┘          └─────┬──────┘          │  otel      │
         │                      │                 └──────┬─────┘
         │                      │                        │
         └──────────────────────┴────────────────────────┘
                                 │
                                 ▼
                        TrueWatch workspace
                     Metrics (M)  ·  APM (T)
```

| Mode | Tag | What leaves the emitter | Typical hop | You prove |
|---|---|---|---|---|
| `dataway` | [v0.0.1](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1) | Line protocol metric (+ optional log) | **Direct** HTTPS → DataWay | `path=dataway` in Metrics |
| `datakit` | [v0.0.2](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2) | Same LP shape | Local DataKit `:9529` → DataWay | `path=datakit` in Metrics |
| `ddtrace` | [v0.0.3](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3) | **StatsD metric + DDTrace span** | DataKit `statsd` + `ddtrace` | Metrics + APM `trace_id` |
| `otel` | [v0.0.4](https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4) | **OTLP metric + OTLP span** (protobuf) | DataKit `opentelemetry` | Metrics + APM (`lab.otel.ping`) |

Decisions: [ADR-0001](docs/ADR/0001-three-ingest-paths.md), [ADR-0002](docs/ADR/0002-release-tags-and-emit-mode.md), [ADR-0003](docs/ADR/0003-otel-trace-path.md).

### Compare all four in the web console

After emitting each mode (lab defaults **1 / 2 / 3 / 4** by path — see
`scripts/lab_path_values.py`), open TrueWatch → **Metrics** →
**Explorer** or **Metric Analysis**. The four paths do **not** share one metric name:

| Path | Measurement | Field | Default value | Distinguish with |
|---|---|---|---|---|
| `dataway` | `truewatch_lab_first_mile` | `ping` | **1** | tag **`path=dataway`** |
| `datakit` | `truewatch_lab_first_mile` | `ping` | **2** | tag **`path=datakit`** |
| `ddtrace` | `truewatch` | `lab_first_mile_ping` | **3** | tag **`path=ddtrace`** |
| `otel` | `otel_service` | `truewatch_lab_first_mile.ping` | **4** | tag **`path=otel`** |

**`dataway` and `datakit` share one measurement.** In Metric Analysis, if you query
`truewatch_lab_first_mile` → `ping` with **Avg** and leave **`by Label` empty**, both
paths collapse into **one** series (looks like a single failure). Set **`by path`**, or
filter `path=dataway` / `path=datakit` separately. That is intentional (same semantic
metric + tags), not four differently named metrics.

**Stagger for the board:** same-second emits still stack on the x-axis. Prefer:

```bash
set -a && source .env && set +a
bash scripts/emit-dashboard-demo.sh          # uses path defaults + ~8s between paths
# bash scripts/emit-dashboard-demo.sh --interval 10
```

Fault inject stays **`--value 900`** (monitor `>=900`). Override any default with
`--value` when needed.

Ignore measurement **`dk`** (DataKit self-metrics). APM spans for `ddtrace` / `otel`:
service **`lab-emitter`** (`lab.ddtrace.ping` / `lab.otel.ping`).

Per-path console steps: runbooks linked under [Quick commands](#quick-commands).

### Suggested fork order

1. Credentials → `.env`
2. **`dataway`** (no DataKit container) — fastest smoke
3. Start DataKit profile → **`datakit`**
4. Same DataKit → **`ddtrace`**, then **`otel`** (dual metric+span)
5. Optional: OWL DQL before Console (runbooks say OWL-first for APM paths)
6. Console: compare four using the table above (`by path` for the LP pair)

---

## Quick commands

```bash
# Portable contract tests (Docker; no host pip)
bash scripts/run-emit-payload-tests.sh

# Load credentials (never commit .env)
set -a && source .env && set +a

# Mode selection: set EMIT_MODE (compose/K8s-style). Optional CLI --mode still works
# but docs prefer the env form.
#
# --dry-run: print assembled URL/payloads only (no POST / no UDP). All four modes:
#   docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit --dry-run
#   docker compose --env-file .env run --rm -e EMIT_MODE=datakit emit --dry-run
#   docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit --dry-run
#   docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --dry-run

# Live verify — DataWay only (do NOT use --profile datakit → no DataKit container)
EMIT_MODE=dataway python3 scripts/emit.py
docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit

# Live verify — DataKit / DDTrace / OTel (explicitly enable the datakit profile)
docker compose --profile datakit --env-file .env up -d datakit
docker compose --env-file .env build emit
docker compose --env-file .env run --rm -e EMIT_MODE=datakit emit
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit

# Console-friendly: two metric points ≥5s apart (any mode; example otel)
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --count 2
```

Per-path steps (OWL verify, Console, gotchas):

| Path | Runbook |
|---|---|
| Credentials | [`docs/runbooks/owl-cli-credentials.md`](docs/runbooks/owl-cli-credentials.md) |
| DataWay | [`docs/runbooks/dataway-emit.md`](docs/runbooks/dataway-emit.md) |
| DataKit | [`docs/runbooks/datakit-emit.md`](docs/runbooks/datakit-emit.md) |
| DDTrace | [`docs/runbooks/ddtrace-emit.md`](docs/runbooks/ddtrace-emit.md) |
| OTel | [`docs/runbooks/otel-emit.md`](docs/runbooks/otel-emit.md) |

Glossary (Metrics / APM / RUM / `trace_id`): [`docs/observability-glossary.md`](docs/observability-glossary.md)  
OWL / MCP rules: [`docs/truewatch-owl.md`](docs/truewatch-owl.md)  
TrueWatch tips (mailGroup id, `is_public`, `by path`, …): [`docs/truewatch-tips.md`](docs/truewatch-tips.md)

---

## Still optional / next tags

- **v0.2.0:** shipped — Monitor + Dashboard + N3 email via TF+JSON (local state). See
  [`CHANGELOG.md`](CHANGELOG.md), [`docs/runbooks/monitor-dashboard-tf.md`](docs/runbooks/monitor-dashboard-tf.md),
  [ADR-0004](docs/ADR/0004-tf-json-closed-loop.md).
- **v0.3.0:** OWL MCP + Tobylike MCP
- Dashboard writes remain **not** via MCP

---

## Security harness

Inherited from [`BinHsu/aegis-template`](https://github.com/BinHsu/aegis-template): Rule → Execution → Verification.  
See [`docs/SECURITY_PRACTICES.md`](docs/SECURITY_PRACTICES.md), `SECURITY.md`, `AGENTS.md`, `.githooks/`, `.github/workflows/security-checks.yml`.

## License / visibility

Public learning lab. **Synthetic data only** — no customer payloads, no real secrets in git.
