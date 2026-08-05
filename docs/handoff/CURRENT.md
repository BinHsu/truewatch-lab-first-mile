# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **v0.0.4 released** (`d1cf739`). Four ingest paths tagged through
OTLP. Optional next: payload unit tests + GHA (owner had deferred until Console; Console done).

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `docs/runbooks/otel-emit.md`
3. `docs/ADR/0002-release-tags-and-emit-mode.md` / `docs/ADR/0003-otel-trace-path.md`
4. `CHANGELOG.md` / `README.md`
5. `AGENTS.md` / `docs/FILE-MAP.md`

## 2. Last completed milestone

**v0.0.4 — OTLP metric + span** (tagged + GitHub release). Owner Console `[VERIFIED]`.
Also: spaced repeats on `emit.py` (`--count` / `--interval`, default 5s).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| `v0.0.4` / `d1cf739` | OTel — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4 |

## 3. Repository state

- Branch: `main` (track `origin/main`)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`
- Tag `v0.0.4` → `d1cf739`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- DataKit: `dk,ddtrace,statsd,opentelemetry`; 9529 + 8125/udp.
- Emitter: `msgpack` + `opentelemetry-proto==1.34.1`.

## 5. Commands already run

```bash
git tag -a v0.0.4 d1cf739 …
git push origin HEAD v0.0.4
gh release create v0.0.4 …
# https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.4
```

## 6. Test results

- Live OTLP + OWL M+T: **pass** `[VERIFIED]`
- Owner Console Metrics + APM (`lab.otel.ping`): **pass** `[VERIFIED]` 2026-08-05 ~10:47+08
- Emit spacing dispatcher dry-run: **pass** `[VERIFIED]`

## 7. Current blockers, in priority order

1. None for ingest path slices v0.0.1–v0.0.4.
2. Optional: `tests/test_emit_payloads.py` + wire into GitHub Actions.

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.
2. Start payload UT + GHA now?

## 9. Exact next safe action

Owner: decide Monitor/Dashboard and/or ask for payload contract tests + CI.

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --count 2 --dry-run
```

## 10. Things that will bite you

- OTLP → `M::otel_service`, quote `truewatch_lab_first_mile.ping`.
- Use `--count 2` for distinct Metrics UI points (5s default gap).
- Never commit `.env`.
