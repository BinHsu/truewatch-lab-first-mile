# Runbook — DataWay direct emit (ADR-0001 path 2)

Send one synthetic metric to TrueWatch **without DataKit**, using the workspace
DataWay write API. Companion to
[`owl-cli-credentials.md`](owl-cli-credentials.md) §5 (Workspace Token +
`DATAWAY_URL`).

**Never paste** `TRUEWATCH_WORKSPACE_TOKEN` or full `DK_DATAWAY` into chat/git.

---

## Prerequisites

1. Local `.env` filled per credentials runbook §5:
   - `TRUEWATCH_WORKSPACE_TOKEN` (usually `tkn_…`)
   - `DATAWAY_URL` (this lab: `https://id1-openway.truewatch.com`)
   - optional: `DK_DATAWAY` (same host + `?token=…`)
2. Python 3 on `PATH` (stdlib only; no pip install).
3. Network can reach the DataWay host over HTTPS.

---

## Steps

Prefer **Docker Compose** when Docker is installed (cleaner host). Host Python 3
is the fallback (stdlib only; verified on the lab machine for v0.0.1).

### 1. Load env

```bash
cd /path/to/truewatch-lab-first-mile
set -a && source .env && set +a
echo "dataway=${DATAWAY_URL}"
test -n "${TRUEWATCH_WORKSPACE_TOKEN}" && echo "workspace_token=set" || echo "MISSING"
```

### 2. Dry-run (no POST)

Host:

```bash
EMIT_MODE=dataway python3 scripts/emit.py --dry-run
# or call the mode script: python3 scripts/emit_dataway.py --dry-run
```

Compose (omit `--profile datakit` → no DataKit container):

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit --dry-run
```

Expect `emit_mode=dataway`, redacted URL (`token=***`), measurement
`truewatch_lab_first_mile`, and `dry_run=1`.

### 3. Live emit

```bash
EMIT_MODE=dataway python3 scripts/emit.py
EMIT_MODE=dataway python3 scripts/emit.py --also-log
# Compose:
docker compose --env-file .env run --rm -e EMIT_MODE=dataway emit
# Distinct Metrics points: --count 2 (default 5s between shots)
```

Expect `metric_http_status` in 2xx and `metric_post=OK`.

Script never prints the raw token.

### 4. See it in the console (Group B)

1. TrueWatch console → Metrics / Explorer (or Metric Analysis).
2. Measurement **`truewatch_lab_first_mile`**, field **`ping`**, tag **`path=dataway`**.
3. Widen time range to the last 15–30 minutes if empty; ingest can lag briefly.
4. Empty result after several minutes → re-check token, `DATAWAY_URL` site match,
   and HTTP status from step 3.

**Comparing with `datakit`:** both use the same measurement + field. In Metric
Analysis, set **`by path`** (or filter `path=dataway` alone). Leaving **`by Label`
empty** with Avg collapses dataway + datakit into one row — that is not a failed
emit. Four-path console map: [`README.md`](../../README.md#compare-all-four-in-the-web-console).

Optional later: confirm with OWL CLI / DQL once a query path is documented for
this measurement (OWL was verified with `owl sync` only so far).

---

## What gets sent

| Field | Value |
|---|---|
| Measurement | `truewatch_lab_first_mile` |
| Tags | `path=dataway`, `service=lab-emitter`, `env=lab` |
| Field | `ping=<float>` (default **`1.0`** for dataway; see `scripts/lab_path_values.py`) |
| Endpoint | `${DATAWAY_URL}/v1/write/metric?token=…` |

Synthetic demo data only — no customer payloads.

---

## Failure triage

| Symptom | Likely cause |
|---|---|
| `Missing ingest env` | `.env` not sourced or keys empty |
| HTTP 401 / 403 with body `error code: 1010` | Cloudflare Browser Integrity Check blocked the client User-Agent. Default `Python-urllib/*` is blocked on `id1-openway` `[VERIFIED]` 2026-08-04. `scripts/emit_dataway.py` sets a lab User-Agent; do not strip it. |
| HTTP 401 / 403 without 1010 | Wrong Workspace Token, or IP allowlist on data reporting |
| HTTP 404 on host | Wrong `DATAWAY_URL` for site |
| `metric_post=OK` but nothing in UI | Wrong workspace, delay, or filter mismatch |

---

## Next after this path works

- DataKit: [`datakit-emit.md`](datakit-emit.md) (`EMIT_MODE=datakit`, v0.0.2)
- DDTrace: [`ddtrace-emit.md`](ddtrace-emit.md) (`EMIT_MODE=ddtrace`, v0.0.3)
- OTel: [`otel-emit.md`](otel-emit.md) (`EMIT_MODE=otel`, v0.0.4)
- Closed loop / MCP: [`monitor-dashboard-tf.md`](monitor-dashboard-tf.md), [`owl-mcp-cursor.md`](owl-mcp-cursor.md)

Status: `docs/handoff/CURRENT.md`.
