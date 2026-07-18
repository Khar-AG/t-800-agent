#!/usr/bin/env python3
"""t800_run_gate.py — канонический machine gate прогона T-800 (v1.13+).

Usage:
  python3 scripts/t800_run_gate.py --memory-path PATH \\
      [--require-validate] [--require-plugin-audit-out DIR] [--plugin-root PATH] \\
      [--require-agents-mirror] [--strict-create] [--factory-brief PATH|SLUG]
"""

from __future__ import annotations

import argparse
import json
import re
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


def _load_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _status_ok(value: Any) -> bool:
    return str(value or "").strip().lower() in {
        "ok",
        "done",
        "completed",
        "pass",
        "passed",
        "success",
    }


def _factory_step_completed(manifest: dict[str, Any]) -> bool:
    for step in manifest.get("steps") or []:
        if not isinstance(step, dict):
            continue
        agent = str(step.get("agent") or step.get("name") or "").lower()
        status = str(step.get("status") or "").lower()
        if "factory" in agent and _status_ok(status):
            return True

    factory = manifest.get("factory")
    if isinstance(factory, str) and _status_ok(factory):
        return True
    if isinstance(factory, dict) and _status_ok(factory.get("status")):
        return True

    # top-level stage markers used by some runs
    stage = str(manifest.get("stage") or "").lower()
    if "factory" in stage and _status_ok(manifest.get("status")):
        return True
    return False


def _fragment_factory_ok(memory_path: Path) -> tuple[bool, str]:
    fragment = memory_path / "fragments" / "t-800-factory.md"
    if not fragment.is_file():
        return False, f"нет {fragment}"
    text = fragment.read_text(encoding="utf-8", errors="replace")
    # Prefer explicit Status / status lines
    for pattern in (
        r"(?im)^\*\*Status:\*\*\s*(\w+)",
        r"(?im)^Status:\s*(\w+)",
        r"(?im)^status:\s*(\w+)",
        r"(?im)^\*\*status:\*\*\s*(\w+)",
    ):
        match = re.search(pattern, text)
        if match and _status_ok(match.group(1)):
            return True, str(fragment)
    # YAML-ish frontmatter
    if text.lstrip().startswith("---"):
        end = text.find("---", 3)
        if end != -1:
            fm = text[3:end]
            match = re.search(r"(?im)^status:\s*(\w+)", fm)
            if match and _status_ok(match.group(1)):
                return True, str(fragment)
    return False, f"{fragment}: status не ok/done/completed"


def _resolve_factory_brief(
    memory_path: Path, brief_arg: str | None
) -> Path | None:
    if not brief_arg:
        return None
    candidate = Path(brief_arg).expanduser()
    if candidate.is_file():
        return candidate.resolve()
    # treat as slug
    slug = brief_arg.strip().removesuffix(".yaml").removesuffix(".yml")
    for name in (f"{slug}.yaml", f"{slug}.yml"):
        path = memory_path / "factory-briefs" / name
        if path.is_file():
            return path.resolve()
    return (memory_path / "factory-briefs" / f"{slug}.yaml").resolve()


def _brief_status_done(brief_path: Path) -> tuple[bool, str]:
    if not brief_path.is_file():
        return False, f"нет factory-brief: {brief_path}"
    text = brief_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?im)^status:\s*[\"']?(\w+)[\"']?", text)
    if match and _status_ok(match.group(1)):
        return True, str(brief_path)
    return False, f"{brief_path}: status не done/ok/completed"


