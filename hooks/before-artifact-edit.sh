#!/usr/bin/env bash
# beforeFileEdit (T-800) — WARN при правке Cursor-артефактов без factory.
# v1: не hard-deny (allow + userMessage). Обычный код не трогаем.
# Pattern: Teya-style stdout JSON {continue, permission, userMessage}.
# Cloud-safe: без секретов в argv; fail-open на parse errors.
set -u

payload=$(cat 2>/dev/null || true)

allow() {
  printf '{"continue":true,"permission":"allow"}'
  exit 0
}

warn_allow() {
  # Escape for JSON string (minimal)
  local msg="${1:-}"
  msg=${msg//\\/\\\\}
  msg=${msg//\"/\\\"}
  msg=${msg//$'\n'/\\n}
  printf '{"continue":true,"permission":"allow","userMessage":"%s"}' "$msg"
  exit 0
}

# Bypass: активный factory run
if [[ -n "${T800_FACTORY_RUN_ID:-}" ]]; then
  allow
fi

edited_path=""
case "$payload" in
  *"filePath"*)
    edited_path=$(printf '%s' "$payload" | sed -n 's/.*"filePath"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
    ;;
  *"path"*)
    edited_path=$(printf '%s' "$payload" | sed -n 's/.*"path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -1)
    ;;
esac

if [[ -z "${edited_path}" ]]; then
  allow
fi

# Normalize path separators
norm=${edited_path//\\//}

is_artifact=0
case "$norm" in
  */agents/*.md|*/agents/*/*.md|agents/*.md)
    is_artifact=1
    ;;
  */commands/*.md|commands/*.md|*/.cursor/commands/*.md)
    is_artifact=1
    ;;
  */skills/*/SKILL.md|skills/*/SKILL.md|*/.cursor/skills/*/SKILL.md)
    is_artifact=1
    ;;
  */rules/*.mdc|rules/*.mdc|*/.cursor/rules/*.mdc)
    is_artifact=1
    ;;
  */hooks.json|hooks.json|*/hooks/*.sh|hooks/*.sh|*/hooks/*.ps1|hooks/*.ps1)
    is_artifact=1
    ;;
esac

# Basename fallbacks (relative edits)
base=$(basename "$norm")
dir=$(dirname "$norm")
dir_base=$(basename "$dir")
if [[ "$is_artifact" -eq 0 ]]; then
  case "$dir_base/$base" in
    agents/*.md|commands/*.md|rules/*.mdc)
      is_artifact=1
      ;;
  esac
  if [[ "$base" == "SKILL.md" && "$dir_base" != "." ]]; then
    case "$norm" in
      *skills*|*/.cursor/skills/*) is_artifact=1 ;;
    esac
  fi
  if [[ "$base" == "hooks.json" ]]; then
    is_artifact=1
  fi
fi

if [[ "$is_artifact" -eq 0 ]]; then
  allow
fi

# Optional soft bypass: manifest already has completed factory (best-effort)
# Look for nearby plugin-memory / t-800-memory / memory under cwd
HERE="$(cd "$(dirname "$0")" 2>/dev/null && pwd)" || HERE="."
PLUGIN_ROOT="$(cd "$HERE/.." 2>/dev/null && pwd)" || PLUGIN_ROOT=""
for mem in \
  "${T800_MEMORY_PATH:-}" \
  "./plugin-memory" \
  "./t-800-memory" \
  "${PLUGIN_ROOT}/../TeyaPlugin/plugin-memory"
do
  [[ -z "$mem" ]] && continue
  man="${mem}/run-manifest.json"
  if [[ -f "$man" ]]; then
    if grep -Eqi '"agent"[[:space:]]*:[[:space:]]*"t-800-factory"' "$man" 2>/dev/null \
      && grep -Eqi '"status"[[:space:]]*:[[:space:]]*"(completed|ok|done)"' "$man" 2>/dev/null; then
      allow
    fi
    # top-level "factory": "completed"
    if grep -Eqi '"factory"[[:space:]]*:[[:space:]]*"(completed|ok|done)"' "$man" 2>/dev/null; then
      allow
    fi
  fi
done

warn_allow "T-800 WARN: правка Cursor-артефакта (${base}) без T800_FACTORY_RUN_ID / factory в run-manifest. Не пишите agents/skills/commands/rules/hooks из main chat — /t800-start или /t800-fix → Task(t-800-factory). Machine gate: t800_factory_bypass_gate.py / t800_run_gate.py --strict-create."
