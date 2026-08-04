# Runbook — DataKit emit (ADR-0001 path 1, release v0.0.2)

Send one synthetic metric to TrueWatch **through local DataKit** (HTTP
`:9529` → DataWay). Companion to
[`dataway-emit.md`](dataway-emit.md) (direct DataWay) and
[`owl-cli-credentials.md`](owl-cli-credentials.md) §5 (`DK_DATAWAY`).

**Never paste** `TRUEWATCH_WORKSPACE_TOKEN` or full `DK_DATAWAY` into chat/git.

Official references:
- Docker deploy: https://docs.truewatch.com/datakit/datakit-docker-deploy/
- HTTP write API: https://docs.truewatch.com/datakit/apis/

---

## Prerequisites

1. Local `.env` with `DK_DATAWAY` = `${DATAWAY_URL}?token=${TRUEWATCH_WORKSPACE_TOKEN}`
   (credentials runbook §5). Site for this lab: **id1**.
2. **Docker Compose** (preferred). This lab host may lack Docker — Compose files
   are still the forker contract; host DataKit install is an optional fallback
   ([host install](https://docs.truewatch.com/datakit/datakit-install/)).
3. Python 3 on `PATH` for host emit (stdlib only), or the Compose `emit` image.

---

## Steps (Compose)

### 1. Load env / confirm DK_DATAWAY shape

```bash
cd /path/to/truewatch-lab-first-mile
set -a && source .env && set +a
# Expect host only + token query; do not echo the token
python3 - <<'PY'
import os, urllib.parse
u = os.environ.get("DK_DATAWAY") or ""
p = urllib.parse.urlsplit(u)
print(f"dk_dataway_host={p.scheme}://{p.netloc}")
print("dk_dataway_token=set" if "token=" in (p.query or "") else "MISSING token in DK_DATAWAY")
PY
```

### 2. Start DataKit (profile `datakit`)

```bash
docker compose --profile datakit --env-file .env up -d datakit
docker compose --profile datakit --env-file .env ps
# Optional: docker compose --profile datakit --env-file .env exec datakit datakit monitor
```

Wait until healthy (`/v1/ping` on 9529). Image pin:
`pubrepo.truewatch.com/truewatch/datakit:2.7.1`.

Lab compose is **write-API oriented**: `ENV_DEFAULT_ENABLED_INPUTS=dk` only — no
privileged rootfs mounts. It is not a full host-metrics DataKit.

### 3. Dry-run emit (no POST)

Host Python (DataKit published on localhost:9529):

```bash
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit --dry-run
```

Compose (emitter reaches service name `datakit`):

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=datakit emit --dry-run
# or: … emit --mode datakit --dry-run
```

Expect `emit_mode=datakit`, `metric_url=…/v1/write/metric`, measurement
`truewatch_lab_first_mile`, tag `path=datakit`, and `dry_run=1`.

### 4. Live emit

```bash
# Host:
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit --also-log
# Compose:
docker compose --env-file .env run --rm -e EMIT_MODE=datakit emit
```

Expect `metric_http_status` in 2xx and `metric_post=OK`.

Local DataKit write URLs do **not** carry the workspace token; DataKit uses
`ENV_DATAWAY` / `DK_DATAWAY` for the upstream hop.

### 5. See it in the console (Group B)

1. TrueWatch console → Metrics / Explorer (or Metric Analysis).
2. Measurement **`truewatch_lab_first_mile`**, tag **`path=datakit`**.
3. Widen time range 15–30 minutes if empty.
4. Still empty → check DataKit logs, `DK_DATAWAY` site match, and step 4 HTTP status.

---

## What gets sent

| Field | Value |
|---|---|
| Measurement | `truewatch_lab_first_mile` |
| Tags | `path=datakit`, `service=lab-emitter`, `env=lab` |
| Field | `ping=<float>` (default `1.0`) |
| Local endpoint | `${DATAKIT_URL}/v1/write/metric` (default host `http://127.0.0.1:9529`) |
| Upstream | DataKit → `ENV_DATAWAY` (`DK_DATAWAY`) |

Synthetic demo data only.

---

## Env vars

| Var | Role |
|---|---|
| `DK_DATAWAY` | Required for Compose `datakit` → maps to `ENV_DATAWAY` |
| `DATAKIT_URL` | Emitter target; host default `http://127.0.0.1:9529`; Compose default `http://datakit:9529` |
| `EMIT_MODE` | Set to `datakit` or pass `--mode datakit` |

---

## Failure triage

| Symptom | Likely cause |
|---|---|
| `Cannot reach DataKit` | Container not up, wrong `DATAKIT_URL`, or port 9529 not published |
| Compose: `DK_DATAWAY` unset | Fill `.env` per credentials §5; use `--profile datakit` |
| Local 2xx but nothing in Explorer | Bad/mismatched `DK_DATAWAY` site/token; check DataKit monitor/logs |
| Healthcheck failing | Image pull / start_period; `docker compose … logs datakit` |
| Still `NOT-IMPLEMENTED` | Old checkout — need `scripts/emit_datakit.py` from v0.0.2+ |

---

## Related

- Direct DataWay (no DataKit): [`dataway-emit.md`](dataway-emit.md)
- Credentials: [`owl-cli-credentials.md`](owl-cli-credentials.md) §5
- Status: [`../handoff/CURRENT.md`](../handoff/CURRENT.md)
