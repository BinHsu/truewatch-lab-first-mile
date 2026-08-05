# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **v0.1.0 released** (`e64a09e`). First-mile lab checkpoint:
four ingest paths + portable payload UT/CI. Optional next: Monitor / Dashboard.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `CHANGELOG.md` / `README.md`
3. `scripts/run-emit-payload-tests.sh`
4. `docs/ADR/0002-release-tags-and-emit-mode.md`

## 2. Last completed milestone

**v0.1.0 — First-mile lab checkpoint** (tagged + GitHub release).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| `v0.0.4` / `d1cf739` | OTel — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4 |
| `v0.1.0` / `e64a09e` | Checkpoint — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.1.0 |

## 3. Repository state

- Branch: `main` (track `origin/main`)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`
- Tag `v0.1.0` → `e64a09e`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- Payload UT: Docker only via `scripts/run-emit-payload-tests.sh`.

## 5. Commands already run

```bash
git tag -a v0.1.0 e64a09e …
git push origin HEAD v0.1.0
gh release create v0.1.0 …
# https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.1.0
```

## 6. Test results

- Ingest paths v0.0.1–v0.0.4: prior OWL/Console `[VERIFIED]` as recorded.
- Payload UT in Docker: **pass** `[VERIFIED]` (9 tests).

## 7. Current blockers, in priority order

1. None for the first-mile emit + contract checkpoint.
2. Optional: Monitor + Dashboard.

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.

## 9. Exact next safe action

Owner: decide Monitor/Dashboard, or next lab goal beyond first-mile ingest.

```bash
bash scripts/run-emit-payload-tests.sh
```

## 10. Things that will bite you

- Portable default: Git + Docker; do not treat host pip as the official path.
- Never commit `.env`.
