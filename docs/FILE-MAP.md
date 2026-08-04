# File map — exhaustive per-file index

This document answers one question: **does something covering X already exist, and where?** It
lists every tracked file and directory, with one line on what each file's *job* is. The failure it
prevents is duplicate work — a worker with no chat history creating `docs/secrets-policy.md` without
noticing `SECURITY.md` already owns that ground.

**Every new file gets a row here, in the same change that creates it.** Not later, not in a
follow-up commit. A `PostToolUse` hook (`scripts/check-file-map.sh`) notices when a newly written
path is missing from this file and says so, but a hook can only nag — it cannot write the row. If a
file genuinely does not belong in the index, say so explicitly rather than skipping it silently.

**This is not a curated reading list.** `README.md` and `docs/handoff/CURRENT.md` tell a reader
*what to open next* for a given goal, and deliberately mention only a fraction of the repository.
This file is the exhaustive manifest and makes no reading recommendations. Two different jobs. Do
not merge them.

**Status is not here.** Project status lives in exactly one place, `docs/handoff/CURRENT.md`
(`AGENTS.md` §3). This index describes what each file is *for*, never how far along it is. Where a
row says "stub" or "placeholder" that is a statement about the file's content, not about project
progress — a stub that reads like real coverage is precisely what causes someone to skip it and
write the same thing again.

The rows below describe the scaffold as shipped. **Replace them as you replace the scaffold.**

---

## Repository root

| Path | What it is for | Who reads it |
|---|---|---|
| `AGENTS.md` | The operating contract for every agent and human: read-first order, single-source-of-status, handoff protocol, evidence standard, decision records, never-commit list, tool-access classes, destructive-action protocol, and the rule against checks that cannot fail. Tool-agnostic. | Any agent or contributor, first |
| `CLAUDE.md` | Claude Code-only mechanics on top of `AGENTS.md`, which it imports on line 1. Permissions, delegation boundary, conflict resolution. Holds no shared policy. | Claude Code sessions |
| `README.md` | What this scaffold is, the 7-practice map from practice to file, and how to specialise it. States no project status by design. | Forkers, first-time readers |
| `SECURITY.md` | Security ground rules an agent must not guess at: secrets, untrusted input, external actions, dependencies. Contains `{{placeholders}}` to fill per project. | Reviewers; anyone touching secrets or external systems |
| `PRODUCT_SENSE.md` | The product red line that hidden destructive actions are a defect, plus the preview/confirm/log/abort protocol. Restates the protocol also given in `AGENTS.md` §10. | Any agent before a destructive command |
| `.gitignore` | Declares what must never be committed. Note the git gotcha recorded in `AGENTS.md` §7: ignore `dir/*`, not `dir/`, or a negation cannot re-include a member. | Anyone adding a file type that might carry secrets |
| `docs/FILE-MAP.md` | This file. The exhaustive manifest. | Anyone about to create a new file |

## `.claude/` — Claude Code harness

| Path | What it is for | Who reads it |
|---|---|---|
| `.claude/settings.json` | Enforces the `AGENTS.md` §9 tool-access table as machine-readable allow/deny lists, and wires the `PostToolUse` hook that checks this index. Execution-layer backstop for rules an agent might miss. | Claude Code (automatically); reviewers auditing privilege |
| `.claude/rules/README.md` | Explains how to add path-scoped rule files loaded on demand by glob. **Instructions only — no rule file exists yet.** | Anyone adding a rule that applies to one directory rather than the whole repo |

## `.githooks/` — local git enforcement

| Path | What it is for | Who reads it |
|---|---|---|
| `.githooks/pre-commit` | Blocks three classes of bad commit before they land: `.env` files, hardcoded-secret patterns in the staged diff, and anything `scripts/cleanup-scanner.py` flags. Requires `git config core.hooksPath .githooks`. | Git (automatically); anyone whose commit was refused |

## `.github/workflows/` — CI

| Path | What it is for | Who reads it |
|---|---|---|
| `.github/workflows/security-checks.yml` | The toolchain-independent check suite on every push, PR and daily: secret scan, semgrep, tool-registry audit, security benchmark, evidence-artifact validator and its self-test. Dependency-audit and lint steps are present but commented out, awaiting a language stack. | CI; anyone diagnosing a red build |

## `.semgrep/` — promoted review rules

| Path | What it is for | Who reads it |
|---|---|---|
| `.semgrep/sql-injection.yml` | Two seed rules showing the review-feedback-promotion pattern: SQL built by string concatenation, and shell execution with interpolated input. **Seed content — retarget or delete per project.** A rule whose languages do not appear in the repo reports zero findings forever and reads as a pass. | CI; anyone adding a rule after the same review comment appears three times |

