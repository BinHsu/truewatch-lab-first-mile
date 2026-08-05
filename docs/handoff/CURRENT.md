# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **Shipping v0.1.0** lab checkpoint (four ingest paths + portable
payload UT/CI). About to commit docs, tag, push, GitHub release.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `CHANGELOG.md` (v0.1.0)
3. `docs/ADR/0002-release-tags-and-emit-mode.md`
4. `scripts/run-emit-payload-tests.sh`

## 2. Last completed milestone

**v0.0.4** tagged earlier. **v0.1.0** = summary of first-mile lab + UT/CI (cutting now).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| `v0.0.4` / `d1cf739` | OTel — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4 |
| *(cutting)* `v0.1.0` | Checkpoint: paths + Docker payload UT + CI |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- Payload UT: `bash scripts/run-emit-payload-tests.sh` only (no host pip).

## 5. Commands already run / about to run

```bash
bash scripts/run-emit-payload-tests.sh   # already OK
git tag -a v0.1.0 && git push origin HEAD v0.1.0
gh release create v0.1.0 …
```

## 6. Test results

- Ingest v0.0.1–v0.0.4: OWL and/or Console as recorded in prior handoffs `[VERIFIED]`
- Payload UT in Docker: **pass** `[VERIFIED]` (9 tests)

## 7. Current blockers, in priority order

1. Finish v0.1.0 tag + release + record URL here.
2. Optional next scope: Monitor + Dashboard (AWAITING DECISION).

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.

## 9. Exact next safe action

If interrupted after commit but before tag: tag the v0.1.0 commit, push, `gh release create`.

```bash
bash scripts/run-emit-payload-tests.sh
```

## 10. Things that will bite you

- Do not retag v0.0.4; checkpoint is **v0.1.0**.
- Never commit `.env`.
