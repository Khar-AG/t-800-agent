#!/usr/bin/env python3
"""t800_audit_to_fixpack.py — audit dir → fix-pack draft (v1.13).

Usage:
  python3 scripts/t800_audit_to_fixpack.py --audit-dir DIR --memory-path PATH [--slug SLUG]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any] | list[Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def extract_orphans(scorecard: dict[str, Any] | None, inventory: dict[str, Any] | None) -> list[str]:
    orphans: list[str] = []
    for src in (scorecard, inventory):
        if not isinstance(src, dict):
            continue
        for key in ("orphans", "orphan_agents", "orphan_skills", "orphan_commands"):
            raw = src.get(key)
            if isinstance(raw, list):
                for item in raw:
                    if isinstance(item, str):
                        orphans.append(item)
                    elif isinstance(item, dict):
                        name = item.get("id") or item.get("name") or item.get("path")
                        if name:
                            orphans.append(str(name))
            elif isinstance(raw, dict):
                for k, v in raw.items():
                    if isinstance(v, list):
                        orphans.extend(str(x) for x in v)
                    else:
                        orphans.append(f"{k}: {v}")
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for o in orphans:
        if o not in seen:
            seen.add(o)
            out.append(o)
    return out


def extract_always_warnings(scorecard: dict[str, Any] | None) -> list[str]:
    warnings: list[str] = []
    if not isinstance(scorecard, dict):
        return warnings
    aa = scorecard.get("alwaysApply") or scorecard.get("always_apply") or {}
    if isinstance(aa, dict):
        count = aa.get("count")
        soft = bool(aa.get("soft_warn"))
        hard = bool(aa.get("hard_fail"))
        # Не шумим при count < soft threshold (норма для T-800: 1 alwaysApply routing)
        if hard:
            warnings.append(f"alwaysApply HARD fail: count={count}")
        elif soft:
            warnings.append(f"alwaysApply soft warn: count={count}")
        for w in as_list(aa.get("warnings") or aa.get("items")):
            warnings.append(str(w))
    for key in ("warnings", "findings", "alwaysApply_warnings"):
        for w in as_list(scorecard.get(key)):
            text = str(w)
            if "always" in text.lower() or "AlwaysApply" in text or "alwaysApply" in text:
                warnings.append(text)
    # dedupe
    seen: set[str] = set()
    out: list[str] = []
    for w in warnings:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


def guess_files(orphans: list[str], inventory: dict[str, Any] | None) -> list[str]:
    files: list[str] = []
    for o in orphans[:15]:
        if "/" in o or o.endswith((".md", ".mdc", ".py", ".sh", ".json")):
            files.append(o)
        elif o.startswith("t-800-") or re.match(r"^[a-z0-9-]+$", o):
            # heuristic agent path
            files.append(f"agents/{o}.md")
    if isinstance(inventory, dict):
        for key, prefix in (
            ("rules_always_apply", "rules/"),
            ("alwaysApply_files", ""),
        ):
            for item in as_list(inventory.get(key)):
                if isinstance(item, str):
                    files.append(item if "/" in item else f"{prefix}{item}")
                elif isinstance(item, dict) and item.get("path"):
                    files.append(str(item["path"]))
    seen: set[str] = set()
    out: list[str] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit → fix-pack draft")
    parser.add_argument("--audit-dir", required=True)
    parser.add_argument("--memory-path", required=True)
    parser.add_argument("--slug", default=None)
    args = parser.parse_args()

    audit_dir = Path(args.audit_dir).expanduser().resolve()
    memory_path = Path(args.memory_path).expanduser().resolve()

    if not audit_dir.is_dir():
        print(f"Ошибка: audit-dir не найден: {audit_dir}", file=sys.stderr)
        return 1

    scorecard = load_json(audit_dir / "scorecard.json")
    inventory = load_json(audit_dir / "inventory.json")
    summary_path = audit_dir / "audit-machine-summary.md"
    summary_text = ""
    if summary_path.is_file():
        try:
            summary_text = summary_path.read_text(encoding="utf-8", errors="replace")[:4000]
        except OSError:
            summary_text = ""

    if scorecard is None and inventory is None and not summary_text:
        print(
            f"Ошибка: в {audit_dir} нет scorecard.json / inventory.json / audit-machine-summary.md",
            file=sys.stderr,
        )
        return 1

    orphans = extract_orphans(
        scorecard if isinstance(scorecard, dict) else None,
        inventory if isinstance(inventory, dict) else None,
    )
    aa_warn = extract_always_warnings(scorecard if isinstance(scorecard, dict) else None)
    files = guess_files(orphans, inventory if isinstance(inventory, dict) else None)

    date_slug = datetime.now().strftime("%Y%m%d")
    slug = args.slug or f"from-audit-{date_slug}"
    out_dir = memory_path / "fix-packs"
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        print(f"Ошибка: не создать {out_dir}: {exc}", file=sys.stderr)
        return 1

    out_path = out_dir / f"{slug}.md"

    p0_lines = [f"- P0 orphan: `{o}`" for o in orphans[:10]]
    if not p0_lines:
        p0_lines = ["- (orphans не найдены в scorecard/inventory — проверьте summary вручную)"]
    p1_lines = [f"- P1 alwaysApply: {w}" for w in aa_warn[:10]]
    if not p1_lines:
        p1_lines = ["- (предупреждений alwaysApply нет или не распарсились)"]

    file_lines = [f"- `{f}`" for f in files] or [
        "- `(уточните пути вручную по audit-summary)`"
    ]

    body = f"""# Fix Pack: {slug}

> Draft из `{audit_dir.name}` · статус: draft для `/t800-fix`  
> Контракт: `shared/fix-pipeline-contract.md`

## goal

Закрыть P0/P1 из plugin-audit: orphans и предупреждения alwaysApply (без silent delete).

## surface

`cursor-plugin`

plugin_root: уточните из discovery / audit.

## files

{chr(10).join(file_lines)}

## changes

### P0 (orphans)

{chr(10).join(p0_lines)}

### P1 (alwaysApply)

{chr(10).join(p1_lines)}

### Notes from machine summary

```text
{summary_text[:1500] if summary_text else "(нет audit-machine-summary.md)"}
```

## constraints

- Не silent prune / автоудаление сирот без решения человека
- Править только listed files (дополните список перед `/t800-fix`)
- Не добавлять новых research/brain агентов

## research_mode

`skip`

## success_criteria

- [ ] Fix-pack утверждён (files[] конкретны)
- [ ] `/t800-fix` → factory PATCH
- [ ] `python3 scripts/t800_run_gate.py --memory-path …` exit 0
"""

    try:
        out_path.write_text(body, encoding="utf-8")
    except OSError as exc:
        print(f"Ошибка записи fix-pack: {exc}", file=sys.stderr)
        return 1

    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
