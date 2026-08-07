#!/usr/bin/env python3
"""t800_run_gate.py — канонический machine gate прогона T-800 (v1.13+).

Usage:
  python3 scripts/t800_run_gate.py --memory-path PATH \\
      [--require-validate] [--require-plugin-audit-out DIR] [--plugin-root PATH] \\
      [--require-agents-mirror] [--require-kb-provenance] \\
      [--require-frontmatter-yaml] \\
      [--require-skill-frontmatter] [--require-plugin-json-schema] \\
      [--require-command-chains] \\
      [--strict-create] [--factory-brief PATH|SLUG]

  При --strict-create + --plugin-root auto-ON:
    agents-mirror, kb-provenance, frontmatter-yaml, skill-frontmatter,
    plugin-json-schema, command-chains.

  Чек fixture_parity включён ВСЕГДА (без флага): новейший fix-pack в
  {memory_path}/fix-packs/, тронувший обязательные шаги пайплайна без
  фикстур tests/fixtures/** в том же pack и без fixtures_exempt → FAIL.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
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
        data = json.loads(path.read_text(encoding="utf-8-sig"))
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


# Sibling-чек fixture_parity (fix-pack t800-fix-fixture-parity-check-2026-08-07).
# Обязательные шаги пайплайна (гейты / preflight / скрипты run-gate), чья правка
# в fix-pack обязывает обновить фикстуры tests/fixtures/** в том же pack.
# Шаги названы по shared/command-chains.json (pipeline t800-fix / teya fix-loop).
FIXTURE_PARITY_CRITICAL: tuple[tuple[str, str, str], ...] = (
    # (путь от plugin_root, обязательный шаг, фикстура, покрывающая шаг)
    ("scripts/t800_run_gate.py", "run-gates (t800_run_gate)", "tests/fixtures/fix-loop/"),
    ("scripts/t800_loop_state.sh", "run-gates STATE (t800_loop_state)", "tests/fixtures/fix-loop/"),
    ("scripts/t800_factory_bypass_gate.py", "factory-patch bypass gate", "tests/fixtures/fix-loop/"),
    ("scripts/t800_command_chains_gate.py", "command-chains gate", "tests/fixtures/command-run/"),
    ("shared/command-chains.json", "command-chains SSOT", "tests/fixtures/command-run/"),
    ("shared/fix-pipeline-contract.md", "fix-pipeline контракт", "tests/fixtures/fix-loop/"),
    ("scripts/teya_controlled_command_run.py", "controlled command-run preflight", "tests/fixtures/command-run/"),
    ("scripts/teya_fix_command_gate.py", "fix-command gate", "tests/fixtures/fix-loop/"),
    ("scripts/teya_fix_kp3.py", "fix preflight KP3", "tests/fixtures/fix-loop/"),
)


def _parse_fix_pack_files(pack_path: Path) -> list[str]:
    """files[] секция fix-pack: строки вида `- `path`` внутри ##/### files."""
    files: list[str] = []
    in_files = False
    for line in pack_path.read_text(encoding="utf-8", errors="replace").splitlines():
        if re.match(r"^#{2,3}\s*files\b", line, re.IGNORECASE):
            in_files = True
            continue
        if in_files and re.match(r"^#{2,3}\s", line):
            break
        if in_files:
            match = re.match(r"^-\s*`([^`]+)`", line.strip())
            if match:
                files.append(match.group(1).strip())
    return files


def _parse_fix_pack_exempt(pack_path: Path) -> str | None:
    """fixtures_exempt: "<причина>" — осознанный opt-out из fixture_parity."""
    text = pack_path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"(?im)^\s*fixtures_exempt\s*:\s*[\"']?(.+?)[\"']?\s*$", text
    )
    if match and match.group(1).strip():
        return match.group(1).strip()
    return None


