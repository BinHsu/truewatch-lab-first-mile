#!/usr/bin/env python3
"""Validate the evidence artifacts that record Group B verification steps.

A Group B step cannot be run by an agent — it needs a person, a device or an instrument.
Its *record* can be checked by anyone. This validator checks that record: header
completeness, evidence tag, result, required content, and the absence of anything
AGENTS.md section 7 forbids committing.

Pure stdlib. No network, no toolchain, no services. Runs anywhere Python 3 runs.

Three modes:

    python3 tests/test_evidence_artifacts.py
        Validate every artifact that exists. Passes when none exist yet.
        Safe to run at any time and in CI.

    python3 tests/test_evidence_artifacts.py --require <phase>
        Also assert every artifact that phase demands exists and passes.
        Fails until that phase's manual work is recorded. This is the command
        that closes a phase exit gate.

    python3 tests/test_evidence_artifacts.py --self-test
        Prove the validator can still fail. Runs synthetic artifacts through the
        real checks and asserts the expected verdicts. See AGENTS.md section 12.

Artifact format: Markdown with a front-matter header.

    ---
    artifact_id: EX-B1
    phase: example
    date: 2026-01-31
    method: what was typed or which instrument was used, enough to repeat it
    evidence_tag: VERIFIED
    result: pass
    ---

    Observed: <what happened, redacted>

Rules enforced here:
  - every required header field present, and no unknown field;
  - evidence_tag is one of AGENTS.md section 5's tags;
  - result: pass requires a tag that can carry a pass. INFERRED, COMMUNITY and
    NO-EVIDENCE-FOUND never pass;
  - source_sha256, when present, is 64 hex characters;
  - no secret or machine-specific value (see global_forbidden_patterns);
  - per-artifact min_body_lines / must_contain / must_not_contain rules.

The authoritative artifact list is docs/validation/evidence/REQUIRED.json.
How to write criteria in the first place: docs/design/acceptance-criteria.md.
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "docs" / "validation" / "evidence" / "REQUIRED.json"


def allowed_fields(cfg: dict) -> set[str]:
    """Every header field an artifact may carry.

    Derived, never hand-maintained. A field listed as required — globally, or by one
    artifact's `requires_fields` — but forgotten from the allowed set would make every
    conforming artifact invalid, so no gate could ever close. Computing the union here
    makes that state unreachable; --self-test guards the regression.
    """
    fields = set(cfg.get("required_fields", [])) | set(cfg.get("optional_fields", []))
    for entries in cfg.get("phases", {}).values():
        for entry in entries:
            fields |= set(entry.get("requires_fields", []))
    return fields


def parse_header(text: str) -> tuple[dict[str, str], str] | None:
    """Split leading '---' front matter from the body. None when absent or malformed."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            header: dict[str, str] = {}
            for raw in lines[1:i]:
                if not raw.strip() or raw.lstrip().startswith("#"):
                    continue
                if ":" not in raw:
                    return None
                key, _, value = raw.partition(":")
                header[key.strip()] = value.strip()
            return header, "\n".join(lines[i + 1:])
    return None


def check_artifact(path: Path, spec: dict, cfg: dict, failures: list[str]) -> str | None:
    """Validate one artifact file. Returns its `result` value, or None."""
    name = path.name
    text = path.read_text(encoding="utf-8", errors="replace")

    def fail(msg: str) -> None:
        failures.append(f"{name}: {msg}")

    parsed = parse_header(text)
    if parsed is None:
        fail("no '---' front-matter header, or a header line without a colon")
        return None
    header, body = parsed

    allowed = allowed_fields(cfg)
    for field in cfg["required_fields"]:
        if not header.get(field):
            fail(f"header field '{field}' missing or empty")
    for field in header:
        if field not in allowed:
            fail(f"unknown header field '{field}' (allowed: {sorted(allowed)})")
    for field in spec.get("requires_fields", []):
        if not header.get(field):
            fail(f"this artifact additionally requires header field '{field}'")

    tag = header.get("evidence_tag", "")
    if tag and tag not in cfg["allowed_tags"]:
        fail(f"evidence_tag '{tag}' is not an AGENTS.md section 5 tag")

    result = header.get("result", "")
    if result and result not in cfg["allowed_results"]:
        fail(f"result '{result}' not one of {cfg['allowed_results']}")

    if result == "pass" and tag not in cfg["passing_tags"]:
        fail(f"result: pass with evidence_tag '{tag}'. Only {cfg['passing_tags']} "
             f"can carry a pass — a non-passing tag never passes")

    sha = header.get("source_sha256")
    if sha and not re.fullmatch(r"[0-9a-fA-F]{64}", sha):
        fail("source_sha256 must be 64 hex characters")

    date = header.get("date", "")
    if date and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        fail("date must be YYYY-MM-DD")

    for what, pattern in cfg["global_forbidden_patterns"]:
        if re.search(pattern, text):
            fail(f"contains {what}. Redact it — AGENTS.md section 7")

    min_lines = spec.get("min_body_lines", 0)
    real = [ln for ln in body.splitlines() if ln.strip()]
    if len(real) < min_lines:
        fail(f"body has {len(real)} non-blank lines, needs at least {min_lines}")

    for pattern in spec.get("must_contain", []):
        if not re.search(pattern, body):
            fail(f"body must record /{pattern}/ and does not")
    for pattern in spec.get("must_not_contain", []):
        if re.search(pattern, body):
            fail(f"body must not contain /{pattern}/")

    return result


