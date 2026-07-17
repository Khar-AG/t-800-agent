# Loop Engineering Contract (v2.0.0)

Машиночитаемый контракт loop вокруг команд T-800.  
Идеи: Habr Loop Engineering / Osmani / Anthropic evaluator-optimizer.  
**Без новых research/brain агентов.** Semi-manual batch — не Ralph Wiggum.

## Цель

Замкнуть цикл:

```
report → lessons → classify → fixpack → /t800-loop → /t800-fix
```

вокруг `/t800-start`, `/t800-plugin-audit`, factory-auditor и machine gates —  
с HITL, без бесконечного self-PASS.

## Полный цикл (v2)

| Шаг | Артефакт / команда |
|-----|-------------------|
| 1. Report | `python3 scripts/t800_run_report.py` → `{memory}/runs/<id>/report.json` |
| 2. Lessons | `python3 scripts/t800_lessons_export.py` → `lessons.json` (`lesson-schema-contract`) |
| 3. Classify | **только** `python3 scripts/t800_risk_classifier.py` → `risk_class` |
| 4. Fixpack | `t800_lessons_to_fixpack.py` (LOW; иначе после HITL) → `fix-packs/` |
| 5. Queue | `/t800-loop` → `Task(t-800-loop-conductor)` → `t800_loop_queue_write.py` |
| 6. Patch | `/t800-fix` по pack + `t800_run_gate.py` |

Пути:

| Ключ | Путь |
|------|------|
| loop_queue | `{memory_path}/loop-queue.md` |
| loop_dir | `{memory_path}/loop/` |
| events_jsonl | `{memory_path}/loop/events.jsonl` |
| paused | `{memory_path}/.loop-paused` |
| policy | `{memory_path}/loop-policy.json` |

## Фазы: Prove → Harden → Automate

| Фаза | Содержание |
|------|------------|
| **Prove** | fixtures `tests/fixtures/loop/`; `t800_golden_check.py` (sha256); classifier **zero false LOW** (denylist wins); `report.json` + `lessons.json` schema-valid на self-t800 |
| **Harden** | fail-open dispatcher + bootstrap; `.loop-paused`; Anti-Ralph out-list; `before-artifact-edit` WARN-only; `risk_class` script-only |
| **Automate** | `bootstrap_invoke` observe (ONE sessionStart); `/t800-loop` semi-manual batch после HITL — **не** stop+followup |

### Daily budget (после Prove)

После **5 зелёных** semi-manual batch (`/t800-loop` → `/t800-fix` + gate pass):

- daily budget **N = 3** автоматических LOW-кандидатов в день (policy).
- **auto-LOW всё ещё OFF по умолчанию**, пока Prove не закрыт (fixtures + zero false LOW + golden).
- Включение auto-LOW — явное решение в `{memory_path}/loop-policy.json`, не default плагина.

## Anti-Ralph OUT list

**Запрещено** как движок цикла:

1. `stop` + `followup_message` автопродолжение  
2. `subagentStop` + `followup_message` как движок цикла  
3. `loop_limit: null`  
4. авто-reprompt без явного `/t800-loop`  
5. hard-deny (exit 2) в loop/observe path  
6. LLM/агент назначает `risk_class: LOW`  
7. второй `sessionStart` entry в `hooks.json`  
8. `continue: false` / guaranteed `additional_context` как control plane  
9. копии ralph-loop / babysitter stop-loop  

## bootstrap_invoke

```
sessionStart (hooks.json: РОВНО ОДИН)
  → hooks/t-800-session-bootstrap.sh
       → t800-auto-version-check (--json, fail-open)
       → first-run hint (optional)
       → scripts/t800-loop-dispatcher.sh (fail-open, observe FS, .loop-paused)
       → stdout ONE JSON, exit 0
```

Dispatcher **не** отдельный sessionStart. Observe ≠ auto-continue.  
Cloud: sessionStart может не бежать → вручную `/t800-update` + `/t800-loop`.

### .loop-paused

Файл `{memory_path}/.loop-paused` → dispatcher и `/t800-loop` **не** крутят очередь.  
Это **kill switch** loop (pause = stop): observe/dispatcher и semi-manual batch уважают файл; снять pause — удалить `.loop-paused` после разбора.

