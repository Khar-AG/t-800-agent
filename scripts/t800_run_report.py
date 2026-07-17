#!/usr/bin/env python3
"""t800_run_report.py — per-run aggregate → {memory}/runs/<run_id>/report.json.

Inputs optional: run_gate JSON, doctor.json, scorecard.json, auditor fragments.
Per-run (not cumulative). Calls telemetry append.

Usage:
  python3 scripts/t800_run_report.py --memory-path PATH --run-id ID \\
      [--run-gate PATH] [--doctor PATH] [--scorecard PATH] \\
      [--auditor-fragment PATH ...] [--status STATUS]

Exit: 0 pass, 1 fail.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "1.0"
SCRIPT_DIR = Path(__file__).resolve().parent


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path | None) -> Any | None:
    if path is None:
        return None
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_fragment_status(path: Path) -> dict[str, Any]:
    text = ""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")[:8000]
    except OSError as exc:
        return {"path": str(path), "ok": False, "error": str(exc)}
    status = None
    for line in text.splitlines()[:40]:
        low = line.lower()
        if "status" in low and (":" in line or "**" in line):
            # crude extract last token
            cleaned = line.replace("*", "").replace("`", "")
            if ":" in cleaned:
                status = cleaned.split(":", 1)[1].strip().split()[0] if cleaned.split(":", 1)[1].strip() else None
                break
    return {
        "path": str(path),
        "ok": str(status or "").lower() in {"ok", "done", "pass", "passed", "completed"},
        "status": status,
        "preview": text[:400],
    }


def append_telemetry(memory_path: Path, event: dict[str, Any]) -> None:
    telem = SCRIPT_DIR / "t800_telemetry.py"
    if not telem.is_file():
        return
    try:
        subprocess.run(
            [
                sys.executable,
                str(telem),
                "--memory-path",
                str(memory_path),
                "--event",
                json.dumps(event, ensure_ascii=False),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        pass


def derive_status(
    explicit: str | None,
    run_gate: Any,
    doctor: Any,
    scorecard: Any,
    fragments: list[dict[str, Any]],
) -> str:
    if explicit:
        return explicit
    flags: list[bool] = []
    if isinstance(run_gate, dict):
        flags.append(bool(run_gate.get("ok", True)))
    if isinstance(doctor, dict) and "ok" in doctor:
        flags.append(bool(doctor.get("ok")))
    if isinstance(scorecard, dict) and "ok" in scorecard:
        flags.append(bool(scorecard.get("ok")))
    for fr in fragments:
        if "ok" in fr:
            flags.append(bool(fr["ok"]))
    if not flags:
        return "partial"
    if all(flags):
        return "pass"
    if any(flags):
        return "partial"
    return "fail"


def main() -> int:
    parser = argparse.ArgumentParser(description="T-800 per-run report aggregator")
    parser.add_argument("--memory-path", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--run-gate", default=None, help="Path to run_gate JSON")
    parser.add_argument("--doctor", default=None, help="Path to doctor.json")
    parser.add_argument("--scorecard", default=None, help="Path to scorecard.json")
    parser.add_argument(
        "--auditor-fragment",
        action="append",
        default=[],
        help="Path to auditor fragment (repeatable)",
    )
    parser.add_argument("--status", default=None, help="Override status: pass|fail|partial")
    parser.add_argument("--slug", default=None)
    parser.add_argument("--no-telemetry", action="store_true")
    args = parser.parse_args()

    memory_path = Path(args.memory_path).expanduser().resolve()
    run_id = str(args.run_id).strip()
    if not run_id or "/" in run_id or ".." in run_id:
        print("FAIL: некорректный --run-id", file=sys.stderr)
        return 1

    run_gate = load_json(Path(args.run_gate).expanduser().resolve() if args.run_gate else None)
    doctor = load_json(Path(args.doctor).expanduser().resolve() if args.doctor else None)
    scorecard = load_json(
        Path(args.scorecard).expanduser().resolve() if args.scorecard else None
    )

    fragments: list[dict[str, Any]] = []
    for raw in args.auditor_fragment or []:
        p = Path(raw).expanduser().resolve()
        if p.is_file():
            fragments.append(read_fragment_status(p))
        else:
            fragments.append({"path": str(p), "ok": False, "error": "missing"})

    # Auto-pick factory-auditor fragment if none given
    if not fragments:
        auto = memory_path / "fragments" / "t-800-factory-auditor.md"
        if auto.is_file():
            fragments.append(read_fragment_status(auto))

    status = derive_status(args.status, run_gate, doctor, scorecard, fragments)
    report: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "run_id": run_id,
        "generated_at": utc_now(),
        "memory_path": str(memory_path),
        "slug": args.slug,
        "status": status,
        "gates": {
            "run_gate": run_gate,
        },
        "doctor": doctor,
        "scorecard": scorecard,
        "auditor_fragments": fragments,
        "inputs_present": {
            "run_gate": run_gate is not None,
            "doctor": doctor is not None,
            "scorecard": scorecard is not None,
            "auditor_fragments": len(fragments),
        },
    }

    out_dir = memory_path / "runs" / run_id
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "report.json"
        out_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"FAIL: не удалось записать report: {exc}", file=sys.stderr)
        return 1

    if not args.no_telemetry:
        append_telemetry(
            memory_path,
            {
                "event": "run_report",
                "run_id": run_id,
                "status": status,
                "path": str(out_path),
            },
        )

    summary = {
        "ok": True,
        "path": str(out_path),
        "run_id": run_id,
        "status": status,
        "schema_version": SCHEMA_VERSION,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
