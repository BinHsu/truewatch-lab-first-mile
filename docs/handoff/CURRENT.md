# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-05 — **Shipping v0.0.4** (OTLP metric + span; emit `--count`/`--interval`).
About to commit, tag `v0.0.4`, push, and create GitHub release. Resume: verify tag URL in this
file after release; then optional payload UT / GHA.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `docs/runbooks/otel-emit.md`
3. `docs/ADR/0002-release-tags-and-emit-mode.md` (spacing addendum)
4. `docs/ADR/0003-otel-trace-path.md`
5. `CHANGELOG.md` / `README.md`

## 2. Last completed milestone

**v0.0.3** tagged. **v0.0.4** implementation + OWL + owner Console `[VERIFIED]` — cutting tag now.

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| `v0.0.3` / `3307a25` | DDTrace — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.3 |
| *(cutting)* `v0.0.4` | OTLP metric + span + emit spacing |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; Colima Docker OK.
- DataKit: `dk,ddtrace,statsd,opentelemetry`; ports 9529 + 8125/udp.
- Emitter: `msgpack==1.1.1`, `opentelemetry-proto==1.34.1`.
- `emit.py`: default interval **5s** between `--count` shots.

## 5. Commands already run / about to run

```bash
# already verified
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit
# metrics_post=OK traces_post=OK; OWL M::otel_service + T lab.otel.ping
# Owner Console: metric value 1 @ 10:47; two APM spans matching OWL trace_ids

# shipping
git add … && git commit && git tag -a v0.0.4 && git push origin HEAD v0.0.4
gh release create v0.0.4 …
```

## 6. Test results

- Live OTLP HTTP 200: **pass** `[VERIFIED]`
- OWL `M::otel_service` / `truewatch_lab_first_mile.ping` `path=otel`: **pass** `[VERIFIED]`
- OWL `T` `resource=lab.otel.ping` `source=opentelemetry`: **pass** `[VERIFIED]`
- Owner Console Metrics + APM: **pass** `[VERIFIED]` (2026-08-05 ~10:47+08)
- Spaced `--count`/`--interval`: code + dry-run dispatcher `[VERIFIED]`; live spaced re-emit optional

## 7. Current blockers, in priority order

1. Finish tag + release + record URL here.
2. Optional: `tests/test_emit_payloads.py` + GHA (owner previously deferred until Console — Console done).

## 8. AWAITING DECISION — owner only

1. Monitor + Dashboard vs Explorer-only.
2. Whether to start payload UT + GHA next.

## 9. Exact next safe action

If this commit lands but tag/push dies: tag the v0.0.4 impl commit, `git push origin v0.0.4`,
`gh release create v0.0.4`, then record SHA/URL in this file.

```bash
docker compose --env-file .env run --rm -e EMIT_MODE=otel emit --count 2
```

## 10. Things that will bite you

- OTLP → `M::otel_service`, quote dotted field `truewatch_lab_first_mile.ping`.
- Sub-second repeats look like one Metrics point — use `--count 2` (5s default).
- Never commit `.env`.
