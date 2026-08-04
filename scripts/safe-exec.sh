#!/usr/bin/env bash
# safe-exec.sh — wrap destructive commands: preview → confirm → log → execute.
# Practice 6 (hidden destructive actions). Alias dangerous commands through this:
#   alias rm='scripts/safe-exec.sh rm'
#   alias kubectl='scripts/safe-exec.sh kubectl'
#   alias terraform='scripts/safe-exec.sh terraform'
set -euo pipefail

CMD="$*"
LOG_DIR=".agent-context"
LOG_FILE="${LOG_DIR}/destructive-log.jsonl"

DESTRUCTIVE_PATTERNS=(
  "rm -rf" "rm -f" "git push --force" "git push -f" "git reset --hard"
  "drop database" "drop table" "truncate" "delete from"
  "kubectl delete" "terraform destroy" "terraform apply"
)

is_destructive=false
for p in "${DESTRUCTIVE_PATTERNS[@]}"; do
  case "$CMD" in *"$p"*) is_destructive=true; break;; esac
done

if [ "$is_destructive" = true ]; then
  echo "⚠️  DESTRUCTIVE ACTION DETECTED"
  echo "Command: $CMD"
  echo
  echo "Preview (dry-run if available):"
  case "$CMD" in
    *"terraform apply"*|*"terraform destroy"*) terraform plan || true ;;
    *"rm -rf"*|*"rm -f"*) echo "Would remove:"; eval "${CMD/rm -rf/ls -la}" 2>/dev/null || eval "${CMD/rm -f/ls -la}" 2>/dev/null || true ;;
    *) echo "(no automatic preview for this command; review manually)" ;;
  esac
  echo
  read -r -p "Type 'confirm' to proceed: " answer
  if [ "$answer" != "confirm" ]; then
    echo "Aborted."
    exit 1
  fi
  mkdir -p "$LOG_DIR"
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '{"ts":"%s","cmd":"%s","user":"%s","cwd":"%s"}\n' "$ts" "$CMD" "${USER:-unknown}" "$PWD" >> "$LOG_FILE"
fi

eval "$CMD"
