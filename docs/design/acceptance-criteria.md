# Writing acceptance criteria an agent can actually run

Most acceptance criteria are written for a reader, not a runner: "the service degrades gracefully
under load", "the operator can recover from a failed migration". A person nods. An agent cannot tell
whether that is true, so it either guesses or stops.

Split every criterion into two groups instead. The split is the whole idea.

|  | Group A | Group B |
|---|---|---|
| Needs a device, an instrument or a person? | No | Yes |
| Needs a live environment? | Noted per criterion | Usually |
| Who can run it | Any agent or person, unattended, in a sandbox | A person at the bench or console |
| Shape | A command with an exit code, or a diffable output | An observation |
| Produces | Its own exit code | **A named evidence artifact** |

**Group B is made auditable by Group A.** Every Group B step writes a record to
`../validation/evidence/` in a fixed format, and `tests/test_evidence_artifacts.py` checks that
record: header completeness, evidence tag, `result`, required content, and the absence of anything
`AGENTS.md` §7 forbids committing.

An agent that cannot press a button can still verify that someone did, recorded what happened, and
did not paste a credential into the log. That is the point: **the observation is out of reach, the
record of it is not.**

So each phase's gate closes with one command:

```bash
python3 tests/test_evidence_artifacts.py --require <phase>
```

It exits non-zero, naming the missing or failing artifact, until that phase's manual work is
recorded. The authoritative artifact list is `../validation/evidence/REQUIRED.json`; the artifact
format is `../validation/evidence/README.md`.

## How to write each group

**Group A.** State the exact command and the exit code that means pass. If you cannot name a
command, it is not Group A — do not pretend otherwise by writing a check that always passes
(`AGENTS.md` §12). Group A criteria are the ones an agent can close alone, so put as much in this
group as honestly fits.

**Group B.** State what must be observed, by whom or with what, and which artifact file records it.
Add the artifact to `REQUIRED.json` in the same change. Write the criterion so a stranger at the
bench knows when it is satisfied — "the status LED is steady green within 5 seconds of power-on",
not "boot works".

**Tag every criterion** with the `AGENTS.md` §5 evidence tag a passing result earns. Group A passes
are `VERIFIED` — observed behaviour of real code, not reasoning about it. Group B passes carry
whatever their evidence earns. `INFERRED`, `COMMUNITY` and `NO-EVIDENCE-FOUND` are never a pass in
either group, and the validator enforces that.

**Say who can close the gate.** If eight of a phase's fifteen criteria are Group B, write that down.
It sets the expectation that an agent gets every Group A criterion green, prepares the artifact
files, and then stops — rather than appearing to stall.

## Two properties of the validator, both earned

**It passes vacuously with zero artifacts.** That is what makes it safe to wire into CI on day one.
`--require <phase>` is what turns it into a gate. Without that split, a validator either breaks CI
before any evidence exists or passes silently forever.

**It rejects a `pass` that the evidence does not support**, and rejects artifacts carrying secrets
or machine-specific values. A record that can claim anything is not a record.

Run `python3 tests/test_evidence_artifacts.py --self-test` to see it fail on demand.

## Phases live in your project, not here

This file describes the mechanism. The phases, their criteria and who closes them belong in your own
`docs/design/` document, marked `AWAITING DECISION` until the owner has agreed to them
(`AGENTS.md` §6). Keep `REQUIRED.json` in step with that document — and where they disagree,
`REQUIRED.json` wins, because it is the one a machine reads.
