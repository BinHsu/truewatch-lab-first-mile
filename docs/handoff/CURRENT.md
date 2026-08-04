# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-04 — releasing **v0.0.1** (DataWay + unified `EMIT_MODE`); next slice v0.0.2 DataKit

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md` / `CHANGELOG.md`
3. `docs/ADR/0002-release-tags-and-emit-mode.md`
4. `docs/runbooks/dataway-emit.md`
5. `docs/runbooks/owl-cli-credentials.md`
6. `AGENTS.md`
7. `docs/FILE-MAP.md` (before creating any new file)

## 2. Last completed milestone

**v0.0.1 — DataWay ingest path.** Unified `scripts/emit.py` (`--mode` / `EMIT_MODE`), working
`emit_dataway.py` (HTTP 200 on id1), stubs for datakit/ddtrace (`NOT-IMPLEMENTED`, exit 2),
Compose emitter image files, credentials + DataWay runbooks, ADR-0001/0002.

| Tag / commit | Content |
|---|---|
| `v0.0.1` | DataWay release (this cut) |
| *(planned)* `v0.0.2` | DataKit |
| *(planned)* `v0.0.3` | DDTrace → DataKit |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Visibility: **public**
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; local `.env` has OWL + Workspace Token + DataWay (gitignored).
- OWL CLI v1.1.1; `owl sync` OK.
- Host Docker: **not installed** on the machine that cut v0.0.1 — Compose files are the forker
  contract; host `python3 scripts/emit.py` is the verified path here.
- DataKit: not installed.

## 5. Commands already run

```bash
set -a && source .env && set +a
python3 scripts/emit.py --mode dataway --dry-run
python3 scripts/emit_dataway.py   # earlier: metric_http_status=200 after UA fix
python3 scripts/emit.py --mode datakit   # → NOT-IMPLEMENTED exit 2
python3 scripts/emit.py --mode ddtrace   # → NOT-IMPLEMENTED exit 2
```

## 6. Test results

- DataWay POST metric/logging: **pass** `[VERIFIED]` HTTP 200 (lab User-Agent; CF 1010 on Python-urllib).
- Unified dispatcher + stubs: **pass** `[VERIFIED]` (datakit/ddtrace exit 2).
- Compose build: **not run** (no Docker on this host) `[UNVERIFIED]`.
- Explorer UI sighting: **owner Group B** `[UNVERIFIED]`.

## 7. Current blockers, in priority order

1. Implement **v0.0.2** DataKit (Compose preferred).
2. Then **v0.0.3** DDTrace → DataKit.
3. Optional: owner confirms Explorer visibility; OWL MCP in Cursor; Monitor/Dashboard scope.

## 8. AWAITING DECISION — owner only

1. ~~Site~~ id1. ~~Ingest set~~ ADR-0001. ~~Release slicing~~ ADR-0002.
2. Whether first visibility milestone includes Monitor + Dashboard, or Explorer-only per path.

## 9. Exact next safe action

Start **v0.0.2** DataKit slice (Compose): install/run DataKit with `DK_DATAWAY`, implement
`scripts/emit_datakit.py`, wire compose service, tag `v0.0.2` when HTTP + Explorer path works.

```bash
# v0.0.1 smoke (host):
set -a && source .env && set +a
python3 scripts/emit.py --mode dataway --dry-run
# If Docker available:
# docker compose --env-file .env run --rm emit --mode dataway --dry-run
ls docs/ADR/0002-release-tags-and-emit-mode.md docker-compose.yml
```

## 10. Things that will bite you

- Cloudflare **1010** if User-Agent is `Python-urllib/*` against id1-openway.
- Do not treat datakit/ddtrace stubs as green — they must stay non-zero until implemented.
- Never commit `.env`.
