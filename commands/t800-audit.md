# /t800-audit — разбор системы Cursor

**Зачем:** понять, какие rules/skills/commands/agents реально нужны, а какие только едят контекст.

## Запуск

```
Task(t-800-system-auditor)
```

Передай: workspace root, уровень (новичок / опытный), фокус (rules / всё).

## Шаг 0 — машинный аудит

```bash
bash scripts/audit-cursor-setup.sh --workspace "."
bash scripts/audit-cursor-bloat.sh "."
```

## Что получит человек

1. Карта: global vs local (rules, skills, commands, agents, plugins)
2. Оценка «жира»: `alwaysApply` + размер → high/medium/low
3. **Диалог:** по каждому рискованному правилу — «оставить / сузить / удалить / что это?»
4. Итоговая таблица рекомендаций (без автоудаления)

## После решений (keep / narrow / remove)

Если нужно **сузить** rules/skills (не удалять молча):

1. Оформи `{memory_path}/fix-packs/<slug>.md` (шаблон `templates/fix-pack.md.template`) с конкретными `files[]`.
2. Запусти **`/t800-fix`** — PATCH через factory, не полный `/t800-start`.

Для карты одного плагина → `/t800-plugin-audit` → `t800_audit_to_fixpack.py` → `/t800-fix`.

## Связанные команды

| Команда | Когда |
|---------|--------|
| `/t800-onboard` | Быстрый обзор «что установлено» без глубокого разбора |
| `/t800-fix` | Сузить/поправить артефакты по fix-pack |
| `/t800-doctor` | Scripts-only здоровье |
| `/t800-start` | Создать новый rule/skill после аудита |
| `/t800-update` | Обновить плагин T-800 до новой версии |
| `/t-800-operator` | Общие вопросы про Cursor |

**Закон:** не отвечай на полный audit из main chat без `Task(t-800-system-auditor)`.
