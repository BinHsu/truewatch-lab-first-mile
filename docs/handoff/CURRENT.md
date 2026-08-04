# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-04 — Owner: v0.0.3/v0.0.4 each prove **metric + span** in
protocol-native formats (ADR-0003). Glossary + OTel stub already in tree. Still:
tag `v0.0.2` pending; then implement DDTrace dual-signal, then OTel dual-signal.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md` / `CHANGELOG.md`
3. `docs/observability-glossary.md` (console map + terms)
4. `docs/runbooks/datakit-emit.md`
5. `docs/ADR/0002-release-tags-and-emit-mode.md` / `docs/ADR/0003-otel-trace-path.md`
6. `docs/runbooks/owl-cli-credentials.md`
7. `AGENTS.md`
8. `docs/FILE-MAP.md` (before creating any new file)

## 2. Last completed milestone

**v0.0.1 — DataWay** (tagged `6be3e7f`). **v0.0.2 DataKit path live-verified on this host**
(untagged until release cut).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| *(ready to tag)* `v0.0.2` | DataKit Compose + `emit_datakit.py` — live HTTP 200 `[VERIFIED]` 2026-08-04 |
| *(planned)* `v0.0.3` | DDTrace **metric (StatsD) + span** → DataKit |
| *(planned)* `v0.0.4` | OTLP **metric + span** → DataKit ([ADR-0003](../ADR/0003-otel-trace-path.md)) |

## 3. Repository state

- Branch: `main` (local commits may be ahead of origin — check `git status`)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Visibility: **public**
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; local `.env` has OWL + Workspace Token + DataWay / `DK_DATAWAY` (gitignored).
- OWL: `owl workspace list` OK `[VERIFIED]`.
- Host Docker: **Colima** running `[VERIFIED]` (Docker 29.x + Compose 5.4).
- DataKit Compose: `pubrepo.truewatch.com/truewatch/datakit:2.7.1`, profile `datakit`,
  port **9529**, health `/v1/ping` → 200 `[VERIFIED]`.

## 5. Commands already run

```bash
colima start --cpu 2 --memory 4 --arch aarch64
docker compose --profile datakit --env-file .env up -d datakit
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:9529/v1/ping   # 200
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit --also-log
# → metric_post=OK / logging_post=OK (HTTP 200)
```

## 6. Test results

- DataWay POST: **pass** `[VERIFIED]` (v0.0.1).
- OWL Open API: **pass** `[VERIFIED]`.
- DataKit dry-run: **pass** `[VERIFIED]`.
- DataKit live POST (local → `:9529` → DataWay): **pass** `[VERIFIED]` HTTP 200 metric + logging.
- Explorer `path=datakit`: **owner Group B** `[UNVERIFIED]`.
- Compose `emit` image build path: optional / not required for host Python emit `[UNVERIFIED]`.

## 7. Current blockers, in priority order

1. Owner: confirm Explorer `path=datakit` (optional but preferred before tag).
2. Commit pending docs (glossary, ADR-0003, `dk` runbook notes, handoff) + cut **`v0.0.2`**.
3. Then **v0.0.3** DDTrace: StatsD metric + span.
4. Then **v0.0.4** OTel: OTLP metric + span.

## 8. AWAITING DECISION — owner only

1. Confirm Explorer sighting for `path=datakit`, or tag `v0.0.2` on HTTP-only evidence.
2. Whether first visibility milestone includes Monitor + Dashboard, or Explorer-only per path.

## 9. Exact next safe action

Owner checks Explorer (`truewatch_lab_first_mile` / `path=datakit`), then cut release:

```bash
# optional Group B: Metrics / Explorer filter path=datakit
git status -sb
# when ready (owner asks): tag v0.0.2 on the DataKit commit, push, update this handoff
```

Keep DataKit up with:
`docker compose --profile datakit --env-file .env up -d datakit`

## 10. Things that will bite you

- Cloudflare **1010** on direct DataWay if User-Agent is `Python-urllib/*`.
- **Client Tokens** ≠ OWL API Key.
- Compose DataKit needs `--profile datakit` + `DK_DATAWAY`.
- Host emit: `DATAKIT_URL=http://127.0.0.1:9529`; Compose emit default `http://datakit:9529`.
- DataKit **DEBUG** logs may print full `ENV_DATAWAY` URLs including token — redact before
  pasting logs; never commit log dumps.
- `emit_ddtrace.py` still `NOT-IMPLEMENTED` until v0.0.3.
- `emit_otel.py` still `NOT-IMPLEMENTED` until v0.0.4.
- Never commit `.env`.
- Official path stays **Docker Compose**; Apple Container is out of scope for this lab.
- Terms / console map: `docs/observability-glossary.md` (span ≠ spam; traces live under **APM**).
