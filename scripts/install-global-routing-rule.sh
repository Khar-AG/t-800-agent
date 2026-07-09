#!/usr/bin/env bash
# install-global-routing-rule.sh — глобальное правило T-800 (после согласия пользователя)
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
RULE_SRC="$ROOT/rules/t-800-mandatory-routing.mdc"
RULE_DEST="${HOME}/.cursor/rules/t-800-mandatory-routing.mdc"
YES=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) YES=true; shift ;;
    *) shift ;;
  esac
done

if [[ "$YES" != true ]]; then
  echo "Требуется подтверждение: install-global-routing-rule.sh --yes" >&2
  exit 2
fi

if [[ ! -f "$RULE_SRC" ]]; then
  echo "Не найден шаблон: $RULE_SRC" >&2
  exit 1
fi

mkdir -p "${HOME}/.cursor/rules"
cp -f "$RULE_SRC" "$RULE_DEST"
bash "$HERE/t800-state.sh" set global_rule_installed true
bash "$HERE/t800-state.sh" set first_run_completed true
VER=$(python3 -c "import json; print(json.load(open('$ROOT/.cursor-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")
bash "$HERE/t800-state.sh" set plugin_version_at_setup "\"$VER\""

echo "OK global rule: $RULE_DEST"
echo "Reload Window в Cursor для применения правила."
