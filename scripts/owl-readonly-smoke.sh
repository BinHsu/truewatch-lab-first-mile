#!/usr/bin/env bash
# Read-only OWL CLI smoke — machine-replayable twin of MCP "intent" checks.
#
# Proves the same owl.* surfaces an IDE would call via MCP (query + monitor list).
# Does not configure MCP; see docs/runbooks/owl-mcp-cursor.md for Cursor wiring.
#
# Usage (repo root):
#   set -a && source .env && set +a
#   bash scripts/owl-readonly-smoke.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:/usr/bin:/bin:/opt/homebrew/bin:${PATH}"

if [[ ! -f .env ]]; then
  echo "MISSING: .env" >&2
  exit 1
fi
set -a && source .env && set +a

if [[ -z "${OWL_TOKEN:-${OWL_API_KEY:-${TRUEWATCH_ACCESS_TOKEN:-}}}" ]]; then
  echo "MISSING: OWL_TOKEN (or OWL_API_KEY / TRUEWATCH_ACCESS_TOKEN)" >&2
  exit 1
fi

if ! command -v owl >/dev/null 2>&1; then
  echo "MISSING: owl on PATH (docs/runbooks/owl-cli-credentials.md)" >&2
  exit 1
fi

NOW_MS="$(python3 -c 'import time; print(int(time.time() * 1000))')"
START_MS="$((NOW_MS - 2 * 3600 * 1000))"
echo "owl_readonly_smoke=1"
echo "window_start_ms=${START_MS}"
echo "window_end_ms=${NOW_MS}"
python3 -c "import datetime as d; s=${START_MS}/1000; e=${NOW_MS}/1000; print('window_utc', d.datetime.utcfromtimestamp(s).isoformat()+'Z', '->', d.datetime.utcfromtimestamp(e).isoformat()+'Z')"

query() {
  local name="$1"
  local qtext="$2"
  echo "=== ${name} ==="
  local out ap
  out="$(owl exec owl.data.query -f json -p "$(python3 -c 'import json,sys; print(json.dumps({"dql_namespace":"M","start_time":int(sys.argv[1]),"end_time":int(sys.argv[2]),"query_text":sys.argv[3]}))' "$START_MS" "$NOW_MS" "$qtext")")"
  ap="$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["file"]["absolutePath"])' "$out")"
  python3 -c 'import json,pathlib,sys; print(json.dumps(json.loads(pathlib.Path(sys.argv[1]).read_text()).get("data"), ensure_ascii=False)[:800])' "$ap"
}

query dataway "M::\`truewatch_lab_first_mile\`:(last(\`ping\`), count(\`ping\`)) { path = 'dataway' }"
query datakit "M::\`truewatch_lab_first_mile\`:(last(\`ping\`), count(\`ping\`)) { path = 'datakit' }"
query ddtrace "M::\`truewatch\`:(last(\`lab_first_mile_ping\`), count(\`lab_first_mile_ping\`)) { path = 'ddtrace' }"
query otel "M::\`otel_service\`:(last(\`truewatch_lab_first_mile.ping\`), count(\`truewatch_lab_first_mile.ping\`)) { path = 'otel' }"

echo "=== monitors lab-first-mile ==="
owl exec owl.monitor.list -f json search="lab-first-mile" | python3 -c '
import json,sys
raw=sys.stdin.read()
d=json.loads(raw)
inner=json.loads(d["output"]) if isinstance(d.get("output"),str) and d["output"].strip().startswith("{") else d
items=((inner.get("data") or {}).get("items")) or []
print("monitor_count", len(items))
for it in items[:8]:
  print({"name": it.get("name"), "rule_uuid": it.get("rule_uuid"), "status": it.get("status")})
'

echo "owl_readonly_smoke=OK"
date -u +'finished_utc=%Y-%m-%dT%H:%M:%SZ'