def run(evidence_dir: Path, cfg: dict, require_phase: str | None) -> tuple[int, str]:
    """Validate a directory of artifacts. Returns (exit_code, summary line)."""
    failures: list[str] = []

    specs: dict[str, dict] = {}
    for phase, entries in cfg["phases"].items():
        for entry in entries:
            specs[entry["file"]] = dict(entry, phase=phase)

    # 1. Every artifact that exists must be well-formed.
    #    Zero artifacts is a vacuous pass, on purpose: this has to be safe in CI from the
    #    first commit. --require is what turns it into a gate (AGENTS.md section 12).
    results: dict[str, str | None] = {}
    present = sorted(p for p in evidence_dir.glob("*.md") if p.name != "README.md") \
        if evidence_dir.is_dir() else []
    for path in present:
        spec = specs.get(path.name)
        if spec is None:
            failures.append(f"{path.name}: not listed in REQUIRED.json. Add it there "
                            f"first, so the plan and the evidence stay in step")
            spec = {}
        results[path.name] = check_artifact(path, spec, cfg, failures)

    # 2. Paired artifacts: if one exists, its declared partner must too.
    for name, spec in specs.items():
        if name not in results:
            continue
        for partner in spec.get("implies", []):
            if partner not in results:
                failures.append(f"{name} exists without {partner}, which it requires")

    # 3. With --require, the named phase's artifacts must exist and pass.
    if require_phase is not None:
        entries = cfg["phases"].get(require_phase)
        if entries is None:
            return 1, (f"FAIL: no phase '{require_phase}' in REQUIRED.json "
                       f"(have {sorted(cfg['phases'])})")
        for entry in entries:
            if entry.get("optional"):
                continue
            name = entry["file"]
            if name not in results:
                failures.append(f"phase {require_phase} gate: {name} missing "
                                f"({entry.get('title', 'no title')})")
            elif results[name] != "pass":
                failures.append(f"phase {require_phase} gate: {name} records "
                                f"result: {results[name] or '<none>'}, not pass")

    if failures:
        lines = [f"{len(failures)} evidence failure(s):"]
        lines += [f"  - {f}" for f in failures]
        return 1, "\n".join(lines)

    scope = f"phase {require_phase} gate" if require_phase is not None else "well-formedness"
    if not present and require_phase is None:
        return 0, ("evidence artifacts: 0 present, nothing to check "
                   "(vacuous pass — use --require <phase> to gate)")
    return 0, f"evidence artifacts: {len(present)} checked, {scope} satisfied"


# ── self-test ────────────────────────────────────────────────────────────────────────
# A validator nobody has watched fail is indistinguishable from one that cannot fail.

SELF_TEST_CFG = {
    "required_fields": ["artifact_id", "date", "evidence_tag", "result"],
    "optional_fields": ["notes"],
    "allowed_tags": ["VERIFIED", "INFERRED"],
    "passing_tags": ["VERIFIED"],
    "allowed_results": ["pass", "fail"],
    "global_forbidden_patterns": [
        ["a MAC address", r"\b([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"],
    ],
    "phases": {
        "t": [
            {"id": "T1", "file": "t1.md", "title": "plain", "must_contain": ["(?i)observed"]},
            {"id": "T2", "file": "t2.md", "title": "needs an extra field",
             "requires_fields": ["build_ref"]},
        ],
    },
}

GOOD = """---
artifact_id: T1
date: 2026-01-31
evidence_tag: VERIFIED
result: pass
---

Observed: the thing did the thing.
"""

