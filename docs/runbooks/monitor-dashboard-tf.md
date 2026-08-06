# Terraform — lab Monitor / Dashboard / N3 email (v0.2.0)

ADR: [`docs/ADR/0004-tf-json-closed-loop.md`](../ADR/0004-tf-json-closed-loop.md)  
Design: [`docs/design/monitor-dashboard-as-code.md`](../design/monitor-dashboard-as-code.md)

**Local state only** for this lab (`*.tfstate` gitignored). Forkers may add a remote `backend` block.

## Install Terraform

Need CLI `>= 1.0` on `PATH` (`terraform version`).

| Platform | Example |
|---|---|
| macOS (Homebrew) | Core formula may be absent (BSL). Use HashiCorp tap: `brew tap hashicorp/tap && brew install hashicorp/tap/terraform` |
| Other | [HashiCorp install docs](https://developer.hashicorp.com/terraform/install) or OpenTofu if you prefer a MPL client (same workflow; binary name may be `tofu`) |

## Agent `confirm` vs you running apply yourself

| Who | What “confirm” means |
|---|---|
| **Owner talking to a lab agent** | Type the word **`confirm`** so the agent may run a workspace write (`tf-with-env.sh apply`). This is a **repo safety gate**, not a Terraform flag. |
| **Forker / you in your own terminal** | No agent confirm. Run `plan` / `apply` yourself after prerequisites below. Terraform may still ask you to type `yes`, or use `-auto-approve`. |

## Forker reminder — always load `.env` first

Terraform does **not** read `.env` by itself. Either:

```bash
bash scripts/tf-with-env.sh plan    # preferred: sources .env, sets TF_VAR_* / token
bash scripts/tf-with-env.sh apply # workspace write (agent sessions need owner confirm first)
```

or manually:

```bash
set -a && source .env && set +a
export TF_VAR_lab_alert_email="$LAB_ALERT_EMAIL"
export TRUEWATCH_ACCESS_TOKEN="${TRUEWATCH_ACCESS_TOKEN:-${OWL_TOKEN:-$OWL_API_KEY}}"
cd terraform && terraform plan
```

If you skip this, plan fails on missing `lab_alert_email` / access token.

## Prerequisites (before `apply`)

1. Terraform installed (see above)
2. Copy `.env.example` → `.env` and set at least:
   - `LAB_ALERT_EMAIL`
   - `OWL_TOKEN` or `TRUEWATCH_ACCESS_TOKEN` (API Key **Secret**, write-capable for notify/monitor/dashboard)
3. Open API endpoint for the site (default id1 in `variables.tf`; override with `TRUEWATCH_END_POINT` / `TF_VAR_truewatch_end_point`)
4. Optional: understand local state will appear under `terraform/` and must not be committed

`terraform.tfvars.example` is optional file-based override; real `terraform.tfvars` stays gitignored.

## Plan (safe)

```bash
bash scripts/tf-with-env.sh init
bash scripts/tf-with-env.sh plan
```

Defaults: `enable_notify_chain=true`, `enable_dashboard=true`, **`enable_monitor=true`**.

**Notify tip:** `mailGroup` `to` must be a workspace **member UUID** (`acnt_…`). Set
`LAB_ALERT_MEMBER_UUID` in `.env` (see [`.env.example`](../../.env.example)). Bare external email
→ empty Console member list / no mail. Lab tips: [`docs/truewatch-tips.md`](../truewatch-tips.md).

Monitors are **four** `truewatch_monitor.lab["<path>"]` resources (dataway / datakit /
ddtrace / otel), each `simpleCheck` with alias **`Result`** and threshold **`>= 900`**.
A single checker with aliases `M1`–`M4` returned `ft.CheckObjectTargetAliasError` on id1
(`[VERIFIED]`). `json/monitor.checker.json` documents DQL per path only — HCL is authoritative.

## Apply (workspace write)

Needs owner **`confirm`** (agent) or intentional local apply. Non-interactive:

```bash
bash scripts/tf-with-env.sh apply -auto-approve -input=false
```

After apply: emit all four `EMIT_MODE`s (lab defaults **1/2/3/4** by path) so the
multi-series chart has data (monitors should stay quiet). Prefer
`bash scripts/emit-dashboard-demo.sh` for staggered x-axis. To **test email**, fault-inject
one path with `--value 900`, then wait for the 1m checker. Refine APM chart in console
if needed, re-export into `json/dashboard.json`, then `apply` again.

## Import (if local state was lost)

```bash
terraform import 'truewatch_notify_object.lab_email[0]' <notify_uuid>
terraform import 'truewatch_alert_policy.lab[0]' <altpl_uuid>
terraform import 'truewatch_dashboard.lab[0]' <dsbd_uuid>
terraform import 'truewatch_monitor.lab["dataway"]' <rul_uuid>
terraform import 'truewatch_monitor.lab["datakit"]' <rul_uuid>
terraform import 'truewatch_monitor.lab["ddtrace"]' <rul_uuid>
terraform import 'truewatch_monitor.lab["otel"]' <rul_uuid>
```

## JSON SSOT

| File | Role |
|---|---|
| `json/dashboard.json` | Dashboard B template (`template_info`) |
| `json/monitor.checker.json` | DQL reference per path; live checkers are in `monitor.tf` |
