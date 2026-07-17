#!/bin/bash
# Verifies T-800 Agent installation after install-plugin.sh
# Канон: артефакты внутри PLUGIN_DEST, не в ~/.cursor/{agents,commands,rules,skills}
# Usage: bash scripts/verify-install.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN="$HOME/.cursor/plugins/local/t-800-agent"
AGENTS="$PLUGIN/agents"
RULES="$PLUGIN/rules"
CMDS="$PLUGIN/commands"
SKILLS="$PLUGIN/skills"
USER_RULES="$HOME/.cursor/rules"
USER_AGENTS="$HOME/.cursor/agents"
USER_SKILLS="$HOME/.cursor/skills"

failed=0
warned=0

check_exists() {
  local name="$1" path="$2" should="$3" marker="${4:-}"
  if [ "$should" = "true" ]; then
    if [ ! -f "$path" ]; then
      echo "FAIL $name: missing $path"
      failed=$((failed + 1))
      return
    fi
    if [ -n "$marker" ] && ! grep -qF "$marker" "$path" 2>/dev/null; then
      echo "FAIL $name: missing marker '$marker'"
      failed=$((failed + 1))
      return
    fi
    echo "OK   $name"
  else
    if [ -f "$path" ]; then
      echo "FAIL $name: should not exist $path"
      failed=$((failed + 1))
      return
    fi
    echo "OK   $name"
  fi
}

warn_if_missing() {
  local name="$1" path="$2" hint="$3"
  if [ ! -f "$path" ]; then
    echo "WARN $name: $hint"
    warned=$((warned + 1))
    return
  fi
  echo "OK   $name"
}

warn_if_present() {
  local name="$1" path="$2" hint="$3"
  if [ -e "$path" ]; then
    echo "WARN $name: $hint ($path)"
    warned=$((warned + 1))
    return
  fi
  echo "OK   $name"
}

check_exists "t-800-operator subagent" "$AGENTS/t-800-operator.md" true "name: t-800-operator"
check_exists "t-800-maintainer subagent" "$AGENTS/t-800-maintainer.md" true "name: t-800-maintainer"
check_exists "maintainer skill" "$SKILLS/t-800-knowledge-base/SKILL.md" true "disable-model-invocation: true"
check_exists "operator routing rule" "$RULES/t-800-operator-routing.mdc" true "Task(t-800-operator)"
check_exists "knowledge refresh rule" "$RULES/t-800-knowledge-refresh.mdc" true "sync-docs"
check_exists "t-800-operator command" "$CMDS/t-800-operator.md" true "Task(t-800-operator)"
check_exists "t-800-sync command" "$CMDS/t-800-sync.md" true "sync-docs"
check_exists "t-800-maintain command" "$CMDS/t-800-maintain.md" true "Task(t-800-maintainer)"
check_exists "t-800-health command" "$CMDS/t-800-health.md" true "health-check"
check_exists "t-800-factory lead" "$AGENTS/t-800-factory.md" true "name: t-800-factory"
check_exists "factory routing rule" "$RULES/t-800-factory-routing.mdc" true "Task(t-800-factory)"
check_exists "t800-bootstrap command" "$CMDS/t800-bootstrap.md" true "install-global-routing-rule"
check_exists "t-800-scout" "$AGENTS/t-800-scout.md" true "name: t-800-scout"
check_exists "t-800-brain-lead" "$AGENTS/t-800-brain-lead.md" true "name: t-800-brain-lead"
check_exists "t800-start command" "$CMDS/t800-start.md" true "Task(t-800-scout)"
check_exists "t800-onboard command" "$CMDS/t800-onboard.md" true "Task(t-800-onboard)"
check_exists "t800-audit command" "$CMDS/t800-audit.md" true "Task(t-800-system-auditor)"
check_exists "t800-plugin-audit command" "$CMDS/t800-plugin-audit.md" true "Task(t-800-plugin-auditor)"
check_exists "t800-fix command" "$CMDS/t800-fix.md" true "t800_run_gate.py"
check_exists "t800-doctor command" "$CMDS/t800-doctor.md" true "t800_doctor.py"
check_exists "t800-update command" "$CMDS/t800-update.md" true "t800-auto-version-check.sh"
check_exists "t800-loop command" "$CMDS/t800-loop.md" true "t-800-loop-conductor"
check_exists "t-800-system-auditor" "$AGENTS/t-800-system-auditor.md" true "name: t-800-system-auditor"
check_exists "t-800-plugin-auditor" "$AGENTS/t-800-plugin-auditor.md" true "name: t-800-plugin-auditor"
check_exists "t-800-loop-conductor" "$AGENTS/t-800-loop-conductor.md" true "name: t-800-loop-conductor"
if [ -f "$PLUGIN/scripts/t800_plugin_audit.py" ]; then
  echo "OK   t800_plugin_audit.py in plugin"
