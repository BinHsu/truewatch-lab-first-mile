# Path-scoped rules

Drop `*.md` files here for rules that apply only to specific file types or directories —
loaded **on demand** when the agent touches matching paths, so they don't bloat global
context.

Example (front-matter declares the path glob):

```markdown
---
paths: ["terraform/**", "**/*.tf"]
---
# Terraform rules
- Module library design; no inline resources in root beyond composition.
- `terraform plan` must show zero diff after apply (no manual drift).
- Destructive ops (`apply`/`destroy` on prod) require approval — see SECURITY.md §3.
```

Typical splits: `terraform.md` (terraform/**), `tests.md` (tests/**, **/*.test.*),
`kubernetes.md` (**/*.yaml), `frontend.md` (src/renderer/**).

Cross-project disciplines stay in `~/.claude/CLAUDE.md`; repo-wide rules in `CLAUDE.md`;
only path-specific rules belong here.
