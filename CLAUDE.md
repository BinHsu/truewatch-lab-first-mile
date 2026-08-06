@AGENTS.md

# CLAUDE.md — truewatch-lab-first-mile (Claude-specific only)

> **All shared agent policy for this repo lives in [`AGENTS.md`](AGENTS.md)**, imported on line 1
> above. Claude Code does not read `AGENTS.md` on its own, which is the only reason that import
> exists.
>
> **Do not put policy here.** If a rule applies to every agent — safety gates, what may not be
> committed, decision-record conventions, handoff protocol, tool-access classes — it belongs in
> `AGENTS.md`. A rule written in both files drifts, and the copy that goes stale is the one that
> gets read.
>
> Cross-project disciplines (language, date handling, bash/zsh word-splitting, safety guardrails,
> externalize-decisions, pre-push-diff, non-host-install, reusable-PII, no-hallucination,
> subagent-delegation) live in `~/.claude/CLAUDE.md` and load globally. They are **not** repeated
> here either.

This file holds only what is specific to Claude Code as a tool.

## Permissions

Least-privilege allow/deny lists are enforced in `.claude/settings.json`. The three-way
classification they implement is defined in `AGENTS.md`, not here — settings are the *mechanism*,
`AGENTS.md` is the *rule*.

## Delegation boundary

- Keep the main session for orchestration, decisions and merge-gating. Delegate independent,
  citation-driven or multi-file work.
- **Work needing interactive per-action approval stays in the main session.** A subagent cannot
  reliably obtain fresh approval, so a permission-gated call can fail silently.
- Name the model when spawning and pick it by stakes: triage and read fan-out → cheap tier;
  exploration and light synthesis → mid tier; cross-file reasoning and decide-what-to-change → top
  tier. An expensive model watching logs scroll is waste — polling is a mechanism job, not an agent
  job.
- **Never read a spawned subagent's `.output` file via the shell.** It is the full JSONL
  conversation transcript and will overflow context. Use the agent's returned result.

## Conflict resolution

If two documents disagree, the more recent and more specific wins — but record the drift in
`docs/handoff/CURRENT.md` rather than silently picking one.

## TrueWatch / OWL

- Product integration rules: `docs/truewatch-owl.md` (do not answer OWL/MCP setup from memory when
  this file disagrees with official docs).
- Lab-verified gotchas: `docs/truewatch-tips.md` — append new tips there (duty defined in
  `AGENTS.md`, not duplicated here).
- Prefer configured OWL MCP (`Authorization: Bearer …`) or local `owl` + `owl-diagnostics` over
  inventing DQL results.
- Legacy Tobylike MCP URL/header must not be recommended unless the owner asks for legacy compat.
