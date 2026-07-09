#!/usr/bin/env bash
# init-project-memory.sh — scaffold памяти для нового плагина
set -euo pipefail

WORKSPACE="."
SLUG=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --slug) SLUG="$2"; shift 2 ;;
    *) echo "Неизвестный аргумент: $1" >&2; exit 1 ;;
  esac
done

WORKSPACE="$(cd "$WORKSPACE" && pwd)"

if [[ -z "$SLUG" ]]; then
  if [[ -f "$WORKSPACE/.cursor-plugin/plugin.json" ]]; then
    SLUG="$(python3 -c "import json; print(json.load(open('$WORKSPACE/.cursor-plugin/plugin.json')).get('name','plugin'))")"
  else
    echo "Укажите --slug" >&2
    exit 1
  fi
fi

MEMORY_DIR="${SLUG}-memory"
MEM="$WORKSPACE/$MEMORY_DIR"
mkdir -p "$MEM/factory-briefs" "$MEM/fragments" "$MEM/audits"

# STATE.md from template (loop engineering)
PLUGIN_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
bash "$PLUGIN_ROOT/scripts/t800_loop_state.sh" init --memory-path "$MEM"

if [[ ! -f "$MEM/run-manifest.json" ]]; then
  cat > "$MEM/run-manifest.json" <<EOF
{
  "schema_version": 1,
  "project": "$SLUG",
  "status": "active",
  "started_at": "$(date +%Y-%m-%d)",
  "steps": []
}
EOF
fi

if [[ ! -f "$MEM/README.md" ]]; then
  cat > "$MEM/README.md" <<EOF
# Память проекта: $SLUG

Создано T-800 \`init-project-memory.sh\`.

- \`STATE.md\` — loop: Last run / In progress / Gates (\`loop-engineering-contract\`)
- \`run-manifest.json\` — шаги прогонов
- \`factory-briefs/\` — брифы конвейера
- \`fragments/\` — отчёты агентов
- \`audits/\` — runtime-аудиты
EOF
fi

marker="$WORKSPACE/project-memory.marker.json"
if [[ ! -f "$marker" ]]; then
  cat > "$marker" <<EOF
{
  "slug": "$SLUG",
  "memory_dir": "$MEMORY_DIR",
  "plugin_root": ".",
  "release_handoff": null
}
EOF
fi

echo "OK memory: $MEM"
echo "OK marker: $marker"
