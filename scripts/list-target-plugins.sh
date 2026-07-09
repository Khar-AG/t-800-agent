#!/usr/bin/env bash
# list-target-plugins.sh — известные plugin_root для выбора цели (универсальный отдел)
set -euo pipefail

REGISTRY="${T800_KNOWN_PLUGINS:-$HOME/.t800/known-plugins.json}"
WORKSPACE="."

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --registry) REGISTRY="$2"; shift 2 ;;
    *) shift ;;
  esac
done

WORKSPACE="$(cd "$WORKSPACE" && pwd)"

# TEYA_PLUGIN_ROOT из global env
if [[ -z "${TEYA_PLUGIN_ROOT:-}" ]] && [[ -f "$HOME/.teya/teya.env.global" ]]; then
  TEYA_PLUGIN_ROOT="$(grep -E '^TEYA_PLUGIN_ROOT=' "$HOME/.teya/teya.env.global" | tail -1 | cut -d= -f2- | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
fi

python3 - <<'PY' "$REGISTRY" "$WORKSPACE" "${TEYA_PLUGIN_ROOT:-}"
import json, sys, os
from pathlib import Path

registry_path, workspace, teya_root = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
plugins = []

def add_unique(slug, name, root, handoff, source):
    root = str(Path(root).resolve()) if root else ""
    if not root or not Path(root).joinpath(".cursor-plugin", "plugin.json").is_file():
        return
    for p in plugins:
        if p["slug"] == slug or p["plugin_root"] == root:
            return
    plugins.append({
        "slug": slug,
        "display_name": name,
        "plugin_root": root,
        "release_handoff": handoff,
        "source": source,
    })

# Registry file
if Path(registry_path).is_file():
    try:
        data = json.loads(Path(registry_path).read_text(encoding="utf-8"))
        for item in data.get("plugins", []):
            add_unique(
                item.get("slug", "unknown"),
                item.get("display_name", item.get("slug", "")),
                item.get("plugin_root", ""),
                item.get("release_handoff"),
                "registry",
            )
    except (json.JSONDecodeError, OSError):
        pass

# Env TEYA
if teya_root:
    add_unique("teya", "Teya Pro", teya_root, "/teya-release-sync", "teya.env.global")

# Workspace marker
marker = workspace / "project-memory.marker.json"
if marker.is_file():
    try:
        m = json.loads(marker.read_text(encoding="utf-8"))
        pr = m.get("plugin_root", ".")
        root = workspace if pr == "." else (workspace / pr).resolve()
        add_unique(m.get("slug", "workspace"), m.get("slug", "workspace"), str(root), m.get("release_handoff"), "marker")
    except (json.JSONDecodeError, OSError):
        pass

# Workspace is plugin repo
pj = workspace / ".cursor-plugin" / "plugin.json"
if pj.is_file():
    try:
        name = json.loads(pj.read_text(encoding="utf-8")).get("name", workspace.name)
        add_unique(name, name, str(workspace), None, "workspace")
    except (json.JSONDecodeError, OSError):
        pass

print(json.dumps({"plugins": plugins, "count": len(plugins)}, ensure_ascii=False, indent=2))
PY
