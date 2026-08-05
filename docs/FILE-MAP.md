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
| `README.md` | What this lab is (TrueWatch first-mile), start-here pointers, and that status lives only in handoff. States no project status by design. | Forkers, first-time readers |
| `CHANGELOG.md` | Release notes for git tags v0.0.1–v0.1.0 (ingest slices + lab checkpoint). | Anyone cutting or consuming a release tag |
| `docker-compose.yml` | Compose: `emit` + optional `datakit` (profile) with `dk,ddtrace,statsd,opentelemetry` (v0.0.2–v0.0.4). | Forkers preferring a clean Docker host |
| `SECURITY.md` | Security ground rules an agent must not guess at: secrets, untrusted input, external actions, dependencies. | Reviewers; anyone touching secrets or external systems |
| `PRODUCT_SENSE.md` | The product red line that hidden destructive actions are a defect, plus the preview/confirm/log/abort protocol. Restates the protocol also given in `AGENTS.md` §10. | Any agent before a destructive command |
| `.gitignore` | Declares what must never be committed. Note the git gotcha recorded in `AGENTS.md` §7: ignore `dir/*`, not `dir/`, or a negation cannot re-include a member. | Anyone adding a file type that might carry secrets |
| `.env.example` | Local env var names (OWL, Workspace Token, DataWay/DK_DATAWAY, DataKit/StatsD); copy to `.env`. | Anyone wiring ingest or OWL |
| `requirements-emitter.txt` | Pinned pip deps for emitter image (`msgpack`, `opentelemetry-proto`). | Compose emit build; host optional for ddtrace/otel |
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
| `.github/workflows/security-checks.yml` | The toolchain-independent check suite on every push, PR and daily: secret scan, semgrep, tool-registry audit, security benchmark, evidence-artifact validator and its self-test, emit payload contracts. Dependency-audit and lint steps are present but commented out, awaiting a language stack. | CI; anyone diagnosing a red build |

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
| `docs/truewatch-owl.md` | Canonical TrueWatch OWL/MCP/CLI guidance for this lab (synced from the trial workspace). Prefer over legacy `/mcp-server/` docs. | Anyone integrating TrueWatch or advising MCP setup |
| `docs/observability-glossary.md` | Metrics/Logs/APM/RUM glossary, span vs spam, and TrueWatch console ↔ signal map for this lab. | Forkers learning platform terms; anyone looking for `trace_id` in the wrong console |
| `docs/runbooks/owl-cli-credentials.md` | Credentials runbook: Open API Key → OWL `.env` (§3–4), Workspace Token + DataWay (§5 W1–W5), OWL CLI install/verify (§6 A–G). | Forkers wiring OWL or ingest credentials |
| `docs/runbooks/dataway-emit.md` | Forker steps to dry-run and POST via DataWay (`scripts/emit.py --mode dataway` or Compose), then find it in Explorer. | Anyone proving ADR-0001 DataWay path |
| `docs/runbooks/datakit-emit.md` | Forker steps for Compose DataKit emit; documents lab series vs side-effect measurement `dk` (self-metrics). | Anyone proving ADR-0001 DataKit path |
| `docs/runbooks/ddtrace-emit.md` | Forker steps for StatsD metric + DDTrace span via DataKit; OWL-first verify then Console. | Anyone proving v0.0.3 / ADR-0003 |
| `docs/runbooks/otel-emit.md` | Forker steps for OTLP protobuf metric + span via DataKit; OWL-first verify then Console. | Anyone proving v0.0.4 / ADR-0003 |
| `docs/ADR/INDEX.md` | Routes decision records by reader goal. | Anyone looking for why a lab choice was made |
| `docs/ADR/0001-three-ingest-paths.md` | Accepted decision: lab exercises DataKit, DataWay direct write, and DDTrace→DataKit (not Datadog Agent→DataKit). | Anyone implementing or scoping ingest emitters |
| `docs/ADR/0002-release-tags-and-emit-mode.md` | Accepted: tags v0.0.1–v0.0.4, `EMIT_MODE` / `--mode`, Docker-first preference. | Anyone cutting releases or adding emit modes |
| `docs/ADR/0003-otel-trace-path.md` | Accepted: v0.0.3/v0.0.4 each emit protocol-native **metric + span** via DataKit. | Anyone implementing ddtrace/otel or comparing to LP ping |
| `docker/Dockerfile.emitter` | Alpine Python emit image; installs `requirements-emitter.txt`, copies emit scripts + payload tests. | Compose `emit`; `scripts/run-emit-payload-tests.sh` |
| `scripts/run-emit-payload-tests.sh` | Builds emitter image and runs `tests/test_emit_payloads.py` inside it (no host pip). | Local verify; CI |
| `tests/test_emit_payloads.py` | In-process contracts: LP/StatsD/OTLP shapes; DataWay dry-run must not print token. Run via Docker script. | CI; anyone changing emit scripts |
| `docs/validation/evidence/README.md` | The fixed artifact format for a Group B observation: header fields, redaction rules, worked template. | Anyone recording a manual or instrumented verification |
| `docs/validation/evidence/REQUIRED.json` | Machine-readable manifest of which artifacts each phase must produce, plus the field, tag and forbidden-pattern configuration the validator enforces. Authoritative — the validator rejects artifacts it does not list. | The validator; anyone adding a phase or an artifact |

