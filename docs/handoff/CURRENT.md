# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-06 — **v0.3.0** released:
https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.3.0
(tag commit `3d6c4d0`).

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `CHANGELOG.md` (v0.3.0)
3. `docs/runbooks/owl-mcp-cursor.md`
4. `docs/truewatch-tips.md`
5. `README.md`

## 2. Last completed milestone

**v0.3.0 — OWL MCP + Tobylike MCP + CLI twin** (tag cut with this release).

| Tag / commit | Content |
|---|---|
| `v0.0.1`–`v0.1.1` | See GitHub releases |
| `v0.2.0` | Notify + policy + 4 monitors + dashboard; path values; N3 email |
| `v0.3.0` (`3d6c4d0`) | OWL + Tobylike MCP dual smoke; CLI/HTTP twins; runbook + tips |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`
- Local `.cursor/mcp.json` / `.env` / tfstate stay gitignored

## 4. Environment / system state

- Site **id1**; Tobylike SITE_KEY **`id2`**

## 5. Commands already run / next

v0.3.0 pushed + tagged. Live TF UUIDs from v0.2.0 (may drift if replaced):

| Resource | UUID |
|---|---|
| notify | `notify_dee7b11f14bd4650ae45f75c71d743d4` |
| alert policy | `altpl_49144e885cbc43f3860680176b31c170` |
| dashboard | `dsbd_d6a2a584ba69436aa4d376ebcfd17676` |
| monitors | see `terraform output` |

## 6. Test results

**Path A — CLI** `[VERIFIED]` `2026-08-06T08:07:30Z` — four paths 1/2/3/4; 4 monitors.

**Path B1 — OWL MCP** `[VERIFIED]` — `owl-registry` 1.0.0; `owl.monitor.list`; `owl.data.simple_query`.

**Path B2 — Tobylike MCP** `[VERIFIED]` `2026-08-06T08:13:31Z` —
`us1-toby-ai` + `Endpoint=id2`; `list_checkers`; `query_metric_data` last=1/count=7.

## 7. Current blockers, in priority order

None for v0.3.0.

## 8. AWAITING DECISION — owner only

None required for this cut. Next product tag TBD by owner.

## 9. Exact next safe action

Optional confirm:

```bash
git fetch --tags && git show v0.3.0 --stat
bash scripts/owl-readonly-smoke.sh
python3 scripts/mcp-dual-smoke.py
```

## 10. Things that will bite you

- Never commit `.env`, `.cursor/mcp.json`, `*.tfstate`, `terraform.tfvars`.
- Tobylike: **`Endpoint=id2`**, global `us1-toby-ai` host.
- OWL MCP metrics: **`owl.data.simple_query`**, not `owl.data.query`.
- Dashboard create is **not** via MCP.
- Tips SSOT: [`docs/truewatch-tips.md`](../truewatch-tips.md).
