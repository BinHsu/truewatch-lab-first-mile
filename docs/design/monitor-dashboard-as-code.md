# Design — Monitor / Dashboard as-code apply contract

> Open design note (`docs/design/`). Not an ADR until the owner accepts scope + this
> contract. Status: `docs/handoff/CURRENT.md`.

## Intent

Ship a reproducible Monitor + Dashboard (thin closed loop). For v0.2.0 with **N3** email
notify, prefer **TF + JSON + local state** so notify object → alert policy → monitor →
dashboard can share one chain. JSON + OWL CLI remains a documented alternative.

This note also records the CLI apply identity contract (path 1) and the release split.

`AWAITING DECISION`: monitor checker JSON finalization; APM chart polish; when to tag v0.2.0.

Release split **v0.2.0 / v0.3.0** and delivery **TF + JSON + local state**: **accepted**
([ADR-0004](../ADR/0004-tf-json-closed-loop.md)). Scaffold: `terraform/`.

---

## Proposed releases

| Tag | Scope | Notes |
|---|---|---|
| **v0.2.0** | Monitor + Dashboard (+ notify/policy for N3) via **TF + JSON**, **local** tfstate | Forkers may use another backend. CLI path 1 remains documented. No MCP required. |
| **v0.3.0** | **MCP: OWL + Tobylike (legacy)** | Document and exercise **both** clients. Day-to-day prefer OWL (`docs/truewatch-owl.md`); Tobylike is the legacy URL/auth compatibility track (composite `DF-API-KEY;Endpoint=…`). Dashboard create still CLI-only on both. |

v0.2.0 does **not** require MCP. v0.3.0 does **not** re-litigate Dashboard create via MCP (still unsupported).

Graduate tags into ADR-0002 addendum (or ADR-0004) when v0.2.0 work starts.

---

## Thin closed-loop content (**accepted** 2026-08-05)

### Dashboard — **B** (owner)

- **Metrics:** emit **all four** paths so each lands on its own metric series; show them on **one** time-series chart (multi-query / multi-series), not four disconnected boards as the primary view.
- **APM:** one additional Trace/APM chart (pick ddtrace and/or otel resource when authoring — still open detail).
- Title / name: `lab-first-mile` (or equivalent).

| Path | Typical Metrics signal |
|---|---|
| dataway / datakit LP | `M::truewatch_lab_first_mile` field `ping`, tag `path=…` |
| ddtrace | `M::truewatch` field `lab_first_mile_ping`, tag `path=ddtrace` |
| otel | `M::otel_service` field `truewatch_lab_first_mile.ping`, tag `path=otel` |

Verify recipe for the board: run each `EMIT_MODE` at least once (spaced emits OK) so all four series appear on the chart.

### Monitor + notify — **N3** (owner) + checker design (2026-08-05)

- Notify: `LAB_ALERT_EMAIL` → mailGroup; policy emails **`critical` only** (not `nodata`).
- Checker SSOT: `terraform/json/monitor.checker.json` (default enabled).
- **Multi-path:** four targets — dataway / datakit / ddtrace / otel (same series as the dashboard metrics chart).
- **Trigger:** any path `last(ping|value) >= 900` (`conditionLogic: or`). Lab default
  emit values are **1 / 2 / 3 / 4** by path (`scripts/lab_path_values.py`) → stay quiet.
- **Why not no-data:** stopping emit would keep firing / re-notify and email-bomb. Fault inject is intentional:
  - any path: `--value 900` (passthrough from `emit.py`)
- Empty `noDataTitle` / `noDataMessage`; do not rely on nodata for this lab.
- After first apply, console-export may rewrite JSON — re-commit export if needed.

---

## Preferred path (lab default for v0.2.0)

| Choice | Why |
|---|---|
| **TF + JSON + local state** (favored for N3) | Notify object + alert policy + monitor + dashboard in one tool chain; owner solo → no remote backend required |
| JSON + OWL CLI (path 1) | Still valid if avoiding TF; notify/policy often console/Open API then bind |
| Not MCP for Dashboard | OWL docs: dashboard create/replace are **CLI-only** |

### Terraform state policy (**accepted** 2026-08-05)

- **This lab (owner):** **local** `terraform.tfstate` only. Already gitignored (`*.tfstate`, `*.tfstate.*`, `**/.terraform/`).
- **No** required S3 / HCP / GitLab backend for the upstream repo.
- **Forkers:** choose their own backend (local, HCP Terraform Free, GitLab state, R2, …). Document in their fork; do not assume upstream state exists.
- Losing local state → explicit **`terraform import`** (or recreate); do not expect `plan` to auto-import.

