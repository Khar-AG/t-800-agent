#!/usr/bin/env bash
# t800-loop-dispatcher.sh — observe-only loop notice for sessionStart (fail-open)
#
# Called from hooks/t-800-session-bootstrap.sh AFTER auto-update.
# MUST NOT pollute parent stdout JSON. Side-effects only under memory_path.
#
# Behavior:
#   - Discover memory via T800_MEMORY_PATH / --memory-path / discover-target-project
#   - If {memory}/.loop-paused exists → silent exit 0
#   - If low-risk fix-packs ready → write notice marker under memory
#   - Always exit 0 (fail-open); no secrets
#
# Usage:
#   bash scripts/t800-loop-dispatcher.sh [--memory-path PATH] [--workspace PATH]
#
set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
LOG_DIR="${T800_LOOP_LOG_DIR:-$PLUGIN_ROOT/.t-800-logs}"
mkdir -p "$LOG_DIR" 2>/dev/null || true
LOG="${LOG_DIR}/loop-dispatcher.log"

log() {
  echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >>"$LOG" 2>/dev/null || true
}

# Never emit control JSON on stdout (parent owns sessionStart JSON)
quiet_exit() {
  exit 0
}

MEMORY_PATH="${T800_MEMORY_PATH:-}"
WORKSPACE="${T800_WORKSPACE:-${CURSOR_PROJECT_DIR:-${PWD:-.}}}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --memory-path) MEMORY_PATH="${2:-}"; shift 2 ;;
    --workspace) WORKSPACE="${2:-}"; shift 2 ;;
    *) shift ;;
  esac
done

# Discover memory if not set
if [[ -z "${MEMORY_PATH}" ]]; then
  DISCOVER="$HERE/discover-target-project.sh"
  if [[ -f "$DISCOVER" ]]; then
    RAW="$(bash "$DISCOVER" --workspace "$WORKSPACE" --plugin-root "$PLUGIN_ROOT" 2>/dev/null || true)"
    MEMORY_PATH="$(python3 -c "import json,sys; t=sys.argv[1]; s=t.rfind('{');
import sys as S
try:
 d=json.loads(t[s:] if s>=0 else '{}'); print(d.get('memory_path') or '')
except Exception:
 print('')" "$RAW" 2>/dev/null || true)"
  fi
fi

if [[ -z "${MEMORY_PATH}" ]]; then
  log "skip: no memory_path"
  quiet_exit
fi

# Normalize
MEMORY_PATH="$(python3 -c "from pathlib import Path; print(Path(r'''$MEMORY_PATH''').expanduser())" 2>/dev/null || echo "$MEMORY_PATH")"

if [[ ! -d "$MEMORY_PATH" ]]; then
  mkdir -p "$MEMORY_PATH" 2>/dev/null || true
fi

PAUSED="$MEMORY_PATH/.loop-paused"
if [[ -e "$PAUSED" ]]; then
  log "paused: $PAUSED"
  quiet_exit
fi

# Low-risk packs: fix-packs/loop-low-*.md or marker from lessons_to_fixpack
READY=0
PACKS_DIR="$MEMORY_PATH/fix-packs"
if [[ -d "$PACKS_DIR" ]]; then
  # shellcheck disable=SC2012
  COUNT="$(ls -1 "$PACKS_DIR"/loop-low-*.md 2>/dev/null | wc -l | tr -d ' ')"
  if [[ "${COUNT:-0}" -gt 0 ]]; then
    READY=1
  fi
fi

# Also: runs/*/lessons.json with risk_class LOW (cheap scan)
if [[ "$READY" -eq 0 ]] && [[ -d "$MEMORY_PATH/runs" ]]; then
  HIT="$(python3 - "$MEMORY_PATH" <<'PY' 2>/dev/null || true
import json, sys
from pathlib import Path
root = Path(sys.argv[1]) / "runs"
found = 0
if root.is_dir():
    for p in root.glob("*/lessons.json"):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for lesson in data.get("lessons") or []:
            if str(lesson.get("risk_class") or "").upper() == "LOW":
                files = (lesson.get("proposed_patch") or {}).get("files") or []
                if files:
                    found = 1
                    break
        if found:
            break
print(found)
PY
)"
  if [[ "${HIT:-0}" == "1" ]]; then
    READY=1
  fi
fi

NOTICE_DIR="$MEMORY_PATH/loop"
mkdir -p "$NOTICE_DIR" 2>/dev/null || true

if [[ "$READY" -eq 1 ]]; then
  NOTICE="$NOTICE_DIR/session-notice.txt"
  MARKER="$NOTICE_DIR/low-risk-ready.marker"
  {
    echo "T-800 loop: есть low-risk элементы в очереди."
    echo "Запустите /t800-loop (semi-manual), затем /t800-fix по pack."
    echo "Пауза: создайте файл $PAUSED"
  } >"$NOTICE" 2>/dev/null || true
  date '+%Y-%m-%dT%H:%M:%SZ' >"$MARKER" 2>/dev/null || true
  log "notice written: $NOTICE"
else
  # Clear stale marker (observe hygiene)
  rm -f "$NOTICE_DIR/low-risk-ready.marker" 2>/dev/null || true
  log "no low-risk packs"
fi

quiet_exit
