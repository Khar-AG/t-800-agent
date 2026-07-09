#!/bin/bash
# Установка T-800 Agent в Cursor Desktop (macOS / Linux)
# Канон: только ~/.cursor/plugins/local/t-800-agent (без зеркал в user-home)
# Запуск: bash scripts/install-plugin.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
PLUGIN_DEST="$HOME/.cursor/plugins/local/t-800-agent"
LEGACY_DEST="$HOME/.cursor/plugins/local/cursor-forge"

echo "T-800 Agent: установка..."
echo "  из:  $ROOT"
echo "  в:   $PLUGIN_DEST"

for legacy in "$LEGACY_DEST" "$HOME/.cursor/plugins/local/cursor-jr" "$HOME/.cursor/plugins/local/t-800-operator"; do
  if [ -d "$legacy" ]; then
    rm -rf "$legacy"
    echo "Удалён legacy: $legacy"
  fi
done

rm -rf "$PLUGIN_DEST"
mkdir -p "$PLUGIN_DEST"
rsync -a "$ROOT/" "$PLUGIN_DEST/" \
  --exclude '.git' \
  --exclude '.DS_Store' \
  --exclude 't-800-memory'

VER=$(python3 -c "import json; print(json.load(open('$PLUGIN_DEST/.cursor-plugin/plugin.json'))['version'])" 2>/dev/null || echo "?")

# Опциональная очистка устаревших зеркал в user-home (allowlist, не rm -rf каталогов)
cleanup_stale_user_home_mirrors() {
  local agents_dir="$HOME/.cursor/agents"
  local rules_dir="$HOME/.cursor/rules"
  local cmds_dir="$HOME/.cursor/commands"
  local skills_dir="$HOME/.cursor/skills"
  local f base

  if [ -d "$agents_dir" ]; then
    for f in "$agents_dir"/t-800-*.md; do
      [ -f "$f" ] || continue
      rm -f "$f"
      echo "  cleanup: removed $f"
    done
    for old in forge-scout forge-brain-lead forge-brain-admin forge-brain-agents forge-brain-cloud \
      forge-brain-context forge-brain-dev forge-brain-security forge-brain-tools \
      forge-factory forge-factory-architect forge-factory-auditor forge-factory-builder forge-factory-integrator \
      cursor-jr cursor-jr-maintainer; do
      if [ -f "$agents_dir/${old}.md" ]; then
        rm -f "$agents_dir/${old}.md"
        echo "  cleanup: removed $agents_dir/${old}.md"
      fi
    done
  fi

  if [ -d "$rules_dir" ]; then
    for f in "$rules_dir"/t-800-*.mdc; do
      [ -f "$f" ] || continue
      base="$(basename "$f")"
      if [ "$base" = "t-800-mandatory-routing.mdc" ]; then
        continue
      fi
      rm -f "$f"
      echo "  cleanup: removed $f"
    done
    for old in forge-mandatory-routing forge-factory-routing cursor-jr-routing cursor-jr-knowledge-refresh; do
      if [ -f "$rules_dir/${old}.mdc" ]; then
        rm -f "$rules_dir/${old}.mdc"
        echo "  cleanup: removed $rules_dir/${old}.mdc"
      fi
    done
  fi

  if [ -d "$cmds_dir" ]; then
    if [ -d "$ROOT/commands" ]; then
      for f in "$ROOT/commands"/*.md; do
        [ -f "$f" ] || continue
        base="$(basename "$f")"
        if [ -f "$cmds_dir/$base" ]; then
          rm -f "$cmds_dir/$base"
          echo "  cleanup: removed $cmds_dir/$base"
        fi
      done
    fi
    for old in forge forge-factory forge-factory-validate cursor-jr cursor-jr-health cursor-jr-maintain cursor-jr-sync t800-teya; do
      if [ -f "$cmds_dir/${old}.md" ]; then
        rm -f "$cmds_dir/${old}.md"
        echo "  cleanup: removed $cmds_dir/${old}.md"
      fi
    done
  fi

  for skill in t-800-knowledge-base cursor-jr-knowledge-base t-800-operator; do
    if [ -d "$skills_dir/$skill" ]; then
      rm -rf "$skills_dir/$skill"
      echo "  cleanup: removed $skills_dir/$skill"
    fi
  done
}

cleanup_stale_user_home_mirrors

# DEFER: project mirror ROOT/.cursor/agents — не блокер 1.12.1; оставляем для совместимости
PROJ_AGENTS="$ROOT/.cursor/agents"
AGENT_SRC="$ROOT/agents"
if [ -d "$AGENT_SRC" ]; then
  mkdir -p "$PROJ_AGENTS"
  for f in "$AGENT_SRC"/t-800-*.md; do
    [ -f "$f" ] || continue
    cp -f "$f" "$PROJ_AGENTS/"
  done
fi

echo ""
echo "Готово. T-800 Agent v$VER установлен."
echo "Артефакты только в: $PLUGIN_DEST"
echo "Первый запуск: /t800-bootstrap (аудит + глобальное правило по согласию)"
echo "Далее: /t800-start для создания subagents/skills/commands/rules"
echo "Перезапустите Cursor (Reload Window)."
