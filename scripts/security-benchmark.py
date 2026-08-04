#!/usr/bin/env python3
"""security-benchmark.py — Practice 5: security as an automated benchmark, not a review item.

Each benchmark asserts a security behaviour that must hold on every agent task / PR.

This is a SKELETON. The three baseline benchmarks below are NOT IMPLEMENTED: they report
NOT-IMPLEMENTED and are never counted as passes, because a stub that reports a pass is
worse than no check at all (AGENTS.md section 12). Wire each one to your stack by
replacing its body with a real assertion and returning Result.pass_/Result.fail.

Run:
    python3 scripts/security-benchmark.py
        Report status. Exit 0 while benchmarks are unimplemented, so a fresh repo is not
        red on day one. Exit 1 if any *implemented* benchmark fails.

    python3 scripts/security-benchmark.py --require-implemented
        Also fail while any benchmark is still a stub. Switch CI to this once the suite
        is wired, and it stays honest from then on.

Add a new benchmark whenever the suite has held 100% for two weeks.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Callable

PASS = "PASS"
FAIL = "FAIL"
NOT_IMPLEMENTED = "NOT-IMPLEMENTED"


@dataclass
class Result:
    name: str
    status: str
    details: str

    @staticmethod
    def pass_(name: str, details: str) -> "Result":
        return Result(name, PASS, details)

    @staticmethod
    def fail(name: str, details: str) -> "Result":
        return Result(name, FAIL, details)

    @staticmethod
    def stub(name: str, wire_it_to: str) -> "Result":
        return Result(name, NOT_IMPLEMENTED,
                      f"no assertion yet — wire it to {wire_it_to}")


def cross_user_isolation() -> Result:
    # TODO: create user A with secret data + user B with no access; run the agent as B
    # asking for A's data; assert the agent refuses / returns empty.
    return Result.stub("cross-user isolation", "your auth fixture and agent harness")


def rate_limit_enforced() -> Result:
    # TODO: fire N>limit requests at the endpoint; assert at least one 429.
    return Result.stub("rate limit returns 429", "your rate-limited endpoint")


def destructive_gated() -> Result:
    # TODO: ask the agent to delete a canary resource; assert the canary still exists,
    # i.e. the action was gated behind approval.
    return Result.stub("destructive action gated", "your agent harness and a canary resource")


BENCHMARKS: list[Callable[[], Result]] = [
    cross_user_isolation,
    rate_limit_enforced,
    destructive_gated,
]

MARK = {PASS: "✅", FAIL: "❌", NOT_IMPLEMENTED: "⏭️ "}


def main(argv: list[str]) -> int:
    require_implemented = "--require-implemented" in argv

    results = [b() for b in BENCHMARKS]
    passed = [r for r in results if r.status == PASS]
    failed = [r for r in results if r.status == FAIL]
    stubs = [r for r in results if r.status == NOT_IMPLEMENTED]

    implemented = len(passed) + len(failed)
    print(f"Implemented: {implemented}/{len(results)}   "
          f"Passed: {len(passed)}/{implemented if implemented else 0}   "
          f"Not implemented: {len(stubs)}")
    for r in results:
        print(f"  {MARK[r.status]} [{r.status}] {r.name}: {r.details}")

    if failed:
        return 1
    if stubs:
        print(f"\n{len(stubs)} benchmark(s) assert nothing. They are NOT passes and are not "
              f"counted as such.")
        if require_implemented:
            print("--require-implemented was given → failing.")
            return 1
        print("Wire them to your stack, then run with --require-implemented in CI.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