else
  echo "FAIL t800_plugin_audit.py missing in $PLUGIN/scripts/"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/plugin-audit-contract.md" ]; then
  echo "OK   plugin-audit-contract.md"
else
  echo "FAIL plugin-audit-contract.md missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/loop-engineering-contract.md" ]; then
  echo "OK   loop-engineering-contract.md"
else
  echo "FAIL loop-engineering-contract.md missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/lesson-schema-contract.md" ]; then
  echo "OK   lesson-schema-contract.md"
else
  echo "FAIL lesson-schema-contract.md missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/templates/STATE.md.template" ]; then
  echo "OK   STATE.md.template"
else
  echo "FAIL STATE.md.template missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/scripts/t800_loop_state.sh" ]; then
  echo "OK   t800_loop_state.sh"
else
  echo "FAIL t800_loop_state.sh missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/fix-pipeline-contract.md" ]; then
  echo "OK   fix-pipeline-contract.md"
else
  echo "FAIL fix-pipeline-contract.md missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/templates/fix-pack.md.template" ]; then
  echo "OK   fix-pack.md.template"
else
  echo "FAIL fix-pack.md.template missing"
  failed=$((failed + 1))
fi
for script in t800_run_gate.py t800_doctor.py t800_audit_to_fixpack.py \
  t800_run_report.py t800_lessons_export.py t800_telemetry.py t800_risk_classifier.py \
  t800_lessons_to_fixpack.py t800_golden_check.py t800-loop-dispatcher.sh t800_loop_queue_write.py; do
  if [ -f "$PLUGIN/scripts/$script" ]; then
    echo "OK   $script"
  else
    echo "FAIL $script missing in $PLUGIN/scripts/"
    failed=$((failed + 1))
  fi
done
if [ -f "$PLUGIN/scripts/t800-update-from-github.sh" ]; then
  echo "OK   t800-update-from-github.sh"
else
  echo "FAIL t800-update-from-github.sh missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/scripts/t800-auto-version-check.sh" ]; then
  echo "OK   t800-auto-version-check.sh"
else
  echo "FAIL t800-auto-version-check.sh missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/auto-update-contract.md" ]; then
  echo "OK   auto-update-contract.md"
else
  echo "FAIL auto-update-contract.md missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/shared/release-channel.json" ]; then
  echo "OK   release-channel.json"
else
  echo "FAIL release-channel.json missing"
  failed=$((failed + 1))
fi
if [ -f "$PLUGIN/hooks/t-800-session-bootstrap.sh" ]; then
  echo "OK   sessionStart hook script"
else
  echo "FAIL sessionStart hook script missing"
  failed=$((failed + 1))
fi
check_exists "t-800 legacy alias" "$CMDS/t-800.md" true "/t800-start"
check_exists "legacy forge command absent" "$CMDS/forge.md" false
check_exists "local plugin" "$PLUGIN/.cursor-plugin/plugin.json" true "t-800-agent"

ACTUAL_VER=$(python3 -c "import json; print(json.load(open('$PLUGIN/.cursor-plugin/plugin.json'))['version'])" 2>/dev/null || echo "")
if [ -z "$ACTUAL_VER" ]; then
  echo "FAIL plugin.json version unreadable"
  failed=$((failed + 1))
else
  echo "OK   plugin.json version $ACTUAL_VER"
fi

if ! grep -q "readonly: true" "$AGENTS/t-800-operator.md" 2>/dev/null; then
  echo "FAIL t-800-operator must stay readonly"
  failed=$((failed + 1))
else
  echo "OK   t-800-operator readonly"
fi
if ! grep -q "readonly: false" "$AGENTS/t-800-maintainer.md" 2>/dev/null; then
  echo "FAIL t-800-maintainer must be writable"
  failed=$((failed + 1))
else
  echo "OK   t-800-maintainer writable"
fi

warn_if_missing "global mandatory-routing rule" \
  "$USER_RULES/t-800-mandatory-routing.mdc" \
  "отсутствует — установите через /t800-bootstrap"

# Stale user-home mirrors = WARN (install должен был почистить)
stale=0
if compgen -G "$USER_AGENTS/t-800-*.md" >/dev/null 2>&1; then
  echo "WARN stale user-home agents: перезапустите install-plugin.sh"
  warned=$((warned + 1))
  stale=1
fi
if [ -d "$USER_SKILLS/t-800-knowledge-base" ]; then
  echo "WARN stale user-home skill t-800-knowledge-base: перезапустите install-plugin.sh"
  warned=$((warned + 1))
  stale=1
fi
if [ "$stale" -eq 0 ]; then
  echo "OK   no stale user-home t-800 mirrors"
fi

if [ "$failed" -gt 0 ]; then
  echo "T-800 Agent verification failed: $failed problem(s). Run bash scripts/install-plugin.sh"
  exit 1
fi

echo "T-800 Agent verification passed (warnings: $warned). Restart Cursor if you just installed."