def _check_strict_create(
    memory_path: Path,
    summary: dict[str, Any],
    brief_arg: str | None,
) -> int | None:
    """Return fail exit code or None if all strict checks pass."""
    manifest_path = memory_path / "run-manifest.json"
    if not manifest_path.is_file():
        summary["checks"]["strict_create_manifest"] = "missing"
        return fail(
            f"--strict-create: нет run-manifest.json в {memory_path}. "
            "Сначала /t800-start|/t800-fix → Task(t-800-factory).",
            summary,
        )
    manifest = _load_json(manifest_path)
    if manifest is None:
        summary["checks"]["strict_create_manifest"] = "invalid"
        return fail(
            f"--strict-create: не удалось прочитать {manifest_path}",
            summary,
        )
    if not _factory_step_completed(manifest):
        summary["checks"]["strict_create_manifest"] = "factory_incomplete"
        return fail(
            "--strict-create: в run-manifest.json нет завершённого шага factory "
            "(agent с 'factory' + status completed/ok/done). "
            "Запустите Task(t-800-factory).",
            summary,
        )
    summary["checks"]["strict_create_manifest"] = "ok"
    print(f"OK  strict-create manifest factory: {manifest_path}")

    frag_ok, frag_msg = _fragment_factory_ok(memory_path)
    if not frag_ok:
        summary["checks"]["strict_create_fragment"] = "fail"
        return fail(
            f"--strict-create: fragments/t-800-factory.md — {frag_msg}",
            summary,
        )
    summary["checks"]["strict_create_fragment"] = "ok"
    print(f"OK  strict-create fragment: {frag_msg}")

    brief_path = _resolve_factory_brief(memory_path, brief_arg)
    if brief_path is not None:
        brief_ok, brief_msg = _brief_status_done(brief_path)
        if not brief_ok:
            summary["checks"]["strict_create_brief"] = "fail"
            return fail(
                f"--strict-create: factory-brief — {brief_msg}",
                summary,
            )
        summary["checks"]["strict_create_brief"] = "ok"
        summary["factory_brief"] = str(brief_path)
        print(f"OK  strict-create brief: {brief_msg}")
    else:
        summary["checks"]["strict_create_brief"] = "skipped_no_slug"
        print("OK  strict-create brief: пропуск (нет --factory-brief / slug)")

    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Machine gate прогона T-800 (STATE + optional validate/audit/strict-create)."
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
        help="Корень плагина (для --require-validate / --require-agents-mirror)",
    )
    parser.add_argument(
        "--require-agents-mirror",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_agents_mirror_gate.py (--plugin-root обязателен). "
            "Non-zero → FAIL. По умолчанию ВЫКЛ."
        ),
    )
    parser.add_argument(
        "--strict-create",
        action="store_true",
        default=False,
        help=(
            "FAIL без завершённого factory в run-manifest, "
            "fragments/t-800-factory.md status ok, и (если задан) factory-brief done. "
            "По умолчанию ВЫКЛ (обратная совместимость)."
        ),
    )
    parser.add_argument(
        "--factory-brief",
        default=None,
        help="Путь или slug factory-brief (для --strict-create: status done)",
    )
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    summary: dict[str, Any] = {
        "ok": True,
        "memory_path": str(memory_path),
        "strict_create": bool(args.strict_create),
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

    if args.strict_create:
        strict_fail = _check_strict_create(
            memory_path, summary, args.factory_brief
        )
        if strict_fail is not None:
            return strict_fail

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

    if args.require_agents_mirror:
        if not args.plugin_root:
            summary["checks"]["agents_mirror"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-agents-mirror требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        mirror_gate = plugin_root / "scripts" / "t800_agents_mirror_gate.py"
        if not mirror_gate.is_file():
            summary["checks"]["agents_mirror"] = "script_missing"
            return fail(
                f"--require-agents-mirror: нет скрипта {mirror_gate}",
                summary,
            )
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(mirror_gate),
                    "--plugin-root",
                    str(plugin_root),
                ],
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["agents_mirror"] = "error"
            return fail(
                f"Не удалось запустить t800_agents_mirror_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["agents_mirror"] = f"fail_exit_{proc.returncode}"
            # stdout уже JSON от mirror gate — пробуем вложить
            try:
                nested = json.loads(proc.stdout or "")
                if isinstance(nested, dict):
                    summary["agents_mirror"] = nested
            except json.JSONDecodeError:
                summary["agents_mirror_stdout"] = (proc.stdout or "")[-800:]
            tail = (proc.stderr or "")[-500:]
            return fail(
                f"t800_agents_mirror_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        summary["checks"]["agents_mirror"] = "ok"
        print("OK  t800_agents_mirror_gate exit 0")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("PASS: t800_run_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
