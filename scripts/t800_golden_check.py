#!/usr/bin/env python3
"""t800_golden_check.py — compare workspace hashes/paths vs expected.json.

Usage:
  python3 scripts/t800_golden_check.py --memory-path PATH
  python3 scripts/t800_golden_check.py --expected PATH [--root PATH]
  python3 scripts/t800_golden_check.py --expected PATH --write-hashes  # helper

Exit: 0 PASS, 1 FAIL. stdout = JSON.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_expected(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("expected.json должен быть объектом")
    return data


def resolve_root(expected: dict[str, Any], root_arg: str | None, expected_path: Path) -> Path:
    if root_arg:
        return Path(root_arg).expanduser().resolve()
    if expected.get("root"):
        r = Path(str(expected["root"]))
        if not r.is_absolute():
            r = (expected_path.parent / r).resolve()
        return r
    return expected_path.parent.resolve()


def check(expected: dict[str, Any], root: Path) -> dict[str, Any]:
    files = expected.get("files") or expected.get("paths") or []
    if not isinstance(files, list):
        raise ValueError("files должен быть списком")

    results: list[dict[str, Any]] = []
    failed = 0
    for item in files:
        if isinstance(item, str):
            rel = item
            want_hash = None
            must_exist = True
        elif isinstance(item, dict):
            rel = str(item.get("path") or item.get("file") or "")
            want_hash = item.get("sha256") or item.get("hash")
            must_exist = bool(item.get("exists", True))
        else:
            failed += 1
            results.append({"ok": False, "error": f"bad entry: {item}"})
            continue

        if not rel:
            failed += 1
            results.append({"ok": False, "error": "empty path"})
            continue

        path = root / rel.replace("\\", "/")
        entry: dict[str, Any] = {"path": rel, "ok": True}
        if must_exist and not path.is_file():
            entry["ok"] = False
            entry["error"] = "missing"
            failed += 1
            results.append(entry)
            continue
        if not must_exist:
            entry["exists"] = path.is_file()
            results.append(entry)
            continue
        if want_hash:
            got = sha256_file(path)
            entry["sha256"] = got
            entry["expected_sha256"] = str(want_hash).lower()
            if got.lower() != str(want_hash).lower():
                entry["ok"] = False
                entry["error"] = "hash_mismatch"
                failed += 1
        else:
            entry["sha256"] = sha256_file(path)
            entry["note"] = "exists_only"
        results.append(entry)

    return {
        "schema_version": SCHEMA_VERSION,
        "ok": failed == 0,
        "status": "PASS" if failed == 0 else "FAIL",
        "root": str(root),
        "failed": failed,
        "checked": len(results),
        "results": results,
    }


def write_hashes(expected_path: Path, root: Path) -> dict[str, Any]:
    data = load_expected(expected_path)
    files = data.get("files") or []
    new_files: list[dict[str, Any]] = []
    for item in files:
        if isinstance(item, str):
            rel = item
        elif isinstance(item, dict):
            rel = str(item.get("path") or item.get("file") or "")
        else:
            continue
        path = root / rel.replace("\\", "/")
        entry: dict[str, Any] = {"path": rel}
        if path.is_file():
            entry["sha256"] = sha256_file(path)
        else:
            entry["exists"] = False
        new_files.append(entry)
    data["files"] = new_files
    data["schema_version"] = data.get("schema_version") or SCHEMA_VERSION
    expected_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(expected_path), "count": len(new_files)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Golden hash/path check")
    parser.add_argument("--memory-path", default=None, help="Читать {memory}/golden/expected.json")
    parser.add_argument("--expected", default=None, help="Путь к expected.json")
    parser.add_argument("--root", default=None, help="Корень для относительных путей")
    parser.add_argument(
        "--write-hashes",
        action="store_true",
        help="Перезаписать sha256 в expected.json (maintainer)",
    )
    args = parser.parse_args()

    try:
        if args.expected:
            expected_path = Path(args.expected).expanduser().resolve()
        elif args.memory_path:
            expected_path = (
                Path(args.memory_path).expanduser().resolve() / "golden" / "expected.json"
            )
        else:
            print("FAIL: нужен --expected или --memory-path", file=sys.stderr)
            return 1

        if not expected_path.is_file():
            print(
                json.dumps(
                    {"ok": False, "status": "FAIL", "error": f"нет {expected_path}"},
                    ensure_ascii=False,
                    indent=2,
                )
            )
            print(f"FAIL: нет {expected_path}", file=sys.stderr)
            return 1

        expected = load_expected(expected_path)
        root = resolve_root(expected, args.root, expected_path)

        if args.write_hashes:
            out = write_hashes(expected_path, root)
            print(json.dumps(out, ensure_ascii=False, indent=2))
            return 0

        report = check(expected, root)
        report["expected"] = str(expected_path)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        if not report["ok"]:
            print("FAIL: golden_check", file=sys.stderr)
            return 1
        print("PASS: golden_check", file=sys.stderr)
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "status": "FAIL", "error": str(exc)}, ensure_ascii=False, indent=2))
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
