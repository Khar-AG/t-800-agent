---
title: "T-800 Factory — отдел создания субагентов"
audience: advanced
tier: 4
last_synced: 2026-07-06
---

# T-800 Factory — карта раздела

Отдел для проектирования, создания, интеграции и валидации субагентов в масштабируемых плагинах (10–100+ агентов).

## Документы

| Файл | Назначение |
|------|------------|
| [subagent-creation-guide.md](subagent-creation-guide.md) | Полный гайд: формат, frontmatter, вызов, антипаттерны |
| [agent-vs-skill-vs-command.md](agent-vs-skill-vs-command.md) | Когда subagent, skill, rule, command, hook |
| [relationship-graph.md](relationship-graph.md) | Связи, оркестрация, цепочки, реестр |
| [scaling-100-plus.md](scaling-100-plus.md) | Масштабирование: категории, роутинг, валидация |
| [hooks-and-scripts.md](hooks-and-scripts.md) | Hooks, скрипты, install, verify |

## Команда субагентов

| Task | Роль |
|------|------|
| `t-800-factory` | Лид-оркестратор: принимает идею, ведёт пайплайн |
| `t-800-factory-architect` | Спецификация: subagent vs skill, связи, контракт |
| `t-800-factory-builder` | Создаёт файлы агента, command, rule-фрагменты |
| `t-800-factory-integrator` | Реестр, T-800-AGENTS, install, routing |
| `t-800-factory-auditor` | Валидация, граф, антипаттерны |

## Вызов

```
Task(t-800-factory)
```

или slash-команда `/t-800-factory`.

## Официальные ссылки

- https://cursor.com/ru/docs/subagents
- https://cursor.com/docs/skills
- https://cursor.com/ru/docs/context/rules
- https://cursor.com/docs/hooks