SELF_TEST_CASES: list[tuple[str, str, str, str | None]] = [
    # (case name, artifact filename, file body, substring expected in a failure)
    ("well-formed artifact passes", "t1.md", GOOD, None),
    ("spec-level required field is not 'unknown'", "t2.md",
     GOOD.replace("artifact_id: T1", "artifact_id: T2\nbuild_ref: abc123"), None),
    ("spec-level required field is enforced", "t2.md", GOOD.replace("T1", "T2"),
     "additionally requires header field 'build_ref'"),
    ("pass under a non-passing tag is rejected", "t1.md",
     GOOD.replace("VERIFIED", "INFERRED"), "never passes"),
    ("unknown tag is rejected", "t1.md", GOOD.replace("VERIFIED", "MADE-UP"),
     "is not an AGENTS.md section 5 tag"),
    ("missing required field is rejected", "t1.md", GOOD.replace("date: 2026-01-31\n", ""),
     "header field 'date' missing"),
    ("unknown header field is rejected", "t1.md",
     GOOD.replace("result: pass", "result: pass\nwhatever: 1"), "unknown header field"),
    ("bad date is rejected", "t1.md", GOOD.replace("2026-01-31", "31/01/2026"),
     "date must be YYYY-MM-DD"),
    ("missing front matter is rejected", "t1.md", "no header here\n",
     "no '---' front-matter header"),
    ("forbidden value is rejected", "t1.md",
     GOOD.replace("did the thing.", "did the thing at de:ad:be:ef:00:01."),
     "contains a MAC address"),
    ("must_contain is enforced", "t1.md", GOOD.replace("Observed:", "Saw:"),
     "must record"),
    ("unlisted artifact is rejected", "stray.md", GOOD, "not listed in REQUIRED.json"),
]


def self_test() -> int:
    problems: list[str] = []

    # The allowed set must be derived, not hand-maintained. This is the bug that once
    # made every conforming artifact invalid, so no gate could close.
    derived = allowed_fields(SELF_TEST_CFG)
    for field in SELF_TEST_CFG["required_fields"]:
        if field not in derived:
            problems.append(f"allowed_fields() omits required field '{field}'")
    if "build_ref" not in derived:
        problems.append("allowed_fields() omits a field required by one artifact's spec")

    # Vacuous pass on an empty directory.
    with tempfile.TemporaryDirectory() as tmp:
        rc, msg = run(Path(tmp), SELF_TEST_CFG, None)
        if rc != 0:
            problems.append(f"empty directory should pass vacuously, got rc={rc}: {msg}")
        if "0 present" not in msg:
            problems.append(f"empty directory should say the scope was empty, said: {msg}")

        # --require on an empty directory must fail: that is the gate.
        rc, msg = run(Path(tmp), SELF_TEST_CFG, "t")
        if rc == 0:
            problems.append("--require on an empty directory should fail, it passed")

        # --require on an unknown phase must fail rather than pass silently.
        rc, _ = run(Path(tmp), SELF_TEST_CFG, "nope")
        if rc == 0:
            problems.append("--require with an unknown phase should fail, it passed")

    for name, filename, body, expect in SELF_TEST_CASES:
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / filename).write_text(body, encoding="utf-8")
            rc, msg = run(d, SELF_TEST_CFG, None)
            if expect is None:
                if rc != 0:
                    problems.append(f"{name}: expected pass, got:\n{msg}")
            else:
                if rc == 0:
                    problems.append(f"{name}: expected failure, got a pass")
                elif expect not in msg:
                    problems.append(f"{name}: expected {expect!r} in output, got:\n{msg}")

    negatives = sum(1 for _, _, _, e in SELF_TEST_CASES if e is not None)
    if negatives == 0:
        problems.append("self-test has no negative cases — it cannot prove anything")

    if problems:
        print(f"SELF-TEST FAILED — {len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"self-test: {len(SELF_TEST_CASES)} cases, {negatives} of them negative — "
          f"the validator can still fail")
    return 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()

    require_phase: str | None = None
    if "--require" in argv:
        i = argv.index("--require")
        if i + 1 >= len(argv):
            print("usage: test_evidence_artifacts.py [--require <phase>] [--self-test]")
            return 2
        require_phase = argv[i + 1]

    if not MANIFEST.exists():
        print(f"FAIL: artifact manifest not found at {MANIFEST.relative_to(REPO)}")
        return 1
    cfg = json.loads(MANIFEST.read_text(encoding="utf-8"))

    rc, msg = run(REPO / cfg["artifact_dir"], cfg, require_phase)
    print(msg)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
