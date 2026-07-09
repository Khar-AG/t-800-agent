#!/usr/bin/env bash
# t800-auto-version-check.sh — проверка/автообновление T-800 с GitHub
# Используется hooks/sessionStart и вручную.
#
# Выход:
#   --json   → один JSON-объект в stdout (для Cursor hooks)
#   иначе    → человекочитаемый лог; exit 0 всегда (fail-open), кроме --strict
#
# Env:
#   T800_SKIP_AUTO_UPDATE=1     — не проверять / не обновлять
#   T800_FORCE_VERSION_CHECK=1  — игнорировать TTL-кэш
#   T800_VERSION_CHECK_TTL_SEC  — кэш проверки (default 21600 = 6ч)
#   T800_GITHUB_REPO / T800_GITHUB_BRANCH / T800_PLUGIN_DEST
set -u

PLUGIN_DEST="${T800_PLUGIN_DEST:-$HOME/.cursor/plugins/local/t-800-agent}"
STATE_DIR="${T800_STATE_DIR:-$HOME/.t800}"
CACHE_FILE="${STATE_DIR}/version-check-cache.json"
TTL_SEC="${T800_VERSION_CHECK_TTL_SEC:-21600}"
REPO_SLUG="${T800_GITHUB_REPO:-Khar-AG/t-800-agent}"
BRANCH="${T800_GITHUB_BRANCH:-main}"
JSON_OUT=0
STRICT=0
APPLY=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --json) JSON_OUT=1; shift ;;
    --check-only) APPLY=0; shift ;;
    --strict) STRICT=1; shift ;;
    --force) T800_FORCE_VERSION_CHECK=1; shift ;;
    *) shift ;;
  esac
done

mkdir -p "$STATE_DIR" "${PLUGIN_DEST}/.t-800-logs" 2>/dev/null || true
LOG="${PLUGIN_DEST}/.t-800-logs/auto-update.log"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG" 2>/dev/null || true
}

emit_json() {
  # args: status local remote message additional_context
  local status="$1" local_v="$2" remote_v="$3" message="$4" ctx="$5"
  python3 - "$status" "$local_v" "$remote_v" "$message" "$ctx" <<'PY'
import json, sys
status, local_v, remote_v, message, ctx = sys.argv[1:6]
out = {
    "env": {
        "T800_VERSION_STATUS": status,
        "T800_LOCAL_VERSION": local_v,
        "T800_REMOTE_VERSION": remote_v,
    },
}
if status == "updated":
    out["env"]["T800_PLUGIN_UPDATED"] = "1"
if ctx.strip():
    out["additional_context"] = ctx
print(json.dumps(out, ensure_ascii=False))
PY
}

fail_open() {
  local msg="$1"
  log "FAIL_OPEN: $msg"
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "skipped" "unknown" "unknown" "$msg" ""
  else
    echo "T-800 auto-update: $msg (продолжаем без блокировки)"
  fi
  exit 0
}

if [[ "${T800_SKIP_AUTO_UPDATE:-0}" == "1" ]]; then
  fail_open "T800_SKIP_AUTO_UPDATE=1"
fi

# Read channel from installed plugin if present
CHANNEL="${PLUGIN_DEST}/shared/release-channel.json"
if [[ -f "$CHANNEL" ]]; then
  REPO_SLUG="$(python3 -c "import json; d=json.load(open('$CHANNEL')); print(d.get('github_repo','$REPO_SLUG'))" 2>/dev/null || echo "$REPO_SLUG")"
  BRANCH="$(python3 -c "import json; d=json.load(open('$CHANNEL')); print(d.get('branch','$BRANCH'))" 2>/dev/null || echo "$BRANCH")"
fi

