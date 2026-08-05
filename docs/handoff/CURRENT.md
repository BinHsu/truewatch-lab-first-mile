# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — Payload UT runs **inside emitter Docker image**
(`bash scripts/run-emit-payload-tests.sh`); no host `pip install` (ADR-0002).

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `tests/test_emit_payloads.py`
3. `docs/runbooks/otel-emit.md` / `docs/ADR/0002-release-tags-and-emit-mode.md`
4. `CHANGELOG.md` / `README.md`

## 2. Last completed milestone

**v0.0.4 released** + **payload contract tests in CI**.

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| `v0.0.4` / `d1cf739` | OTel — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4 |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Unchanged lab host (id1, Colima).
- Payload UT: Docker only — pins live in emitter image, not host site-packages.

## 5. Commands already run

```bash
bash scripts/run-emit-payload-tests.sh
# Ran 9 tests — OK (inside truewatch-lab-first-mile-emit:payload-test)
```

## 6. Test results

- `tests/test_emit_payloads.py` via Docker: **pass** `[VERIFIED]` (9 tests), including
  dry-run stdout must not contain canary token.

## 7. Current blockers, in priority order

1. None for ingest paths / payload contracts.
2. Optional: Monitor + Dashboard (still AWAITING DECISION).

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.

## 9. Exact next safe action

```bash
bash scripts/run-emit-payload-tests.sh
```

Or owner decides Monitor/Dashboard scope.

## 10. Things that will bite you

- OTLP → `M::otel_service`; quote dotted field names in DQL.
- `--count 2` for distinct Metrics UI points (5s default).
- Never commit `.env`.
