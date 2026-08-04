# Handoff — current state

> **This file is the single source of truth for project status.** If any other document disagrees
> with it, this one wins and the drift should be fixed. See `AGENTS.md` §3.
>
> **Update this BEFORE starting a long or risky operation, not after.** State what you are about to
> do, the exact command, and where the next worker resumes if you never come back. Commit it. Then
> do the thing. Then update with the result. A post-hoc-only handoff is worthless precisely when it
> is needed. See `AGENTS.md` §4.

**Last updated:** {{DATE}} — {{who / which milestone}}

---

## 1. Read these first

1. `docs/handoff/CURRENT.md` (this file)
2. `README.md`
3. `AGENTS.md`
4. `docs/ADR/INDEX.md`

You do **not** need any conversation history. If something here is unclear, that is a defect in this
file — fix it rather than guessing.

## 2. Last completed milestone

{{What is actually done. Not what was attempted.}}

| Commit | Content |
|---|---|
| {{sha}} | {{one line}} |

## 3. Repository state

- Branch: {{}}
- Remote: {{}}
- Visibility: {{public / private — note that private→public is one command, while the reverse does
  not un-publish anything already fetched, forked or indexed}}
- Hooks active: `git config core.hooksPath .githooks` → {{yes/no}}
- Local path is machine-specific and deliberately not recorded here.

## 4. Environment / system state

{{Whatever a stranger must know before running anything: services up or down, toolchain installed or
not, migrations applied, external resources provisioned and billing, hardware attached. Tag each with
an evidence tag from `AGENTS.md` §5.}}

## 5. Commands already run

```
{{exact commands, so nobody repeats a destructive one or re-derives a result}}
```

## 6. Test results

{{What passed, what failed, what was never run. "Not run" is a valid and useful answer;
"probably fine" is not.}}

## 7. Current blockers, in priority order

1. {{}}

## 8. AWAITING DECISION — owner only

Do not resolve these by inference. They are recorded, not forgotten.

1. {{}}

## 9. Exact next safe action

```bash
{{a runnable command, not a description of one}}
```

{{If the next action is irreversible or outward-facing, say so here and say that it needs owner
confirmation first.}}

## 10. Things that will bite you

{{Traps already discovered the hard way, each with a pointer to where it is documented in full.
For anyone arriving cold this is the highest-value section in the file — the difference between
losing an evening and not.}}
