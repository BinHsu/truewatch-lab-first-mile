# Runbook — OWL + Tobylike MCP in Cursor + CLI twin

Lab N4 / v0.3.0: **two MCP clients** (OWL + Tobylike legacy) plus a **CLI replay twin**.
MCP is an IDE wiring face — not new observability power. Design:
[`docs/design/mcp-dual-verify.md`](../design/mcp-dual-verify.md). Product rules:
[`docs/truewatch-owl.md`](../truewatch-owl.md).

Day-to-day prefer **OWL**. Tobylike is the ADR-0004 contrast track (different URL, auth, tools).

## 1. Credentials (same key as CLI)

1. Copy `.env.example` → `.env` if needed.
2. Set **`OWL_TOKEN`** (or `OWL_API_KEY`) = Management → **API Key Management** → Key **Secret**.
3. Confirm CLI first (cheaper failure mode than MCP):

```bash
set -a && source .env && set +a
owl whoami   # or: owl sync && owl exec owl.member.list -f json | head
```

## 2. Path A — CLI smoke (machine-replayable)

```bash
bash scripts/owl-readonly-smoke.sh
```

Expect `owl_readonly_smoke=OK` and non-empty metric windows when recent emit exists.
Record `finished_utc=…` in `docs/handoff/CURRENT.md`.

## 3. Path B — dual MCP (OWL + Tobylike)

### 3.1 Config template (no secrets in git)

Tracked example: [`.cursor/mcp.json.example`](../../.cursor/mcp.json.example) — **both** servers.

| Server key | URL | Auth header value |
|---|---|---|
| `truewatch-owl` | `https://id1-owl-mcp.truewatch.com/mcp` | `Bearer <API Key Secret>` |
| `truewatch-toby-legacy` | `https://us1-toby-ai.truewatch.com/toby_ai_mcp/mcp` | `<API Key Secret>;Endpoint=id2` |

Notes:

- There is **no** `id1-toby-ai.truewatch.com` DNS — Tobylike is a **global** host; workspace site is
  selected with **`Endpoint=<SITE_KEY>`**. For this lab’s id1 / Jakarta OpenAPI, SITE_KEY = **`id2`**
  (see legacy docs `SITE_KEY_MAP`).
- Copy example → local `.cursor/mcp.json` (gitignored) and substitute the real secret.
- Replayable HTTP twin (no Cursor required):

```bash
python3 scripts/mcp-dual-smoke.py
```

Expect `mcp_dual_smoke=OK`.

### 3.2 Intent → tools

| Intent | OWL MCP | Tobylike MCP |
|---|---|---|
| Handshake / list tools | `list_catalogs` → `list_tools` → `exec_tool` | Fixed 7 tools after session init |
| List lab monitors | `exec_tool` → `owl.monitor.list` search `lab-first-mile` | `list_checkers` (page; names include lab) |
| Query dataway ping ~2h | `exec_tool` → **`owl.data.simple_query`** (not `owl.data.query`) | `query_metric_data` with `dql` + `time_delta` ms |
| Create dashboard | **Refuse** — CLI/TF only | **Refuse** — `list_dashboards` is read-only here |

Absolute times in answers; empty series are valid if emit was not recent.

### 3.3 What “dual MCP verified” means

- OWL: Bearer + id1 OWL URL; monitor list + metric via `owl.data.simple_query`.
- Tobylike: composite auth with **`Endpoint=id2`**; `list_checkers` sees lab monitors;
  `query_metric_data` returns `last(ping)`.
- Bearer-only on Tobylike may initialize but **tool calls 401** against the wrong OpenAPI host —
  do not treat Bearer as sufficient for Tobylike on id1.

## 4. Side-by-side

| | OWL MCP (default) | Tobylike (legacy contrast) |
|---|---|---|
| Host | `https://id1-owl-mcp.truewatch.com/mcp` | `https://us1-toby-ai.truewatch.com/toby_ai_mcp/mcp` |
| Auth | `Authorization: Bearer …` | `Authorization: <key>;Endpoint=id2` |
| Tool shape | Wrapper + `owl.*` via `exec_tool` | Fixed names (see list below) |
| Session | Often works without `Mcp-Session-Id` | Needs session from `initialize` + `notifications/initialized` |
| Metric tool | `owl.data.simple_query` | `query_metric_data` |

Tobylike tools observed on id1 smoke (`guance-mcp-server` 1.21.0): `list_checkers`,
`list_logging_query_rules`, `list_dashboards`, `query_log_data`, `query_metric_data`,
`query_trace_data`, `query_rum_data`.

OWL MCP wrapper tools: `list_catalogs`, `list_tools`, `exec_tool` (then catalog `owl.*`).

## 5. Failure modes

| Symptom | Likely cause |
|---|---|
| MCP 401 | Client Token instead of API Key Secret |
| Tobylike tools 401 / `openapi.guance.com` | Missing `Endpoint=id2` (Bearer-only) |
| `id1-toby-ai` NXDOMAIN | Wrong host — use `us1-toby-ai…/toby_ai_mcp/mcp` |
| OWL `owl.data.query` not found | Use `owl.data.simple_query` (tips) |
| Query empty | No recent emit — `scripts/emit-dashboard-demo.sh` |
| Agent promises dashboard via MCP | Redirect to `owl` CLI / Terraform |

## 6. Related

- Credentials: [`owl-cli-credentials.md`](owl-cli-credentials.md)
- Tips: [`docs/truewatch-tips.md`](../truewatch-tips.md)
- Emit verify DQL: path runbooks under `docs/runbooks/*-emit.md`
