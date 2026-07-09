#!/usr/bin/env bash
# first-run-status.sh — статус первого запуска и глобального routing rule
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
RULE_GLOBAL="${HOME}/.cursor/rules/t-800-mandatory-routing.mdc"
STATE_SCRIPT="$HERE/t800-state.sh"

FR="$(bash "$STATE_SCRIPT" get first_run_completed 2>/dev/null || echo false)"
GR="$(bash "$STATE_SCRIPT" get global_rule_installed 2>/dev/null || echo false)"
[[ -f "$RULE_GLOBAL" ]] && RULE_PRESENT=true || RULE_PRESENT=false

NEEDS_BOOTSTRAP=true
if [[ "$FR" == "true" && "$RULE_PRESENT" == true ]]; then
  NEEDS_BOOTSTRAP=false
fi

python3 - <<PY
import json
fr = "$FR" == "true"
gr = "$GR" == "true"
rule_present = "$RULE_PRESENT" == "true"
needs = "$NEEDS_BOOTSTRAP" == "true"
print(json.dumps({
  "first_run_completed": fr,
  "global_rule_installed_flag": gr,
  "global_rule_file_present": rule_present,
  "global_rule_path": "$RULE_GLOBAL",
  "needs_bootstrap": needs,
  "recommended_command": "/t800-bootstrap" if needs else "/t800-onboard"
}, ensure_ascii=False, indent=2))
PY
