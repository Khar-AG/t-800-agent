#!/usr/bin/env bash
# t800-update-from-github.sh — полуавтообновление T-800 с публичного GitHub
# Сравнивает remote version с локальной; при отличии скачивает и ставит.
set -euo pipefail

REPO_SLUG="${T800_GITHUB_REPO:-Khar-AG/t-800-agent}"
BRANCH="${T800_GITHUB_BRANCH:-main}"
PLUGIN_DEST="${T800_PLUGIN_DEST:-$HOME/.cursor/plugins/local/t-800-agent}"
CACHE_DIR="${T800_UPDATE_CACHE:-$HOME/.t800/update-cache}"
FORCE=0
CHECK_ONLY=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/t800-update-from-github.sh [--check] [--force] [--repo OWNER/NAME] [--branch main]

  --check   только сравнить версии, не ставить
  --force   обновить даже если версии совпадают
  --repo    GitHub slug (default: Khar-AG/t-800-agent)
  --branch  ветка (default: main)

Env:
  T800_GITHUB_REPO, T800_GITHUB_BRANCH, T800_PLUGIN_DEST, T800_UPDATE_CACHE
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --check) CHECK_ONLY=1; shift ;;
    --force) FORCE=1; shift ;;
    --repo) REPO_SLUG="$2"; shift 2 ;;
    --branch) BRANCH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Неизвестный аргумент: $1" >&2; usage; exit 2 ;;
  esac
done

mkdir -p "$CACHE_DIR"

remote_zip_url="https://github.com/${REPO_SLUG}/archive/refs/heads/${BRANCH}.zip"
api_plugin_json_url="https://api.github.com/repos/${REPO_SLUG}/contents/.cursor-plugin/plugin.json?ref=${BRANCH}"
raw_plugin_json_url="https://raw.githubusercontent.com/${REPO_SLUG}/${BRANCH}/.cursor-plugin/plugin.json"

echo "T-800 update: репозиторий ${REPO_SLUG}@${BRANCH}"

fetch_remote_version() {
  local tmp
  tmp="$(mktemp)"
  # GitHub API first (без CDN-лага raw.githubusercontent.com)
  if ! curl -fsSL --connect-timeout 6 --max-time 20 \
      -H "Accept: application/vnd.github.raw+json" \
      -H "X-GitHub-Api-Version: 2022-11-28" \
      -H "User-Agent: t-800-agent-update" \
      "$api_plugin_json_url" -o "$tmp" 2>/dev/null; then
    if ! curl -fsSL --connect-timeout 6 --max-time 20 \
        -H "Cache-Control: no-cache" \
        -H "User-Agent: t-800-agent-update" \
        "${raw_plugin_json_url}?$(date +%s)" -o "$tmp" 2>/dev/null; then
      rm -f "$tmp"
      echo "ERROR: не удалось скачать remote plugin.json" >&2
      echo "  API: $api_plugin_json_url" >&2
      echo "  RAW: $raw_plugin_json_url" >&2
      exit 1
    fi
  fi
  python3 -c "import json; print(json.load(open('$tmp'))['version'])"
  rm -f "$tmp"
}

local_version() {
  if [[ -f "$PLUGIN_DEST/.cursor-plugin/plugin.json" ]]; then
    python3 -c "import json; print(json.load(open('$PLUGIN_DEST/.cursor-plugin/plugin.json'))['version'])"
  else
    echo "none"
  fi
}

REMOTE_VER="$(fetch_remote_version)"
LOCAL_VER="$(local_version)"

echo "  локальная:  $LOCAL_VER"
echo "  на GitHub:  $REMOTE_VER"

version_gt() {
  # true if $1 > $2 (semver-ish)
  python3 - "$1" "$2" <<'PY'
import sys
from packaging.version import Version
a, b = sys.argv[1], sys.argv[2]
try:
    print("1" if Version(a) > Version(b) else "0")
except Exception:
    print("1" if a != b else "0")
PY
}

# packaging may be missing — fallback
cmp_need_update() {
  if [[ "$FORCE" == "1" ]]; then
    return 0
  fi
  if [[ "$LOCAL_VER" == "none" ]]; then
    return 0
  fi
  if [[ "$LOCAL_VER" == "$REMOTE_VER" ]]; then
    return 1
  fi
  # try packaging; else string inequality = update
  if python3 -c "from packaging.version import Version" 2>/dev/null; then
    [[ "$(version_gt "$REMOTE_VER" "$LOCAL_VER")" == "1" ]]
  else
    python3 - "$REMOTE_VER" "$LOCAL_VER" <<'PY'
import sys
r, l = sys.argv[1], sys.argv[2]
def parts(v):
    out=[]
    for p in v.replace('-','.').split('.'):
        try: out.append(int(p))
        except: out.append(p)
    return out
rp, lp = parts(r), parts(l)
# pad
n=max(len(rp),len(lp))
rp += [0]*(n-len(rp)); lp += [0]*(n-len(lp))
sys.exit(0 if rp>lp else 1)
PY
  fi
}

if [[ "$CHECK_ONLY" == "1" ]]; then
  if cmp_need_update; then
    echo "UPDATE_AVAILABLE: $LOCAL_VER → $REMOTE_VER"
    exit 10
  else
    echo "UP_TO_DATE: $LOCAL_VER"
    exit 0
  fi
fi

if ! cmp_need_update; then
  echo "Уже актуальная версия ($LOCAL_VER). Нечего обновлять."
  echo "Подсказка: --force для переустановки."
  exit 0
fi

ZIP="$CACHE_DIR/t-800-agent-${BRANCH}.zip"
EXTRACT="$CACHE_DIR/extract-$$"
rm -rf "$EXTRACT"
mkdir -p "$EXTRACT"

echo "Скачиваю: $remote_zip_url"
curl -fsSL "$remote_zip_url" -o "$ZIP"

echo "Распаковываю…"
unzip -q "$ZIP" -d "$EXTRACT"
# GitHub zip → t-800-agent-<branch>/
SRC="$(find "$EXTRACT" -maxdepth 1 -type d -name 't-800-agent-*' | head -1)"
if [[ -z "$SRC" || ! -f "$SRC/.cursor-plugin/plugin.json" ]]; then
  echo "ERROR: в архиве нет .cursor-plugin/plugin.json" >&2
  ls -la "$EXTRACT" >&2 || true
  exit 1
fi

INSTALL_SH="$SRC/scripts/install-plugin.sh"
if [[ ! -f "$INSTALL_SH" ]]; then
  echo "ERROR: нет scripts/install-plugin.sh" >&2
  exit 1
fi

echo "Устанавливаю через install-plugin.sh…"
bash "$INSTALL_SH"

VERIFY="$PLUGIN_DEST/scripts/verify-install.sh"
if [[ -f "$VERIFY" ]]; then
  bash "$VERIFY" || {
    echo "WARN: verify-install вернул ошибку — проверьте вручную" >&2
  }
fi

NEW_VER="$(local_version)"
echo ""
echo "Готово. Локальная версия: $NEW_VER (было $LOCAL_VER, remote $REMOTE_VER)"
echo "Обязательно: Developer: Reload Window"
echo "Потом: /t800-onboard или /t800-doctor"

# cleanup extract (keep zip cache)
rm -rf "$EXTRACT"
