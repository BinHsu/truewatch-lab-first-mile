# aegis-template

> **Secure-by-default starter scaffold + DevSecOps reference implementation.** A GitHub
> *template repository* (not a fork) — "Use this template" copies these files into a fresh
> repo with a clean first commit. Every new project starts with the full security harness
> baked in: the friction differential does the persuasion, not a checklist nobody reads.

This is a complete implementation of the **Harness Engineering 7 security practices**
(see [`docs/SECURITY_PRACTICES.md`](docs/SECURITY_PRACTICES.md) for the per-practice
rationale; framework adapted from [Wisely Chen](https://ai-coding.wiselychen.com/harness-engineering-security-best-practices/)),
organized in three layers: **Rule → Execution → Verification.**

## The 7 practices → files in this repo

| # | Practice | Layer | Files |
|---|---|---|---|
| 1 | **Least-privilege tool access** | Execution | `.claude/settings.json` (allow/deny), `AGENTS.md` (3-way tool table) |
| 2 | **Security rules not buried mid-file** | Rule | `AGENTS.md` (primary policy, all agents), `CLAUDE.md` (thin Claude-only router), `SECURITY.md` at top; `scripts/audit-agent-compliance.sh` (monthly drift test) |
| 3 | **SECURITY.md pins the rules** | Rule | `SECURITY.md` (4 categories: secrets / untrusted input / external actions / dependencies) |
| 4 | **Sandbox isolation + review-feedback promotion** | Execution / Verification | `.githooks/pre-commit` (secret block), `.semgrep/` (promoted review rules), CI runs them |
| 5 | **Security in the benchmark, not just review** | Verification | `scripts/security-benchmark.py`, `scripts/cleanup-scanner.py`, `tests/test_evidence_artifacts.py`, `.github/workflows/security-checks.yml` |
| 6 | **Hidden destructive actions = product red line** | Rule / Execution | `PRODUCT_SENSE.md` (protocol), `scripts/safe-exec.sh` (preview→confirm→log→exec), `.agent-context/destructive-log.jsonl` |
| 7 | **Tool safety is production-grade** | Execution | `tools/registry.yaml` (single source of truth), `scripts/audit-tool-registry.sh` |

Cross-cutting: `docs/THREAT_MODEL.md` (Practice 3/4 — entry required for auth/crypto/payments/PII
surfaces) and `docs/handoff/CURRENT.md` (single source of project status, and the file that lets a
cold agent or human resume with no chat history).

Two more that are not security controls but keep a cold agent from wasting a day:
`docs/FILE-MAP.md` (exhaustive per-file index, so nobody re-creates a file that already exists under
a name they would not have guessed — nagged by a `PostToolUse` hook) and
`docs/design/acceptance-criteria.md` (how to split criteria into ones an agent can run and ones only
a person can, so the second kind is still auditable).

## AGENTS.md is primary; CLAUDE.md is thin

`AGENTS.md` holds all shared policy for every agent and human. `CLAUDE.md` imports it on **line 1**
and contains nothing but Claude-specific mechanics — permissions, delegation boundary, transcript
handling. Claude Code does not read `AGENTS.md` on its own, which is the only reason the import
exists.

A rule written in both files drifts, and the copy that goes stale is the one that gets read. So:
shared rule → `AGENTS.md`; Claude-only mechanism → `CLAUDE.md`; machine-wide discipline →
`~/.claude/CLAUDE.md`.

The same principle governs status, which is written **only** in `docs/handoff/CURRENT.md`. A stale
status banner in a README is worse than none, because it is read with confidence.

## What's runnable today (stack-agnostic)

- `python3 scripts/cleanup-scanner.py` — real secret-residue scan (exit 1 on finding)
- `python3 tests/test_evidence_artifacts.py` — validate manual-verification records
- `python3 tests/test_evidence_artifacts.py --self-test` — prove that validator can still fail
- `python3 scripts/security-benchmark.py` — benchmark status (stubs report `NOT-IMPLEMENTED`)
- `bash scripts/safe-exec.sh rm -rf foo` — destructive-command preview + confirm + log
- `bash scripts/audit-tool-registry.sh` — tool-layer hole detection, exit 1 on finding (needs `yq`)
- `.githooks/pre-commit` — enable with `git config core.hooksPath .githooks`
- CI (`security-checks.yml`) — wires all of the above

**Stubs to specialise per stack.** Every one of them announces itself rather than reporting a pass —
`AGENTS.md` §12, the rule this scaffold most needs you to keep:

- `security-benchmark.py` — 3 unimplemented benchmarks; add `--require-implemented` to CI once wired
- `tools/registry.yaml` — example entries; delete the tools you do not call
- `.semgrep/` — seed rules; retarget or delete for your languages
- `docs/validation/evidence/REQUIRED.json` — one example phase; replace with your own
- the dependency-audit and lint steps in CI (uncomment the matching language)
- the `{{placeholders}}` in `AGENTS.md` / `SECURITY.md` / `CLAUDE.md` / `THREAT_MODEL.md` /
  `docs/handoff/CURRENT.md`, and the seeded rows in `docs/FILE-MAP.md`

## Cross-project rules live in `~/.claude/CLAUDE.md`

Language · date · bash · safety guardrails (a/h/i/k/m) · externalize-decisions ·
pre-push-diff · non-host-install · reusable-PII · AWS-tech-blog tone · subagent-delegation ·
no-hallucination — these load globally and are **not** duplicated in this template. The
template's `CLAUDE.md` points to them and `@import`s `AGENTS.md` (Claude Code does not read
AGENTS.md on its own).

## How to use

1. On GitHub: Settings → check **"Template repository"**.
2. New project → **"Use this template"** → fresh repo, clean history, full harness inherited.
3. `git config core.hooksPath .githooks` ; fill the `{{PLACEHOLDER}}` spots in `AGENTS.md`,
   `CLAUDE.md`, `SECURITY.md`, `THREAT_MODEL.md` and `docs/handoff/CURRENT.md`.
4. Pick an archetype direction (stateless-sync / async-decoupled / stateful), add workload code,
   wire the CI dependency-audit + lint steps for your language, specialise the benchmark stubs.
5. Rewrite `docs/FILE-MAP.md` as you replace the scaffold — and keep adding a row per new file, in
   the change that creates it.

## Relationship to the aegis archetype ecosystem

Base scaffold the workload archetypes share. Specialise into:
- **stateless sync** (greeter-style) — Deployment, shared cluster, namespace isolation
- **async-decoupled** (enclave-style) — + queue compute decoupling
- **stateful** (statefulset-style) — StatefulSet + persistent storage

Platform substrate (landing-zone + platform tier) consumed via a standard interface, so a
workload promotes from shared-cluster to dedicated-cluster without rewriting its integration.

---

*DevSecOps reference implementation — v1. Specialise per actual use.*
