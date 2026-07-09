#!/usr/bin/env bash
# t800_loop_state.sh — init/touch STATE.md в memory_path целевого проекта
# Usage:
#   bash scripts/t800_loop_state.sh init --memory-path <PATH>
#   bash scripts/t800_loop_state.sh touch --memory-path <PATH> --stage <name> --message "..."
#
# exit 0 always unless bad args

set -u

HERE="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_ROOT="$(cd "$HERE/.." && pwd)"
TEMPLATE="$PLUGIN_ROOT/templates/STATE.md.template"

usage() {
  echo "Usage:" >&2
  echo "  bash scripts/t800_loop_state.sh init --memory-path <PATH>" >&2
  echo "  bash scripts/t800_loop_state.sh touch --memory-path <PATH> --stage <name> --message \"...\"" >&2
  exit 1
}

CMD="${1:-}"
if [[ -z "$CMD" ]]; then
  usage
fi
shift

MEMORY_PATH=""
STAGE=""
MESSAGE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --memory-path)
      MEMORY_PATH="${2:-}"
      shift 2
      ;;
    --stage)
      STAGE="${2:-}"
      shift 2
      ;;
    --message)
      MESSAGE="${2:-}"
      shift 2
      ;;
    *)
      echo "Неизвестный аргумент: $1" >&2
      usage
      ;;
  esac
done

if [[ -z "$MEMORY_PATH" ]]; then
  echo "Нужен --memory-path" >&2
  usage
fi

mkdir -p "$MEMORY_PATH" 2>/dev/null || true
STATE_FILE="$MEMORY_PATH/STATE.md"
export STATE_FILE TEMPLATE MEMORY_PATH STAGE MESSAGE
export TS
TS="$(date '+%Y-%m-%d %H:%M')"

cmd_init() {
  python3 - <<'PY'
import os
from pathlib import Path

state = Path(os.environ["STATE_FILE"])
template = Path(os.environ.get("TEMPLATE", ""))
ts = os.environ["TS"]
slug = Path(os.environ["MEMORY_PATH"]).name

if state.exists():
    print(f"OK STATE exists: {state}")
    raise SystemExit(0)

if template.is_file():
    text = template.read_text(encoding="utf-8")
    text = text.replace("{{PROJECT_SLUG}}", slug).replace("{{TIMESTAMP}}", ts)
    state.write_text(text, encoding="utf-8")
    print(f"OK STATE created: {state}")
else:
    state.write_text(
        f"""# STATE — {slug}

## Last run

- **Когда:** {ts}
- **Команда:** —
- **Research mode:** —
- **Статус:** in_progress

## In progress

- init: STATE инициализирован

## Completed

## Blockers / Escalated

## Lessons

## Stop conditions

- Repair budget исчерпан (max_repair_attempts = 2)

## Gates

| Gate | Результат |
|------|-----------|
| factory-auditor | n/a |
| validate-agents | n/a |
| audit-agent-graph | n/a |
| verify-install | n/a |
| plugin-audit inventory | n/a |
""",
        encoding="utf-8",
    )
    print(f"OK STATE created (fallback): {state}")
PY
}

cmd_touch() {
  if [[ -z "$STAGE" ]]; then
    echo "Нужен --stage" >&2
    usage
  fi
  if [[ -z "$MESSAGE" ]]; then
    MESSAGE="обновление"
  fi
  export STAGE MESSAGE

  if [[ ! -f "$STATE_FILE" ]]; then
    cmd_init
  fi

  python3 - <<'PY'
import os
import re
from pathlib import Path

path = Path(os.environ["STATE_FILE"])
ts = os.environ["TS"]
stage = os.environ["STAGE"]
msg = os.environ["MESSAGE"]
line = f"- {ts} — `{stage}`: {msg}"

text = path.read_text(encoding="utf-8")
text, _ = re.subn(r"(\*\*Когда:\*\*)\s*.*", rf"\1 {ts}", text, count=1)

completed_hint = (
    stage.lower()
    in ("done", "completed", "factory", "auditor", "plugin-audit", "gate")
    or "готов" in msg.lower()
    or "pass" in msg.lower()
    or "completed" in msg.lower()
)


def insert_after_heading(src: str, heading: str, new_line: str) -> str:
    lines = src.splitlines(keepends=True)
    out = []
    i = 0
    inserted = False
    while i < len(lines):
        out.append(lines[i])
        if not inserted and lines[i].startswith(heading):
            i += 1
            while i < len(lines) and lines[i].strip() == "":
                out.append(lines[i])
                i += 1
            out.append(new_line + "\n")
            inserted = True
            continue
        i += 1
    if not inserted:
        out.append(f"\n{heading}\n\n{new_line}\n")
    return "".join(out)


text = insert_after_heading(text, "## In progress", line)
if completed_hint:
    text = insert_after_heading(text, "## Completed", line)
path.write_text(text, encoding="utf-8")
print(f"OK STATE touched: {path}")
PY
}

case "$CMD" in
  init) cmd_init ;;
  touch) cmd_touch ;;
  *)
    echo "Неизвестная команда: $CMD" >&2
    usage
    ;;
esac

exit 0
