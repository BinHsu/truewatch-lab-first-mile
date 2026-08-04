#!/usr/bin/env python3
"""cleanup-scanner.py — Practice 5 (security in the pipeline, not just review).

Scans the working tree for secret-residue at session-end / pre-commit / in CI:
  - critical files that should never be committed (.env*, SSH keys, cloud creds)
  - hardcoded-secret content patterns in tracked/staged files

Exit 1 on any finding (so CI blocks). Stack-agnostic — pure stdlib.
Run: python3 scripts/cleanup-scanner.py
"""
from __future__ import annotations
import os
import re
import subprocess
import sys

CRITICAL_FILES = [
    ".env", ".env.local", ".env.production", ".env.staging",
    "id_rsa", "id_ed25519", ".ssh/config",
    ".aws/credentials", ".gcloud/credentials.json",
]

CONTENT_PATTERNS = [
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"ghp_[A-Za-z0-9]{36}")),
    ("OpenAI key", re.compile(r"sk-[A-Za-z0-9]{48}")),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9-]{90,}")),
    ("Generic secret", re.compile(r"(?i)(secret|password|api[_-]?key|token)\s*[:=]\s*[\"'][A-Za-z0-9]{16,}")),
]

EXCLUDE_SUFFIXES = (".example", ".sample", ".md")


def staged_files() -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"], text=True
        ).strip()
        return [f for f in out.splitlines() if f]
    except subprocess.CalledProcessError:
        return []


def tracked_files() -> list[str]:
    try:
        out = subprocess.check_output(["git", "ls-files"], text=True).strip()
        return [f for f in out.splitlines() if f]
    except subprocess.CalledProcessError:
        return []


def scan() -> list[str]:
    issues: list[str] = []

    # 1. critical files present anywhere in tree
    for name in CRITICAL_FILES:
        if os.path.exists(name):
            issues.append(f"CRITICAL: sensitive file present: {name}")

    # 2. critical files tracked by git (worse — committed)
    for f in tracked_files():
        base = os.path.basename(f)
        if base.startswith(".env") and not f.endswith(EXCLUDE_SUFFIXES):
            issues.append(f"CRITICAL: .env file is tracked: {f}")

    # 3. content scan on staged files (pre-commit) or tracked (CI)
    targets = staged_files() or tracked_files()
    for f in targets:
        if f.endswith(EXCLUDE_SUFFIXES) or not os.path.isfile(f):
            continue
        try:
            content = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for name, rx in CONTENT_PATTERNS:
            if rx.search(content):
                issues.append(f"CRITICAL: {name} in {f}")

    return issues


def main() -> int:
    issues = scan()
    if issues:
        print("❌ Cleanup scan failed:")
        for i in issues:
            print(f"  {i}")
        print("→ Move secrets to env / secrets manager (SECURITY.md §1).")
        return 1
    print("✅ Clean state verified — no secret residue.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
