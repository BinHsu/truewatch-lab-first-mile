# PRODUCT_SENSE.md

> Product-judgment red lines for agent-driven work. Distinct from `SECURITY.md` (security
> rules): this file is about **product behaviour that must never surprise the user** — the
> placement itself signals "hidden destructive action is a product principle, not just a
> security one".

## No-Go Pattern #1 — Hidden destructive actions

A destructive action removes data, overwrites without backup, or changes state visible to
other users (`rm`, `drop`, `delete`, `truncate`, `git reset --hard`, force push, deploy,
send message, charge payment).

**These must NEVER be hidden.** Anti-patterns (all forbidden):
- An agent prints "done" but quietly deleted files.
- A UI control labelled "Optimize" that actually truncates a table.
- A script whose **default** behaviour is destructive and needs `--dry-run` to preview
  (the order is reversed — preview must be the default; destruction needs an explicit flag).

## Destructive Action Protocol (mandatory)

For every destructive action you MUST, in order:
1. **Preview** — print exactly what will change: "About to delete/overwrite X, Y, Z. This is irreversible."
2. **Confirm** — stop and wait for the user to type **`confirm`** (not "ok", not "yes", not "go ahead").
3. **Log before executing** — append to `.agent-context/destructive-log.jsonl` BEFORE running.
4. **Abort if unconfirmed** — if the user does not confirm in the same turn, abort.

If you are about to run a destructive command and have NOT done all four, STOP and re-read this.

Enforcement: route destructive commands through `scripts/safe-exec.sh` (preview + confirm +
log + execute). The cross-project global rule (`~/.claude/CLAUDE.md`) carries the same posture.

## Real incidents this prevents

The Replit / PocketOS / DataTalks.Club database-wipe incidents share one pattern: the
destructive action was **hidden** (agent did `git reset --hard` / dropped the DB without a
preview-and-confirm step). This protocol would have caught ~90% of them.