def _check_fixture_parity(memory_path: Path, summary: dict[str, Any]) -> int | None:
    """FAIL, если новейший fix-pack тронул обязательный шаг пайплайна без
    фикстур tests/fixtures/** в том же pack и без fixtures_exempt.

    Закон: shared/fix-pipeline-contract.md § «Fixture parity». Включён всегда
    (без флага): канонический вызов gate в конце /t800-fix — без флагов.
    """
    packs_dir = memory_path / "fix-packs"
    packs = sorted(packs_dir.glob("*.md")) if packs_dir.is_dir() else []
    if not packs:
        summary["checks"]["fixture_parity"] = "skipped_no_packs"
        print("OK  fixture_parity: нет fix-packs — пропуск")
        return None
    # Новейший pack = текущий прогон; при равном mtime — по имени (детерминизм)
    pack = max(packs, key=lambda p: (p.stat().st_mtime, p.name))
    files = [f.replace("\\", "/").lstrip("./") for f in _parse_fix_pack_files(pack)]

    hits = [
        (crit, step, fixture)
        for crit, step, fixture in FIXTURE_PARITY_CRITICAL
        if any(f == crit or f.endswith("/" + crit) for f in files)
    ]
    summary["fixture_parity"] = {
        "pack": str(pack),
        "critical_hits": [
            {"file": crit, "step": step, "fixture": fixture}
            for crit, step, fixture in hits
        ],
    }
    if not hits:
        summary["checks"]["fixture_parity"] = "ok_no_critical"
        print(f"OK  fixture_parity: {pack.name} — обязательные шаги не тронуты")
        return None

    has_fixtures = any(f.startswith("tests/fixtures/") for f in files)
    exempt = _parse_fix_pack_exempt(pack)
    summary["fixture_parity"]["fixtures_in_pack"] = has_fixtures
    summary["fixture_parity"]["fixtures_exempt"] = exempt

    if has_fixtures:
        summary["checks"]["fixture_parity"] = "ok"
        print(
            f"OK  fixture_parity: {pack.name} — фикстуры tests/fixtures/** "
            "в том же pack"
        )
        return None
    if exempt:
        summary["checks"]["fixture_parity"] = "ok_exempt"
        print(f"OK  fixture_parity: {pack.name} — fixtures_exempt: {exempt}")
        return None

    summary["checks"]["fixture_parity"] = "fail"
    details = "; ".join(
        f"{crit} (шаг: {step}, покрывает фикстура: {fixture})"
        for crit, step, fixture in hits
    )
    return fail(
        f"fixture_parity: fix-pack {pack.name} меняет обязательные шаги "
        f"пайплайна без фикстур в том же pack: {details}. "
        "Добавьте пути tests/fixtures/** в files[] pack (обновив фикстуры) "
        'или явный opt-out `fixtures_exempt: "<причина>"` в pack.',
        summary,
    )


