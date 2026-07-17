#!/usr/bin/env python3
"""t800_telemetry.py — append-only JSONL telemetry (Loop Engineering v2).

Usage:
  python3 scripts/t800_telemetry.py --memory-path PATH --event JSON
  python3 scripts/t800_telemetry.py --memory-path PATH --event-file PATH
  echo '{...}' | python3 scripts/t800_telemetry.py --memory-path PATH --stdin

Appends one JSON object per line to {memory}/telemetry/runs.jsonl.
Exit: 0 pass, 1 fail. Fail-open callers may ignore exit code.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
DEFAULT_REL = "telemetry/runs.jsonl"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_event(raw: str) -> dict[str, Any]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"невалидный JSON события: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("событие должно быть JSON-объектом")
    return data


def append_event(memory_path: Path, event: dict[str, Any], rel: str = DEFAULT_REL) -> Path:
    out = memory_path / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(event)
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("ts", utc_now())
    line = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    # Append with best-effort lock on POSIX
    with open(out, "a", encoding="utf-8") as fh:
        try:
            if hasattr(os, "lockf"):
                os.lockf(fh.fileno(), os.F_LOCK, 0)
        except OSError:
            pass
        fh.write(line + "\n")
        fh.flush()
        try:
            os.fsync(fh.fileno())
        except OSError:
            pass
        try:
            if hasattr(os, "lockf"):
                os.lockf(fh.fileno(), os.F_ULOCK, 0)
        except OSError:
            pass
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="T-800 telemetry — append JSONL")
    parser.add_argument("--memory-path", required=True)
    parser.add_argument("--event", default=None, help="JSON-строка события")
    parser.add_argument("--event-file", default=None, help="Путь к JSON-файлу события")
    parser.add_argument("--stdin", action="store_true", help="Читать JSON из stdin")
    parser.add_argument(
        "--rel",
        default=DEFAULT_REL,
        help=f"Относительный путь JSONL (default {DEFAULT_REL})",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    summary: dict[str, Any] = {
        "ok": True,
        "memory_path": str(memory_path),
        "path": None,
        "error": None,
    }

    try:
        if args.event_file:
            raw = Path(args.event_file).expanduser().resolve().read_text(encoding="utf-8")
            event = load_event(raw)
        elif args.event:
            event = load_event(args.event)
        elif args.stdin or (not sys.stdin.isatty() and not args.event and not args.event_file):
            raw = sys.stdin.read()
            if not raw.strip():
                raise ValueError("пустой stdin / нет --event")
            event = load_event(raw)
        else:
            raise ValueError("нужен --event, --event-file или --stdin")

        path = append_event(memory_path, event, rel=args.rel)
        summary["path"] = str(path)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        summary["ok"] = False
        summary["error"] = str(exc)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
