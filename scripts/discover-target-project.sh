#!/usr/bin/env bash
# discover-target-project.sh — универсальное обнаружение plugin_root и memory_path
set -euo pipefail

WORKSPACE="."
PLUGIN_ROOT_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --plugin-root) PLUGIN_ROOT_OVERRIDE="$2"; shift 2 ;;
    *) WORKSPACE="$1"; shift ;;
  esac
done

WORKSPACE="$(cd "$WORKSPACE" && pwd)"

# TEYA_PLUGIN_ROOT из ~/.teya/teya.env.global (без source всего файла секретов)
if [[ -z "${TEYA_PLUGIN_ROOT:-}" ]] && [[ -f "$HOME/.teya/teya.env.global" ]]; then
  TEYA_PLUGIN_ROOT="$(grep -E '^TEYA_PLUGIN_ROOT=' "$HOME/.teya/teya.env.global" | tail -1 | cut -d= -f2- | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  export TEYA_PLUGIN_ROOT
fi

needs_user_question=false
profile="unknown"
plugin_root=""
memory_dir=""
memory_path=""
slug=""
release_handoff="null"
plugin_json=""
artifact_surface="cursor-workspace"

# 1) project-memory.marker.json (walk up)
search="$WORKSPACE"
while [[ "$search" != "/" ]]; do
  marker="$search/project-memory.marker.json"
  if [[ -f "$marker" ]]; then
    slug="$(python3 -c "import json; d=json.load(open('$marker')); print(d.get('slug',''))" 2>/dev/null || echo "")"
    memory_dir="$(python3 -c "import json; d=json.load(open('$marker')); print(d.get('memory_dir',''))" 2>/dev/null || echo "")"
    pr="$(python3 -c "import json; d=json.load(open('$marker')); print(d.get('plugin_root','.'))" 2>/dev/null || echo ".")"
    rh="$(python3 -c "import json; d=json.load(open('$marker')); print(d.get('release_handoff') or '')" 2>/dev/null || echo "")"
    if [[ -n "$rh" ]]; then release_handoff="\"$rh\""; fi
    if [[ "$pr" == "." ]]; then
      plugin_root="$search"
    else
      plugin_root="$(cd "$search/$pr" && pwd)"
    fi
    memory_path="$search/$memory_dir"
    profile="marker"
    break
  fi
  search="$(dirname "$search")"
done

# 2) Teya plugin dev: plugin-memory + .cursor-plugin
if [[ -z "$plugin_root" ]] && [[ -d "$WORKSPACE/plugin-memory" ]] && [[ -f "$WORKSPACE/.cursor-plugin/plugin.json" ]]; then
  if [[ -f "$WORKSPACE/scripts/teya_plugin_root.py" ]] || [[ -f "$WORKSPACE/scripts/teya_docs_build.py" ]]; then
    profile="teya-plugin-dev"
    plugin_root="$WORKSPACE"
    memory_dir="plugin-memory"
    memory_path="$WORKSPACE/plugin-memory"
    slug="teya"
    artifact_surface="cursor-plugin"
    release_handoff="\"/teya-release-sync\""
  fi
fi

# 3) Teya client: teya-memory/
if [[ -z "$memory_dir" ]] && [[ -d "$WORKSPACE/teya-memory" ]]; then
  profile="teya-client"
  memory_dir="teya-memory"
  memory_path="$WORKSPACE/teya-memory"
  slug="teya"
  # plugin_root from env
  if [[ -n "${TEYA_PLUGIN_ROOT:-}" ]] && [[ -d "${TEYA_PLUGIN_ROOT}" ]]; then
    plugin_root="$(cd "${TEYA_PLUGIN_ROOT}" && pwd)"
  elif command -v python3 >/dev/null 2>&1; then
    for candidate in "$HOME/.cursor/plugins/local/teya" "$WORKSPACE/../TeyaPlugin" "$WORKSPACE/../../TeyaPlugin"; do
      if [[ -f "$candidate/scripts/teya_plugin_root.py" ]]; then
        resolved="$(TEYA_PLUGIN_ROOT="$candidate" python3 "$candidate/scripts/teya_plugin_root.py" 2>/dev/null || true)"
        if [[ -n "$resolved" ]] && [[ -d "$resolved" ]]; then
          plugin_root="$(cd "$resolved" && pwd)"
          break
        fi
      fi
    done
  fi
  if [[ -z "$plugin_root" ]]; then
    needs_user_question=true
  fi
  release_handoff="\"/teya-release-sync\""
  artifact_surface="cursor-plugin"
fi

