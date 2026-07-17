#!/usr/bin/env bash
# T-800 Agent — sessionStart hook
# 1) Автопроверка версии с GitHub (при необходимости — установка)
# 2) Loop dispatcher observe (fail-open) — bootstrap_invoke, НЕ второй sessionStart
# 3) Подсказка bootstrap при первом запуске
# stdout: JSON для Cursor (additional_context / env). Логи — только в файл/stderr.
set -u

# stdin от Cursor (JSON события) — читаем и игнорируем тело
cat >/dev/null 2>&1 || true

PLUGIN="${HOME}/.cursor/plugins/local/t-800-agent"
LOG_DIR="${PLUGIN}/.t-800-logs"
mkdir -p "$LOG_DIR" 2>/dev/null || true
LOG="${LOG_DIR}/session.log"

# Путь к скрипту: из установленного плагина или рядом с hooks/
HERE="$(cd "$(dirname "$0")" && pwd)"
CHECK_SH="${PLUGIN}/scripts/t800-auto-version-check.sh"
if [[ ! -f "$CHECK_SH" ]]; then
  CHECK_SH="$(cd "$HERE/.." && pwd)/scripts/t800-auto-version-check.sh"
fi

CTX_PARTS=()
ENV_STATUS="unknown"

if [[ -f "$CHECK_SH" ]]; then
  RAW="$(bash "$CHECK_SH" --json 2>>"$LOG" || true)"
  if [[ -n "${RAW:-}" ]]; then
    # Склеиваем additional_context + bootstrap ниже
    VER_CTX="$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print(d.get('additional_context') or '')" "$RAW" 2>/dev/null || true)"
    ENV_STATUS="$(python3 -c "import json,sys; d=json.loads(sys.argv[1] or '{}'); print((d.get('env') or {}).get('T800_VERSION_STATUS','unknown'))" "$RAW" 2>/dev/null || echo unknown)"
    if [[ -n "${VER_CTX:-}" ]]; then
      CTX_PARTS+=("$VER_CTX")
    fi
    echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart version_status=$ENV_STATUS" >>"$LOG" 2>/dev/null || true
  fi
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart missing auto-version-check" >>"$LOG" 2>/dev/null || true
fi

# Loop dispatcher (observe FS, fail-open) — AFTER auto-update; stdout → log only
# Composition: bootstrap_invoke (hooks.json остаётся с ОДНИМ sessionStart).
# .loop-paused и discovery memory_path — ответственность dispatcher (child).
DISPATCHER="${PLUGIN}/scripts/t800-loop-dispatcher.sh"
if [[ ! -f "$DISPATCHER" ]]; then
  DISPATCHER="$(cd "$HERE/.." && pwd)/scripts/t800-loop-dispatcher.sh"
fi
if [[ -f "$DISPATCHER" ]]; then
  if ! bash "$DISPATCHER" >>"$LOG" 2>&1; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart loop-dispatcher fail-open (non-zero)" >>"$LOG" 2>/dev/null || true
  else
    echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart loop-dispatcher ok" >>"$LOG" 2>/dev/null || true
  fi
else
  echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart loop-dispatcher missing (skip)" >>"$LOG" 2>/dev/null || true
fi

# First-run bootstrap hint
STATUS_SCRIPT="${PLUGIN}/scripts/first-run-status.sh"
if [[ -x "$STATUS_SCRIPT" || -f "$STATUS_SCRIPT" ]]; then
  NEEDS="$(bash "$STATUS_SCRIPT" 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('needs_bootstrap', False))" 2>/dev/null || echo False)"
  if [[ "$NEEDS" == "True" ]]; then
    CTX_PARTS+=("T-800: первый запуск ещё не завершён. После ответа на текущий запрос предложи /t800-bootstrap (аудит + глобальное правило по согласию).")
    echo "$(date '+%Y-%m-%d %H:%M:%S') sessionStart needs_bootstrap=true" >>"$LOG" 2>/dev/null || true
  fi
fi

# Собрать итоговый JSON
python3 - "$ENV_STATUS" "${CTX_PARTS[@]+${CTX_PARTS[@]}}" <<'PY'
import json, sys
status = sys.argv[1] if len(sys.argv) > 1 else "unknown"
parts = [p for p in sys.argv[2:] if p and p.strip()]
out = {
    "env": {
        "T800_VERSION_STATUS": status,
    }
}
if status == "updated":
    out["env"]["T800_PLUGIN_UPDATED"] = "1"
if parts:
    out["additional_context"] = "\n\n".join(parts)
print(json.dumps(out, ensure_ascii=False))
PY

exit 0
