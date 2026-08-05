#!/usr/bin/env bash
# Load gitignored .env then run terraform in terraform/.
# Usage: bash scripts/tf-with-env.sh plan|apply|init|…  [extra terraform args]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="${ROOT}/.env"
TF_DIR="${ROOT}/terraform"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "MISSING: ${ENV_FILE}" >&2
  echo "Copy .env.example → .env and set LAB_ALERT_EMAIL, OWL_TOKEN (or TRUEWATCH_ACCESS_TOKEN)." >&2
  exit 1
fi

# shellcheck disable=SC1090
set -a && source "${ENV_FILE}" && set +a

if [[ -z "${LAB_ALERT_EMAIL:-}" ]]; then
  echo "MISSING: LAB_ALERT_EMAIL in .env (needed as TF_VAR_lab_alert_email)." >&2
  exit 1
fi

export TF_VAR_lab_alert_email="${LAB_ALERT_EMAIL}"
export TRUEWATCH_ACCESS_TOKEN="${TRUEWATCH_ACCESS_TOKEN:-${OWL_TOKEN:-${OWL_API_KEY:-}}}"
if [[ -z "${TRUEWATCH_ACCESS_TOKEN}" ]]; then
  echo "MISSING: TRUEWATCH_ACCESS_TOKEN or OWL_TOKEN / OWL_API_KEY in .env." >&2
  exit 1
fi

if [[ -n "${TRUEWATCH_END_POINT:-}" ]]; then
  export TF_VAR_truewatch_end_point="${TRUEWATCH_END_POINT}"
fi

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <terraform-subcommand> [args…]" >&2
  echo "Example: $0 plan" >&2
  echo "Example: $0 apply" >&2
  exit 1
fi

cd "${TF_DIR}"
echo "env: LAB_ALERT_EMAIL=set TRUEWATCH_ACCESS_TOKEN=set (values not printed)"
exec terraform "$@"
