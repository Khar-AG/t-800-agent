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

  # Per-run архив манифеста: только для стадий fix|factory (fix-pipeline-contract).
  # Корневой run-manifest.json не трогаем — он принадлежит текущему /t800-start прогону.
  if [[ "$STAGE" == "fix" || "$STAGE" == "factory" ]]; then
    python3 - <<'PY'
import json
import os
import re
from pathlib import Path

memory = Path(os.environ["MEMORY_PATH"])
stage = os.environ["STAGE"]
msg = os.environ.get("MESSAGE", "")
ts = os.environ["TS"]

packs_dir = memory / "fix-packs"
packs = []
if packs_dir.is_dir():
    packs = sorted(
        packs_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True
    )
if not packs:
    # Graceful: прогоны без fix-pack (например чистый /t800-start) — пропуск
    print("OK archive: нет fix-packs — пропуск")
    raise SystemExit(0)

pack = packs[0]
# slug = имя fix-pack без даты вида -YYYY-MM-DD на конце
slug = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", pack.stem)
archive = memory / f"run-manifest.archive.{slug}.json"

# files[] из секции «### files» pack-а (строки вида: - `path`)
files = []
in_files = False
for line in pack.read_text(encoding="utf-8", errors="replace").splitlines():
    if re.match(r"^#{2,3}\s*files\b", line, re.IGNORECASE):
        in_files = True
        continue
    if in_files and re.match(r"^#{2,3}\s", line):
        break
    if in_files:
        m = re.match(r"^-\s*`([^`]+)`", line.strip())
        if m:
            files.append(m.group(1))

low = msg.lower()
if "fail" in low or "blocker" in low:
    verdict = "fail"
elif "pass" in low or "готов" in low or "ok" in low:
    verdict = "pass"
else:
    verdict = "recorded"

data = {}
if archive.is_file():
    try:
        loaded = json.loads(archive.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            data = loaded
    except (OSError, json.JSONDecodeError):
        data = {}

data.setdefault("run_id", slug)
data["slug"] = slug
data["fix_pack"] = f"fix-packs/{pack.name}"
data.setdefault("created_at", ts)
data["updated_at"] = ts
data.setdefault("fragment", "fragments/t-800-factory.md")
data.setdefault("run_gate", None)
if files:
    data["files"] = files

# одна запись на стадию: повторный touch заменяет прежнюю
stages = [
    s
    for s in data.get("stages", [])
    if isinstance(s, dict) and s.get("stage") != stage
]
stages.append({"stage": stage, "ts": ts, "verdict": verdict, "message": msg})
data["stages"] = stages

archive.write_text(
    json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"OK archive manifest: {archive}")
PY
  fi
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
