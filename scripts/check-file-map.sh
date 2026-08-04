#!/usr/bin/env bash
# check-file-map.sh — PostToolUse(Write) hook: remind whoever just created a file to
# record it in docs/FILE-MAP.md, the exhaustive per-file index.
#
# Why this exists: an agent with no chat history re-creates a file that already exists
# under a name it would not have guessed. The index is the cheap defence, and an index
# nobody updates is worse than none — so the reminder is automated.
#
# Contract with docs/FILE-MAP.md: a file counts as recorded if its repo-relative path
# appears anywhere in that document. The index uses a `| path | purpose | reader |`
# table, but this check only needs the path to be present.
#
# This hook NEVER blocks a write and ALWAYS exits 0. It only injects context. It cannot
# write the row for you — see AGENTS.md, "Before you create any file".
#
# Reads the Claude Code hook JSON payload on stdin.
# Wire-up lives in .claude/settings.json under hooks.PostToolUse.

set -u

# $CLAUDE_PROJECT_DIR is set by Claude Code. Fall back to this script's parent so the
# hook is testable by hand from any working directory.
REPO_ROOT="${CLAUDE_PROJECT_DIR:-}"
if [ -z "$REPO_ROOT" ]; then
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)" || exit 0
fi
MAP="$REPO_ROOT/docs/FILE-MAP.md"

# Every early exit below is a deliberate silent pass: a nag hook that errors, blocks, or
# fires on files nobody indexes gets switched off by the first annoyed user.
[ -f "$MAP" ] || exit 0
command -v python3 >/dev/null 2>&1 || exit 0

RAW="$(cat)" || exit 0

FILE="$(printf '%s' "$RAW" | python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if not isinstance(d, dict):
    sys.exit(0)
ti = d.get("tool_input") if isinstance(d.get("tool_input"), dict) else {}
tr = d.get("tool_response") if isinstance(d.get("tool_response"), dict) else {}
print(ti.get("file_path") or tr.get("filePath") or "")
' 2>/dev/null)" || exit 0

[ -n "$FILE" ] || exit 0

# Only care about files inside this repo.
case "$FILE" in
  "$REPO_ROOT"/*) REL="${FILE#"$REPO_ROOT"/}" ;;
  /*)             exit 0 ;;   # absolute path outside the repo
  *)              REL="$FILE" ;;
esac

# Never worth indexing.
case "$REL" in
  .git/*|docs/FILE-MAP.md) exit 0 ;;
esac

# Anything git ignores is not part of the tracked manifest.
if git -C "$REPO_ROOT" check-ignore -q -- "$REL" 2>/dev/null; then
  exit 0
fi

# Already recorded? Plain substring match on the path.
if grep -qF -- "$REL" "$MAP" 2>/dev/null; then
  exit 0
fi

MSG="docs/FILE-MAP.md does not list \`$REL\`. That index is what stops the next worker — who has no chat history — from re-creating a file that already exists. Add a row for it now: the path, one line on what it is for, and who reads it. If the file is temporary or does not belong in the index, say so explicitly rather than skipping silently."

MSG="$MSG" python3 -c '
import json, os
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PostToolUse",
    "additionalContext": os.environ["MSG"],
}}))
' 2>/dev/null

exit 0
