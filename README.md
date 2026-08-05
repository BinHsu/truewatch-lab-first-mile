# truewatch-lab-first-mile

Public PDSA lab: a **synthetic first-mile** TrueWatch observability loop
(ingest → Explorer/DQL → monitor → optional OWL MCP / `owl-diagnostics`).

Bootstrapped from [`BinHsu/aegis-template`](https://github.com/BinHsu/aegis-template) (Harness
Engineering security scaffold). Workload code is not written yet — start from
`docs/handoff/CURRENT.md`.

## Start here

1. `docs/handoff/CURRENT.md` — status and next safe action (no chat history required)
2. [`docs/runbooks/owl-cli-credentials.md`](docs/runbooks/owl-cli-credentials.md) — console → `.env` (OWL §3–4, ingest Workspace Token/DataWay **§5**, OWL CLI **§6**)
3. [`docs/runbooks/dataway-emit.md`](docs/runbooks/dataway-emit.md) — DataWay synthetic metric (v0.0.1)
4. [`docs/runbooks/datakit-emit.md`](docs/runbooks/datakit-emit.md) — DataKit via Compose `:9529` (v0.0.2)
5. [`docs/runbooks/ddtrace-emit.md`](docs/runbooks/ddtrace-emit.md) — StatsD + DDTrace via DataKit (v0.0.3)
6. [`docs/observability-glossary.md`](docs/observability-glossary.md) — Metrics/Logs/APM/RUM terms + TrueWatch console map
7. `docs/truewatch-owl.md` — OWL / MCP / CLI product rules for this lab
8. `AGENTS.md` — operating contract for every agent and human
9. Copy `.env.example` → `.env` locally (never commit `.env`)

```bash
git config core.hooksPath .githooks   # if not already set after clone
```

Credential and CLI steps live in the runbook (not duplicated here).

## Intended first-mile scope

- Ingest paths ([ADR-0001](docs/ADR/0001-three-ingest-paths.md) + [ADR-0003](docs/ADR/0003-otel-trace-path.md)): **DataKit**, **DataWay**, **DDTrace (metric+span)**, **OTel (metric+span)**
- Select path with `--mode` / `EMIT_MODE` ([ADR-0002](docs/ADR/0002-release-tags-and-emit-mode.md)): `dataway` (v0.0.1), `datakit` (v0.0.2), `ddtrace` (v0.0.3), `otel` (v0.0.4)
- Docker Compose preferred for a clean host; host `python3` OK for DataWay
- Visible data in TrueWatch Explorer per path
- Optional: one Monitor + one thin Dashboard (Dashboard writes via OWL CLI / console, not MCP)
- Optional: OWL MCP in Cursor with Bearer auth

```bash
set -a && source .env && set +a
python3 scripts/emit.py --mode dataway          # or: docker compose --env-file .env run --rm emit
# DataKit (needs Compose profile datakit — see docs/runbooks/datakit-emit.md):
# docker compose --profile datakit --env-file .env up -d datakit
# DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
```

## Security harness (inherited)

This repo keeps the aegis **Rule → Execution → Verification** controls. See
[`docs/SECURITY_PRACTICES.md`](docs/SECURITY_PRACTICES.md) and the root files `SECURITY.md`,
`AGENTS.md`, `.githooks/`, `.github/workflows/security-checks.yml`.

Status is written **only** in `docs/handoff/CURRENT.md` — never duplicate it in this README.

## License / visibility

Public learning lab. Synthetic data only.
