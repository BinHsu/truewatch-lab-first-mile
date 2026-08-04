# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-04 — **v0.0.2 released** (`e287eb7`); next implement **v0.0.3**
DDTrace metric (StatsD) + span per ADR-0003.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md` / `CHANGELOG.md`
3. `docs/runbooks/datakit-emit.md`
4. `docs/observability-glossary.md`
5. `docs/ADR/0002-release-tags-and-emit-mode.md` / `docs/ADR/0003-otel-trace-path.md`
6. `docs/runbooks/owl-cli-credentials.md`
7. `AGENTS.md`
8. `docs/FILE-MAP.md` (before creating any new file)

## 2. Last completed milestone

**v0.0.2 — DataKit ingest path** (tagged). Live POST HTTP 200 + OWL `path=datakit` /
`ping=1` `[VERIFIED]` 2026-08-04 on id1 (Colima Compose).

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| `v0.0.2` / `e287eb7` | DataKit — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.2 |
| *(planned)* `v0.0.3` | DDTrace **metric (StatsD) + span** → DataKit |
| *(planned)* `v0.0.4` | OTLP **metric + span** → DataKit ([ADR-0003](../ADR/0003-otel-trace-path.md)) |

## 3. Repository state

- Branch: `main` (track `origin/main`)
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Visibility: **public**
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; local `.env` has OWL + Workspace Token + DataWay / `DK_DATAWAY` (gitignored).
- OWL: Open API key OK; metric query for lab series OK `[VERIFIED]`.
- Host Docker: **Colima** running `[VERIFIED]`.
- DataKit Compose may still be up from verify (`--profile datakit`).

## 5. Commands already run

```bash
docker compose --profile datakit --env-file .env up -d datakit
DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
# metric_post=OK; OWL: ping=1 path=datakit
git tag -a v0.0.2 && git push origin v0.0.2
gh release create v0.0.2
```

## 6. Test results

- DataWay POST: **pass** `[VERIFIED]` (v0.0.1).
- DataKit live POST + OWL metric: **pass** `[VERIFIED]` (v0.0.2).
- DDTrace / OTel: stubs exit 2 `[VERIFIED]`.

## 7. Current blockers, in priority order

1. Implement **v0.0.3** (StatsD metric + DDTrace span via DataKit).
2. Then **v0.0.4** (OTLP metric + span).
3. Optional: Monitor/Dashboard scope (`AWAITING DECISION`).

## 8. AWAITING DECISION — owner only

1. Whether first visibility milestone includes Monitor + Dashboard, or Explorer-only per path.

## 9. Exact next safe action

Start **v0.0.3** per ADR-0003: enable DataKit `ddtrace` + `statsd` inputs in Compose,
implement `scripts/emit_ddtrace.py` (metric + span), runbook, tag when both signals
visible in Metrics + APM.

```bash
python3 scripts/emit.py --mode ddtrace   # currently NOT-IMPLEMENTED exit 2
ls docs/ADR/0003-otel-trace-path.md
```

## 10. Things that will bite you

- Cloudflare **1010** on direct DataWay if User-Agent is `Python-urllib/*`.
- **Client Tokens** ≠ OWL API Key.
- Compose DataKit needs `--profile datakit` + `DK_DATAWAY`.
- Measurement **`dk`** is DataKit self-metrics, not lab `ping`.
- DataKit DEBUG logs may include DataWay token — redact.
- `emit_ddtrace` / `emit_otel` must stay non-zero until implemented (dual metric+span).
- Never commit `.env`.