## Revert protocol (golden FAIL)

Когда `python3 scripts/t800_golden_check.py` завершается с **exit ≠ 0**:

| Запрещено | Разрешено |
|-----------|-----------|
| Объявлять «готово» | Остановить loop-batch; разобрать diff / missing paths |
| Включать auto-LOW в `loop-policy.json` | Держать auto-LOW **OFF** |
| Крутить `/t800-fix` batch «из golden-пути» как будто Prove зелёный | Чинить причину FAIL, затем снова golden |

**Восстановление (после явного HITL maintainer):**

1. Вернуть файлы из last known good: `git checkout` / tag до изменения **или**
2. Пересчитать hashes только через `--write-hashes` (не молча, не агентом без HITL).

**Опционально до разбора:** `touch {memory_path}/.loop-paused` — тот же kill switch, что в секции `.loop-paused` выше (dispatcher + `/t800-loop` стоп).

Prove считается закрытым только при golden exit 0 **и** classifier zero false LOW на fixtures.

## risk_class

| | |
|--|--|
| Owner | `scripts/t800_risk_classifier.py` |
| Labels | `LOW`, `MEDIUM`, `HIGH`, `BLOCK_CANDIDATE` (+ `unset` до classify) |
| Rule | denylist wins |
| Forbid | LLM / agent assigns LOW |

Схема урока: `shared/lesson-schema-contract.md`.

## Материализация queue

**Prefer:** readonly conductor → JSON handoff →

```bash
python3 scripts/t800_loop_queue_write.py --memory-path "<memory_path>"
# stdin = handoff JSON
```

→ `{memory_path}/loop-queue.md`.  
Fallback: шаги родителя в `/t800-loop`. Агент **никогда** не Write в queue.

## Универсальность

Только discovery + `{memory_path}` + profiles.  
**Запрещено** вшивать business logic чужого плагина (Teya/client) в loop-промпты/скрипты.

## Четыре условия (перед тяжёлым loop / DEEP)

Перед DEEP research или repair-loop — **все** четыре:

| # | Условие | Иначе |
|---|---------|--------|
| 1 | Задача **повторяется** или **сложная** | Один точный промпт, без loop |
| 2 | Есть **machine gate** (скрипт / validate / verify, exit code) | Не объявлять «готово» по словам агента |
| 3 | Бюджет: `max_repair_attempts = 2` | После 2 FAIL → escalate пользователю |
| 4 | Агент может **читать файлы** + **запускать scripts** | Иначе только отчёт / ручной шаг |

```yaml
loop_preflight:
  repeating_or_complex: true|false
  machine_gate_exists: true|false
  max_repair_attempts: 2
  can_read_and_run_scripts: true|false
  heavy_loop_allowed: # all four true
```

## Research mode test (Директор)

Перед `Task(t-800-research-lead)` — режим по **тесту**, не только по фразе:

| Режим | Когда |
|-------|--------|
| **DEEP** | default: новый домен / «изучи свежее» / сложный multi-source |
| **LIGHT** | мелкий твик, известный паттерн, «быстрый обзор» |
| **SKIP** | «только KB», offline, тривиальный copy |

```yaml
research_mode_test:
  new_domain_or_fresh: → DEEP
  known_pattern_tweak: → LIGHT
  kb_only_or_trivial: → SKIP
  user_phrase_override: # «без интернета» → SKIP; «быстрый обзор» → LIGHT
```

Связано: `shared/deep-research-contract.md`, `shared/department-orchestration-contract.md`.

## STATE.md

| Поле | Значение |
|------|----------|
| Путь | `{memory_path}/STATE.md` |
| Где | **Целевой проект** (не `knowledge-base/` T-800) |
| Шаблон | `templates/STATE.md.template` |
| Скрипт | `bash scripts/t800_loop_state.sh` |

### Секции

1. Last run  
2. In progress  
3. Completed  
4. Blockers / Escalated  
5. Lessons  
6. Stop conditions  
7. Gates  

### Обязанности Директора

