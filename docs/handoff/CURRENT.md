# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **Shipping v0.1.1** docs close-out (forker README + EMIT_MODE-first).
First-mile ingest chapter formally wrapped; optional next remains Monitor / Dashboard.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md` / `CHANGELOG.md`
3. `scripts/run-emit-payload-tests.sh`
4. `docs/ADR/0002-release-tags-and-emit-mode.md`

## 2. Last completed milestone

**v0.1.0** lab checkpoint. **v0.1.1** = docs close-out (cutting now).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| `v0.0.4` / `d1cf739` | OTel — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4 |
| `v0.1.0` / `e64a09e` | Checkpoint — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.1.0 |
| *(cutting)* `v0.1.1` | Docs close-out: README flow + EMIT_MODE-first |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- Docs prefer `EMIT_MODE`; DataWay omits `--profile datakit`.

## 5. Commands already run / about to run

```bash
git tag -a v0.1.1 && git push origin HEAD v0.1.1
gh release create v0.1.1 …
```

## 6. Test results

- Unchanged from v0.1.0: payload UT in Docker `[VERIFIED]`; ingest paths prior `[VERIFIED]`.

## 7. Current blockers, in priority order

1. Finish v0.1.1 tag + release + record URL here.
2. Optional: Monitor + Dashboard (`AWAITING DECISION`).

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.

## 9. Exact next safe action

Tag/push/release v0.1.1, then record SHA/URL in this file.

```bash
bash scripts/run-emit-payload-tests.sh
```

## 10. Things that will bite you

- Prefer `EMIT_MODE` in examples; do not teach `--no-deps` as no-DataKit.
- Never commit `.env`.
