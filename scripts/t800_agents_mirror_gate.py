#!/usr/bin/env python3
"""t800_agents_mirror_gate.py — parity agents/*.md ↔ .cursor/agents/<same>.

Checks:
  1) FS: каждый agents/*.md имеет зеркало в .cursor/agents/ (и reverse)
  2) content identity: sha256 обеих сторон пары совпадает
  3) git readonly: если изменена только одна сторона пары — FAIL

Usage:
  python3 scripts/t800_agents_mirror_gate.py --plugin-root PATH

Exit 0 = PASS (или SKIP: нет agents/). Exit 1 = FAIL + JSON summary.
Stdout: JSON {ok, drift, reason?}. Stderr: RU-сообщения.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def _sha256_file(path: Path) -> str | None:
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except OSError:
        return None


def _list_md_basenames(directory: Path) -> set[str]:
    if not directory.is_dir():
        return set()
    return {p.name for p in directory.glob("*.md") if p.is_file()}


def _find_git_root(start: Path) -> Path | None:
    """Ищем .git вверх от start (plugin_root) и от parent workspace."""
    candidates = [start.resolve()]
    parent = start.resolve().parent
    if parent not in candidates:
        candidates.append(parent)
    for base in candidates:
        cur = base
        for _ in range(32):
            git_meta = cur / ".git"
            if git_meta.exists():
                return cur
            if cur.parent == cur:
                break
            cur = cur.parent
    return None


def _collect_git_changed(git_root: Path) -> set[str]:
    """Readonly: status/diff --name-only (worktree + index + untracked). Без checkout/reset."""
    files: set[str] = set()
    cmds: list[list[str]] = [
        [
            "git",
            "-C",
            str(git_root),
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
        ],
        [
            "git",
            "-C",
            str(git_root),
            "diff",
            "--name-only",
            "--cached",
            "--diff-filter=ACMR",
        ],
        [
            "git",
            "-C",
            str(git_root),
            "ls-files",
            "--others",
            "--exclude-standard",
        ],
    ]
    for cmd in cmds:
        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
            )
        except OSError:
            continue
        if proc.returncode != 0:
            continue
        for line in (proc.stdout or "").splitlines():
            line = line.strip().replace("\\", "/")
            if line:
                files.add(line)
    return files


def _rel_to_plugin(path_str: str, plugin_root: Path, git_root: Path) -> str | None:
    """Нормализуем путь из git к относительному от plugin_root (posix)."""
    raw = path_str.replace("\\", "/").lstrip("./")
    abs_path = (git_root / raw).resolve()
    try:
        rel = abs_path.relative_to(plugin_root.resolve())
        return str(rel).replace("\\", "/")
    except ValueError:
        # путь уже относительно plugin или вне плагина
        if raw.startswith("agents/") or raw.startswith(".cursor/agents/"):
            return raw
        # иногда workspace = plugin_root
        plugin_name = plugin_root.name
        marker = f"{plugin_name}/"
        if marker in raw:
            idx = raw.find(marker)
            return raw[idx + len(marker) :]
        return None


def _pair_sides_from_changed(
    changed: set[str], plugin_root: Path, git_root: Path
) -> dict[str, set[str]]:
    """basename → {'canon' | 'mirror'} для изменённых сторон пары."""
    sides: dict[str, set[str]] = {}
    for raw in changed:
        rel = _rel_to_plugin(raw, plugin_root, git_root)
        if not rel:
            continue
        if rel.startswith("agents/") and rel.count("/") == 1 and rel.endswith(".md"):
            name = Path(rel).name
            sides.setdefault(name, set()).add("canon")
        elif (
            rel.startswith(".cursor/agents/")
            and rel.count("/") == 2
            and rel.endswith(".md")
        ):
            name = Path(rel).name
            sides.setdefault(name, set()).add("mirror")
    return sides


def _emit(summary: dict[str, Any], code: int) -> int:
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return code


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gate: agents/*.md ↔ .cursor/agents/ (FS + sha256 + git pair)."
    )
    parser.add_argument(
        "--plugin-root",
        default=None,
        help="Корень плагина (по умолчанию: cwd, если есть agents/ или .cursor-plugin/)",
    )
    args = parser.parse_args()

    if args.plugin_root:
        plugin_root = Path(args.plugin_root).expanduser().resolve()
    else:
        cwd = Path.cwd().resolve()
        if (cwd / "agents").is_dir() or (cwd / ".cursor-plugin").is_dir():
            plugin_root = cwd
        elif (cwd / "scripts" / "t800_agents_mirror_gate.py").is_file():
            plugin_root = cwd
        else:
            summary = {
                "ok": False,
                "drift": [],
                "reason": "укажите --plugin-root: cwd не похож на корень плагина",
            }
            print(
                "FAIL: нужен --plugin-root PATH (cwd не содержит agents/ "
                "и не является plugin root).",
                file=sys.stderr,
            )
            return _emit(summary, 1)

    summary: dict[str, Any] = {
        "ok": True,
        "plugin_root": str(plugin_root),
        "drift": [],
        "checks": {},
    }

    if not plugin_root.is_dir():
        summary["ok"] = False
        summary["reason"] = f"plugin-root не найден: {plugin_root}"
        print(f"FAIL: {summary['reason']}", file=sys.stderr)
        return _emit(summary, 1)

    agents_dir = plugin_root / "agents"
    mirror_dir = plugin_root / ".cursor" / "agents"

    if not agents_dir.is_dir():
        summary["ok"] = True
        summary["reason"] = "нет agents/ — SKIP"
        summary["checks"]["agents_dir"] = "missing_skip"
        print("SKIP: нет agents/ — зеркало не требуется.", file=sys.stderr)
        return _emit(summary, 0)

    canon = _list_md_basenames(agents_dir)
    summary["checks"]["agents_md_count"] = len(canon)

    if not canon:
        summary["ok"] = True
        summary["reason"] = "agents/ без .md — SKIP"
        summary["checks"]["agents_dir"] = "empty_skip"
        print("SKIP: agents/ без .md файлов.", file=sys.stderr)
        return _emit(summary, 0)

    if not mirror_dir.is_dir():
        summary["ok"] = False
        summary["reason"] = "missing_mirror_dir"
        summary["drift"].append(
            {
                "kind": "missing_mirror_dir",
                "path": str(mirror_dir),
                "detail": "agents/ содержит .md, но .cursor/agents отсутствует",
            }
        )
        print(
            f"FAIL: есть agents/*.md, но нет зеркала {mirror_dir}",
            file=sys.stderr,
        )
        return _emit(summary, 1)

    mirror = _list_md_basenames(mirror_dir)
    summary["checks"]["mirror_md_count"] = len(mirror)

    drift: list[dict[str, Any]] = []

    for name in sorted(canon - mirror):
        drift.append(
            {
                "kind": "missing_mirror",
                "basename": name,
                "canon": f"agents/{name}",
                "mirror": f".cursor/agents/{name}",
            }
        )
        print(
            f"FAIL: нет зеркала .cursor/agents/{name} для agents/{name}",
            file=sys.stderr,
        )

    for name in sorted(mirror - canon):
        drift.append(
            {
                "kind": "missing_canon",
                "basename": name,
                "canon": f"agents/{name}",
                "mirror": f".cursor/agents/{name}",
            }
        )
        print(
            f"FAIL: .cursor/agents/{name} без канона agents/{name}",
            file=sys.stderr,
        )

    for name in sorted(canon & mirror):
        left = agents_dir / name
        right = mirror_dir / name
        left_hash = _sha256_file(left)
        right_hash = _sha256_file(right)
        if left_hash is None or right_hash is None:
            drift.append(
                {
                    "kind": "read_error",
                    "basename": name,
                    "canon": f"agents/{name}",
                    "mirror": f".cursor/agents/{name}",
                }
            )
            print(f"FAIL: не удалось прочитать пару {name}", file=sys.stderr)
            continue
        if left_hash != right_hash:
            drift.append(
                {
                    "kind": "content_drift",
                    "basename": name,
                    "canon": f"agents/{name}",
                    "mirror": f".cursor/agents/{name}",
                    "canon_sha256": left_hash,
                    "mirror_sha256": right_hash,
                }
            )
            print(
                f"FAIL: drift sha256 agents/{name} ≠ .cursor/agents/{name}",
                file=sys.stderr,
            )

    # Git readonly: односторонняя правка пары
    git_root = _find_git_root(plugin_root)
    if git_root is not None:
        summary["checks"]["git_root"] = str(git_root)
        changed = _collect_git_changed(git_root)
        pair_sides = _pair_sides_from_changed(changed, plugin_root, git_root)
        for name, sides in sorted(pair_sides.items()):
            if sides == {"canon"} or sides == {"mirror"}:
                only = "canon" if sides == {"canon"} else "mirror"
                drift.append(
                    {
                        "kind": "git_one_sided",
                        "basename": name,
                        "changed_side": only,
                        "canon": f"agents/{name}",
                        "mirror": f".cursor/agents/{name}",
                    }
                )
                print(
                    f"FAIL: git — изменена только сторона {only} пары {name} "
                    f"(agents/ ↔ .cursor/agents/). Синхронизируйте обе.",
                    file=sys.stderr,
                )
        summary["checks"]["git_pair"] = "ok" if not any(
            d.get("kind") == "git_one_sided" for d in drift
        ) else "fail"
    else:
        summary["checks"]["git_root"] = "none"
        summary["checks"]["git_pair"] = "skipped_no_git"

    summary["drift"] = drift
    if drift:
        summary["ok"] = False
        summary["reason"] = f"drift_count={len(drift)}"
        print(
            f"FAIL: t800_agents_mirror_gate — {len(drift)} нарушений зеркала",
            file=sys.stderr,
        )
        return _emit(summary, 1)

    summary["reason"] = "agents_mirror_ok"
    print("PASS: t800_agents_mirror_gate", file=sys.stderr)
    return _emit(summary, 0)


if __name__ == "__main__":
    sys.exit(main())
