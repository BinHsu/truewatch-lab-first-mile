# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-06 — **v0.2.0** released:
https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.2.0
(`c04596f`). Next product slice when owner asks: **v0.3.0** OWL + Tobylike MCP.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `CHANGELOG.md` (v0.2.0)
3. `docs/truewatch-tips.md`
4. `docs/runbooks/monitor-dashboard-tf.md`
5. `README.md`

## 2. Last completed milestone

**v0.2.0 — TF+JSON closed loop + N3 email** (tag cut with this release).

| Tag / commit | Content |
|---|---|
| `v0.0.1`–`v0.1.1` | See GitHub releases |
| `v0.2.0` | Notify + policy + 4 monitors + dashboard; path values 1/2/3/4; tips; email verified |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`
- Local `terraform.tfstate` gitignored (do not commit)

## 4. Environment / system state

- Site **id1**; `.env` with OWL token, DataWay, **`LAB_ALERT_MEMBER_UUID`** (preferred) or member email
- DataKit Compose optional for ddtrace/otel/datakit paths

## 5. Commands already run / next

v0.2.0 apply + verify done on id1. Live UUIDs (workspace; may drift if replaced):

| Resource | UUID |
|---|---|
| notify | `notify_dee7b11f14bd4650ae45f75c71d743d4` |
| alert policy | `altpl_49144e885cbc43f3860680176b31c170` |
| dashboard | `dsbd_d6a2a584ba69436aa4d376ebcfd17676` |
| monitors | see `terraform output` / handoff history |

## 6. Test results

Four-path emit + DQL `[VERIFIED]`; N3 email after `dataway --value 900` `[VERIFIED]` 2026-08-06
(owner received mail). Details in prior handoff rows / `docs/truewatch-tips.md`.

## 7. Current blockers, in priority order

None for v0.2.0. Next product slice: **v0.3.0** OWL MCP + Tobylike MCP (not started).

## 8. AWAITING DECISION — owner only

None required for v0.2.0 cut.

## 9. Exact next safe action

Optional confirm:

```bash
git fetch --tags && git show v0.2.0 --stat
```

Start **v0.3.0** (OWL MCP + Tobylike) only when the owner asks.

## 10. Things that will bite you

- Never commit `.env`, `*.tfstate`, `terraform.tfvars`.
- mailGroup `to` = **`acnt_…`** (`LAB_ALERT_MEMBER_UUID`).
- Tips SSOT: [`docs/truewatch-tips.md`](../truewatch-tips.md) (agents append per `AGENTS.md`).
