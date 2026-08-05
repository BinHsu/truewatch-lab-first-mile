#!/usr/bin/env bash
# Run emit payload contracts inside the emitter image (ADR-0002: do not pip-install
# pins on the lab host). Needs Docker only.
#
# Usage (from repo root):
#   bash scripts/run-emit-payload-tests.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
IMAGE="${EMIT_TEST_IMAGE:-truewatch-lab-first-mile-emit:payload-test}"

docker build -f "$ROOT/docker/Dockerfile.emitter" -t "$IMAGE" "$ROOT"
docker run --rm --entrypoint python3 "$IMAGE" tests/test_emit_payloads.py -v
