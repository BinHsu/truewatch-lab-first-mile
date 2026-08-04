# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** 2026-08-04 — v0.0.2 DataKit **code + docs landed**; live Compose POST still
`[UNVERIFIED]` (no Docker on this host). Do **not** cut `v0.0.2` tag until HTTP 2xx through
DataKit is observed.

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md` / `CHANGELOG.md`
3. `docs/runbooks/datakit-emit.md`
4. `docs/ADR/0002-release-tags-and-emit-mode.md`
5. `docs/runbooks/owl-cli-credentials.md`
6. `AGENTS.md`
7. `docs/FILE-MAP.md` (before creating any new file)

## 2. Last completed milestone

**v0.0.1 — DataWay ingest path** (tagged). **v0.0.2 implementation in tree** (untagged):
`scripts/emit_datakit.py`, Compose `datakit` profile, `docs/runbooks/datakit-emit.md`.

| Tag / commit | Content |
|---|---|
| `v0.0.1` / `6be3e7f` | DataWay release — https://github.com/BinHsu/truewatch-lab-first-mile/releases/tag/v0.0.1 |
| *(untagged)* | DataKit emitter + Compose — await live verify, then tag `v0.0.2` |
| *(planned)* `v0.0.3` | DDTrace → DataKit |

## 3. Repository state

- Branch: `main`
- Remote: `https://github.com/BinHsu/truewatch-lab-first-mile.git`
- Visibility: **public**
- Hooks: `core.hooksPath=.githooks`

## 4. Environment / system state

- Site **id1**; local `.env` has OWL + Workspace Token + DataWay (gitignored).
- OWL CLI v1.1.1; Open API key in `.env`; `owl workspace list` OK `[VERIFIED]` 2026-08-04.
- Host Docker: **not installed** — cannot pull/run `pubrepo.truewatch.com/truewatch/datakit:2.7.1`
  here. Compose is the forker contract.
- DataKit: not running on this host.

## 5. Commands already run

```bash
set -a && source .env && set +a
python3 scripts/emit.py --mode dataway --dry-run
python3 scripts/emit_dataway.py   # earlier: metric_http_status=200 after UA fix
python3 scripts/emit.py --mode datakit --dry-run   # after v0.0.2 impl (expect dry_run=1)
owl workspace list                # OK after Open API key (was 401 with Client Token)
# NOT yet (needs Docker):
# docker compose --profile datakit --env-file .env up -d datakit
# DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
```

## 6. Test results

- DataWay POST metric/logging: **pass** `[VERIFIED]` HTTP 200 (lab User-Agent; CF 1010 on Python-urllib).
- OWL Open API auth: **pass** `[VERIFIED]` `owl workspace list`.
- DataKit dry-run (script): **pass** `[VERIFIED]` `python3 scripts/emit.py --mode datakit --dry-run`
  → `dry_run=1`, `path=datakit`, URL `http://127.0.0.1:9529/v1/write/metric`.
- DataKit live POST via Compose: **not run** (no Docker) `[UNVERIFIED]`.
- Explorer `path=datakit`: **not run** `[UNVERIFIED]` (Group B).
- Compose build / image pull: **not run** `[UNVERIFIED]`.
- DDTrace stub: still exit 2 `NOT-IMPLEMENTED` `[VERIFIED]`.

## 7. Current blockers, in priority order

1. **Install Docker** (or use another host) → live-verify DataKit → tag `v0.0.2`.
2. Then **v0.0.3** DDTrace → DataKit.
3. Optional: OWL MCP in Cursor; Monitor/Dashboard scope.

## 8. AWAITING DECISION — owner only

1. ~~Site~~ id1. ~~Ingest set~~ ADR-0001. ~~Release slicing~~ ADR-0002.
2. Whether first visibility milestone includes Monitor + Dashboard, or Explorer-only per path.
3. When to cut `v0.0.2` tag (after live HTTP + optional Explorer sighting).

## 9. Exact next safe action

Verify dry-run on this host, then (on a Docker host) bring up DataKit and live-emit:

```bash
set -a && source .env && set +a
python3 scripts/emit.py --mode datakit --dry-run
# On a machine with Docker + DK_DATAWAY in .env:
# docker compose --profile datakit --env-file .env up -d datakit
# DATAKIT_URL=http://127.0.0.1:9529 python3 scripts/emit.py --mode datakit
# Expect metric_post=OK; Explorer filter path=datakit
# Then tag v0.0.2 and update this handoff with the release SHA/URL
```

## 10. Things that will bite you

- Cloudflare **1010** if User-Agent is `Python-urllib/*` against id1-openway (DataWay path).
- **Management → Client Tokens** is RUM-only; OWL needs API Key Secret → `OWL_TOKEN`.
- Compose `datakit` needs `--profile datakit` and `DK_DATAWAY`; DataWay-only emit does not.
- `emit` Compose service defaults `DATAKIT_URL=http://datakit:9529` (service DNS); host Python
  should use `http://127.0.0.1:9529`.
- Do not treat `emit_ddtrace.py` as green — still `NOT-IMPLEMENTED` until v0.0.3.
- Never commit `.env`.
- Do not tag `v0.0.2` until live DataKit POST is verified.
