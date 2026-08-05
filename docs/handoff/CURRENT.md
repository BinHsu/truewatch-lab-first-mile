# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **v0.2.0 opened:** ADR-0004 + `terraform/` scaffold (TF+JSON,
local state). Monitor gated off until checker JSON is validated. No cloud `apply` yet.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `docs/ADR/0004-tf-json-closed-loop.md`
3. `docs/runbooks/monitor-dashboard-tf.md`
4. `docs/design/monitor-dashboard-as-code.md`
5. `README.md` / `CHANGELOG.md`

## 2. Last completed milestone

**v0.1.1 — Docs close-out.** **v0.2.0 in progress** (scaffold only).

| Tag / commit | Content |
|---|---|
| `v0.0.1`–`v0.1.1` | See prior rows / GitHub releases |
| *(wip)* `v0.2.0` | TF+JSON closed loop scaffold under `terraform/` |

## 3. Repository state

- Branch: `main` (uncommitted scaffold until owner commits)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; set `LAB_ALERT_EMAIL`, `TRUEWATCH_ACCESS_TOKEN` / `OWL_TOKEN`,
  `TRUEWATCH_END_POINT=https://id1-openapi.truewatch.com` in `.env` (gitignored).

## 5. Commands already run / next

Scaffold written. Optional local:

```bash
cd terraform && terraform init && terraform plan
# apply only after owner confirm — workspace write
```

## 6. Test results

- Prior ingest / payload UT `[VERIFIED]`.
- Upsert missing-uuid probe `[VERIFIED]` (design note).
- TF plan/apply against id1: **not run** this segment.

## 7. Current blockers, in priority order

1. Owner: fill `.env` / `terraform.tfvars`, `terraform plan`, then `confirm` before `apply`.
2. Validate checker after first apply (console export back into JSON if provider rewrites).
3. Refine APM chart (console export) after metrics chart works.

## 8. AWAITING DECISION — owner only

1. Optional polish after first apply: monitor threshold / no-data behavior; APM chart.
2. When to cut git tag **v0.2.0** (after successful apply + emit verify).

## 9. Exact next safe action

```bash
bash scripts/tf-with-env.sh init
bash scripts/tf-with-env.sh plan
```

Then owner types **`confirm`** before `bash scripts/tf-with-env.sh apply`.

## 10. Things that will bite you

- Never commit `.env`, `*.tfstate`, `terraform.tfvars`.
- `enable_monitor` defaults **true** (checker in `json/monitor.checker.json` — review before apply).
- Losing local state → `terraform import` (runbook).