# 4) Self T-800
if [[ -z "$memory_dir" ]] && [[ -d "$WORKSPACE/t-800-memory" ]] && [[ -d "$WORKSPACE/t-800-agent/.cursor-plugin" ]]; then
  profile="self-t800"
  plugin_root="$WORKSPACE/t-800-agent"
  artifact_surface="cursor-plugin"
  memory_dir="t-800-memory"
  memory_path="$WORKSPACE/t-800-memory"
  slug="t-800-agent"
fi

# 5) Generic: .cursor-plugin + {name}-memory
if [[ -z "$plugin_root" ]] && [[ -f "$WORKSPACE/.cursor-plugin/plugin.json" ]]; then
  plugin_json="$WORKSPACE/.cursor-plugin/plugin.json"
  pname="$(python3 -c "import json; print(json.load(open('$plugin_json')).get('name','plugin'))" 2>/dev/null || echo "plugin")"
  slug="$pname"
  plugin_root="$WORKSPACE"
  candidate="${pname}-memory"
  if [[ -d "$WORKSPACE/$candidate" ]]; then
    memory_dir="$candidate"
    memory_path="$WORKSPACE/$candidate"
    profile="generic-plugin"
    artifact_surface="cursor-plugin"
  else
    profile="generic-plugin"
    artifact_surface="cursor-plugin"
    memory_dir="$candidate"
    memory_path="$WORKSPACE/$candidate"
    needs_user_question=true
  fi
fi

# 6) t-800-agent inside workspace only
if [[ -z "$plugin_root" ]] && [[ -d "$WORKSPACE/t-800-agent/.cursor-plugin" ]]; then
  profile="self-t800"
  plugin_root="$WORKSPACE/t-800-agent"
  artifact_surface="cursor-plugin"
  if [[ -d "$WORKSPACE/t-800-memory" ]]; then
    memory_dir="t-800-memory"
    memory_path="$WORKSPACE/t-800-memory"
  elif [[ -d "$WORKSPACE/t-800-agent/t-800-memory" ]]; then
    memory_dir="t-800-memory"
    memory_path="$WORKSPACE/t-800-agent/t-800-memory"
  else
    memory_dir="t-800-memory"
    memory_path="$WORKSPACE/t-800-memory"
    needs_user_question=true
  fi
  slug="t-800-agent"
  artifact_surface="cursor-plugin"
fi

# 7) Workspace — skills/rules в .cursor/ (не плагин)
if [[ "$profile" == "unknown" ]] && [[ -z "$plugin_root" ]]; then
  if [[ -d "$WORKSPACE/.cursor" ]] || [[ -d "$WORKSPACE/.git" ]]; then
    profile="workspace-cursor"
    artifact_surface="cursor-workspace"
    memory_dir=".cursor/t800-memory"
    memory_path="$WORKSPACE/.cursor/t800-memory"
    slug="workspace"
    mkdir -p "$memory_path/fragments" "$memory_path/factory-briefs" 2>/dev/null || true
  fi
fi

if [[ -z "$plugin_root" ]] && [[ "$profile" != "teya-client" ]] && [[ "$profile" != "workspace-cursor" ]]; then
  needs_user_question=true
  if [[ -z "$memory_dir" ]]; then
    profile="unknown"
  fi
elif [[ "$profile" == "teya-client" ]] && [[ -z "$plugin_root" ]]; then
  needs_user_question=true
fi

if [[ -n "$memory_dir" ]] && [[ ! -d "$memory_path" ]]; then
  needs_user_question=true
fi

# Явный выбор оператора (--plugin-root после list-target-plugins)
if [[ -n "$PLUGIN_ROOT_OVERRIDE" ]] && [[ -d "$PLUGIN_ROOT_OVERRIDE/.cursor-plugin" ]]; then
  plugin_root="$(cd "$PLUGIN_ROOT_OVERRIDE" && pwd)"
  needs_user_question=false
  if [[ "$profile" == "unknown" ]]; then
    profile="generic-plugin"
    artifact_surface="cursor-plugin"
  fi
  if [[ -f "$plugin_root/.cursor-plugin/plugin.json" ]]; then
    slug="$(python3 -c "import json; print(json.load(open('$plugin_root/.cursor-plugin/plugin.json')).get('name','plugin'))" 2>/dev/null || echo "$slug")"
  fi
fi

cat <<EOF
{
  "workspace_root": "$WORKSPACE",
  "plugin_root": "${plugin_root:-}",
  "memory_dir": "${memory_dir:-}",
  "memory_path": "${memory_path:-}",
  "profile": "$profile",
  "slug": "${slug:-}",
  "artifact_surface": "$artifact_surface",
  "release_handoff": $release_handoff,
  "needs_user_question": $needs_user_question
}
EOF
