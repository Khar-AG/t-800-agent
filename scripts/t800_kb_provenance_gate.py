#!/usr/bin/env python3
"""t800_kb_provenance_gate.py — KB changes must be in manifest or manual provenance.

LEGAL if changed/added file under knowledge-base/:
  (a) path listed in knowledge-base/manifest.json pages[].file (or entries), OR
  (b) YAML/MD frontmatter has provenance: manual AND non-empty author

Usage:
  python3 scripts/t800_kb_provenance_gate.py --plugin-root .
  python3 scripts/t800_kb_provenance_gate.py --fixture-dir tests/fixtures/kb-provenance/legal-sync

Exit 0 = no violations (or no KB changes). Exit 1 = violations + JSON summary.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    """Minimal YAML-ish frontmatter: key: value lines only."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    out: dict[str, str] = {}
    for line in m.group(1).splitlines():
        line = line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        out[key.strip()] = val.strip().strip("\"'")
    return out


def load_manifest_files(manifest_path: Path) -> set[str]:
    """Collect relative paths allowed by manifest (posix, under knowledge-base/)."""
    allowed: set[str] = set()
    if not manifest_path.is_file():
        return allowed
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return allowed
    if not isinstance(data, dict):
        return allowed

    def add_file(raw: Any) -> None:
        if not isinstance(raw, str) or not raw.strip():
            return
        rel = raw.replace("\\", "/").lstrip("./")
        if rel.startswith("knowledge-base/"):
            allowed.add(rel)
        else:
            allowed.add(f"knowledge-base/{rel}")
            allowed.add(rel)

    pages = data.get("pages")
    if isinstance(pages, dict):
        for entry in pages.values():
            if isinstance(entry, dict):
                add_file(entry.get("file"))
            elif isinstance(entry, str):
                add_file(entry)
    elif isinstance(pages, list):
        for entry in pages:
            if isinstance(entry, dict):
                add_file(entry.get("file") or entry.get("path"))
            elif isinstance(entry, str):
                add_file(entry)

    for key in ("entries", "files", "cards"):
        block = data.get(key)
        if isinstance(block, list):
            for entry in block:
                if isinstance(entry, dict):
                    add_file(entry.get("file") or entry.get("path"))
                elif isinstance(entry, str):
                    add_file(entry)
        elif isinstance(block, dict):
            for entry in block.values():
                if isinstance(entry, dict):
                    add_file(entry.get("file") or entry.get("path"))
                elif isinstance(entry, str):
                    add_file(entry)

    return allowed


def normalize_kb_rel(path: str) -> str:
    raw = path.replace("\\", "/").lstrip("./")
    if not raw.startswith("knowledge-base/"):
        if raw == "knowledge-base" or raw.startswith("knowledge-base"):
            return raw
        return f"knowledge-base/{raw}"
    return raw


def is_manual_provenance(file_path: Path) -> bool:
    try:
        text = file_path.read_text(encoding="utf-8")
    except OSError:
        return False
    fm = parse_frontmatter(text)
    if fm.get("provenance", "").lower() != "manual":
        return False
    return bool(fm.get("author", "").strip())


