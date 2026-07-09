# Fix Pipeline Contract (v1.13.0)

Контракт жизненного цикла **правка существующих** Cursor-артефактов:  
`audit → fix-pack → /t800-fix → machine gate`.  
Без новых research/brain агентов. Связано: `shared/loop-engineering-contract.md`.

## `/t800-fix` vs `/t800-start`

| | `/t800-fix` | `/t800-start` |
|--|--------------|---------------|
| Цель | Правка по **fix-pack** (узкий PATCH) | Создание / крупное изменение с нуля |
| Research | default **SKIP** или **LIGHT**; DEEP только если pack `research_mode: deep` / `need_research: deep` | default DEEP (тест режима) |
| Factory | `mode: PATCH` — только файлы из pack | полный CREATE/UPDATE |
| Вход | `{memory_path}/fix-packs/<slug>.md` | brief / задача пользователя |
| Выход | правки + `t800_run_gate.py` | артефакты + machine gates |

**Закон:** не делать полный fix артефактов из main chat без `Task(t-800-factory)` (когда создаёте/правите agents/skills/commands/rules/hooks).

## Fix-pack path

| Поле | Значение |
|------|----------|
| Путь | `{memory_path}/fix-packs/<slug>.md` |
| Шаблон | `templates/fix-pack.md.template` |
| Источник | вручную / `scripts/t800_audit_to_fixpack.py` после plugin-audit |

### Обязательные секции pack

`goal`, `surface`, `files[]`, `changes[]`, `constraints`, `research_mode`, `success_criteria`.

```yaml
research_mode: skip | light | deep   # default skip|light
need_research: deep                  # опциональный алиас → deep
```

## Оркестрация `/t800-fix`

```text
discover + STATE
→ Read fix-pack
→ research SKIP|LIGHT (DEEP только по pack)
→ brain-lead (обычно 1 domain)
→ factory mode: PATCH (только files[] из pack)
→ python3 scripts/t800_run_gate.py --memory-path …
→ update STATE (Gates / Completed)
```

### Factory PATCH

- Править **только** пути из `files[]` (и явно разрешённые companion-файлы в pack).
- Писать вне списка — **запрещено** без обновления pack и согласия.
- После factory — канонический machine gate: `scripts/t800_run_gate.py`.

## Machine gate

Канон: `python3 scripts/t800_run_gate.py --memory-path "<PATH>" […]`  
См. `shared/loop-engineering-contract.md` (анти–Ralph Wiggum).

«Готово» запрещено при exit ≠ 0 у run_gate (когда gate обязателен для прогона).

## Связанные команды

| Команда | Роль |
|---------|------|
| `/t800-plugin-audit` | карта → опционально `t800_audit_to_fixpack.py` |
| `/t800-audit` | bloat Cursor → сужение через fix-pack / `/t800-fix` |
| `/t800-doctor` | здоровье системы (scripts-only) |
| `/t800-start` | создание, не узкий PATCH |

## Запреты

- DEEP research по умолчанию на `/t800-fix`
- Factory пишет вне `files[]` pack
- Self-PASS без `t800_run_gate.py` / machine evidence
- Новые research/brain агенты ради fix-loop

## Версия

- Введён: 2026-07-09 · T-800 **1.13.0**
- Связанные: `loop-engineering-contract.md`, `plugin-audit-contract.md`, `department-orchestration-contract.md`, `commands/t800-fix.md`
