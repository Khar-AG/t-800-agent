#!/usr/bin/env bash
# audit-cursor-bloat.sh — оценка «жира» rules/skills (размер, alwaysApply)
set -euo pipefail

WORKSPACE="${1:-.}"
WORKSPACE="$(cd "$WORKSPACE" && pwd)"
CURSOR_HOME="${HOME}/.cursor"
export WORKSPACE CURSOR_HOME

python3 - <<'PY'
import json, os, re
from pathlib import Path

workspace = Path(os.environ["WORKSPACE"])
cursor_home = Path(os.environ["CURSOR_HOME"])

def analyze_rule(path: Path, scope: str) -> dict:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        return {"path": str(path), "error": str(e)}
    chars = len(text)
    lines = text.count("\n") + 1
    head = text[:1200]
    always = bool(re.search(r"alwaysApply:\s*true", head))
    # heuristic risk
    risk = "low"
    reasons = []
    if always and chars > 4000:
        risk = "high"
        reasons.append("alwaysApply + большой объём (>4k) — ест контекст каждого чата")
    elif always and chars > 1500:
        risk = "medium"
        reasons.append("alwaysApply + средний объём — стоит проверить нужность")
    elif always:
        risk = "medium"
        reasons.append("alwaysApply: true — попадает во все чаты")
    elif chars > 8000:
        risk = "medium"
        reasons.append("очень большой файл — возможно дубли или устаревшее")
    # vague / template smell
    if re.search(r"Lorem|TODO|FIXME|скопируй|example only", text, re.I):
        risk = "high" if risk != "high" else risk
        reasons.append("похоже на шаблон/заглушку")
    desc = ""
    m = re.search(r"^description:\s*>?\s*\n?\s*(.+)$", head, re.M)
    if m:
        desc = m.group(1).strip()[:120]
    return {
        "name": path.stem,
        "path": str(path),
        "scope": scope,
        "chars": chars,
        "lines": lines,
        "always_apply": always,
        "risk": risk,
        "reasons": reasons,
        "description_snip": desc,
        "suggested_action": (
            "remove_or_narrow" if risk == "high"
            else "review_with_user" if risk == "medium"
            else "keep"
        ),
    }

rules = []
for base, scope in [
    (cursor_home / "rules", "global"),
    (workspace / ".cursor" / "rules", "local"),
]:
    if not base.is_dir():
        continue
    for p in sorted(base.glob("**/*.mdc")):
        rules.append(analyze_rule(p, scope))

# root project files that also inject context
root_files = []
for name in (".cursorrules", "AGENTS.md", "CLAUDE.md"):
    p = workspace / name
    if p.is_file():
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            root_files.append({
                "name": name,
                "path": str(p),
                "chars": len(text),
                "risk": "high" if len(text) > 5000 else ("medium" if len(text) > 2000 else "low"),
                "note": "корневой файл — часто always-on для workspace",
            })
        except OSError:
            pass

skills = []
for base, scope in [
    (cursor_home / "skills", "global"),
    (workspace / ".cursor" / "skills", "local"),
]:
    if not base.is_dir():
        continue
    for p in sorted(base.glob("**/SKILL.md")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
            skills.append({
                "name": p.parent.name,
                "path": str(p),
                "scope": scope,
                "chars": len(text),
                "risk": "medium" if len(text) > 6000 else "low",
            })
        except OSError:
            pass

high = [r for r in rules if r.get("risk") == "high"]
medium = [r for r in rules if r.get("risk") == "medium"]
always_count = sum(1 for r in rules if r.get("always_apply"))
total_always_chars = sum(r.get("chars", 0) for r in rules if r.get("always_apply"))

out = {
    "schema_version": 1,
    "workspace": str(workspace),
    "summary": {
        "rules_total": len(rules),
        "always_apply_count": always_count,
        "always_apply_total_chars": total_always_chars,
        "high_risk": len(high),
        "medium_risk": len(medium),
        "skills_total": len(skills),
        "root_context_files": len(root_files),
    },
    "rules": rules,
    "skills": skills,
    "root_files": root_files,
    "talking_points": [
        f"Правил alwaysApply: {always_count}, суммарно ~{total_always_chars} символов в каждый чат",
        f"Кандидаты на разбор (high): {len(high)}",
        f"Кандидаты на вопрос (medium): {len(medium)}",
    ],
}

mem = workspace / ".cursor" / "t800-memory" / "audits"
mem.mkdir(parents=True, exist_ok=True)
json_path = mem / "cursor-bloat-audit.json"
json_path.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(out, ensure_ascii=False, indent=2))
print(f"REPORT_JSON={json_path}", flush=True)
PY
