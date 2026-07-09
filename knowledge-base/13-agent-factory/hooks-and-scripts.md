---
title: "Hooks и скрипты для субагентов"
source: https://cursor.com/docs/hooks
audience: advanced
tier: 4
last_synced: 2026-07-06
---

# Hooks и скрипты

## Когда hook, а не subagent

| Hook | Сценарий |
|------|----------|
| `subagentStart` | Разрешить/запретить запуск определённых Task |
| `subagentStop` | Цепочка: после auditor → уведомить integrator |
| `sessionStart` | Проверить health плагина |
| `afterFileEdit` | Авто-валидация нового `agents/*.md` |
| `beforeSubmitPrompt` | Блок секретов в промптах |

## Расположение

| Тип | Путь |
|-----|------|
| Проект | `.cursor/hooks.json`, `.cursor/hooks/*` |
| Пользователь | `~/.cursor/hooks.json` |

## Пример: валидация после правки агента

```json
{
  "version": 1,
  "hooks": {
    "afterFileEdit": [
      {
        "command": ".cursor/hooks/validate-agent-edit.ps1",
        "matcher": "tool == \"edit\" && file matches \"agents/.*\\.md\""
      }
    ]
  }
}
```

## Скрипты T-800 Factory

| Скрипт | Назначение |
|--------|------------|
| `install-plugin.ps1` | Деплой в `~/.cursor/` |
| `verify-install.ps1` | Проверка установки |
| `validate-agents.ps1` | Frontmatter, name, description |
| `audit-agent-graph.ps1` | Реестр vs файлы, связи |
| `register-agent.ps1` | Добавить запись в registry |

## Skill со скриптами

Skill может включать `scripts/` — Agent запускает их по инструкции в SKILL.md. Для maintainer-операций (sync, audit) — skill с `disable-model-invocation: true`.

## Безопасность hooks

- Нет удаления без backup
- Нет секретов в hook-файлах
- `failClosed` только когда критично

## Ссылка

https://cursor.com/docs/hooks
