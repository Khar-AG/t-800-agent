#!/usr/bin/env python3
"""t800_run_gate.py — канонический machine gate прогона T-800 (v1.13).

Usage:
  python3 scripts/t800_run_gate.py --memory-path PATH \\
      [--require-validate] [--require-plugin-audit-out DIR] [--plugin-root PATH]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def fail(msg: str, summary: dict[str, Any], code: int = 1) -> int:
    summary["ok"] = False
    summary["error"] = msg
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"FAIL: {msg}", file=sys.stderr)
    return code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Machine gate прогона T-800 (STATE + optional validate/audit)."
    )
    parser.add_argument("--memory-path", required=True, help="Путь к memory целевого проекта")
    parser.add_argument(
        "--require-validate",
        action="store_true",
        help="Запустить validate-agents.sh в --plugin-root (если есть)",
    )
    parser.add_argument(
        "--require-plugin-audit-out",
        default=None,
        help="Директория аудита: должен быть inventory.json",
    )
    parser.add_argument(
        "--plugin-root",
        default=None,
        help="Корень плагина (для --require-validate)",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    summary: dict[str, Any] = {
        "ok": True,
        "memory_path": str(memory_path),
        "checks": {},
        "error": None,
    }

    state = memory_path / "STATE.md"
    if not state.is_file():
        summary["checks"]["STATE.md"] = "missing"
        return fail(
            f"Не найден STATE.md в {memory_path}. "
            "Сначала: bash scripts/t800_loop_state.sh init --memory-path …",
            summary,
        )
    summary["checks"]["STATE.md"] = "ok"
    print(f"OK  STATE.md: {state}")

    if args.require_plugin_audit_out:
        audit_dir = Path(args.require_plugin_audit_out).expanduser().resolve()
        inventory = audit_dir / "inventory.json"
        if not inventory.is_file():
            summary["checks"]["plugin_audit_inventory"] = "missing"
            return fail(
                f"Нет inventory.json в {audit_dir}. "
                "Сначала запустите t800_plugin_audit.py или /t800-plugin-audit.",
                summary,
            )
        summary["checks"]["plugin_audit_inventory"] = "ok"
        summary["plugin_audit_out"] = str(audit_dir)
        print(f"OK  inventory.json: {inventory}")

    if args.require_validate:
        if not args.plugin_root:
            summary["checks"]["validate"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-validate требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        validate = plugin_root / "scripts" / "validate-agents.sh"
        if not validate.is_file():
            summary["checks"]["validate"] = "script_missing"
            print(f"WARN validate-agents.sh отсутствует: {validate} (пропуск)")
            summary["checks"]["validate"] = "skipped_missing_script"
        else:
            try:
                proc = subprocess.run(
                    ["bash", str(validate)],
                    cwd=str(plugin_root),
                    capture_output=True,
                    text=True,
                    check=False,
                )
            except OSError as exc:
                summary["checks"]["validate"] = "error"
                return fail(f"Не удалось запустить validate-agents.sh: {exc}", summary)
            if proc.returncode != 0:
                summary["checks"]["validate"] = f"fail_exit_{proc.returncode}"
                tail = (proc.stdout or "")[-500:] + (proc.stderr or "")[-500:]
                return fail(
                    f"validate-agents.sh завершился с кодом {proc.returncode}. {tail}",
                    summary,
                )
            summary["checks"]["validate"] = "ok"
            print("OK  validate-agents.sh exit 0")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("PASS: t800_run_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