# Версию читаем через GitHub API (не raw CDN — у raw бывает лаг после push).
# Fallback: raw.githubusercontent.com.
fetch_remote_plugin_json() {
  local out="$1"
  local api_url="https://api.github.com/repos/${REPO_SLUG}/contents/.cursor-plugin/plugin.json?ref=${BRANCH}"
  local raw_url="https://raw.githubusercontent.com/${REPO_SLUG}/${BRANCH}/.cursor-plugin/plugin.json"
  if curl -fsSL --connect-timeout 4 --max-time 12 \
      -H "Accept: application/vnd.github.raw+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "User-Agent: t-800-agent-auto-update" \
      "$api_url" -o "$out" 2>/dev/null; then
    return 0
  fi
  if curl -fsSL --connect-timeout 4 --max-time 12 \
      -H "Cache-Control: no-cache" \
      -H "User-Agent: t-800-agent-auto-update" \
      "${raw_url}?$(date +%s)" -o "$out" 2>/dev/null; then
    return 0
  fi
  return 1
}

local_version() {
  if [[ -f "$PLUGIN_DEST/.cursor-plugin/plugin.json" ]]; then
    python3 -c "import json; print(json.load(open('$PLUGIN_DEST/.cursor-plugin/plugin.json'))['version'])" 2>/dev/null || echo "none"
  else
    echo "none"
  fi
}

cache_fresh() {
  [[ "${T800_FORCE_VERSION_CHECK:-0}" == "1" ]] && return 1
  [[ -f "$CACHE_FILE" ]] || return 1
  python3 - "$CACHE_FILE" "$TTL_SEC" <<'PY'
import json, sys, time
path, ttl = sys.argv[1], int(sys.argv[2])
try:
    d = json.load(open(path))
    ts = float(d.get("checked_at", 0))
    sys.exit(0 if (time.time() - ts) < ttl else 1)
except Exception:
    sys.exit(1)
PY
}

write_cache() {
  local local_v="$1" remote_v="$2" status="$3"
  python3 - "$CACHE_FILE" "$local_v" "$remote_v" "$status" <<'PY'
import json, sys, time
path, local_v, remote_v, status = sys.argv[1:5]
json.dump({
    "checked_at": time.time(),
    "local": local_v,
    "remote": remote_v,
    "status": status,
}, open(path, "w"), ensure_ascii=False, indent=2)
PY
}

LOCAL_VER="$(local_version)"

# TTL: если недавно проверяли и не было update — не долбим сеть каждый чат
if cache_fresh; then
  CACHED_STATUS="$(python3 -c "import json; print(json.load(open('$CACHE_FILE')).get('status','ok'))" 2>/dev/null || echo ok)"
  CACHED_REMOTE="$(python3 -c "import json; print(json.load(open('$CACHE_FILE')).get('remote','?'))" 2>/dev/null || echo "?")"
  log "cache hit status=$CACHED_STATUS local=$LOCAL_VER remote=$CACHED_REMOTE"
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "$CACHED_STATUS" "$LOCAL_VER" "$CACHED_REMOTE" "cache" ""
  else
    echo "T-800: версия актуальна (кэш) $LOCAL_VER"
  fi
  exit 0
fi

TMP="$(mktemp)"
if ! fetch_remote_plugin_json "$TMP"; then
  rm -f "$TMP"
  fail_open "нет сети или GitHub недоступен"
fi

REMOTE_VER="$(python3 -c "import json; print(json.load(open('$TMP'))['version'])" 2>/dev/null || echo "")"
rm -f "$TMP"

if [[ -z "$REMOTE_VER" ]]; then
  fail_open "не удалось прочитать remote version"
fi

need_update() {
  if [[ "$LOCAL_VER" == "none" ]]; then
    return 0
  fi
  if [[ "$LOCAL_VER" == "$REMOTE_VER" ]]; then
    return 1
  fi
  python3 - "$REMOTE_VER" "$LOCAL_VER" <<'PY'
import sys
r, l = sys.argv[1], sys.argv[2]
def parts(v):
    out=[]
    for p in v.replace("-", ".").split("."):
        try: out.append(int("".join(ch for ch in p if ch.isdigit()) or 0))
        except Exception: out.append(0)
    return out
rp, lp = parts(r), parts(l)
n=max(len(rp), len(lp))
rp += [0]*(n-len(rp)); lp += [0]*(n-len(lp))
sys.exit(0 if rp > lp else 1)
PY
}

