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

## Fixture parity (фикстуры в том же pack)

**Закон:** fix-pack, меняющий обязательные шаги пайплайна (гейты / preflight /
скрипты run-gate — таблица `FIXTURE_PARITY_CRITICAL` в `scripts/t800_run_gate.py`,
шаги по `shared/command-chains.json`), обязан обновить фикстуры
`tests/fixtures/fix-loop/` / `tests/fixtures/command-run/` **в том же pack** —
иначе gate FAIL до релиза, а не в следующем.

- **Machine:** sibling-чек `fixture_parity` в `t800_run_gate.py` (всегда ON, без флага):
  новейший pack в `{memory_path}/fix-packs/` тронул критический файл, а в `files[]`
  нет ни одного пути `tests/fixtures/**` → FAIL с подсказкой (какой шаг тронут,
  какая фикстура его покрывает).
- **Opt-out:** `fixtures_exempt: "<причина>"` в pack — для packs, где шаг
  осознанно не покрыт фикстурами.
- **Шаблон:** `templates/fix-pack.md.template` содержит пункт success_criteria
  про fixture parity — не выкидывать его при заполнении pack.
- **Фикстуры самого чека:** `tests/fixtures/fix-loop/fixture-parity-*` (TeyaPlugin),
  runner `scripts/teya_fixture_parity_fixture_test.py`.

## Machine gate

Канон: `python3 scripts/t800_run_gate.py --memory-path "<PATH>" […]`  
См. `shared/loop-engineering-contract.md` (анти–Ralph Wiggum).

«Готово» запрещено при exit ≠ 0 у run_gate (когда gate обязателен для прогона).

## Per-run manifest (архив прогона)

**Закон:** каждый прогон `/t800-fix` сохраняет архивный манифест
`{memory_path}/run-manifest.archive.<slug>.json` (slug = имя fix-pack без даты).
Корневой `run-manifest.json` принадлежит текущему `/t800-start` прогону — не трогаем.

- **Запись:** `scripts/t800_loop_state.sh touch --stage fix|factory` создаёт/обновляет архив
  (stages[] + files[] из pack) сразу после записи STATE.
- **Финал:** `scripts/t800_run_gate.py` при PASS дописывает шаг `run_gate` (exit code + verdict).
- **Обязательность:** для **серий из ≥2 fix-прогонов подряд** архив обязателен —
  без него teya-run-auditor не может машинно сверить chains релизного окна.
- **Graceful:** старые прогоны без архива — WARN, не FAIL; запись архива best-effort
  и никогда не ломает gate / touch.
- Схема файла: `shared/run-manifest-contract.md`.

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
- Правка обязательных шагов пайплайна без фикстур `tests/fixtures/**` в том же pack (и без `fixtures_exempt`)

## Версия

- Введён: 2026-07-09 · T-800 **1.13.0**
- 2026-08-07: добавлен раздел «Per-run manifest (архив прогона)» (fix-pack `t800-fix-per-run-manifest-2026-08-07`)
- 2026-08-07: добавлен раздел «Fixture parity (фикстуры в том же pack)» (fix-pack `t800-fix-fixture-parity-check-2026-08-07`)
- Связанные: `loop-engineering-contract.md`, `run-manifest-contract.md`, `plugin-audit-contract.md`, `department-orchestration-contract.md`, `commands/t800-fix.md`
