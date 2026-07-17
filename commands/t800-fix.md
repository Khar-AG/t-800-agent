# /t800-fix — правка по fix-pack (PATCH)

**Зачем:** узкая правка существующих agents / skills / commands / rules / hooks по pack — без полного DEEP `/t800-start`.

Контракт: `shared/fix-pipeline-contract.md`.  
Loop / STATE / gates: `shared/loop-engineering-contract.md`.

## Закон

Не делай полный fix Cursor-артефактов из main chat без `Task(t-800-factory)`, когда создаёшь или правишь agents/skills/commands/rules/hooks.  
Factory в режиме **PATCH** — только файлы из fix-pack.

## Шаги

### 0. Discovery + STATE

```bash
bash scripts/discover-target-project.sh --workspace "<WORKSPACE>" [--plugin-root "<PLUGIN_ROOT>"]
bash scripts/t800_loop_state.sh init --memory-path "<memory_path>"
# Read STATE.md
```

### 1. Read fix-pack

Путь: `{memory_path}/fix-packs/<slug>.md`  
(шаблон: `templates/fix-pack.md.template`; из аудита: `scripts/t800_audit_to_fixpack.py`)

**Batch из loop:** если есть `{memory_path}/loop-queue.md` (после `/t800-loop`) — возьми пункты **Open** или сгенерируй packs (только `status=open` + LOW):

```bash
python3 scripts/t800_lessons_to_fixpack.py --memory-path "<memory_path>" --lessons "<run_id|path>"
```

Если pack нет — спроси slug / создай draft из аудита или queue, не угадывай `files[]`.

### 2. Research (SKIP | LIGHT)

Default: **SKIP** или **LIGHT**, если в pack конкретные пути.  
**DEEP** только если `research_mode: deep` / `need_research: deep`.

```
# SKIP → сразу brain
# LIGHT → Task(t-800-research-lead) с research_mode: light
```

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "research" --message "skip|light|deep"
```

### 3. Brain

```
Task(t-800-brain-lead)
```

Обычно 1 domain. В `brief_for_factory` укажи: `mode: PATCH`, путь fix-pack, `files[]`.

### 4. Factory PATCH

```
Task(t-800-factory)
```

Передай: `mode: PATCH`, fix-pack path, список файлов, `success_criteria`.  
Factory **не** пишет вне `files[]`.

### 5. Run gate

```bash
python3 scripts/t800_run_gate.py --memory-path "<memory_path>" \
  [--require-validate] [--plugin-root "<PLUGIN_ROOT>"] \
  [--require-plugin-audit-out "<DIR>"]
```

Exit ≠ 0 → не «готово»; repair ≤2 (`loop-engineering-contract`).

### 5a. Lesson lifecycle — закрытие (loop packs)

После **run_gate PASS** для pack из loop:

```bash
python3 scripts/t800_lessons_to_fixpack.py --memory-path "<memory_path>" --lessons "<run_id|path>" \
  --mark-applied "<lesson_id>" --applied-in "<plugin_version>"
```

HITL **reject** (не применять pack):

```bash
python3 scripts/t800_lessons_to_fixpack.py --memory-path "<memory_path>" --lessons "<run_id|path>" \
  --mark-rejected "<lesson_id>" --closed-reason "<причина>"
```

Generate пишет только open; закрытые → `skipped_closed`.

### 6. STATE

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "fix" --message "run_gate pass|fail"
```

Обнови Completed / Gates / Lessons.

## vs другие команды

| | `/t800-fix` | `/t800-start` | `/t800-audit` | `/t800-plugin-audit` | `/t800-doctor` |
|--|--------------|---------------|---------------|----------------------|----------------|
| Цель | PATCH по pack | создать / крупно | bloat Cursor | карта плагина | здоровье (scripts) |
| Research | SKIP/LIGHT | DEEP default | — | — | — |
| Factory | PATCH | CREATE | нет | нет | нет |
| Gate | `t800_run_gate.py` | validate/auditor | диалог | inventory.json | doctor report |

## Связанные

| Команда | Когда |
|---------|--------|
| `/t800-plugin-audit` | сначала карта → `t800_audit_to_fixpack` |
| `/t800-loop` | lessons / `loop-queue.md` → `t800_lessons_to_fixpack` → этот PATCH |
| `/t800-start` | нет pack / новое с нуля |
| `/t800-doctor` | проверить здоровье до/после |