| Когда | Действие |
|-------|----------|
| Старт `/t800-start`, `/t800-plugin-audit`, `/t800-loop` | `init` + **Read** `STATE.md` |
| После каждого отдела | `touch` + progress line |
| Конец прогона | Completed / Lessons / Gates; не «готово» без machine evidence |

Канон STATE чужого плагина — в **его** `memory_path`. Писать STATE чужого плагина в `t-800-memory/` как канон **запрещено** (кроме `profile: self-t800`).

## Machine gate (анти–Ralph Wiggum)

**Каноническая команда gate:**

```bash
python3 scripts/t800_run_gate.py --memory-path "<memory_path>" \
  [--require-validate] [--plugin-root "<PLUGIN_ROOT>"] \
  [--require-plugin-audit-out "<DIR>"]
```

Проверяет `STATE.md`; опционально `inventory.json` и `validate-agents.sh`.  
Используется в конце `/t800-fix` и как единый machine gate прогона.

«Готово» **запрещено**, если:

| Контекст | Условие FAIL |
|----------|--------------|
| Factory / fix | `factory-auditor` `status` ≠ `ok` |
| Factory / fix | `t800_run_gate.py` exit ≠ 0 (когда обязателен) |
| Factory | `validate-agents` / `audit-agent-graph` / `verify-install` (когда применимо) ≠ exit 0 |
| Plugin-audit | нет `inventory.json` **или** `t800_plugin_audit.py` fail |

**Self-PASS без скриптов = запрещён.**  
`ralph_wiggum_risk: true` если в отчёте нет machine evidence.

```yaml
done_gate:
  factory_auditor: ok
  run_gate: exit_0
  machine_scripts: exit_0
  plugin_audit_inventory: present  # для /t800-plugin-audit
```

Правки по pack: `shared/fix-pipeline-contract.md` (`/t800-fix`).

## Repair budget

| Попытка | Действие |
|---------|----------|
| 0 | Первый `factory-auditor` |
| 1–2 | FAIL → fix (builder/integrator) → re-audit |
| 3-й FAIL | **Escalate** пользователю — не крутить бесконечно |

```yaml
repair:
  max_repair_attempts: 2
  on_exhaust: escalate_user
```

## Минимальный MVP loop (слои)

| Слой | Что |
|------|-----|
| Automation | slash: `/t800-start`, `/t800-fix`, `/t800-loop`, `/t800-plugin-audit`, `/t800-doctor` |
| Conductor | `Task(t-800-loop-conductor)` readonly + `t800_loop_queue_write.py` |
| Skill / KB | существующие (не community auto-install) |
| STATE | `{memory_path}/STATE.md` |
| Gate | `scripts/t800_run_gate.py` + validate/audit по флагам |
| Observe | bootstrap → `t800-loop-dispatcher.sh` fail-open |

## Запреты

- Новые research/brain агенты ради loop  
- Писать STATE чужого плагина в `t-800-memory` как канон (только self-t800)  
- Автоустановка community skills  
- Loop на архитектуре / платежах **без человека**  
- «Готово» при FAIL auditor или machine scripts  
- Бесконечный repair после бюджета 2  
- Всё из Anti-Ralph OUT list  
- Второй `sessionStart` / agent Write в `loop-queue.md`  

## Связанные

- `shared/lesson-schema-contract.md`  
- `shared/department-orchestration-contract.md`  
- `shared/fix-pipeline-contract.md`  
- `shared/project-memory-contract.md`  
- `shared/t-800-factory-contract.md`  
- `templates/STATE.md.template`  
- `templates/loop-policy.json.template`  
- `scripts/t800_loop_state.sh`  
- `scripts/t800_run_gate.py`  
- `scripts/t800_risk_classifier.py`  
- `scripts/t800_loop_queue_write.py`  
- `commands/t800-loop.md`  
- `agents/t-800-loop-conductor.md`  

## Версия

- Обновлён: 2026-07-17 · Loop Engineering **2.0.0** (+ Revert protocol golden FAIL / `.loop-paused` kill switch)  
- Предыдущий канон gate: 2026-07-09 · T-800 **1.13.0** (`t800_run_gate.py`, `/t800-fix`)  
- Введён MVP: 2026-07-09 · T-800 **1.12.0**
