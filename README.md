# truewatch-lab-first-mile

Public PDSA lab: a **synthetic first-mile** TrueWatch observability loop
(ingest → Explorer/DQL → monitor → optional OWL MCP / `owl-diagnostics`).

Bootstrapped from [`BinHsu/aegis-template`](https://github.com/BinHsu/aegis-template) (Harness
Engineering security scaffold). Workload code is not written yet — start from
`docs/handoff/CURRENT.md`.

## Start here

1. `docs/handoff/CURRENT.md` — status and next safe action (no chat history required)
2. `docs/truewatch-owl.md` — current TrueWatch OWL / MCP / CLI rules for this lab
3. `AGENTS.md` — operating contract for every agent and human
4. Copy `.env.example` → `.env` locally (never commit `.env`)

```bash
git config core.hooksPath .githooks   # if not already set after clone
```

## Intended first-mile scope

- Short-lived synthetic metric/log emitter (Python and/or Docker), not a fake full backend
- Visible data in TrueWatch Explorer
- Optional: one Monitor + one thin Dashboard (Dashboard writes via OWL CLI / console, not MCP)
- Optional: OWL MCP in Cursor with Bearer auth

## Security harness (inherited)

This repo keeps the aegis **Rule → Execution → Verification** controls. See
[`docs/SECURITY_PRACTICES.md`](docs/SECURITY_PRACTICES.md) and the root files `SECURITY.md`,
`AGENTS.md`, `.githooks/`, `.github/workflows/security-checks.yml`.

Status is written **only** in `docs/handoff/CURRENT.md` — never duplicate it in this README.

## License / visibility

Public learning lab. Synthetic data only.