def git_changed_kb(plugin_root: Path, base: str) -> list[str]:
    """Return knowledge-base/ paths changed/added vs base (git)."""
    cmd = [
        "git",
        "-C",
        str(plugin_root),
        "diff",
        "--name-only",
        "--diff-filter=ACMR",
        f"{base}...HEAD",
        "--",
        "knowledge-base/",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except OSError:
        return []
    if proc.returncode != 0:
        # uncommitted / no commits — try working tree vs base
        cmd2 = [
            "git",
            "-C",
            str(plugin_root),
            "diff",
            "--name-only",
            "--diff-filter=ACMR",
            base,
            "--",
            "knowledge-base/",
        ]
        proc = subprocess.run(cmd2, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            return []
    lines = [ln.strip() for ln in proc.stdout.splitlines() if ln.strip()]
    # also untracked under knowledge-base/
    ut = subprocess.run(
        [
            "git",
            "-C",
            str(plugin_root),
            "ls-files",
            "--others",
            "--exclude-standard",
            "--",
            "knowledge-base/",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if ut.returncode == 0:
        lines.extend(ln.strip() for ln in ut.stdout.splitlines() if ln.strip())
    # dedupe preserve order
    seen: set[str] = set()
    out: list[str] = []
    for ln in lines:
        rel = normalize_kb_rel(ln)
        if rel.endswith("/") or rel == "knowledge-base/manifest.json":
            continue
        if not rel.startswith("knowledge-base/"):
            continue
        if rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def check_files(
    root: Path,
    changed: list[str],
    allowed: set[str],
) -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for rel in changed:
        rel_n = normalize_kb_rel(rel)
        if rel_n.endswith("manifest.json") or rel_n == "knowledge-base/manifest.json":
            continue
        # skip non-content extensions? check all files under kb
        name = Path(rel_n).name
        if name.startswith("."):
            continue
        abs_path = root / rel_n
        in_manifest = rel_n in allowed or rel_n.removeprefix("knowledge-base/") in {
            a.removeprefix("knowledge-base/") for a in allowed
        }
        # also match if allowed has path without knowledge-base/ prefix equal to stem
        if not in_manifest:
            bare = rel_n.removeprefix("knowledge-base/")
            in_manifest = any(
                a == rel_n or a.removeprefix("knowledge-base/") == bare for a in allowed
            )
        if in_manifest:
            continue
        if abs_path.is_file() and is_manual_provenance(abs_path):
            continue
        violations.append(
            {
                "file": rel_n,
                "reason": "not_in_manifest_and_no_manual_provenance",
            }
        )
    return violations


def run_fixture(fixture_dir: Path) -> int:
    case_path = fixture_dir / "case.json"
    if not case_path.is_file():
        summary = {
            "ok": False,
            "mode": "fixture",
            "error": f"missing case.json in {fixture_dir}",
            "violations": [],
        }
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 1

    case = json.loads(case_path.read_text(encoding="utf-8"))
    mode = case.get("mode", "files")
    expect_exit = int(case.get("expect_exit", 0))
    kb_root = fixture_dir
    manifest = kb_root / "knowledge-base" / "manifest.json"
    allowed = load_manifest_files(manifest)

    if mode == "files":
        changed = [normalize_kb_rel(p) for p in (case.get("changed") or [])]
    else:
        changed = []
        kb = kb_root / "knowledge-base"
        if kb.is_dir():
            for p in kb.rglob("*"):
                if p.is_file() and p.name != "manifest.json":
                    changed.append(
                        normalize_kb_rel(str(p.relative_to(kb_root)).replace("\\", "/"))
                    )

    violations = check_files(kb_root, changed, allowed)
    ok = len(violations) == 0
    actual_exit = 0 if ok else 1
    summary: dict[str, Any] = {
        "ok": ok,
        "mode": "fixture",
        "fixture": str(fixture_dir),
        "changed": changed,
        "violations": violations,
        "expect_exit": expect_exit,
        "exit_code": actual_exit,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if actual_exit != expect_exit:
        print(
            f"FAIL: expect_exit={expect_exit} actual={actual_exit}",
            file=sys.stderr,
        )
        return 1
    return actual_exit


def run_git(plugin_root: Path, base: str) -> int:
    changed = git_changed_kb(plugin_root, base)
    allowed = load_manifest_files(plugin_root / "knowledge-base" / "manifest.json")
    violations = check_files(plugin_root, changed, allowed)
    ok = len(violations) == 0
    summary: dict[str, Any] = {
        "ok": ok,
        "mode": "git",
        "plugin_root": str(plugin_root),
        "base": base,
        "changed": changed,
        "violations": violations,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not ok:
        print(f"FAIL: {len(violations)} KB provenance violation(s)", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KB provenance gate")
    parser.add_argument("--plugin-root", default=".", type=Path)
    parser.add_argument("--base", default="HEAD", help="git base ref (default HEAD)")
    parser.add_argument(
        "--fixture-dir",
        type=Path,
        default=None,
        help="offline fixture dir with knowledge-base/ + case.json",
    )
    args = parser.parse_args(argv)

    if args.fixture_dir is not None:
        return run_fixture(args.fixture_dir.resolve())

    plugin_root = args.plugin_root.resolve()
    return run_git(plugin_root, args.base)


if __name__ == "__main__":
    sys.exit(main())
