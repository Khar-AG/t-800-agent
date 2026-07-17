#!/usr/bin/env python3
"""t800_lessons_export.py — STATE Lessons + fragments → lessons.json (per run).

Schema fields per lesson (v1.1):
  id, severity, class, agent_id, evidence[], symptom,
  proposed_patch{files[], change}, risk_class (placeholder unset), recurrence_of,
  status=open on new lessons (lifecycle: open|applied|rejected)

Usage:
  python3 scripts/t800_lessons_export.py --memory-path PATH --run-id ID \\
      [--state PATH] [--fragment PATH ...] [--classify]

Exit: 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.1"
SCRIPT_DIR = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str, fallback: str = "lesson") -> str:
    s = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ_-]+", "-", text.strip().lower())
    s = re.sub(r"-+", "-", s).strip("-")
    return (s[:48] or fallback)


def parse_state_lessons(text: str) -> list[dict[str, Any]]:
    """Extract bullets under ## Lessons."""
    lines = text.splitlines()
    in_section = False
    bullets: list[str] = []
    for line in lines:
        if re.match(r"^##\s+Lessons\b", line, re.I):
            in_section = True
            continue
        if in_section and re.match(r"^##\s+", line):
            break
        if in_section:
            m = re.match(r"^[-*]\s+(.+)$", line.strip())
            if m:
                bullets.append(m.group(1).strip())
    lessons: list[dict[str, Any]] = []
    for i, b in enumerate(bullets, start=1):
        severity = "medium"
        low = b.lower()
        if any(x in low for x in ("critical", "block", "критич")):
            severity = "high"
        elif any(x in low for x in ("high", "высок")):
            severity = "high"
        elif any(x in low for x in ("low", "низк")):
            severity = "low"
        lessons.append(
            {
                "id": f"state-{i}-{slugify(b)[:24]}",
                "severity": severity,
                "class": "state_lesson",
                "agent_id": None,
                "evidence": [f"STATE.md##Lessons#{i}"],
                "symptom": b,
                "proposed_patch": {"files": [], "change": ""},
                "risk_class": "unset",
                "recurrence_of": None,
                "status": "open",
                "source": "STATE.md",
            }
        )
    return lessons


