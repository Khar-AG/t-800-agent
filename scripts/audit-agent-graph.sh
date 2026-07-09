#!/bin/bash
# Audits registry/agents-registry.json against agents/ files and graph symmetry
# Usage: bash scripts/audit-agent-graph.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
REGISTRY="$ROOT/registry/agents-registry.json"
AGENTS_DIR="$ROOT/agents"
failed=0

if [ ! -f "$REGISTRY" ]; then
  echo "Registry not found: $REGISTRY"
  exit 1
fi

python3 << PY
import json, sys
from pathlib import Path

root = Path("$ROOT")
registry = json.loads((root / "registry/agents-registry.json").read_text(encoding="utf-8-sig"))
agents = {a["id"]: a for a in registry["agents"]}
failed = 0

for entry in registry["agents"]:
    fp = root / entry["file"]
    if not fp.exists():
        print(f"FAIL Registry file missing: {entry['id']} -> {entry['file']}")
        failed += 1
    else:
        print(f"OK   file exists: {entry['id']}")

for md in (root / "agents").glob("t-800-*.md"):
    aid = md.stem
    if aid not in agents:
        print(f"WARN Agent file not in registry: {aid}")

for entry in registry["agents"]:
    eid = entry["id"]
    for called in entry.get("calls", []):
        if called not in agents:
            print(f"FAIL {eid}.calls -> unknown '{called}'")
            failed += 1
            continue
        if eid not in agents[called].get("calledBy", []):
            print(f"FAIL Asymmetric: {eid} calls {called} but {called}.calledBy lacks {eid}")
            failed += 1
    for caller in entry.get("calledBy", []):
        if caller == "main-agent":
            continue
        if caller not in agents:
            print(f"FAIL {eid}.calledBy -> unknown '{caller}'")
            failed += 1
            continue
        if eid not in agents[caller].get("calls", []):
            print(f"FAIL Asymmetric: {caller} should call {eid}")
            failed += 1

if failed:
    print(f"Agent graph audit failed: {failed} problem(s).")
    sys.exit(1)
print(f"Agent graph audit passed ({len(registry['agents'])} registry entries).")
PY
