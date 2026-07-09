# Loop Engineering Contract (v1.13.0)

Машиночитаемый контракт минимального loop вокруг существующих команд T-800.  
Идеи: Habr Loop Engineering / Osmani / Anthropic evaluator-optimizer.  
**Без новых research/brain агентов.**

## Цель

Замкнуть цикл «сделал → проверил machine gate → починил (бюджет) → STATE» вокруг `/t800-start`, `/t800-plugin-audit` и factory-auditor — без бесконечного self-PASS (анти–Ralph Wiggum).

## Четыре условия (перед тяжёлым loop / DEEP)

Перед DEEP research или repair-loop должны выполняться **все** четыре:

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

Перед `Task(t-800-research-lead)` Директор выбирает режим по **тесту**, не только по фразе пользователя:

| Режим | Когда |
|-------|--------|
| **DEEP** | default для нового домена / «изучи свежее» / сложный multi-source |
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
| Старт `/t800-start`, `/t800-plugin-audit` | `init` + **Read** `STATE.md` |
| После каждого отдела | `touch` + progress line |
| Конец прогона | Completed / Lessons / Gates; не «готово» без machine evidence |

Канон STATE чужого плагина — в **его** `memory_path`. Писать STATE чужого плагина в `t-800-memory/` как канон **запрещено** (кроме `profile: self-t800`).

## Machine gate (анти–Ralph Wiggum)

**Каноническая команда gate (v1.13):**

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
  run_gate: exit_0          # scripts/t800_run_gate.py (канон)
  machine_scripts: exit_0   # или skip если не применимо
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

## Минимальный MVP loop

| Слой | Что |
|------|-----|
| Automation | slash command (`/t800-start`, `/t800-fix`, `/t800-plugin-audit`, `/t800-doctor`) |
| Skill / KB | существующие (не community auto-install) |
| STATE | `{memory_path}/STATE.md` |
| Gate | `scripts/t800_run_gate.py` (канон) + validate/audit по флагам |

## Запреты

- Новые research/brain агенты ради loop  
- Писать STATE чужого плагина в `t-800-memory` как канон (только self-t800)  
- Автоустановка community skills  
- Loop на архитектуре / платежах **без человека**  
- «Готово» при FAIL auditor или machine scripts  
- Бесконечный repair после бюджета 2  

## Связанные

- `shared/department-orchestration-contract.md`  
- `shared/fix-pipeline-contract.md`  
- `shared/project-memory-contract.md`  
- `shared/t-800-factory-contract.md`  
- `templates/STATE.md.template`  
- `scripts/t800_loop_state.sh`  
- `scripts/t800_run_gate.py`  

## Версия

- Обновлён: 2026-07-09 · T-800 **1.13.0** (канон `t800_run_gate.py`, `/t800-fix`)  
- Введён: 2026-07-09 · T-800 **1.12.0**
