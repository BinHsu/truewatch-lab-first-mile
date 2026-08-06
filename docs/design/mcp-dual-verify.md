# Design — N4 / v0.3.0 MCP showcase (CLI + OWL + Tobylike)

> Design note (`docs/design/`). **Accepted / shipped as v0.3.0.** Live status:
> `docs/handoff/CURRENT.md`. Relates: [ADR-0004](../ADR/0004-tf-json-closed-loop.md),
> [`docs/truewatch-owl.md`](../truewatch-owl.md).

## Intent

Show **MCP as an IDE/agent wiring face** for tools the lab already reaches via CLI — not a new
observability capability. Exercise **both** MCP stacks named in ADR-0004. Dashboard create remains
out of scope (MCP cannot).

| Path | What it proves | Replayable? |
|---|---|---|
| **A. CLI smoke** | `owl exec` read-only twin | `scripts/owl-readonly-smoke.sh` |
| **B1. OWL MCP** | Bearer + id1 OWL endpoint; `owl.*` via wrapper | `scripts/mcp-dual-smoke.py` |
| **B2. Tobylike MCP** | Global toby host + `Endpoint=id2`; fixed tool names | same script |

## GitHub deliverables

- `.cursor/mcp.json.example` — OWL + Tobylike (no secrets)
- `docs/runbooks/owl-mcp-cursor.md` — wire Cursor + intent→tool map for both
- `scripts/owl-readonly-smoke.sh` — CLI twin
- `scripts/mcp-dual-smoke.py` — OWL + Tobylike HTTP twin
- Tips for gotchas → `docs/truewatch-tips.md`

## Acceptance

Smokes and cut recorded in handoff / `CHANGELOG.md` (2026-08-06). Do not duplicate live results here.

## Non-goals

- MCP write path for dashboard / notify / monitor create
- Replacing `terraform/` or emit scripts
- Recommending Tobylike as the default (OWL wins for new work)