## `docs/` — documentation

| Path | What it is for | Who reads it |
|---|---|---|
| `docs/SECURITY_PRACTICES.md` | Why the harness exists: the three-layer model (rule / execution / verification) and the mapping from each practice to the file implementing it. Credits the external framework it adapts. | Anyone asking why a control is here rather than what it does |
| `docs/THREAT_MODEL.md` | STRIDE-lite entry template, one per security-sensitive surface, plus the agent-era additions. **Template only until a surface exists.** | Anyone changing auth, crypto, payments or PII handling |
| `docs/design/README.md` | Rule that open proposals live in `docs/design/`, not in decision records, and must be marked `AWAITING DECISION`. | Anyone writing up an undecided question |
| `docs/design/acceptance-criteria.md` | How to write acceptance criteria an agent can actually run: the Group A / Group B split, and how a Group B step is made auditable by a Group A command. | Anyone defining a milestone, phase or exit gate |
| `docs/handoff/CURRENT.md` | The single source of project status and the exact next safe action. The file that lets a cold agent or human resume with no chat history. | Every worker, before anything else |
| `docs/validation/evidence/README.md` | The fixed artifact format for a Group B observation: header fields, redaction rules, worked template. | Anyone recording a manual or instrumented verification |
| `docs/validation/evidence/REQUIRED.json` | Machine-readable manifest of which artifacts each phase must produce, plus the field, tag and forbidden-pattern configuration the validator enforces. Authoritative — the validator rejects artifacts it does not list. | The validator; anyone adding a phase or an artifact |

## `scripts/` — runnable checks and wrappers

| Path | What it is for | Who reads it |
|---|---|---|
| `scripts/audit-agent-compliance.sh` | Periodically re-tests that an agent still obeys a named `SECURITY.md` rule under realistic prompting, catching "the rule drifted to the unread middle of the file". Reports `SKIP` when no agent CLI is on `PATH` and `INCONCLUSIVE` when the harness returns nothing — neither grades as a finding. | Whoever runs the monthly drift check |
| `scripts/audit-tool-registry.sh` | Finds holes in the tool layer: tools called in code but undeclared, declared tools with no timeout, destructive tools with no approval gate. Exits non-zero on any finding and reports `SKIPPED` for the section it could not evaluate. Needs `yq`. | CI; anyone adding a tool |
| `scripts/check-file-map.sh` | `PostToolUse(Write)` hook backing this index. Nags when a newly written, non-ignored, in-repo path is missing here. Never blocks, always exits 0. | Claude Code (automatically) |
| `scripts/cleanup-scanner.py` | Real secret-residue scan of the working tree and staged diff: sensitive filenames, tracked `.env` files, hardcoded-credential patterns. Exit 1 on any finding. Pure stdlib. | CI; the pre-commit hook; anyone ending a session |
| `scripts/safe-exec.sh` | Wraps a destructive command in preview → confirm → log → execute, so destruction is never the silent default. | Anyone aliasing a dangerous command |
| `scripts/security-benchmark.py` | Security asserted as a benchmark rather than a review item. **Ships with three unimplemented benchmarks that report `NOT-IMPLEMENTED` and are never counted as passes.** `--require-implemented` turns it into a gate once wired. | CI; whoever specialises the benchmarks per stack |

## `tests/` — toolchain-independent checks

| Path | What it is for | Who reads it |
|---|---|---|
| `tests/test_evidence_artifacts.py` | Validates the record of every Group B verification: header completeness, evidence tag, `result`, forbidden content, per-artifact content rules. Passes vacuously with zero artifacts; `--require <phase>` turns it into a phase gate; `--self-test` proves the validator can still fail. Pure stdlib. | CI; anyone closing a phase gate |

## `tools/` — tool layer

| Path | What it is for | Who reads it |
|---|---|---|
| `tools/registry.yaml` | Single source of truth for which tools an agent may call, with timeout, concurrency, lock and approval gate per tool. **Ships with example entries — delete the ones your project does not use.** A registry declaring tools nobody calls audits clean and proves nothing. | The tool-runner wrapper; `scripts/audit-tool-registry.sh`; anyone adding a tool |

## Directories referenced but not present

Named by other documents, deliberately not created empty. Create one when it gets its first real
member, and add its rows here in the same change.

| Path | What it would hold |
|---|---|
| `docs/ADR/` | Decision records, MADR format, plus `INDEX.md` routing by reader goal (`AGENTS.md` §6) |
| `docs/validation/evidence/*.md` | The Group B evidence artifacts themselves, one per observation |
| `.agent-context/` | `destructive-log.jsonl` and other operator-local agent state. Gitignored — never committed |