---

## Apply contract (JSON + CLI)

### Monitor (`owl.monitor.upsert`)

| JSON has `rule_uuid`? | Action |
|---|---|
| **No** | Create: call `upsert` **without** `rule_uuid`. On success only, write returned uuid back into the JSON (or sidecar meta). |
| **Yes** | Update: call `upsert` **with** that `rule_uuid`. On failure, stop — do not invent a new uuid or fall back to create unless the operator explicitly chooses recreate. |

**Verified behaviour** `[VERIFIED]` 2026-08-05 (site workspace via local `owl` v1.1.1):

- Fake but well-formed id `rul_deadbeefdeadbeefdeadbeefdeadbeef`
- `owl.monitor.get` → `ft.NotFoundRuleInspector`
- `owl.monitor.upsert` with that `rule_uuid` + OuterEventChecker body → **same** `ft.NotFoundRuleInspector`
- No new monitor appeared in `owl.monitor.list` search

So OWL “upsert” here means: **if `rule_uuid` is provided, force update**; missing target → error, **not** create-with-that-id. True create = omit `rule_uuid`.

Also: CLI may print `Error:` while exiting **0** — apply scripts must parse the payload / error code, not trust exit status alone `[VERIFIED]` same probe.

### Dashboard (`owl.dashboard.create` / `replace`)

| Situation | Action |
|---|---|
| No uuid yet | `create` (optionally Open API `specifyDashboardUUID` = `dsbd_custom_` + 32 lowercase alnum). Persist uuid only after success. |
| Uuid present | `replace` with that `dashboard_uuid`. Failure → stop (no silent create). |

Do not treat dashboard as server-side upsert; tools are explicitly create + replace.

### Identity write-back rule

**Only write uuid into the repo file after the cloud accepts the create.**  
Failed calls must not mutate identity fields.

---

## Does Terraform (incl. TF + JSON) remove this problem?

**Mostly yes for the “did we create or update?” dance — the problem moves to state.**

| Concern | JSON + CLI (path 1) | Terraform / TF + `file(*.json)` |
|---|---|---|
| Know create vs update | Your script checks JSON for uuid | Provider + **state** decide; first apply create, later apply update |
| Persist id after create | You write uuid back to JSON | TF writes id into **state** (JSON content need not hold uuid) |
| Repeat apply | Safe if contract above is followed | Safe **while state is intact** |
| Lose tracking | Lose JSON uuid / meta → risk duplicate create | Lose **state** → same class of failure (orphan cloud objects, accidental second create) unless `import` / `specify_dashboard_uuid` |

So:

- TF does **not** magically delete identity concerns; it **centralises** them in `terraform.tfstate`.
- TF + JSON still uses the same JSON **content**; it does **not** require your small program’s write-back logic **if** state is trusted.
- Choosing TF to avoid write-back **uses local state in this lab** (see § Terraform state policy); forkers may point `backend` elsewhere.
- Path 1 → TF migration remains **content reuse + import**, never seamless.

`specify_dashboard_uuid` / stable identifiers can make TF (and CLI) less brittle, but empty/wrong state still hurts.

### Path 1 → TF + JSON is not a seamless upgrade

There is **no** zero-touch handoff. Terraform cannot “inherit” cloud objects that path 1 already created just because the JSON files exist.

| What migrates | What does not |
|---|---|
| Dashboard / monitor **JSON content** → `file()` / `template_info` / `checker_json` | “Already exists in the workspace” |
| Operator knowledge of uuids | An empty TF state that somehow knows those uuids |

**Required migration steps** (if resources already live in the workspace):

1. Point TF resources at the **same** JSON files.
2. **`terraform import`** each existing object (seed state with the real uuid) — **or** destroy the CLI-created objects and let TF create anew (explicit choice; destructive).
3. Only then rely on `plan` / `apply`.

Empty state + existing cloud resources ≈ path 1 without uuid write-back: risk of a **second** create. Document migrations as **“content reuse + one-time import”**, never as an automatic upgrade path.

---

## Out of scope here

- Exact chart queries / monitor thresholds for the lab ping series (separate when v0.2.0 starts).
- Deleting probe or lab monitors (needs explicit owner `confirm` each time).
- Implementing the apply script (only after the release plan is accepted).
- Full Cursor MCP client wiring details (belong in v0.3.0 runbook).

## Re-check trigger

- OWL renames upsert semantics or documents create-on-missing-uuid.
- Owner picks Terraform as the lab default for Monitor/Dashboard.
- Owner drops Tobylike from v0.3.0 (OWL-only) or rejects the 0.2 / 0.3 split.
