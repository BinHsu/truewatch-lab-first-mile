# Terraform — lab Monitor / Dashboard / N3 email (v0.2.0)

ADR: [`docs/ADR/0004-tf-json-closed-loop.md`](../ADR/0004-tf-json-closed-loop.md)  
Design: [`docs/design/monitor-dashboard-as-code.md`](../design/monitor-dashboard-as-code.md)

**Local state only** for this lab (`*.tfstate` gitignored). Forkers may add a remote `backend` block.

## Forker reminder — always load `.env` first

Terraform does **not** read `.env` by itself. Either:

```bash
bash scripts/tf-with-env.sh plan    # preferred: sources .env, sets TF_VAR_* / token
bash scripts/tf-with-env.sh apply # workspace write — confirm in agent sessions
```

or manually:

```bash
set -a && source .env && set +a
export TF_VAR_lab_alert_email="$LAB_ALERT_EMAIL"
export TRUEWATCH_ACCESS_TOKEN="${TRUEWATCH_ACCESS_TOKEN:-${OWL_TOKEN:-$OWL_API_KEY}}"
cd terraform && terraform plan
```

If you skip this, plan fails on missing `lab_alert_email` / access token.

## Prerequisites

- Terraform `>= 1.0`
- Copy `.env.example` → `.env`: `LAB_ALERT_EMAIL`, `OWL_TOKEN` (or `TRUEWATCH_ACCESS_TOKEN`)
- Open API endpoint for the site (default id1 in `variables.tf`; override with `TRUEWATCH_END_POINT` / `TF_VAR_truewatch_end_point`)

`terraform.tfvars.example` is optional file-based override; real `terraform.tfvars` stays gitignored.

## Plan (safe)

```bash
bash scripts/tf-with-env.sh init
bash scripts/tf-with-env.sh plan
```

Defaults: `enable_notify_chain=true`, `enable_dashboard=true`, **`enable_monitor=true`**
(checker designed in `json/monitor.checker.json` — review before first apply).

## Apply (workspace write — owner `confirm` required in agent sessions)

```bash
bash scripts/tf-with-env.sh apply
```

After apply: emit all four `EMIT_MODE`s at default **1.0** so the multi-series chart has
data (monitor should stay quiet). To **test email**, fault-inject one path with
`--ping 900` or `--value 900`, then wait for the 1m checker. Refine APM chart in console
if needed, re-export into `json/dashboard.json`, then `apply` again.

## Import (if local state was lost)

```bash
terraform import 'truewatch_notify_object.lab_email[0]' <notify_uuid>
terraform import 'truewatch_alert_policy.lab[0]' <altpl_uuid>
terraform import 'truewatch_dashboard.lab[0]' <dsbd_uuid>
# monitor when enabled:
# terraform import 'truewatch_monitor_json.lab[0]' <rul_uuid>
```

## JSON SSOT

| File | Role |
|---|---|
| `json/dashboard.json` | Dashboard B template (`template_info`) |
| `json/monitor.checker.json` | Multi-path fault inject `>=900` (quiet at normal 1.0; no nodata spam) |
