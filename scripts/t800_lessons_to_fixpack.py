#!/usr/bin/env python3
"""t800_lessons_to_fixpack.py — open LOW lessons → fix-pack drafts; mark applied/rejected.

Generate: risk_class=LOW AND status=open AND proposed_patch.files[] filled.
Mark: --mark-applied / --mark-rejected persist back to lessons.json (schema 1.1).
Mutual exclusion: mark XOR generate.

Usage:
  python3 scripts/t800_lessons_to_fixpack.py --memory-path PATH \\
      --lessons PATH|run_id [--plugin-root PATH] [--dry-run]
  python3 scripts/t800_lessons_to_fixpack.py --memory-path PATH --lessons PATH \\
      --mark-applied ID --applied-in VER
  python3 scripts/t800_lessons_to_fixpack.py --memory-path PATH --lessons PATH \\
      --mark-rejected ID --closed-reason TEXT

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


def lesson_status(lesson: Any) -> str:
    if not isinstance(lesson, dict):
        return "open"
    s = str(lesson.get("status") or "open").lower().strip()
    return s if s in ("open", "applied", "rejected") else "open"


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

> Автоиз lessons.json (risk_class=LOW, status=open). Контракт: `shared/fix-pipeline-contract.md`

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
- Только status=open (Lesson Lifecycle v1.1)
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


def persist_lessons(path: Path, data: Any) -> None:
    if isinstance(data, dict):
        ver = str(data.get("schema_version") or "1.0")
        if ver in ("1.0", ""):
            data["schema_version"] = "1.1"
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def mark_status(
    data: Any,
    lesson_id: str,
    status: str,
    *,
    applied_in: str | None = None,
    closed_reason: str | None = None,
) -> bool:
    lessons = data.get("lessons") if isinstance(data, dict) else data
    if not isinstance(lessons, list):
        return False
    found = False
    for lesson in lessons:
        if not isinstance(lesson, dict):
            continue
        if str(lesson.get("id")) != lesson_id:
            continue
        lesson["status"] = status
        if applied_in is not None:
            lesson["applied_in"] = applied_in
        if closed_reason is not None:
            lesson["closed_reason"] = closed_reason
        found = True
        break
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description="LOW open lessons → fix-pack drafts / mark status")
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
    parser.add_argument("--mark-applied", default=None, metavar="ID", help="Закрыть урок как applied")
    parser.add_argument("--applied-in", default=None, metavar="VER", help="Версия/релиз (с --mark-applied)")
    parser.add_argument("--mark-rejected", default=None, metavar="ID", help="Закрыть урок как rejected")
    parser.add_argument(
        "--closed-reason",
        default=None,
        metavar="TEXT",
        help="Причина (с --mark-rejected)",
    )
    args = parser.parse_args()

    mark_applied = bool(args.mark_applied)
    mark_rejected = bool(args.mark_rejected)
    marking = mark_applied or mark_rejected

    if mark_applied and mark_rejected:
        print(
            "FAIL: нельзя одновременно --mark-applied и --mark-rejected",
            file=sys.stderr,
        )
        return 1
    if mark_applied and not args.applied_in:
        print(
            "FAIL: для --mark-applied обязателен флаг --applied-in <версия>",
            file=sys.stderr,
        )
        return 1
    if mark_rejected and not args.closed_reason:
        print(
            "FAIL: для --mark-rejected обязателен флаг --closed-reason <текст>",
            file=sys.stderr,
        )
        return 1

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
        "skipped_closed": [],
        "marked_applied": [],
        "marked_rejected": [],
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

    # Mark XOR generate
    if marking:
        if mark_applied:
            ok = mark_status(
                data,
                str(args.mark_applied),
                "applied",
                applied_in=str(args.applied_in),
            )
            if not ok:
                summary["ok"] = False
                summary["error"] = f"урок не найден: {args.mark_applied}"
                print(json.dumps(summary, ensure_ascii=False, indent=2))
                print(f"FAIL: {summary['error']}", file=sys.stderr)
                return 1
            if not args.dry_run:
                persist_lessons(lessons_path, data)
            summary["marked_applied"].append(
                {"id": args.mark_applied, "applied_in": args.applied_in}
            )
        else:
            ok = mark_status(
                data,
                str(args.mark_rejected),
                "rejected",
                closed_reason=str(args.closed_reason),
            )
            if not ok:
                summary["ok"] = False
                summary["error"] = f"урок не найден: {args.mark_rejected}"
                print(json.dumps(summary, ensure_ascii=False, indent=2))
                print(f"FAIL: {summary['error']}", file=sys.stderr)
                return 1
            if not args.dry_run:
                persist_lessons(lessons_path, data)
            summary["marked_rejected"].append(
                {"id": args.mark_rejected, "closed_reason": args.closed_reason}
            )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

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
        if lesson_status(lesson) != "open":
            summary["skipped_closed"].append(
                {"id": lesson.get("id"), "status": lesson_status(lesson)}
            )
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
