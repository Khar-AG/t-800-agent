# T-800 Agent — реестр Task-субагентов (36)

Плагин: **T-800 Agent** v1.13.0 — `/t800-fix` + `/t800-doctor` + `t800_run_gate.py` + fix-pack из audit + loop engineering + `/t800-plugin-audit` + DEEP research + factory (без новых leaf-агентов).

## Сценарий старта (4 шага)

См. **`docs/СЦЕНАРИЙ-СТАРТА.md`**. Обновление со старой версии: **`docs/ОБНОВЛЕНИЕ.md`**.

## Первый запуск

**`/t800-bootstrap`** — аудит → возможности → глобальное rule по согласию.

## Обязательная цепочка (создание артефактов)

```
intake-clarifier?
  → scout
  → research-lead DEEP (strategist → specialists → synthesizer)
  → prompt-craft?
  → brain-lead
  → factory → prompt-auditor → auditor
```

## Команды

| Команда | Назначение |
|---------|------------|
| `/t800-bootstrap` | Первый запуск |
| `/t800-onboard` | Карта системы |
| **`/t800-doctor`** | Здоровье (scripts-only) |
| **`/t800-audit`** | Интерактивный разбор rules/skills (что удалить) |
| **`/t800-plugin-audit`** | Карта одного плагина → `{memory}/audits/` → fix-pack |
| **`/t800-fix`** | Правка по fix-pack (PATCH + run_gate) |
| **`/t800-update`** | Обновить плагин с zip / папки |
| `/t800-start` | Создать артефакт |
| `/t-800-health` | Диагностика |

## Mentor / System

| Task | Роль |
|------|------|
| `t-800-onboard` | Онбординг |
| `t-800-system-auditor` | Разбор bloat / keep-narrow-remove |
| `t-800-plugin-auditor` | Аудит одного plugin-root (inventory/graph/orphans) |
| `t-800-operator` | Наставник Cursor |

Полный roster research/brains/factory — `registry/agents-registry.json`.
