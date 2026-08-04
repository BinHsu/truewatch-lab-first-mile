# TrueWatch OWL guidance (synced from trial workspace)

Prefer the **OWL** stack. Do not treat the legacy Tobylike MCP page as current.

## Canonical sources

| Need | Source |
|------|--------|
| OWL overview | https://docs.truewatch.com/owl/ |
| MCP connect (current) | https://docs.truewatch.com/owl/mcp-quickstart/ |
| MCP tool catalog | https://docs.truewatch.com/owl/mcp-tools-reference/ |
| OWL CLI install | https://docs.truewatch.com/owl/install-owl/ |
| OWL CLI tools | https://docs.truewatch.com/owl/owl-cli-tools-reference/ |
| Agent diagnostics skill | https://github.com/TrueWatchTech/ai-skills/tree/main/owl-diagnostics |

## Do not use as primary docs

- https://docs.truewatch.com/mcp-server/ — stale Tobylike MCP guide (old endpoint + composite auth header). Same content is marked **Legacy** under https://docs.truewatch.com/owl/mcp-server/.
- Trust the **actual files** in `TrueWatchTech/ai-skills` over the repo About text. Today the repo only ships `owl-diagnostics` (diagnostics via local `owl` CLI). It does **not** currently ship dedicated skills for creating dashboards, monitors, DQL builders, or 3rd-party dashboard conversion—despite the repo description.

## Two integration paths (do not mix)

### A. OWL MCP Server (remote tools for MCP clients)

- Transport: `streamableHttp`
- Endpoint pattern (pick site of the workspace), e.g. Global Oregon: `https://us1-owl-mcp.truewatch.com/mcp`
- Auth header: `Authorization: Bearer <TrueWatch API Key>`
- Call pattern: `list_catalogs` → `list_tools` → `exec_tool` with `owl.*` tool names
- Time ranges: 13-digit millisecond timestamps
- **Dashboard tools are CLI-only**; they are not executable via MCP. Prefer OWL CLI (or console/OpenAPI) for dashboard create/replace.

### B. OWL CLI + `owl-diagnostics` skill (local agent workflow)

- Install/configure `owl`, set token (`OWL_TOKEN` / `OWL_API_KEY` = DF-API-KEY), run `owl sync`
- Skill: https://github.com/TrueWatchTech/ai-skills/tree/main/owl-diagnostics
- Depends on a working local `owl` binary—not on the legacy Tobylike MCP URL
- Prefer read-only tools; write ops (`create` / `replace` / `upsert` / `add` / …) only with explicit user intent
- For DQL: discover → `owl.data.check_dql` → `owl.data.query` only when `valid=true`
- Save diagnostic reports under `./owl-reports/` by default when using the skill

## Legacy vs current

| | Legacy `/mcp-server/` | Current OWL MCP |
|--|----------------------|-----------------|
| URL example | `https://us1-toby-ai.truewatch.com/toby_ai_mcp/mcp` | `https://us1-owl-mcp.truewatch.com/mcp` |
| Auth | `Authorization=DF-API-KEY;Endpoint=SITE_KEY` | `Authorization: Bearer <API Key>` |
| Tools | Fixed high-level names (Monitor Management, Log Query, …) | Wrapper + `owl.*` via `exec_tool` |

If docs disagree, prefer OWL Quick Start / MCP Tools Reference over `/mcp-server/`.

## Working rules for this lab

1. When advising MCP setup, use **OWL MCP** endpoints and **Bearer** auth—never the Tobylike URL or composite `Endpoint=SITE_KEY` header unless the owner explicitly asks about legacy compatibility.
2. For observability diagnostics, prefer `owl-diagnostics` + local `owl` if available; otherwise use OWL MCP read tools.
3. Do not promise dashboard creation/conversion via MCP or via missing skills; state CLI vs MCP vs console limitations clearly.
4. Never commit API keys, `OWL_TOKEN`, or Bearer tokens into this repo.
5. Cite absolute times in answers (not only “last 15 minutes”). Empty results are valid—report scope and emptiness.
