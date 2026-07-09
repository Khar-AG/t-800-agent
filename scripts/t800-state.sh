#!/usr/bin/env bash
# t800-state.sh — чтение/запись ~/.t800/state.json
set -euo pipefail

STATE_DIR="${HOME}/.t800"
STATE_FILE="${STATE_DIR}/state.json"

ensure_state() {
  mkdir -p "$STATE_DIR"
  if [[ ! -f "$STATE_FILE" ]]; then
    cat > "$STATE_FILE" <<'EOF'
{
  "schema_version": 1,
  "first_run_completed": false,
  "global_rule_installed": false,
  "onboard_completed_at": null,
  "plugin_version_at_setup": null
}
EOF
  fi
}

cmd_get() {
  local key="$1"
  ensure_state
  python3 -c "
import json
from pathlib import Path
d = json.loads(Path('$STATE_FILE').read_text(encoding='utf-8'))
v = d.get('$key')
if isinstance(v, bool):
    print('true' if v else 'false')
elif v is None:
    print('')
else:
    print(v)
"
}

cmd_set() {
  local key="$1" val="$2"
  ensure_state
  python3 -c "
import json
from pathlib import Path
p = Path('$STATE_FILE')
d = json.loads(p.read_text(encoding='utf-8'))
raw = '$val'
if raw in ('true', 'false'):
    d['$key'] = raw == 'true'
elif raw.startswith('\"') and raw.endswith('\"'):
    d['$key'] = json.loads(raw)
elif raw == 'null':
    d['$key'] = None
else:
    d['$key'] = raw
p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
"
}

ensure_state
case "${1:-}" in
  get) cmd_get "${2:?key}" ;;
  set) cmd_set "${2:?key}" "${3:?value}" ;;
  path) echo "$STATE_FILE" ;;
  *) echo "Usage: t800-state.sh get|set <key> [value]|path" >&2; exit 1 ;;
esac
