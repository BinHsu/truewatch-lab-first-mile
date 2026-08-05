# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **v0.0.3 implementation + OWL verify pass** (StatsD metric +
DDTrace span). Console Group B still for owner; tag `v0.0.3` when ready.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `docs/runbooks/ddtrace-emit.md`
3. `docs/ADR/0003-otel-trace-path.md`
4. `CHANGELOG.md` / `README.md`
5. `AGENTS.md` / `docs/FILE-MAP.md`

## 2. Last completed milestone

**v0.0.2** tagged. **v0.0.3 code + OWL `[VERIFIED]`** (untagged until release cut).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| *(ready to tag)* `v0.0.3` | DDTrace StatsD metric + span — OWL M+T pass 2026-08-05 |
| *(planned)* `v0.0.4` | OTLP metric + span |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- DataKit Compose: inputs `dk,ddtrace,statsd`; ports 9529 + 8125/udp.
- Emitter image builds with `msgpack==1.1.1`.

## 5. Commands already run

```bash
docker compose --profile datakit --env-file .env up -d --force-recreate datakit
docker compose --env-file .env build emit
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit
# statsd_send=OK traces_http_status=200 traces_post=OK
```

## 6. Test results

- Compose live emit: **pass** `[VERIFIED]` StatsD + `/v0.4/traces` HTTP 200.
- OWL Metrics: **pass** `[VERIFIED]`  
  `M::truewatch:(last(lab_first_mile_ping), count(lab_first_mile_ping)) { path = 'ddtrace' } [2h]`  
  → `last=1`, `count=2` (2026-08-05 ~01:04–01:05 UTC / 09:04–09:05+08).
- OWL Traces: **pass** `[VERIFIED]`  
  `T::'lab-emitter':(trace_id, span_id, resource, service, duration) [2h] LIMIT 5`  
  → `trace_id=974926597694416500`, `resource=lab.ddtrace.ping`, `service=lab-emitter`.
- Console APM/Metrics sighting: **owner Group B** `[UNVERIFIED]`.

## 7. Current blockers, in priority order

1. Owner Console check (optional before tag) — OWL already green.
2. Cut **`v0.0.3`** tag + GitHub release; record SHA/URL here.
3. Then **v0.0.4** OTel dual-signal.

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only (unchanged).
2. When to tag `v0.0.3`.

## 9. Exact next safe action

Owner: optional APM/Metrics console check per `docs/runbooks/ddtrace-emit.md`, then ask to
tag `v0.0.3`. Or start v0.0.4 design/impl.

```bash
# re-smoke
docker compose --env-file .env run --rm -e EMIT_MODE=ddtrace emit --dry-run
```

## 10. Things that will bite you

- StatsD name `truewatch_lab_first_mile.ping` → measurement **`truewatch`**, field
  **`lab_first_mile_ping`** (separator `_`).
- DQL service with hyphen: use `T::'lab-emitter':…` not bare `T::lab-emitter`.
- Broad `M::*` queries may hit “excessive resource usage” — query named measurement.
- DataKit DEBUG logs may include DataWay token — redact.
- `emit_otel.py` still stub until v0.0.4.
- Never commit `.env`.
