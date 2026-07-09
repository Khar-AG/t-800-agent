#!/bin/bash
# T-800 Agent — session bootstrap hook
# Подсказка первого запуска в лог (расширяемо под manifest)

set -euo pipefail

PLUGIN="${HOME}/.cursor/plugins/local/t-800-agent"
LOG_DIR="${PLUGIN}/.t-800-logs"
mkdir -p "$LOG_DIR"

STATUS_SCRIPT="${PLUGIN}/scripts/first-run-status.sh"
if [[ -x "$STATUS_SCRIPT" ]]; then
  NEEDS=$(bash "$STATUS_SCRIPT" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('needs_bootstrap', False))" 2>/dev/null || echo False)
  if [[ "$NEEDS" == "True" ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart needs_bootstrap=true hint=/t800-bootstrap" >> "$LOG_DIR/session.log"
    exit 0
  fi
fi

echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart" >> "$LOG_DIR/session.log"
