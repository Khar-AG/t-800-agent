# /t800-loop — semi-manual Loop Engineering batch

**Зачем:** после прогона (report + lessons) — HITL-очередь в `{memory_path}/loop-queue.md`,
затем batch `/t800-fix` по fix-packs. **Не** автопродолжение через stop/followup.

Контракт: `shared/loop-engineering-contract.md` (v2).  
Схема lessons: `shared/lesson-schema-contract.md`.

## 0. Discovery + pause

```bash
bash scripts/discover-target-project.sh --workspace "<WORKSPACE>" [--plugin-root "<PLUGIN_ROOT>"]
bash scripts/t800_loop_state.sh init --memory-path "<memory_path>"
```

Если существует `{memory_path}/.loop-paused` — **стоп**. Сообщи пользователю; не зови conductor.

## 1. Первая обязанность — conductor

```
Task(t-800-loop-conductor)
```

Передай полный контекст:

- `memory_path`
- `plugin_root`
- `run_id` (если известен; иначе conductor берёт последний run)
- цель пользователя / HITL-заметки

Если `Task(t-800-loop-conductor)` недоступен:

```
Task(generalPurpose)
```

Промпт: полное содержимое `agents/t-800-loop-conductor.md` из плагина.

## 2. Материализация loop-queue

Conductor **readonly** — не пишет `loop-queue.md`. Родитель:

```bash
# stdin = JSON handoff (queue_patch) от conductor
python3 scripts/t800_loop_queue_write.py --memory-path "<memory_path>"
```

Путь: `{memory_path}/loop-queue.md`.

## 3. Опционально — classify / fixpack (только LOW)

Если lessons ещё без `risk_class` или нужен refresh:

```bash
python3 scripts/t800_risk_classifier.py --patch-file "<lesson.json>" --memory-path "<memory_path>"
```

Для **LOW только** (после classifier, не LLM):

```bash
python3 scripts/t800_lessons_to_fixpack.py --memory-path "<memory_path>" --lessons "<run_id|path/to/lessons.json>"
```

MEDIUM / HIGH / BLOCK_CANDIDATE — только после явного HITL, не silent batch.

## 4. Дальше — /t800-fix

После HITL по очереди:

```
/t800-fix
```

Пакеты: `{memory_path}/fix-packs/<slug>.md`.  
Gate: `python3 scripts/t800_run_gate.py --memory-path "<memory_path>"`.

## Bootstrap observe (не auto-continue)

`sessionStart` → `hooks/t-800-session-bootstrap.sh` → `scripts/t800-loop-dispatcher.sh`
(**fail-open**, observe FS, уважает `.loop-paused`).

Это **не** запуск `/t800-loop` и **не** auto-reprompt. Cloud: sessionStart может
не сработать — вручную `/t800-update` + `/t800-loop`.

## Anti-Ralph

Запрещено в этой команде:

- stop + `followup_message` автопродолжение
- `subagentStop` followup как движок цикла
- авто-reprompt без явного `/t800-loop`
- назначение `risk_class: LOW` агентом

## Связанные

| Команда | Когда |
|---------|--------|
| `/t800-fix` | PATCH batch по pack из очереди |
| `/t800-start` | CREATE / крупно — не этот путь |
| `/t800-doctor` | здоровье scripts до/после |
| `/t800-update` | cloud / без sessionStart |
