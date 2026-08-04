# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-04 — bootstrap from `BinHsu/aegis-template` + sync TrueWatch OWL notes from trial workspace; handoff ready for Open Folder

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md`
3. `AGENTS.md`
4. `docs/truewatch-owl.md`
5. `docs/FILE-MAP.md` (before creating any new file)

`docs/ADR/INDEX.md` is referenced by the scaffold but **does not exist yet** — create `docs/ADR/` when the first decision is recorded.

You do **not** need any conversation history. If something here is unclear, that is a defect in this
file — fix it rather than guessing.

## 2. Last completed milestone

Repo bootstrapped as a public GitHub project from the aegis template. TrueWatch OWL integration guidance synced into `docs/truewatch-owl.md`. Project identity placeholders filled in `AGENTS.md` / `CLAUDE.md` / `README.md` / `SECURITY.md`. Local git hooks path set. **No synthetic emitter or DataKit wiring yet.**

| Commit | Content |
|---|---|
| `c838e64` | Initial commit (from `BinHsu/aegis-template`) |
| `7eaacf5` | Sync OWL docs + fill project placeholders + this handoff |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Visibility: **public**
- Hooks active: `git config core.hooksPath .githooks` → **yes** (set after clone)
- Local path is machine-specific and deliberately not recorded here.

## 4. Environment / system state

- TrueWatch test workspace / API Key: owner has a PDSA trial account; **credentials are not in this repo** `[ASSUMED]` until `.env` is created locally from `.env.example`.
- DataKit / OWL CLI / OWL MCP: **not installed or verified in this repo yet** `[UNVERIFIED]`.
- Synthetic emitter: **not written yet**.
- Prior scratch notes lived in a separate Cursor workspace (`bin.hsu.truewatch.trial`); canonical continuity is this repo after Open Folder.

## 5. Commands already run

```bash
gh repo create truewatch-lab-first-mile --template BinHsu/aegis-template --public --clone
# (clone landed under the owner's Documents directory)
git config core.hooksPath .githooks
gh repo view --json name,url,visibility
# → PUBLIC https://github.com/BinHsu/truewatch-lab-first-mile
```

## 6. Test results

- Scaffold security scripts / CI: **not run** in this handoff cycle.
- TrueWatch ingest / DQL / Monitor / Dashboard: **not run** (no emitter yet).

## 7. Current blockers, in priority order

1. Owner must **Open Folder** on this repo in Cursor so subsequent agent work targets the correct workspace (not the trial scratch folder).
2. Site / API Key / DataKit install base URL still need owner input before live ingest.
3. First-mile emitter + loop acceptance criteria not implemented.

## 8. AWAITING DECISION — owner only

Do not resolve these by inference. They are recorded, not forgotten.

1. TrueWatch **site / OWL MCP endpoint** for the test workspace (e.g. `us1-owl-mcp.truewatch.com`).
2. Ingest path for the emitter: DataKit (preferred for realism) vs direct/custom push for the first slice.
3. Whether Day-1 scope includes a Monitor trigger + Dashboard JSON, or emitter + Explorer visibility only.

## 9. Exact next safe action

```bash
# After Cursor → File → Open Folder on this repository:
# 1) Confirm hooks still set
git config --get core.hooksPath
# expect: .githooks

# 2) Start the first-mile workload (no secrets in git):
#    create emitter under services/ or scripts/ per FILE-MAP update in same change
#    copy .env.example → .env locally and fill TrueWatch token (never commit .env)
ls README.md docs/truewatch-owl.md docs/handoff/CURRENT.md
```

Next implementation milestone (after Open Folder): add a short-lived synthetic metric/log emitter (Docker or plain Python), document how to see data in TrueWatch Explorer, keep secrets in `.env` only.

## 10. Things that will bite you

- **Wrong Cursor workspace:** continuing in `bin.hsu.truewatch.trial` edits the scratch folder, not this public repo. Open this folder first.
- **Legacy MCP docs:** https://docs.truewatch.com/mcp-server/ is stale; use OWL docs in `docs/truewatch-owl.md`.
- **Dashboard via MCP:** dashboard create/replace is CLI-only per OWL docs — do not promise MCP dashboard writes.
- **ai-skills About text overpromises:** only `owl-diagnostics` exists today; see `docs/truewatch-owl.md`.
- **Agent sandbox vs `gh`:** Cursor Agent may inject invalid `GH_TOKEN` or stay sandboxed; owner terminal `gh auth status` can be fine while the agent cannot. Prefer owner terminal for `gh` auth-sensitive ops if the agent fails.
- **Public repo:** never commit API keys, workspace tokens, or customer data; synthetic data only.
