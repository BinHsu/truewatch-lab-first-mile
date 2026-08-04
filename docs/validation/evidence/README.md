# Evidence artifacts

One file per observation that only a person or an instrument could make. An agent cannot watch a
screen, press a physical button, or stand next to a rack. It can check the record of someone who
did — provided the record has a fixed shape.

That is all this directory is: the fixed shape.

- What each phase must produce: [`REQUIRED.json`](REQUIRED.json) — machine-readable, authoritative.
- Why the split exists: [`../../design/acceptance-criteria.md`](../../design/acceptance-criteria.md).
- Validator: `python3 tests/test_evidence_artifacts.py` (pure stdlib, no network, no services).
- Evidence tags: `AGENTS.md` §5.

## Template

Copy this, keep the header, replace the body with what you actually observed.

```markdown
---
artifact_id: EX-B1
phase: example
date: 2026-01-31
method: the command typed or the instrument used — enough for someone else to repeat it
evidence_tag: VERIFIED
result: pass
---

Observed:

    <the output, the reading, or what was on the screen — redacted>
```

Header fields, from `REQUIRED.json`:

| Field | Required | Meaning |
|---|---|---|
| `artifact_id` | yes | Matches the id in `REQUIRED.json` |
| `phase` | yes | The phase key in `REQUIRED.json` |
| `date` | yes | `YYYY-MM-DD`, the day it was observed |
| `method` | yes | The command typed or the instrument used. Enough to repeat it |
| `evidence_tag` | yes | `AGENTS.md` §5 tag. `INFERRED`, `COMMUNITY` and `NO-EVIDENCE-FOUND` can never carry `result: pass` |
| `result` | yes | `pass`, `fail` or `blocked` |
| `commit` | sometimes | Git SHA of the code that produced the observation |
| `source_sha256` | sometimes | SHA-256 of a photograph, trace or capture held outside the repo |
| `stopped_at` | optional | For `result: fail`, the exact point it stopped |
| `notes` | optional | Anything a future reader needs |

An artifact may also declare fields listed in its own `requires_fields` entry. The validator derives
the allowed set from the manifest, so a field required by one artifact is never rejected as unknown.

## Rules

1. **A failure is recorded, not deleted.** `result: fail` with `stopped_at` is worth more than a
   missing file. A gate that never closes because the truth is written down is working correctly.
2. **Redact before saving.** No credentials, tokens, network names, MAC addresses, device node names
   or absolute local paths. The validator rejects them; that is a backstop, not your first line.
3. **Binaries stay out.** Photographs, traces and dumps live outside the repository. The artifact
   records the file's SHA-256 in `source_sha256` and describes what it shows.
4. **A new artifact means editing `REQUIRED.json` first.** The validator rejects files it does not
   know about, so the plan and the evidence cannot drift apart quietly.
5. **The tag and the result must agree.** `result: pass` requires a tag from `passing_tags`.
   Reasoning about a system is not an observation of it.