## `scripts/` — runnable checks and wrappers

| Path | What it is for | Who reads it |
|---|---|---|
| `scripts/audit-agent-compliance.sh` | Periodically re-tests that an agent still obeys a named `SECURITY.md` rule under realistic prompting, catching "the rule drifted to the unread middle of the file". Reports `SKIP` when no agent CLI is on `PATH` and `INCONCLUSIVE` when the harness returns nothing — neither grades as a finding. | Whoever runs the monthly drift check |
| `scripts/audit-tool-registry.sh` | Finds holes in the tool layer: tools called in code but undeclared, declared tools with no timeout, destructive tools with no approval gate. Exits non-zero on any finding and reports `SKIPPED` for the section it could not evaluate. Needs `yq`. | CI; anyone adding a tool |
| `scripts/check-file-map.sh` | `PostToolUse(Write)` hook backing this index. Nags when a newly written, non-ignored, in-repo path is missing here. Never blocks, always exits 0. | Claude Code (automatically) |
| `scripts/cleanup-scanner.py` | Secret-residue scan: staged/tracked sensitive files and credential patterns. Gitignored local `.env` is allowed (approved lab path). Exit 1 on findings. Pure stdlib. | CI; the pre-commit hook; anyone ending a session |
| `scripts/safe-exec.sh` | Wraps a destructive command in preview → confirm → log → execute, so destruction is never the silent default. | Anyone aliasing a dangerous command |
| `scripts/security-benchmark.py` | Security asserted as a benchmark rather than a review item. **Ships with three unimplemented benchmarks that report `NOT-IMPLEMENTED` and are never counted as passes.** `--require-implemented` turns it into a gate once wired. | CI; whoever specialises the benchmarks per stack |
| `scripts/emit.py` | Unified emitter entry: `--mode` / `EMIT_MODE`; `--count` / `--interval` (default 5s) for spaced repeats across all modes. | Anyone emitting lab telemetry |
| `scripts/emit_dataway.py` | DataWay mode (v0.0.1): synthetic metric/log to `/v1/write/…`; redacts token; lab User-Agent (avoids CF 1010). | Forkers / agents proving DataWay ingest |
| `scripts/emit_datakit.py` | DataKit mode (v0.0.2): synthetic metric/log to local DataKit `/v1/write/…` (`DATAKIT_URL`, default `:9529`). | Forkers / agents proving DataKit ingest |
| `scripts/emit_ddtrace.py` | DDTrace mode (v0.0.3): DogStatsD metric + `/v0.4/traces` span (needs msgpack). | Forkers / agents proving DDTrace ingest |
| `scripts/emit_otel.py` | OTel mode (v0.0.4): OTLP protobuf metric + span to `/otel/v1/{metrics,traces}`. | Forkers / agents proving OTel ingest |

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
| `docs/validation/evidence/*.md` | The Group B evidence artifacts themselves, one per observation |
| `.agent-context/` | `destructive-log.jsonl` and other operator-local agent state. Gitignored — never committed |