def _record_run_archive(memory_path: Path, exit_code: int) -> None:
    """Best-effort запись результата gate в per-run архив прогона.
    t800_loop_state.sh на touch --stage fix|factory) и дописывает шаг run_gate
    с exit code. Graceful: архива нет (старые прогоны) — пропуск, запись
    никогда не влияет на exit code самого gate.
    """
    try:
        archives = sorted(
            memory_path.glob("run-manifest.archive.*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        if not archives:
            print("OK  run-archive: нет run-manifest.archive.*.json (пропуск)")
            return
        archive = archives[0]
        try:
            loaded = json.loads(archive.read_text(encoding="utf-8"))
            data = loaded if isinstance(loaded, dict) else {}
        except (OSError, json.JSONDecodeError):
            data = {}
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        verdict = "pass" if exit_code == 0 else "fail"
        stages = [
            s
            for s in data.get("stages", [])
            if isinstance(s, dict) and s.get("stage") != "run_gate"
        ]
        stages.append(
            {"stage": "run_gate", "ts": ts, "verdict": verdict, "exit_code": exit_code}
        )
        data["stages"] = stages
        data["run_gate"] = {"exit_code": exit_code, "ts": ts, "verdict": verdict}
        data["updated_at"] = ts
        archive.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"OK  run-archive обновлён: {archive}")
    except OSError as exc:
        # Запись архива — вторична: gate не ломаем из-за проблем с архивом
        print(f"WARN run-archive: запись не удалась ({exc})", file=sys.stderr)


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
            "Auto-ON при --strict-create, если задан --plugin-root. "
            "Non-zero → FAIL. По умолчанию ВЫКЛ."
        ),
    )
    parser.add_argument(
        "--require-kb-provenance",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_kb_provenance_gate.py (--plugin-root обязателен). "
            "Auto-ON при --strict-create, если задан --plugin-root. "
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
    parser.add_argument(
        "--require-frontmatter-yaml",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_agent_frontmatter_yaml_gate.py (--plugin-root обязателен). "
            "Auto-ON при --strict-create, если задан --plugin-root. "
            "Нет скрипта → FAIL."
        ),
    )
    parser.add_argument(
        "--require-skill-frontmatter",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_skill_frontmatter_gate.py (--plugin-root обязателен). "
            "Auto-ON при --strict-create, если задан --plugin-root. "
            "Нет скрипта → FAIL."
        ),
    )
    parser.add_argument(
        "--require-plugin-json-schema",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_plugin_schema_gate.py (--plugin-root обязателен). "
            "Auto-ON при --strict-create, если задан --plugin-root. "
            "Нет скрипта → FAIL."
        ),
    )
    parser.add_argument(
        "--require-command-chains",
        action="store_true",
        default=False,
        help=(
            "Запустить t800_command_chains_gate.py (--plugin-root обязателен). "
            "Auto-ON при --strict-create, если задан --plugin-root "
            "(shared/command-chains.json — deliverable; missing → FAIL). "
            "Нет скрипта → FAIL."
        ),
    )
    args = parser.parse_args()

    # Auto-ON sibling gates under strict-create when plugin-root is set
    require_agents_mirror = bool(args.require_agents_mirror)
    require_kb_provenance = bool(args.require_kb_provenance)
    require_frontmatter_yaml = bool(args.require_frontmatter_yaml)
    require_skill_frontmatter = bool(args.require_skill_frontmatter)
    require_plugin_json_schema = bool(args.require_plugin_json_schema)
    require_command_chains = bool(args.require_command_chains)
    if args.strict_create and args.plugin_root:
        require_agents_mirror = True
        require_kb_provenance = True
        require_frontmatter_yaml = True
        require_skill_frontmatter = True
        require_plugin_json_schema = True
        require_command_chains = True

    memory_path = Path(args.memory_path).expanduser().resolve()
    summary: dict[str, Any] = {
        "ok": True,
        "memory_path": str(memory_path),
        "strict_create": bool(args.strict_create),
        "require_agents_mirror": require_agents_mirror,
        "require_kb_provenance": require_kb_provenance,
        "require_frontmatter_yaml": require_frontmatter_yaml,
        "require_skill_frontmatter": require_skill_frontmatter,
        "require_plugin_json_schema": require_plugin_json_schema,
        "require_command_chains": require_command_chains,
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

    # fixture_parity — всегда ON: ловит «тронут обязательный шаг без фикстур»
    # до релиза, в каноническом вызове без флагов.
    parity_fail = _check_fixture_parity(memory_path, summary)
    if parity_fail is not None:
        return parity_fail

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

    if require_agents_mirror:
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

    if require_kb_provenance:
        if not args.plugin_root:
            summary["checks"]["kb_provenance"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-kb-provenance требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        kb_gate = plugin_root / "scripts" / "t800_kb_provenance_gate.py"
        if not kb_gate.is_file():
            summary["checks"]["kb_provenance"] = "script_missing"
            return fail(
                f"--require-kb-provenance: нет скрипта {kb_gate}",
                summary,
            )
        # base: origin/main, если доступен; иначе offline worktree fallback
        base_ref: str | None = None
        try:
            probe = subprocess.run(
                ["git", "-C", str(plugin_root), "rev-parse", "--verify", "origin/main"],
                capture_output=True,
                text=True,
                check=False,
            )
            if probe.returncode == 0 and (probe.stdout or "").strip():
                base_ref = "origin/main"
        except OSError:
            base_ref = None
        kb_cmd = [
            sys.executable,
            str(kb_gate),
            "--plugin-root",
            str(plugin_root),
        ]
        if base_ref:
            kb_cmd += ["--base", base_ref]
        else:
            kb_cmd += ["--worktree"]
        try:
            proc = subprocess.run(
                kb_cmd,
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["kb_provenance"] = "error"
            return fail(
                f"Не удалось запустить t800_kb_provenance_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["kb_provenance"] = f"fail_exit_{proc.returncode}"
            tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
            return fail(
                f"t800_kb_provenance_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        if not base_ref:
            wt_changed: list[Any] | None = None
            try:
                nested = json.loads(proc.stdout or "")
                if isinstance(nested, dict) and isinstance(nested.get("changed"), list):
                    wt_changed = nested["changed"]
            except json.JSONDecodeError:
                wt_changed = None
            if wt_changed == []:
                summary["checks"]["kb_provenance"] = "skipped_no_base_offline"
                print(
                    "OK  kb_provenance: skipped_no_base_offline "
                    "(origin/main недоступен, KB-изменений в worktree нет)"
                )
            else:
                summary["checks"]["kb_provenance"] = "ok_worktree"
                print("OK  t800_kb_provenance_gate exit 0 (worktree fallback)")
        else:
            summary["checks"]["kb_provenance"] = "ok"
            print("OK  t800_kb_provenance_gate exit 0")

    if require_frontmatter_yaml:
        if not args.plugin_root:
            summary["checks"]["frontmatter_yaml"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-frontmatter-yaml требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        yaml_gate = plugin_root / "scripts" / "t800_agent_frontmatter_yaml_gate.py"
        if not yaml_gate.is_file():
            summary["checks"]["frontmatter_yaml"] = "script_missing"
            return fail(
                f"--require-frontmatter-yaml: нет скрипта {yaml_gate}",
                summary,
            )
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(yaml_gate),
                    "--plugin-root",
                    str(plugin_root),
                ],
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["frontmatter_yaml"] = "error"
            return fail(
                f"Не удалось запустить t800_agent_frontmatter_yaml_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["frontmatter_yaml"] = f"fail_exit_{proc.returncode}"
            tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
            return fail(
                f"t800_agent_frontmatter_yaml_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        summary["checks"]["frontmatter_yaml"] = "ok"
        print("OK  t800_agent_frontmatter_yaml_gate exit 0")

    if require_skill_frontmatter:
        if not args.plugin_root:
            summary["checks"]["skill_frontmatter"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-skill-frontmatter требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        skill_gate = plugin_root / "scripts" / "t800_skill_frontmatter_gate.py"
        if not skill_gate.is_file():
            summary["checks"]["skill_frontmatter"] = "script_missing"
            return fail(
                f"--require-skill-frontmatter: нет скрипта {skill_gate}",
                summary,
            )
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(skill_gate),
                    "--plugin-root",
                    str(plugin_root),
                ],
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["skill_frontmatter"] = "error"
            return fail(
                f"Не удалось запустить t800_skill_frontmatter_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["skill_frontmatter"] = f"fail_exit_{proc.returncode}"
            tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
            return fail(
                f"t800_skill_frontmatter_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        summary["checks"]["skill_frontmatter"] = "ok"
        print("OK  t800_skill_frontmatter_gate exit 0")

    if require_plugin_json_schema:
        if not args.plugin_root:
            summary["checks"]["plugin_json_schema"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-plugin-json-schema требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        schema_gate = plugin_root / "scripts" / "t800_plugin_schema_gate.py"
        if not schema_gate.is_file():
            summary["checks"]["plugin_json_schema"] = "script_missing"
            return fail(
                f"--require-plugin-json-schema: нет скрипта {schema_gate}",
                summary,
            )
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(schema_gate),
                    "--plugin-root",
                    str(plugin_root),
                ],
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["plugin_json_schema"] = "error"
            return fail(
                f"Не удалось запустить t800_plugin_schema_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["plugin_json_schema"] = f"fail_exit_{proc.returncode}"
            tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
            return fail(
                f"t800_plugin_schema_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        summary["checks"]["plugin_json_schema"] = "ok"
        print("OK  t800_plugin_schema_gate exit 0")

    if require_command_chains:
        if not args.plugin_root:
            summary["checks"]["command_chains"] = "skipped_no_plugin_root"
            return fail(
                "Флаг --require-command-chains требует --plugin-root.",
                summary,
            )
        plugin_root = Path(args.plugin_root).expanduser().resolve()
        chains_gate = plugin_root / "scripts" / "t800_command_chains_gate.py"
        if not chains_gate.is_file():
            summary["checks"]["command_chains"] = "script_missing"
            return fail(
                f"--require-command-chains: нет скрипта {chains_gate}",
                summary,
            )
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(chains_gate),
                    "--plugin-root",
                    str(plugin_root),
                ],
                cwd=str(plugin_root),
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError as exc:
            summary["checks"]["command_chains"] = "error"
            return fail(
                f"Не удалось запустить t800_command_chains_gate.py: {exc}",
                summary,
            )
        if proc.returncode != 0:
            summary["checks"]["command_chains"] = f"fail_exit_{proc.returncode}"
            tail = ((proc.stdout or "") + (proc.stderr or ""))[-800:]
            return fail(
                f"t800_command_chains_gate.py exit {proc.returncode}. {tail}",
                summary,
            )
        summary["checks"]["command_chains"] = "ok"
        print("OK  t800_command_chains_gate exit 0")

    # PASS: фиксируем шаг в per-run архиве прогона (run_id = slug fix-pack)
    _record_run_archive(memory_path, 0)

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("PASS: t800_run_gate")
    return 0


if __name__ == "__main__":
    sys.exit(main())
