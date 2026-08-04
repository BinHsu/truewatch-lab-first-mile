# Security Practices — why the harness in this template exists

> **Framework credit:** the 7-practice model below is adapted from Wisely Chen's
> *"Harness Engineering — security best practices for AI agents"* —
> <https://ai-coding.wiselychen.com/harness-engineering-security-best-practices/>.
> That article is the canonical source; this file is a short summary **in our own words**
> plus the mapping to where each practice is implemented in this template. Read the
> original for the full reasoning.

## The mental model — three layers, in order

An AI agent staying out of trouble is not luck. It comes from writing security into every
layer of the harness, so "be careful" becomes an engineering property instead of a hope.
The seven practices form three layers, applied in a strict order:

| Layer | The claim it makes | Practices |
|---|---|---|
| **1. Rule** — what the agent reads | "The agent must never have to guess the rule." | 2, 3, 6 |
| **2. Execution** — what the agent *can do* | "Even if the rule is missed, the unsafe action is physically blocked." | 1, 4, 7 |
| **3. Verification** — did it actually hold | "Prove it on every run, not on reviewer mood." | 4, 5 |

A rule the agent can ignore is a suggestion. A rule the execution layer enforces is a
boundary. The verification layer is what tells you the boundary is still standing.
(This is the same posture as `~/.claude/CLAUDE.md` rule: *environment is sustained by
boundaries, not by virtue*.)

## The 7 practices → where this template implements them

### 1. Least-privilege tool access *(Execution)*
The agent gets read-only by default; write and destructive tools are granted explicitly.
- **In this template:** `.claude/settings.json` allow/deny lists; `AGENTS.md` three-way
  tool table (read-only / write / destructive).

### 2. Security rules are not buried mid-file *(Rule)*
Rules an agent must follow live where it will actually read them — top of the file, or a
file it is told to read first — not in paragraph 40 of a long doc.
- **In this template:** `CLAUDE.md` opens by pointing at the rule sources; `AGENTS.md`
  has a "⚠️ Read first" block; `scripts/audit-agent-compliance.sh` periodically tests
  whether the agent still honours them (drift check).

### 3. SECURITY.md pins the rules *(Rule)*
One file the agent treats as non-negotiable security ground truth, covering the recurring
hazards: secrets, untrusted input, external actions, dependencies.
- **In this template:** `SECURITY.md` (four categories); `docs/THREAT_MODEL.md` for any
  auth / crypto / payments / PII surface (STRIDE-lite, one entry per surface).

### 4. Sandbox isolation + review-feedback promotion *(Execution → Verification)*
Run untrusted work in isolation; and every time the same security comment appears in
review, promote it from a human reminder to an automated check so it can never regress.
- **In this template:** `.githooks/pre-commit` blocks `.env` files + hardcoded secrets;
  `.semgrep/` holds promoted review rules (e.g. raw-SQL-concat → parameterized);
  CI runs both on every push.

### 5. Security lives in the benchmark, not just in review *(Verification)*
Security checks run automatically on every change — they do not depend on whether a
reviewer happened to look for them that day.
- **In this template:** `scripts/cleanup-scanner.py` (secret-residue scan, real),
  `scripts/security-benchmark.py` (cross-user-isolation / rate-limit / destructive-gated
  baselines — stubs to specialise), wired into `.github/workflows/security-checks.yml`.

### 6. Hidden destructive actions are a product red line *(Rule → Execution)*
A "done" that quietly deleted data, or a destructive-by-default script that needs a flag
to *preview*, is a product defect — not a UX nit. Destructive actions are always visible,
confirmed, and logged before they run.
- **In this template:** `PRODUCT_SENSE.md` (the red line + protocol);
  `scripts/safe-exec.sh` (preview → confirm → log → execute);
  `.agent-context/destructive-log.jsonl` (append-only audit trail).

### 7. Tool safety is production-grade *(Execution)*
Tools the agent can call are treated like production endpoints: declared in one place,
with type, timeout, concurrency limits, and an approval gate on destructive ones.
- **In this template:** `tools/registry.yaml` (single source of truth);
  `scripts/audit-tool-registry.sh` (flags undeclared tools, missing timeouts, and
  destructive tools without an approval gate).

## How to use this in a new repo

1. Keep the harness; fill the `{{PLACEHOLDER}}` spots in `SECURITY.md`, `CLAUDE.md`,
   `THREAT_MODEL.md` for your domain.
2. Enable the hook: `git config core.hooksPath .githooks`.
3. Specialise the per-stack stubs: the benchmark baselines, and the dependency-audit +
   lint steps in the CI workflow (uncomment the line for your language).
4. When the same security comment shows up in review ~3 times, add a `.semgrep/` rule for
   it (practice 4) — that is how the harness gets stronger over time.

---

*Summary maintained for this template. The authoritative treatment is the source article
linked at the top.*
