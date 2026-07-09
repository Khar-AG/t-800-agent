#!/bin/bash
# Validates all subagent files in agents/
# Usage: bash scripts/validate-agents.sh

set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/.." && pwd)"
AGENTS_DIR="$ROOT/agents"
failed=0
checked=0

for f in "$AGENTS_DIR"/t-800-*.md; do
  [ -f "$f" ] || continue
  checked=$((checked + 1))
  base=$(basename "$f" .md)

  if ! head -1 "$f" | grep -q '^---'; then
    echo "FAIL $base: missing YAML frontmatter"
    failed=$((failed + 1))
    continue
  fi

  name=$(grep -E '^name:' "$f" | head -1 | sed 's/^name:[[:space:]]*//' | tr -d '\r')
  if [ -z "$name" ]; then
    echo "FAIL $base: missing name in frontmatter"
    failed=$((failed + 1))
    continue
  fi
  if [ "$name" != "$base" ]; then
    echo "FAIL $base: name '$name' does not match filename"
    failed=$((failed + 1))
    continue
  fi
  if ! grep -q 'description:' "$f"; then
    echo "FAIL $base: missing description"
    failed=$((failed + 1))
    continue
  fi

  lines=$(wc -l < "$f" | tr -d ' ')
  if [ "$lines" -gt 200 ]; then
    echo "WARN $base: prompt is long ($lines lines)"
  fi

  echo "OK   $base ($name)"
done

if [ "$checked" -eq 0 ]; then
  echo "No agent files found in $AGENTS_DIR"
  exit 1
fi

if [ "$failed" -gt 0 ]; then
  echo "Agent validation failed: $failed problem(s)."
  exit 1
fi

echo "Agent validation passed ($checked agents)."