if ! need_update; then
  write_cache "$LOCAL_VER" "$REMOTE_VER" "ok"
  log "up_to_date $LOCAL_VER"
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "ok" "$LOCAL_VER" "$REMOTE_VER" "up_to_date" ""
  else
    echo "T-800: актуально $LOCAL_VER"
  fi
  exit 0
fi

# Есть новая версия
log "update_available $LOCAL_VER -> $REMOTE_VER apply=$APPLY"

if [[ "$APPLY" != "1" ]]; then
  write_cache "$LOCAL_VER" "$REMOTE_VER" "available"
  CTX="T-800 Agent: на GitHub есть версия ${REMOTE_VER} (локально ${LOCAL_VER}). Предложи пользователю /t800-update или запусти scripts/t800-update-from-github.sh, затем Reload Window."
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "available" "$LOCAL_VER" "$REMOTE_VER" "available" "$CTX"
  else
    echo "T-800: доступно обновление $LOCAL_VER → $REMOTE_VER"
  fi
  exit 0
fi

UPDATE_SH="${PLUGIN_DEST}/scripts/t800-update-from-github.sh"
# Если плагина ещё нет — клонировать нельзя из hook надёжно; только сообщение
if [[ ! -f "$UPDATE_SH" && "$LOCAL_VER" == "none" ]]; then
  CTX="T-800 Agent не установлен локально. Установите: git clone https://github.com/${REPO_SLUG}.git && bash scripts/install-plugin.sh && Reload Window."
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "missing" "none" "$REMOTE_VER" "missing" "$CTX"
  else
    echo "$CTX"
  fi
  exit 0
fi

# Применить обновление (fail-open при ошибке)
if bash "$UPDATE_SH" >>"$LOG" 2>&1; then
  NEW_VER="$(local_version)"
  write_cache "$NEW_VER" "$REMOTE_VER" "updated"
  log "updated_ok $LOCAL_VER -> $NEW_VER"
  CTX="T-800 Agent автоматически обновлён с GitHub: ${LOCAL_VER} → ${NEW_VER}.
Обязательные шаги для Директора:
1) Одной строкой сообщи пользователю, что плагин обновлён.
2) Попроси сделать Developer: Reload Window (без Reload подтянутся не все агенты/hooks).
3) После Reload продолжи ИСХОДНУЮ задачу пользователя с того же места — не начинай конвейер заново без нужды.
До Reload считай, что на диске уже новая версия, но в памяти сессии могут быть старые определения."
  if [[ "$JSON_OUT" == "1" ]]; then
    emit_json "updated" "$LOCAL_VER" "$NEW_VER" "updated" "$CTX"
  else
    echo "T-800: обновлено $LOCAL_VER → $NEW_VER (нужен Reload Window)"
  fi
  exit 0
fi

log "update_failed $LOCAL_VER -> $REMOTE_VER"
write_cache "$LOCAL_VER" "$REMOTE_VER" "failed"
CTX="T-800 Agent: на GitHub ${REMOTE_VER}, локально ${LOCAL_VER}, автообновление не удалось. Предложи вручную: bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh и Reload Window. Затем продолжи задачу."
if [[ "$JSON_OUT" == "1" ]]; then
  emit_json "failed" "$LOCAL_VER" "$REMOTE_VER" "failed" "$CTX"
else
  echo "T-800: автообновление не удалось ($LOCAL_VER → $REMOTE_VER)"
fi
if [[ "$STRICT" == "1" ]]; then
  exit 1
fi
exit 0
