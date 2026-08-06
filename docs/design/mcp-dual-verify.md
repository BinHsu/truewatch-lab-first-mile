# Design — N4 / v0.3.0 MCP showcase (CLI + OWL + Tobylike)

> Open design note (`docs/design/`). Status: `docs/handoff/CURRENT.md`.
> Relates: [ADR-0004](../ADR/0004-tf-json-closed-loop.md), [`docs/truewatch-owl.md`](../truewatch-owl.md).

## Intent

Show **MCP as an IDE/agent wiring face** for tools the lab already reaches via CLI — not a new
observability capability. Exercise **both** MCP stacks named in ADR-0004. Dashboard create remains
out of scope (MCP cannot).

**Owner direction:**

1. CLI smoke + MCP smoke (2026-08-06).
2. MCP must cover **Toby + OWL** (same day).

| Path | What it proves | Replayable? |
|---|---|---|
| **A. CLI smoke** | `owl exec` read-only twin | `scripts/owl-readonly-smoke.sh` |
| **B1. OWL MCP** | Bearer + id1 OWL endpoint; `owl.*` via wrapper | `scripts/mcp-dual-smoke.py` |
| **B2. Tobylike MCP** | Global toby host + `Endpoint=id2`; fixed tool names | same script |

## GitHub deliverables (thin)

- `.cursor/mcp.json.example` — OWL + Tobylike (no secrets)
- `docs/runbooks/owl-mcp-cursor.md` — wire Cursor + intent→tool map for both
- `scripts/owl-readonly-smoke.sh` — CLI twin
- `scripts/mcp-dual-smoke.py` — OWL + Tobylike HTTP twin
- Tips for gotchas → `docs/truewatch-tips.md`

## Acceptance (smoke evidence 2026-08-06)

1. CLI: `[VERIFIED]` `2026-08-06T08:07:30Z` (handoff).
2. OWL MCP: `[VERIFIED]` `2026-08-06T08:08:54Z` / dual script `08:13:31Z`.
3. Tobylike MCP: `[VERIFIED]` `2026-08-06T08:13:31Z` (`Endpoint=id2`).
4. Docs: CLI = automation SSOT; MCP = agent/IDE; Tobylike = legacy contrast only day-to-day.

**Owner 2026-08-06:** cut as **v0.3.0** (commit + CHANGELOG + GitHub release).

## Non-goals

- MCP write path for dashboard / notify / monitor create
- Replacing `terraform/` or emit scripts
- Recommending Tobylike as the default (OWL wins for new work)
