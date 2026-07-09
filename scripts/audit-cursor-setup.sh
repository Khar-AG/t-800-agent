#!/usr/bin/env bash
# audit-cursor-setup.sh — инвентаризация global vs local Cursor (rules, skills, agents, commands)
set -euo pipefail

WORKSPACE="."
OUTPUT_MD=""
CURSOR_HOME="${HOME}/.cursor"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace) WORKSPACE="$2"; shift 2 ;;
    --output) OUTPUT_MD="$2"; shift 2 ;;
    *) WORKSPACE="$1"; shift ;;
  esac
done

WORKSPACE="$(cd "$WORKSPACE" && pwd)"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

export WORKSPACE CURSOR_HOME OUTPUT_MD
python3 - <<'PY'
import json, os, re
from pathlib import Path
from datetime import date

workspace = Path(os.environ["WORKSPACE"])
cursor_home = Path(os.environ["CURSOR_HOME"])
output_md = os.environ.get("OUTPUT_MD", "")

def list_artifacts(base: Path, kind: str) -> list[dict]:
    items = []
    if not base.is_dir():
        return items
    if kind == "rules":
        for p in sorted(base.glob("**/*.mdc")):
            items.append({"path": str(p), "name": p.stem})
    elif kind == "skills":
        for p in sorted(base.glob("**/SKILL.md")):
            items.append({"path": str(p), "name": p.parent.name})
    elif kind == "commands":
        for p in sorted(base.glob("**/*.md")):
            if p.name.startswith("."):
                continue
            items.append({"path": str(p), "name": p.stem})
    elif kind == "agents":
        for p in sorted(base.glob("**/*.md")):
            items.append({"path": str(p), "name": p.stem})
    elif kind == "plugins":
        plugins_dir = base / "plugins" / "local"
        if plugins_dir.is_dir():
            for d in sorted(plugins_dir.iterdir()):
                if d.is_dir():
                    ver = ""
                    pj = d / ".cursor-plugin" / "plugin.json"
                    if pj.is_file():
                        try:
                            ver = json.loads(pj.read_text(encoding="utf-8")).get("version", "")
                        except (json.JSONDecodeError, OSError):
                            pass
                    items.append({"path": str(d), "name": d.name, "version": ver})
    return items

def read_rule_scope(path: Path) -> str:
    try:
        head = path.read_text(encoding="utf-8", errors="replace")[:800]
        if "alwaysApply: true" in head or "always_apply: true" in head:
            return "always"
        m = re.search(r"description:\s*>?\s*\n?\s*(.+)", head)
        return "conditional" if m else "unknown"
    except OSError:
        return "unknown"

global_layers = {
    "rules": list_artifacts(cursor_home / "rules", "rules"),
    "skills": list_artifacts(cursor_home / "skills", "skills"),
    "commands": list_artifacts(cursor_home / "commands", "commands"),
    "agents": list_artifacts(cursor_home / "agents", "agents"),
    "plugins": list_artifacts(cursor_home, "plugins"),
}

local_base = workspace / ".cursor"
local_layers = {
    "rules": list_artifacts(local_base / "rules", "rules"),
    "skills": list_artifacts(local_base / "skills", "skills"),
    "commands": list_artifacts(local_base / "commands", "commands"),
    "agents": list_artifacts(local_base / "agents", "agents"),
}

project_rules = []
for name in (".cursorrules", "AGENTS.md", "CLAUDE.md"):
    p = workspace / name
    if p.is_file():
        project_rules.append({"path": str(p), "name": name})

memory_hints = []
for rel in ("teya-memory", "plugin-memory", "t-800-memory", ".cursor/t800-memory"):
    p = workspace / rel if not rel.startswith(".cursor") else workspace / rel
    if p.is_dir():
        memory_hints.append(rel)

t800_installed = (cursor_home / "plugins" / "local" / "t-800-agent").is_dir()
t800_agents = [a["name"] for a in global_layers["agents"] if a["name"].startswith("t-800-")]

report = {
    "schema_version": 1,
    "date": str(date.today()),
    "workspace_root": str(workspace),
    "cursor_home": str(cursor_home),
    "global": {k: {"count": len(v), "items": v} for k, v in global_layers.items()},
    "local": {k: {"count": len(v), "items": v} for k, v in local_layers.items()},
    "project_root_files": project_rules,
    "memory_folders": memory_hints,
    "t800": {
        "plugin_installed": t800_installed,
        "subagents_count": len(t800_agents),
        "subagents": t800_agents,
        "bootstrap_command": "/t800-bootstrap",
        "main_command": "/t800-onboard",
        "factory_command": "/t800-start",
    },
}

lines = [
    "# Аудит Cursor — global vs local",
    "",
    f"**Дата:** {report['date']}",
    f"**Workspace:** `{workspace}`",
    "",
    "## Глобально (~/.cursor/)",
    "",
    "| Слой | Кол-во |",
    "|------|--------|",
]
for key, label in [
    ("rules", "Rules"),
    ("skills", "Skills"),
    ("commands", "Commands"),
    ("agents", "Subagents"),
    ("plugins", "Plugins (local)"),
]:
    c = report["global"][key]["count"]
    lines.append(f"| {label} | {c} |")

lines += ["", "### Список (global)", ""]
for key in ("rules", "skills", "commands", "agents"):
    lines.append(f"**{key}:**")
    items = report["global"][key]["items"]
    if not items:
        lines.append("- (пусто)")
    else:
        for it in items[:30]:
            lines.append(f"- `{it['name']}` — `{it['path']}`")
        if len(items) > 30:
            lines.append(f"- … ещё {len(items) - 30}")
    lines.append("")

lines += [
    "## Локально (проект /.cursor/)",
    "",
    "| Слой | Кол-во |",
    "|------|--------|",
]
for key, label in [
    ("rules", "Rules"),
    ("skills", "Skills"),
    ("commands", "Commands"),
    ("agents", "Subagents"),
]:
    c = report["local"][key]["count"]
    lines.append(f"| {label} | {c} |")

lines += ["", "### Список (local)", ""]
for key in ("rules", "skills", "commands", "agents"):
    lines.append(f"**{key}:**")
    items = report["local"][key]["items"]
    if not items:
        lines.append("- (пусто)")
    else:
        for it in items:
            lines.append(f"- `{it['name']}` — `{it['path']}`")
    lines.append("")

if project_rules:
    lines += ["## Файлы в корне проекта", ""]
    for it in project_rules:
        lines.append(f"- `{it['name']}`")
    lines.append("")

if memory_hints:
    lines += ["## Память проекта", ""]
    for m in memory_hints:
        lines.append(f"- `{m}/`")
    lines.append("")

lines += [
    "## T-800 Agent",
    "",
    f"- Плагин установлен: **{'да' if t800_installed else 'нет'}**",
    f"- Subagents T-800: **{len(t800_agents)}**",
    "- Первый запуск: `/t800-bootstrap`",
    "- Онбординг: `/t800-onboard`",
    "- Разбор rules/skills: `/t800-audit`",
    "- Обновление плагина: `/t800-update`",
    "- Создание артефактов: `/t800-start`",
    "",
]

md_text = "\n".join(lines)
print(json.dumps(report, ensure_ascii=False, indent=2))

out = output_md
if not out:
    mem = workspace / ".cursor" / "t800-memory" / "audits"
    mem.mkdir(parents=True, exist_ok=True)
    out = str(mem / "cursor-setup-audit.md")

Path(out).parent.mkdir(parents=True, exist_ok=True)
Path(out).write_text(md_text, encoding="utf-8")
print(f"REPORT_MD={out}", flush=True)
PY
