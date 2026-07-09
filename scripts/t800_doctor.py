#!/usr/bin/env python3
"""t800_doctor.py — scripts-only health report (v1.13).

Usage:
  python3 scripts/t800_doctor.py --workspace PATH [--plugin-root PATH] [--out DIR]
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


ALWAYS_RE = re.compile(r"^alwaysApply:\s*true\b", re.M | re.I)
SCRIPT_DIR = Path(__file__).resolve().parent


def find_plugin_json(plugin_root: Path) -> Path | None:
    for rel in (".cursor-plugin/plugin.json", "plugin.json"):
        p = plugin_root / rel
        if p.is_file():
            return p
    return None


def count_md(directory: Path, pattern: str = "*.md") -> int:
    if not directory.is_dir():
        return 0
    return sum(1 for p in directory.glob(pattern) if p.is_file())


def count_rules(rules_dir: Path) -> tuple[int, int]:
    if not rules_dir.is_dir():
        return 0, 0
    total = 0
    always = 0
    for p in rules_dir.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".mdc", ".md"}:
            continue
        total += 1
        try:
            head = p.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            continue
        if ALWAYS_RE.search(head):
            always += 1
    return total, always


def discover(workspace: Path, plugin_root: Path | None) -> dict[str, Any] | None:
    script = SCRIPT_DIR / "discover-target-project.sh"
    if not script.is_file():
        return None
    cmd = ["bash", str(script), "--workspace", str(workspace)]
    if plugin_root is not None:
        cmd.extend(["--plugin-root", str(plugin_root)])
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or "").strip()
    # last JSON object in stdout
    start = text.rfind("{")
    if start < 0:
        return None
    try:
        return json.loads(text[start:])
    except json.JSONDecodeError:
        return None


def list_audit_dirs(memory_path: Path, limit: int = 8) -> list[str]:
    audits = memory_path / "audits"
    if not audits.is_dir():
        return []
    dirs = [p for p in audits.iterdir() if p.is_dir()]
    dirs.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return [p.name for p in dirs[:limit]]


def main() -> int:
    parser = argparse.ArgumentParser(description="T-800 doctor — health report")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--plugin-root", default=None)
    parser.add_argument("--out", default=None, help="Директория для doctor-report.md + doctor.json")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    plugin_root = (
        Path(args.plugin_root).expanduser().resolve() if args.plugin_root else None
    )

    if plugin_root is not None:
        pj = find_plugin_json(plugin_root)
        if pj is None:
            print(
                f"Ошибка: в {plugin_root} нет plugin.json / .cursor-plugin/plugin.json",
                file=sys.stderr,
            )
            return 1

    disc = discover(workspace, plugin_root)
    memory_path: Path
    profile = "unknown"
    slug = None
    if disc:
        memory_path = Path(disc.get("memory_path") or (workspace / "t-800-memory"))
        profile = str(disc.get("profile") or "unknown")
        slug = disc.get("slug")
        if plugin_root is None and disc.get("plugin_root"):
            plugin_root = Path(str(disc["plugin_root"]))
    else:
        memory_path = workspace / "t-800-memory"

    version = None
    plugin_name = None
    broken_plugin = False
    if plugin_root is not None:
        pj = find_plugin_json(plugin_root)
        if pj is None:
            broken_plugin = True
        else:
            try:
                meta = json.loads(pj.read_text(encoding="utf-8"))
                version = meta.get("version")
                plugin_name = meta.get("name") or meta.get("displayName")
            except (OSError, json.JSONDecodeError) as exc:
                print(f"Ошибка чтения plugin.json: {exc}", file=sys.stderr)
                return 1

    agents_n = commands_n = rules_n = always_n = 0
    if plugin_root is not None and not broken_plugin:
        agents_n = count_md(plugin_root / "agents")
        commands_n = count_md(plugin_root / "commands")
        rules_n, always_n = count_rules(plugin_root / "rules")

    state_present = (memory_path / "STATE.md").is_file()
    audits = list_audit_dirs(memory_path)

    report: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "workspace": str(workspace),
        "plugin_root": str(plugin_root) if plugin_root else None,
        "plugin_name": plugin_name,
        "version": version,
        "profile": profile,
        "slug": slug,
        "memory_path": str(memory_path),
        "state_present": state_present,
        "counts": {
            "agents": agents_n,
            "commands": commands_n,
            "rules": rules_n,
            "alwaysApply": always_n,
        },
        "last_audits": audits,
        "verify_install_hint": "bash scripts/verify-install.sh",
        "discover_ok": disc is not None,
    }

    lines = [
        "# T-800 Doctor Report",
        "",
        f"- workspace: `{workspace}`",
        f"- plugin_root: `{plugin_root}`",
        f"- version: **{version}**",
        f"- profile: `{profile}`",
        f"- memory_path: `{memory_path}`",
        f"- STATE.md: {'есть' if state_present else 'нет'}",
        f"- agents / commands / rules: {agents_n} / {commands_n} / {rules_n}",
        f"- alwaysApply (plugin rules): {always_n}",
        f"- last audits: {', '.join(audits) if audits else '(нет)'}",
        f"- verify: `{report['verify_install_hint']}`",
        "",
    ]
    md = "\n".join(lines)

    print(md)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.out:
        out_dir = Path(args.out).expanduser().resolve()
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            (out_dir / "doctor-report.md").write_text(md, encoding="utf-8")
            (out_dir / "doctor.json").write_text(
                json.dumps(report, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"Wrote: {out_dir / 'doctor-report.md'}")
            print(f"Wrote: {out_dir / 'doctor.json'}")
        except OSError as exc:
            print(f"Предупреждение: не удалось записать --out: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
