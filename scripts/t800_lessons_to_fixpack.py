#!/usr/bin/env python3
"""t800_lessons_to_fixpack.py — lessons with risk_class=LOW → fix-pack drafts.

Only lessons where risk_class=low AND proposed_patch.files[] filled.
Missing paths → skip, leave in HIGH queue.

Usage:
  python3 scripts/t800_lessons_to_fixpack.py --memory-path PATH \\
      --lessons PATH|run_id [--plugin-root PATH] [--dry-run]

Exit: 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT_DEFAULT = SCRIPT_DIR.parent


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def slugify(text: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return s[:48] or "lesson"


def resolve_lessons(memory_path: Path, arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.is_file():
        return p.resolve()
    # treat as run_id
    candidate = memory_path / "runs" / arg / "lessons.json"
    if candidate.is_file():
        return candidate.resolve()
    raise FileNotFoundError(f"нет lessons.json: {arg}")


def path_exists(plugin_root: Path, rel: str) -> bool:
    rel_n = rel.replace("\\", "/").lstrip("/")
    return (plugin_root / rel_n).is_file() or (plugin_root / rel_n).is_dir()


def render_fixpack(
    lesson: dict[str, Any],
    plugin_root: Path,
    slug: str,
) -> str:
    files = list((lesson.get("proposed_patch") or {}).get("files") or [])
    change = str((lesson.get("proposed_patch") or {}).get("change") or lesson.get("symptom") or "")
    file_lines = "\n".join(f"- `{f}`" for f in files) or "- _(пусто)_"
    return f"""# Fix Pack: {slug}

> Автоиз lessons.json (risk_class=LOW). Контракт: `shared/fix-pipeline-contract.md`

## goal

{lesson.get("symptom") or change}

## surface

`cursor-plugin`

plugin_root:

```text
{plugin_root}
```

## files

{file_lines}

## changes

1. {change}

## constraints

- Не трогать файлы вне `files`
- risk_class назначен `t800_risk_classifier.py` (LOW)
- Не invent LOW вручную

## research_mode

`skip`

## success_criteria

- [ ] Изменения только в listed files
- [ ] `python3 scripts/t800_run_gate.py --memory-path …` exit 0

## meta

- lesson_id: `{lesson.get("id")}`
- severity: {lesson.get("severity")}
- class: {lesson.get("class")}
- generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="LOW lessons → fix-pack drafts")
    parser.add_argument("--memory-path", required=True)
    parser.add_argument(
        "--lessons",
        required=True,
        help="Path to lessons.json или run_id под {memory}/runs/<id>/",
    )
    parser.add_argument("--plugin-root", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--require-low",
        action="store_true",
        default=True,
        help="Только risk_class=LOW (default)",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    plugin_root = (
        Path(args.plugin_root).expanduser().resolve()
        if args.plugin_root
        else PLUGIN_ROOT_DEFAULT
    )

    summary: dict[str, Any] = {
        "ok": True,
        "created": [],
        "skipped_high": [],
        "skipped_missing_paths": [],
        "skipped_no_files": [],
        "error": None,
    }

    try:
        lessons_path = resolve_lessons(memory_path, args.lessons)
        data = load_json(lessons_path)
    except (OSError, json.JSONDecodeError, FileNotFoundError) as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    lessons = data.get("lessons") if isinstance(data, dict) else data
    if not isinstance(lessons, list):
        summary["ok"] = False
        summary["error"] = "lessons не список"
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    packs_dir = memory_path / "fix-packs"
    if not args.dry_run:
        packs_dir.mkdir(parents=True, exist_ok=True)

    for lesson in lessons:
        if not isinstance(lesson, dict):
            continue
        risk = str(lesson.get("risk_class") or "unset").upper()
        if risk != "LOW":
            summary["skipped_high"].append(
                {"id": lesson.get("id"), "risk_class": risk}
            )
            continue
        patch = lesson.get("proposed_patch") or {}
        files = list(patch.get("files") or []) if isinstance(patch, dict) else []
        if not files:
            summary["skipped_no_files"].append({"id": lesson.get("id")})
            continue
        missing = [f for f in files if not path_exists(plugin_root, str(f))]
        if missing:
            summary["skipped_missing_paths"].append(
                {"id": lesson.get("id"), "missing": missing}
            )
            continue

        slug = f"loop-low-{slugify(str(lesson.get('id') or 'lesson'))}"
        out = packs_dir / f"{slug}.md"
        body = render_fixpack(lesson, plugin_root, slug)
        if not args.dry_run:
            out.write_text(body, encoding="utf-8")
        summary["created"].append({"id": lesson.get("id"), "path": str(out), "slug": slug})

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