def parse_fragment_lessons(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    agent_id = path.stem
    lessons: list[dict[str, Any]] = []

    # YAML-ish lessons: blocks or bullet "lesson:"
    for i, m in enumerate(
        re.finditer(
            r"(?im)^(?:[-*]\s+)?(?:\*\*)?(?:lesson|урок|finding)(?:\*\*)?\s*[:：]\s*(.+)$",
            text,
        ),
        start=1,
    ):
        symptom = m.group(1).strip()
        lessons.append(
            {
                "id": f"{agent_id}-{i}-{slugify(symptom)[:20]}",
                "severity": "medium",
                "class": "fragment_finding",
                "agent_id": agent_id,
                "evidence": [str(path)],
                "symptom": symptom,
                "proposed_patch": {"files": [], "change": ""},
                "risk_class": "unset",
                "recurrence_of": None,
                "status": "open",
                "source": str(path),
            }
        )

    # Explicit JSON block ```json ... lessons
    for block in re.finditer(r"```json\s*(\{.*?\}|\[.*?\])\s*```", text, re.S):
        try:
            data = json.loads(block.group(1))
        except json.JSONDecodeError:
            continue
        items = data if isinstance(data, list) else data.get("lessons") if isinstance(data, dict) else None
        if not isinstance(items, list):
            continue
        for j, item in enumerate(items, start=1):
            if not isinstance(item, dict):
                continue
            patch = item.get("proposed_patch") or {}
            if not isinstance(patch, dict):
                patch = {"files": [], "change": str(patch)}
            lessons.append(
                {
                    "id": str(item.get("id") or f"{agent_id}-json-{j}"),
                    "severity": str(item.get("severity") or "medium").lower(),
                    "class": str(item.get("class") or "fragment_json"),
                    "agent_id": item.get("agent_id") or agent_id,
                    "evidence": list(item.get("evidence") or [str(path)]),
                    "symptom": str(item.get("symptom") or item.get("title") or ""),
                    "proposed_patch": {
                        "files": list(patch.get("files") or []),
                        "change": str(patch.get("change") or ""),
                    },
                    "risk_class": "unset",
                    "recurrence_of": item.get("recurrence_of"),
                    "status": str(item.get("status") or "open"),
                    "source": str(path),
                }
            )
    return lessons


def detect_recurrence(lessons: list[dict[str, Any]]) -> None:
    seen: dict[str, str] = {}
    for lesson in lessons:
        key = re.sub(r"\s+", " ", (lesson.get("symptom") or "").lower().strip())
        if not key:
            continue
        if key in seen:
            lesson["recurrence_of"] = seen[key]
            lesson["class"] = "recurrence"
        else:
            seen[key] = lesson["id"]


def classify_lesson(memory_path: Path, lesson: dict[str, Any]) -> str:
    clf = SCRIPT_DIR / "t800_risk_classifier.py"
    if not clf.is_file():
        return "unset"
    patch = {
        "files": list((lesson.get("proposed_patch") or {}).get("files") or []),
        "change": (lesson.get("proposed_patch") or {}).get("change") or lesson.get("symptom"),
        "symptom": lesson.get("symptom"),
        "evidence": lesson.get("evidence"),
    }
    if not patch["files"]:
        return "unset"
    try:
        proc = subprocess.run(
            [
                sys.executable,
                str(clf),
                "--memory-path",
                str(memory_path),
                "--patch",
                json.dumps(patch, ensure_ascii=False),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return "unset"
    if proc.returncode != 0:
        return "unset"
    try:
        data = json.loads(proc.stdout)
        return str(data.get("risk_class") or "unset")
    except json.JSONDecodeError:
        return "unset"


def main() -> int:
    parser = argparse.ArgumentParser(description="Export structured lessons.json for a run")
    parser.add_argument("--memory-path", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--state", default=None)
    parser.add_argument("--fragment", action="append", default=[])
    parser.add_argument(
        "--classify",
        action="store_true",
        help="Вызвать t800_risk_classifier для lessons с files[]",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    run_id = str(args.run_id).strip()
    if not run_id or "/" in run_id or ".." in run_id:
        print("FAIL: некорректный --run-id", file=sys.stderr)
        return 1

    state_path = (
        Path(args.state).expanduser().resolve()
        if args.state
        else memory_path / "STATE.md"
    )

    lessons: list[dict[str, Any]] = []
    if state_path.is_file():
        try:
            lessons.extend(parse_state_lessons(state_path.read_text(encoding="utf-8", errors="replace")))
        except OSError as exc:
            print(f"FAIL: STATE: {exc}", file=sys.stderr)
            return 1

    frag_paths: list[Path] = []
    for raw in args.fragment or []:
        frag_paths.append(Path(raw).expanduser().resolve())
    if not frag_paths:
        frag_dir = memory_path / "fragments"
        if frag_dir.is_dir():
            for p in sorted(frag_dir.glob("t-800-*.md")):
                frag_paths.append(p)

    for fp in frag_paths:
        if fp.is_file():
            lessons.extend(parse_fragment_lessons(fp))

    detect_recurrence(lessons)

    if args.classify:
        for lesson in lessons:
            lesson["risk_class"] = classify_lesson(memory_path, lesson)

    payload = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": utc_now(),
        "memory_path": str(memory_path),
        "lesson_count": len(lessons),
        "lessons": lessons,
    }

    out_dir = memory_path / "runs" / run_id
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "lessons.json"
        out_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"FAIL: запись lessons.json: {exc}", file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "path": str(out_path),
                "run_id": run_id,
                "lesson_count": len(lessons),
                "schema_version": SCHEMA_VERSION,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
