# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **v0.0.3 released** (`3307a25`). Next: finish owner Console if
needed; then commit/verify/tag **v0.0.4** OTel (WIP may be in stash or working tree). Payload UT
/ GHA still deferred until after Console.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `docs/runbooks/ddtrace-emit.md`
3. `docs/ADR/0003-otel-trace-path.md`
4. `CHANGELOG.md` / `README.md`
5. `AGENTS.md` / `docs/FILE-MAP.md`

## 2. Last completed milestone

**v0.0.3 — DDTrace StatsD metric + span** (tagged). OWL M+T `[VERIFIED]` 2026-08-05 on id1.

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| *(next)* `v0.0.4` | OTLP metric + span (impl done locally; commit/tag pending) |

## 3. Repository state

- Branch: `main` (track `origin/main`)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`
- Tag `v0.0.3` points at `3307a25` (does **not** include uncommitted OTel WIP).

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- DataKit Compose at tag: inputs `dk,ddtrace,statsd`; ports 9529 + 8125/udp.
- Emitter image pins `msgpack==1.1.1`.

## 5. Commands already run

```bash
git tag -a v0.0.3 3307a25 -m "v0.0.3 — DDTrace StatsD metric + span via DataKit"
git push origin v0.0.3
gh release create v0.0.3 …
# https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3
```

## 6. Test results

- Compose live emit: **pass** `[VERIFIED]` StatsD + `/v0.4/traces` HTTP 200.
- OWL Metrics: **pass** `[VERIFIED]`  
  `M::truewatch:(last(lab_first_mile_ping), count(lab_first_mile_ping)) { path = 'ddtrace' } [2h]`  
  → `last=1`, `count=2` (2026-08-05 ~01:04–01:05 UTC / 09:04–09:05+08).
- OWL Traces: **pass** `[VERIFIED]`  
  `T::'lab-emitter':…` → `trace_id=974926597694416500`, `resource=lab.ddtrace.ping`.
- Console APM/Metrics: **owner Group B** `[UNVERIFIED]` (optional).

## 7. Current blockers, in priority order

1. Owner optional Console check for v0.0.3.
2. Commit + OWL-record + tag **v0.0.4** (OTLP; local WIP stashed or dirty).
3. **Deferred:** `tests/test_emit_payloads.py` + GHA — after Console.

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only (unchanged).
2. When to cut `v0.0.4`.

## 9. Exact next safe action

```bash
# restore OTel WIP if stashed
git stash list   # look for "wip v0.0.4 otel"
git stash pop    # when ready to continue v0.0.4 commit

# or re-smoke tagged v0.0.3
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit --dry-run
```

## 10. Things that will bite you

- StatsD name `truewatch_lab_first_mile.ping` → measurement **`truewatch`**, field
  **`lab_first_mile_ping`**.
- DQL: `T::'lab-emitter':…`
- Never commit `.env`.
- Do not fold uncommitted OTel files into a v0.0.3 retag — tag already shipped on `3307a25`.
