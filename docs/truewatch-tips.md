# TrueWatch tips (lab-verified)

> Living **gotcha / tip** sheet for this lab. Not status (`docs/handoff/CURRENT.md`).
> Not a substitute for product docs — prefer [TrueWatch docs](https://docs.truewatch.com/) and
> [`docs/truewatch-owl.md`](truewatch-owl.md) for OWL/MCP rules.
>
> **Agents (required):** when you verify a TrueWatch/Console/OpenAPI/OWL behaviour that docs or the
> UI do not make obvious, **append a tip here in the same change**. Policy:
> [`AGENTS.md`](../AGENTS.md) (“TrueWatch lab tips” + §13). Do **not** create a second tips file;
> do **not** leave the finding only in chat or handoff.
>
> **What belongs here:** settings and behaviours the **product UI / docs do not spell out
> clearly** (or that contradict a naive reading), that this lab verified on **id1**. Examples:
> wrong token type still “looks like a key”, API accepts a field the Console never resolves,
> same metric name collapses in Metric Analysis, OWL tool name ≠ upsert semantics.
>
> **How to add a tip:** one short heading, what bites you, the fix, evidence tag + date/site when
> known. Keep secrets out (no emails, tokens, or full `acnt_` dumps in examples — use shapes).

Site used for most rows below: **id1**.

---

## Console & visibility

### Dashboard created by API Key but missing from Console list

**Symptom:** Terraform/OpenAPI shows the dashboard; **Scenarios → Dashboards** is empty (All = 0).
Tags like `lab-first-mile` may still appear in filters.

**Cause:** `is_public = 0` → private to the **API Key** creator (`wsak_…`), not your login user.

**Fix:** set `is_public = 1` on `truewatch_dashboard` (this lab: `terraform/dashboard.tf`), then
`bash scripts/tf-with-env.sh apply`.

`[VERIFIED]` 2026-08-06 id1 — after `0→1`, `lab-first-mile` appeared in the list.

---

## Notify / mailGroup (N3)

### mailGroup `to` must be a workspace **member id**, not an arbitrary email

**Symptom:** Notification Targets shows `lab-first-mile-mail` but **member list empty**; Monitor
events fire (`critical`) but **no email**. OpenAPI `optSet.to` may still show an email string.

**Cause:** `type=mailGroup` expects **workspace members** (Member Management). Product docs call
`to` a member account list. A bare external address can be stored by the API without resolving in
the Console UI or delivering mail.

**Fix:**

1. `owl exec owl.member.list` (or Management → Members) → take **`member_uuid`** shaped like
   `acnt_…` (or a member email that already appears in that list).
2. Put it in `.env` as **`LAB_ALERT_MEMBER_UUID=acnt_…`** (preferred).  
   `scripts/tf-with-env.sh` sets `TF_VAR_lab_alert_email` from `LAB_ALERT_MEMBER_UUID` first, else
   `LAB_ALERT_EMAIL`.
3. Replace/apply the notify object so alert policy still points at the new notify UUID.

**Do not** treat “email string in OpenAPI” as “Console member bound.”

`[VERIFIED]` 2026-08-06 id1 — email-only `to` → empty UI / no mail; `to=[acnt_…]` for member
`bin.hsu` → Console showed the member; fault inject `dataway --value 900` → critical event →
**owner received email**.

Official: [Notification Targets](https://docs.truewatch.com/monitoring/notify-target/),
[notify-object create](https://docs.truewatch.com/open-api/notify-object/create/) (`mailGroup` /
`optSet.to`).

---

## Metrics / Console compare

### Shared measurement needs **`by path`** (or a path filter)

**Symptom:** Metric Analysis on `truewatch_lab_first_mile` + `ping` + Avg shows **one** series;
looks like dataway or datakit failed.

**Cause:** dataway and datakit share one measurement/field; empty **by Label** collapses them.

**Fix:** set **by `path`**, or filter `path=dataway` / `path=datakit`. Identity is the **`path`**
tag. Lab default emit values are **1 / 2 / 3 / 4** by path (`scripts/lab_path_values.py`) for
y-axis separation; stagger with `bash scripts/emit-dashboard-demo.sh`.

See README: [Compare all four in the web console](../README.md#compare-all-four-in-the-web-console).

`[VERIFIED]` 2026-08-06 id1.

### StatsD name ≠ line-protocol measurement

**Symptom:** ddtrace metric is under measurement **`truewatch`**, field **`lab_first_mile_ping`**,
not `truewatch_lab_first_mile` / `ping`.

**Cause:** StatsD packet `truewatch_lab_first_mile.ping` is split by DataKit differently than LP.

**Fix:** query / dashboard DQL for that mapping; still filter **`path=ddtrace`**. Prefer Compose
`emit` for StatsD (host→`:8125` can miss).

`[VERIFIED]` 2026-08-05/06 id1 — see `docs/runbooks/ddtrace-emit.md`.

### Host StatsD OK locally ≠ metric in workspace

**Symptom:** `statsd_send=OK` from host Python, traces appear, but `M::truewatch` /
`lab_first_mile_ping` stays empty for minutes.

**Cause:** UDP to published `8125` can fail silently or never flush the same as the Compose
network path `datakit:8125`.

**Fix:** verify ddtrace **metrics** with  
`docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit`.

`[VERIFIED]` 2026-08-06 id1.

### Do not confuse lab series with measurement **`dk`**

**Symptom:** Explorer shows huge numbers / many fields; no `ping≈1`.

**Cause:** DataKit self-metrics measurement **`dk`** (Compose enables `dk` input). Lab LP series
is still **`truewatch_lab_first_mile`**.

**Fix:** filter lab measurement + `path=datakit` (or dataway). See `docs/runbooks/datakit-emit.md`.

`[VERIFIED]` 2026-08-04 id1.

### OTLP HTTP on DataKit is **protobuf only**

**Symptom:** OTLP JSON posts fail or never land; metric not under LP measurement names.

**Cause:** DataKit `:9529/otel/v1/{metrics,traces}` expects protobuf. After ingest, gauges often
sit on **`otel_service`** with field **`truewatch_lab_first_mile.ping`** (dots kept).

**Fix:** use lab Compose emit (`opentelemetry-proto`); query that measurement/field + `path=otel`.

`[VERIFIED]` 2026-08-05 id1 — `docs/runbooks/otel-emit.md`.

### Hyphenated APM service names need quotes in DQL

**Symptom:** empty `T::` results for `lab-emitter`.

**Fix:** quote the service: `T::'lab-emitter':(…)`.

`[VERIFIED]` in ddtrace/otel runbooks.

---

## Auth / credentials

### OWL / Open API needs **API Key Secret**, not RUM Client Token

**Symptom:** `401 ft.InvalidAPIKey` with a Client Token.

**Fix:** Management → **API Key Management** → Key (Secret) → `OWL_TOKEN`. Client Tokens are
RUM-only.

`[VERIFIED]` 2026-08-04 — `docs/runbooks/owl-cli-credentials.md`, `docs/truewatch-owl.md`.

### DataWay Cloudflare **1010** on default Python User-Agent

**Symptom:** HTTP 403 / CF error 1010 posting to `id1-openway`.

**Fix:** lab emitters set a lab User-Agent (`scripts/emit_dataway.py`); do not strip it.

`[VERIFIED]` 2026-08-04 — `docs/runbooks/dataway-emit.md`.

---

## Monitors (Terraform)

### Multi-alias one `simpleCheck` may fail create

**Symptom:** `ft.CheckObjectTargetAliasError` when one checker has aliases `M1`–`M4`.

**Fix:** this lab uses **four** monitors (`for_each` path), each with alias **`Result`**, threshold
`>= 900`. See `terraform/monitor.tf`.

`[VERIFIED]` 2026-08-06 id1.

### OWL `monitor.upsert` with a made-up `rule_uuid` does **not** create

**Symptom:** expect create-or-update; get `ft.NotFoundRuleInspector` instead.

**Cause:** with `rule_uuid` set, OWL forces **update**. Missing rule → error, not create-with-that-id.

**Fix:** create = **omit** `rule_uuid`; update = pass a real one. Also: CLI may print `Error:` and
still exit **0** — parse payload, do not trust exit code alone.

`[VERIFIED]` 2026-08-05 — `docs/design/monitor-dashboard-as-code.md`.

### Dashboard create/replace is **CLI/OpenAPI**, not MCP

**Symptom:** MCP catalog has no usable dashboard create path (or tools are CLI-only).

**Fix:** Terraform / OWL CLI / Console. Do not promise MCP dashboard writes.

See `docs/truewatch-owl.md`.

### MCP metric query ≠ CLI `owl.data.query` (id1)

**Symptom:** via OWL MCP `exec_tool`, `owl.data.query` / `owl.data.check_dql` return
`Tool '…' not found`. CLI `owl exec owl.data.query` works on the same key.

**Cause:** id1 MCP `data` catalog exposes **`owl.data.simple_query`** (assembled DQL), not the
full-DQL `owl.data.query` tool. Docs may still mention `owl.data.query` for complex DQL.

**Fix (MCP):** `exec_tool` → `owl.data.simple_query` with `namespace`, `source`,
`select_clause`, `where_clause`, `start_time`, `end_time` (ms). Example lab ping:

`namespace=M`, `source=truewatch_lab_first_mile`, `select_clause=last(ping), count(ping)`,
`where_clause=path = 'dataway'`.

**Fix (replayable twin):** keep using CLI `owl.data.query` in `scripts/owl-readonly-smoke.sh`.

`[VERIFIED]` 2026-08-06T08:08:54Z id1 — MCP simple_query `last(ping)=1` / `count=7`;
`owl.monitor.list` search `lab-first-mile` → 4 rules. Handshake `initialize` → server
`owl-registry` 1.0.0.

### Tobylike MCP is global host + SITE_KEY (not `id1-toby-ai`)

**Symptom:** `id1-toby-ai.truewatch.com` does not resolve. Or Tobylike `initialize` works with
Bearer, but `list_checkers` / `query_metric_data` return 401 against `openapi.guance.com`.

**Cause:** Legacy Tobylike MCP is served from **`https://us1-toby-ai.truewatch.com/toby_ai_mcp/mcp`**.
Workspace routing uses composite auth **`Authorization: <API Key Secret>;Endpoint=<SITE_KEY>`**.
For Indonesia / id1 OpenAPI, SITE_KEY = **`id2`** (`SITE_KEY_MAP` in legacy MCP docs). Bearer-only
is enough for OWL, **not** for Tobylike tool calls on this lab.

**Also:** Tobylike needs `Mcp-Session-Id` from `initialize` (then `notifications/initialized`)
before `tools/list` / `tools/call`. Tool names are fixed (`list_checkers`, `query_metric_data`, …),
not `owl.*`.

**Fix:** dual config in `.cursor/mcp.json.example`; replay with `python3 scripts/mcp-dual-smoke.py`.

`[VERIFIED]` 2026-08-06T08:13:31Z — Tobylike `guance-mcp-server` 1.21.0; 4 lab checkers;
`query_metric_data` `last(ping)=1` / `count=7` with `Endpoint=id2`. Bearer-only tool calls 401.

---

## Related lab docs

| Doc | Role |
|---|---|
| [`truewatch-owl.md`](truewatch-owl.md) | OWL / MCP / CLI rules |
| [`runbooks/owl-mcp-cursor.md`](runbooks/owl-mcp-cursor.md) | Cursor MCP + dual smoke |
| [`runbooks/monitor-dashboard-tf.md`](runbooks/monitor-dashboard-tf.md) | TF apply closed loop |
| [`runbooks/owl-cli-credentials.md`](runbooks/owl-cli-credentials.md) | Credentials → `.env` |
| [`observability-glossary.md`](observability-glossary.md) | Console ↔ signal map |
| [`handoff/CURRENT.md`](handoff/CURRENT.md) | Status only |
