#!/usr/bin/env python3
"""t800_loop_queue_write.py — materialize {memory}/loop-queue.md from conductor handoff.

Prefer this over agent Write (loop-conductor is readonly).
Renders ## Open (approve candidates) and ## Closed (applied|rejected, no action).

Usage:
  echo '<json>' | python3 scripts/t800_loop_queue_write.py --memory-path PATH
  python3 scripts/t800_loop_queue_write.py --memory-path PATH --stdin
  python3 scripts/t800_loop_queue_write.py --memory-path PATH --input PATH.json

Exit: 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def lesson_status(lesson: Any) -> str:
    if not isinstance(lesson, dict):
        return "open"
    s = str(lesson.get("status") or "open").lower().strip()
    return s if s in ("open", "applied", "rejected") else "open"


def split_open_closed(data: dict[str, Any]) -> tuple[list[Any], list[Any]]:
    """Prefer data['closed'] if present; also split items by status."""
    items = as_list(data.get("items") or data.get("queue") or data.get("lessons") or [])
    open_items: list[Any] = []
    closed_items: list[Any] = list(as_list(data.get("closed") or []))

    for item in items:
        if not isinstance(item, dict):
            open_items.append(item)
            continue
        st = lesson_status(item)
        if st == "open":
            open_items.append(item)
        else:
            closed_items.append(item)

    return open_items, closed_items


def _render_item(idx: int, item: Any, *, allow_action: bool) -> list[str]:
    lines: list[str] = []
    if isinstance(item, str):
        lines.append(f"{idx}. {item}")
        return lines
    if not isinstance(item, dict):
        lines.append(f"{idx}. {item}")
        return lines

    lid = item.get("id") or item.get("lesson_id") or f"item-{idx}"
    risk = item.get("risk_class") or item.get("risk") or "unset"
    symptom = item.get("symptom") or item.get("title") or ""
    pack = item.get("fix_pack") or item.get("fixpack") or ""
    files = as_list(
        (item.get("proposed_patch") or {}).get("files")
        if isinstance(item.get("proposed_patch"), dict)
        else item.get("files")
    )
    st = lesson_status(item)
    lines.append(f"### {idx}. `{lid}`")
    lines.append("")
    lines.append(f"- **status:** {st}")
    lines.append(f"- **risk_class:** {risk}")
    if symptom:
        lines.append(f"- **symptom:** {symptom}")
    if pack:
        lines.append(f"- **fix_pack:** `{pack}`")
    if files:
        lines.append("- **files:**")
        for f in files:
            lines.append(f"  - `{f}`")
    if not allow_action:
        applied_in = item.get("applied_in")
        if applied_in:
            lines.append(f"- **applied_in:** {applied_in}")
        closed_reason = item.get("closed_reason")
        if closed_reason:
            lines.append(f"- **closed_reason:** {closed_reason}")
    else:
        action = item.get("action") or item.get("next")
        if action:
            lines.append(f"- **action:** {action}")
    lines.append("")
    return lines


def render_markdown(data: dict[str, Any]) -> str:
    run_id = str(data.get("run_id") or data.get("runId") or "—")
    status = str(data.get("status") or "ready")
    ts = str(data.get("generated_at") or data.get("ts") or utc_now())
    summary = str(data.get("summary") or data.get("note") or "").strip()
    open_items, closed_items = split_open_closed(data)

    lines = [
        "# Loop Queue",
        "",
        f"- **generated_at:** {ts}",
        f"- **run_id:** `{run_id}`",
        f"- **status:** {status}",
        "",
        "> Материализовано скриптом `t800_loop_queue_write.py` (не agent Write).",
        "",
    ]
    if summary:
        lines.extend(["## Summary", "", summary, ""])

    lines.extend(["## Open", ""])
    if not open_items:
        lines.append("_нет открытых уроков_")
        lines.append("")
    else:
        for idx, item in enumerate(open_items, start=1):
            lines.extend(_render_item(idx, item, allow_action=True))

    lines.extend(["## Closed", ""])
    if not closed_items:
        lines.append("_пусто_")
        lines.append("")
    else:
        for idx, item in enumerate(closed_items, start=1):
            lines.extend(_render_item(idx, item, allow_action=False))

    high = as_list(data.get("high_queue") or data.get("deferred") or [])
    if high:
        lines.extend(["## HIGH / deferred", ""])
        for h in high:
            if isinstance(h, dict):
                lines.append(f"- `{h.get('id', '?')}`: {h.get('symptom') or h.get('reason') or ''}")
            else:
                lines.append(f"- {h}")
        lines.append("")

    raw_note = data.get("raw_markdown")
    if isinstance(raw_note, str) and raw_note.strip():
        lines.extend(["## Notes", "", raw_note.strip(), ""])

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Materialize loop-queue.md from JSON handoff")
    parser.add_argument("--memory-path", required=True)
    parser.add_argument("--input", default=None, help="Путь к JSON handoff")
    parser.add_argument("--stdin", action="store_true", help="Читать JSON из stdin")
    parser.add_argument(
        "--out",
        default=None,
        help="Путь выхода (default: {memory}/loop-queue.md)",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    out = (
        Path(args.out).expanduser().resolve()
        if args.out
        else memory_path / "loop-queue.md"
    )
    summary: dict[str, Any] = {
        "ok": True,
        "memory_path": str(memory_path),
        "path": str(out),
        "error": None,
    }

    try:
        if args.input:
            raw = Path(args.input).expanduser().resolve().read_text(encoding="utf-8")
        else:
            raw = sys.stdin.read()
            if not raw.strip():
                raise ValueError("пустой stdin / нет --input")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("handoff должен быть JSON-объектом")

        memory_path.mkdir(parents=True, exist_ok=True)
        open_items, closed_items = split_open_closed(data)
        text = render_markdown(data)
        out.write_text(text, encoding="utf-8")
        open_count = len(open_items)
        closed_count = len(closed_items)
        summary["open_count"] = open_count
        summary["closed_count"] = closed_count
        summary["items"] = open_count  # compat: items = open candidates
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
