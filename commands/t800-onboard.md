# /t800-onboard — онбординг для новичков

**Для чата с новичками.** Показывает, что настроено в Cursor (global + local), и что умеет отдел T-800.

**Первый раз в системе?** Сначала **`/t800-bootstrap`** — тот же аудит + предложение глобального правила.

## Запуск

```
Task(t-800-onboard)
```

Передай: workspace root, уровень (новичок), цель, `first_run: true` если это bootstrap.

## Шаг 0 — машинный аудит

```bash
bash scripts/first-run-status.sh
bash scripts/audit-cursor-setup.sh --workspace "."
```

## Что получит новичок

1. **Глобально** (`~/.cursor/`): rules, skills, commands, subagents, plugins
2. **Локально** (проект `.cursor/`): то же для текущего workspace
3. **Память проекта** — `teya-memory`, `plugin-memory`, и т.д.
4. **Возможности T-800** — команды и цепочка
5. **Следующий шаг** — `/t800-bootstrap` или `/t800-start`
6. **Глобальное правило** — предложение установить (только при bootstrap)

## Связанные команды

| Команда | Когда |
|---------|--------|
| `/t800-bootstrap` | Первый запуск + глобальное rule по согласию |
| `/t800-start` | Создать/править subagent, skill, rule |
| `/t-800-operator` | Общие вопросы про Cursor (режимы, MCP) |
| `/t-800-health` | Техдиагностика плагина T-800 |

**Закон:** не отвечай на онбординг из main chat без `Task(t-800-onboard)`.
