#!/usr/bin/env bash
# audit-tool-registry.sh — Practice 7: verify the tool layer has no holes.
#
# Three sections. Each either reports findings, reports clean, or reports SKIPPED with
# the reason it could not be evaluated. Any finding exits 1 — a check that prints ❌ and
# returns 0 is a check that cannot fail (AGENTS.md section 12).
#
# Requires: yq (https://github.com/mikefarah/yq).
# Run: bash scripts/audit-tool-registry.sh
#      SCAN_DIR=app bash scripts/audit-tool-registry.sh    # where your code lives
set -uo pipefail

REG="${REG:-tools/registry.yaml}"
SCAN_DIR="${SCAN_DIR:-src}"

[ -f "$REG" ] || { echo "❌ registry not found: $REG"; exit 1; }
command -v yq >/dev/null 2>&1 || { echo "❌ yq not on PATH — install it or skip this check deliberately"; exit 1; }

findings=0
skipped=0

echo "=== Tools called in code but NOT declared in the registry ==="
if [ ! -d "$SCAN_DIR" ]; then
  # Silence here would mean "clean", and this section would then be clean forever in any
  # repo that keeps its code somewhere else. Say what did not run instead.
  echo "  ⏭️  SKIPPED: no '$SCAN_DIR/' directory. Set SCAN_DIR to where your code lives."
  skipped=$((skipped + 1))
else
  # Adjust the grep to your runner's call shape, e.g. runTool("name") / call_tool('name').
  ACTUAL=$(grep -rEoh "(runTool|call_tool)\(['\"][a-z_]+['\"]" "$SCAN_DIR" 2>/dev/null \
            | sed -E "s/.*['\"]([a-z_]+)['\"].*/\1/" | sort -u)
  if [ -z "$ACTUAL" ]; then
    echo "  ⏭️  SKIPPED: no tool calls matched in '$SCAN_DIR/'. Adjust the call-shape grep."
    skipped=$((skipped + 1))
  else
    DECLARED=$(yq '.tools[].name' "$REG" | sort -u)
    UNDECLARED=$(comm -23 <(printf '%s\n' "$ACTUAL") <(printf '%s\n' "$DECLARED"))
    if [ -n "$UNDECLARED" ]; then
      printf '  ❌ called but undeclared: %s\n' $UNDECLARED
      findings=$((findings + 1))
    else
      echo "  ✅ clean"
    fi
  fi
fi

echo "=== Declared tools missing a timeout ==="
NO_TIMEOUT=$(yq '.tools[] | select(.timeout_ms == null) | .name' "$REG" | grep -v '^null$' || true)
if [ -n "$NO_TIMEOUT" ]; then
  printf '  ❌ no timeout: %s\n' $NO_TIMEOUT
  findings=$((findings + 1))
else
  echo "  ✅ clean"
fi

echo "=== Destructive tools missing an approval gate ==="
NO_GATE=$(yq '.tools[] | select(.type == "destructive" and .requires_approval != true and (.requires_approval_if == null)) | .name' "$REG" | grep -v '^null$' || true)
if [ -n "$NO_GATE" ]; then
  printf '  ❌ destructive without approval: %s\n' $NO_GATE
  findings=$((findings + 1))
else
  echo "  ✅ clean"
fi

echo "=== Audit complete: $findings finding(s), $skipped section(s) skipped ==="
[ "$findings" -eq 0 ] || exit 1
exit 0
