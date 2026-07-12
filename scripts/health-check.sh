#!/bin/bash
# Runs T-800 health checks and writes knowledge-base/HEALTH-REPORT.md
# Канон: маркеры внутри ROOT (plugin tree), не user-home mirrors
# Usage: bash scripts/health-check.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
KB="$ROOT/knowledge-base"
REPORT="$KB/HEALTH-REPORT.md"
MANIFEST="$KB/manifest.json"
PLUGIN_DEST="$HOME/.cursor/plugins/local/t-800-agent"
failed=0
warned=0

checks=()

# Пути в отчёте — без абсолютных путей машины (плагин общий).
display_path() {
  local p="$1"
  case "$p" in
    "$ROOT"/*) printf '%s' "${p#"$ROOT"/}" ;;
    "$HOME"/*) printf '~/%s' "${p#"$HOME"/}" ;;
    *) printf '%s' "$p" ;;
  esac
}

sanitize_details() {
  local d="$1"
  d="${d//"$ROOT/"/}"
  d="${d//"$HOME/"/"~/"}"
  printf '%s' "$d"
}

add_check() {
  local details
  details="$(sanitize_details "$3")"
  checks+=("$1|$2|$details")
  if [ "$2" = "FAIL" ]; then failed=$((failed + 1)); fi
  if [ "$2" = "WARN" ]; then warned=$((warned + 1)); fi
}

test_marker() {
  local name="$1" path="$2" marker="$3" should="${4:-true}"
  if [ "$should" = "true" ]; then
    if [ ! -f "$path" ]; then
      add_check "$name" "FAIL" "Missing: $(display_path "$path")"
      return
    fi
    if [ -n "$marker" ] && ! grep -qF "$marker" "$path" 2>/dev/null; then
      add_check "$name" "FAIL" "Missing marker: $marker"
      return
    fi
    add_check "$name" "OK" "$(display_path "$path")"
  else
    if [ -f "$path" ]; then
      add_check "$name" "FAIL" "Must be absent: $(display_path "$path")"
      return
    fi
    add_check "$name" "OK" "absent"
  fi
}

test_marker "t-800-operator subagent" "$ROOT/agents/t-800-operator.md" "readonly: true"
test_marker "t-800-maintainer subagent" "$ROOT/agents/t-800-maintainer.md" "readonly: false"
test_marker "maintainer skill disabled" "$ROOT/skills/t-800-knowledge-base/SKILL.md" "disable-model-invocation: true"
test_marker "health command installed" "$ROOT/commands/t-800-health.md" "health-check"

if [ -f "$HOME/.cursor/rules/t-800-mandatory-routing.mdc" ]; then
  add_check "global mandatory-routing" "OK" "$(display_path "$HOME/.cursor/rules/t-800-mandatory-routing.mdc")"
else
  add_check "global mandatory-routing" "WARN" "отсутствует — /t800-bootstrap"
fi

if [ -d "$PLUGIN_DEST/agents" ]; then
  add_check "plugin dest agents" "OK" "$(display_path "$PLUGIN_DEST/agents")"
else
  add_check "plugin dest agents" "WARN" "нет $(display_path "$PLUGIN_DEST") — запустите install-plugin.sh"
fi

if compgen -G "$HOME/.cursor/agents/t-800-*.md" >/dev/null 2>&1; then
  add_check "stale user-home agents" "WARN" "устаревшее зеркало — перезапустите install"
elif [ -d "$HOME/.cursor/skills/t-800-knowledge-base" ]; then
  add_check "stale user-home skill" "WARN" "устаревшее зеркало — перезапустите install"
else
  add_check "no stale user-home mirrors" "OK" "clean"
fi

if [ -f "$MANIFEST" ]; then
  age=$(python3 -c "
import json
from datetime import datetime
from pathlib import Path
m = json.loads(Path('$MANIFEST').read_text(encoding='utf-8-sig'))
dates = [v.get('last_synced') for v in m.get('pages',{}).values() if v.get('last_synced')]
if not dates:
    print('WARN|No page sync dates')
else:
    latest = max(datetime.strptime(d, '%Y-%m-%d') for d in dates)
    days = (datetime.now() - latest).days
    if days <= 30:
        print(f'OK|Latest sync: {latest.date()} ({days} days)')
    else:
        print(f'WARN|Latest sync: {latest.date()} ({days} days)')
" 2>/dev/null || echo "FAIL|manifest parse error")
  IFS='|' read -r st det <<< "$age"
  add_check "manifest freshness" "$st" "$det"
else
  add_check "manifest freshness" "FAIL" "Missing manifest.json"
fi

if bash "$HERE/validate-agents.sh" >/dev/null 2>&1; then
  add_check "validate-agents" "OK" "passed"
else
  add_check "validate-agents" "FAIL" "see validate-agents.sh"
fi

if bash "$HERE/audit-agent-graph.sh" >/dev/null 2>&1; then
  add_check "audit-agent-graph" "OK" "passed"
else
  add_check "audit-agent-graph" "FAIL" "see audit-agent-graph.sh"
fi

if bash "$HERE/audit-coverage.sh" >/dev/null 2>&1; then
  add_check "coverage audit" "OK" "Missing=0"
else
  cov_missing=$(python3 -c "
import json,re
from pathlib import Path
kb=Path('$KB'); m=json.loads((kb/'manifest.json').read_text(encoding='utf-8-sig'))
sm={}
for c in kb.rglob('*.md'):
    if 'raw' in c.parts: continue
    for line in c.read_text(encoding='utf-8-sig',errors='ignore').splitlines():
        if line.startswith('source:'): sm.setdefault(line.split(':',1)[1].strip(),1)
print(sum(1 for u in m['pages'] if u not in sm))
" 2>/dev/null || echo "?")
  add_check "coverage audit" "WARN" "missing URLs: $cov_missing"
fi

status="OK"
[ "$failed" -gt 0 ] && status="FAIL"
[ "$failed" -eq 0 ] && [ "$warned" -gt 0 ] && status="WARN"

{
  echo "# HEALTH-REPORT"
  echo ""
  echo "**Generated:** $(date '+%Y-%m-%d %H:%M')"
  echo "**Status:** $status"
  echo "**Failed:** $failed"
  echo "**Warnings:** $warned"
  echo ""
  echo "| Status | Check | Details |"
  echo "|--------|-------|---------|"
  for c in "${checks[@]}"; do
    IFS='|' read -r n s d <<< "$c"
    echo "| $s | $n | $d |"
  done
  echo ""
  echo "## Next step"
  echo ""
  echo 'If status is FAIL, run: bash scripts/install-plugin.sh && bash scripts/verify-install.sh'
} > "$REPORT"

for c in "${checks[@]}"; do
  IFS='|' read -r n s d <<< "$c"
  echo "$s $n: $d"
done
echo "Health report: $(display_path "$REPORT")"

[ "$failed" -gt 0 ] && exit 2
exit 0
