#!/usr/bin/env bash
# Emit all four paths with stagger for dashboard readability.
#
# Default metric values are lab contract (scripts/lab_path_values.py):
#   dataway=1, datakit=2, ddtrace=3, otel=4  (≪ monitor threshold 900)
# Tag path=… remains identity. Override with --value on a single-path emit.
#
# Usage (repo root):
#   set -a && source .env && set +a
#   bash scripts/emit-dashboard-demo.sh
#   bash scripts/emit-dashboard-demo.sh --interval 8
#   bash scripts/emit-dashboard-demo.sh --dry-run
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

INTERVAL_SEC=8
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --interval)
      INTERVAL_SEC="${2:?}"
      shift 2
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      sed -n '2,14p' "$0"
      exit 0
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -f .env ]]; then
  echo "missing .env — copy from .env.example and fill credentials" >&2
  exit 1
fi
set -a && source .env && set +a

# Order matches lab_path_values.DEFAULT_VALUE_BY_PATH (defaults applied by emit_*.py).
PATHS=(dataway datakit ddtrace otel)
N=${#PATHS[@]}

echo "emit_dashboard_demo=1"
echo "stagger_sec=${INTERVAL_SEC}"
echo "defaults=lab_path_values.py (dataway=1,datakit=2,ddtrace=3,otel=4)"

i=0
for mode in "${PATHS[@]}"; do
  i=$((i + 1))
  echo "=== ${i}/${N} mode=${mode} (path default value) ==="

  case "$mode" in
    dataway|datakit)
      if [[ "$DRY_RUN" -eq 1 ]]; then
        python3 scripts/emit.py --mode "$mode" --dry-run
      else
        python3 scripts/emit.py --mode "$mode"
      fi
      ;;
    ddtrace|otel)
      if [[ "$DRY_RUN" -eq 1 ]]; then
        docker compose --env-file .env run --rm -e "EMIT_MODE=${mode}" emit --dry-run
      else
        docker compose --env-file .env run --rm -e "EMIT_MODE=${mode}" emit
      fi
      ;;
  esac

  if [[ "$i" -lt "$N" && "$DRY_RUN" -eq 0 && "$INTERVAL_SEC" != "0" ]]; then
    echo "emit_sleep_sec=${INTERVAL_SEC}"
    sleep "$INTERVAL_SEC"
  fi
done

echo "done — Metric Analysis / dashboard: Past 15m; series at y≈1,2,3,4 by path"
date -u +'finished_utc=%Y-%m-%dT%H:%M:%SZ'
