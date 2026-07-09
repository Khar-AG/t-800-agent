#!/bin/bash
# Audits T-800 Agent KB coverage against knowledge-base/manifest.json
# Usage: bash scripts/audit-coverage.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
KB="$ROOT/knowledge-base"
REPORT="$KB/COVERAGE-REPORT.md"
MANIFEST="$KB/manifest.json"

if [ ! -f "$MANIFEST" ]; then
  echo "Missing manifest: $MANIFEST"
  exit 1
fi

python3 << PY
import json, re
from datetime import datetime
from pathlib import Path

root = Path("$ROOT")
kb = root / "knowledge-base"
manifest = json.loads((kb / "manifest.json").read_text(encoding="utf-8-sig"))
source_map = {}

for card in kb.rglob("*.md"):
    if "raw" in card.parts or card.name in ("INDEX.md", "CHANGELOG.md", "UPDATE-QUEUE.md", "COVERAGE-REPORT.md", "HEALTH-REPORT.md"):
        continue
    text = card.read_text(encoding="utf-8-sig", errors="ignore")
    for m in re.finditer(r"(?m)^source:\s*(\S+)", text):
        source_map.setdefault(m.group(1), []).append(str(card.relative_to(kb)))

groups = [
    ("Docs/Learn/Help overview", r"https://cursor\.com/ru/(docs|learn|help)$", "INDEX.md"),
    ("Security and run modes", r"https://cursor\.com/docs/agent/security", "04-bezopasnost/"),
    ("Agent modes and tools", r"https://cursor\.com/(docs|help)/agent|https://cursor\.com/help/ai-features", "02-agent-i-rezhimy/ and 09-tools/"),
    ("Rules/Skills/MCP/Subagents", r"https://cursor\.com/(ru/)?docs/(rules|subagents)|https://cursor\.com/docs/(skills|mcp)", "03-kontekst/"),
    ("Cloud and automations", r"https://cursor\.com/docs/cloud-agent|https://cursor\.com/docs/hooks", "10-cloud-automation/"),
    ("Team/admin/integrations", r"https://cursor\.com/docs/account|https://cursor\.com/docs/integrations|https://cursor\.com/docs/bugbot|https://cursor\.com/docs/security-agents|https://cursor\.com/docs/models-and-pricing|https://cursor\.com/help/models-and-usage", "11-team-admin/"),
    ("Advanced developer layer", r"https://cursor\.com/docs/(cli|sdk)|https://cursor\.com/docs/cloud-agent/api", "12-advanced-dev/"),
]

rows = []
explicit = grouped = missing = 0

for url in manifest["pages"]:
    status = "missing"
    coverage = ""
    if url in source_map:
        status = "explicit"
        coverage = ", ".join(source_map[url])
        explicit += 1
    else:
        for label, pattern, card in groups:
            if re.search(pattern, url):
                status = "grouped"
                coverage = f"{label}: {card}"
                grouped += 1
                break
        if status == "missing":
            missing += 1
    rows.append((status, url, coverage))

now = datetime.now().strftime("%Y-%m-%d %H:%M")
lines = [
    "# COVERAGE-REPORT",
    "",
    f"**Generated:** {now}",
    f"**Manifest pages:** {len(rows)}",
    f"**Explicit cards:** {explicit}",
    f"**Grouped coverage:** {grouped}",
    f"**Missing:** {missing}",
    "",
    "## Summary",
    "",
    "| Status | Count | Meaning |",
    "|--------|-------|---------|",
    f"| explicit | {explicit} | URL appears as source: in a card |",
    f"| grouped | {grouped} | URL covered by broader card |",
    f"| missing | {missing} | Needs new card or INDEX mapping |",
    "",
    "## Details",
    "",
    "| Status | URL | Coverage |",
    "|--------|-----|----------|",
]
for status, url, coverage in sorted(rows, key=lambda r: (r[0], r[1])):
    lines.append(f"| {status} | {url} | {coverage} |")

lines += [
    "",
    "## Maintainer next steps",
    "",
    "1. Create cards for missing URLs.",
    "2. Update INDEX.md, CHANGELOG.md, then run install-plugin.sh.",
]

(kb / "COVERAGE-REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"Coverage report: {kb / 'COVERAGE-REPORT.md'}")
print(f"Explicit={explicit} Grouped={grouped} Missing={missing}")
import sys
sys.exit(2 if missing > 0 else 0)
PY
