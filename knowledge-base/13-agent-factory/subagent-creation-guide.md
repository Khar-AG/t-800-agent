---
title: "Гайд по созданию субагентов"
source: https://cursor.com/ru/docs/subagents
audience: advanced
tier: 4
last_synced: 2026-07-06
---

# Создание субагентов — полный гайд

## Где лежат файлы

| Область | Путь |
|---------|------|
| Проект | `.cursor/agents/имя.md` |
| Плагин (канон install) | `~/.cursor/plugins/local/t-800-agent/agents/имя.md` |
| User-home (опционально) | `~/.cursor/agents/имя.md` — **не** пишет `install-plugin` с 1.12.1 |
| Исходники плагина | `agents/имя.md` → rsync в `plugins/local/t-800-agent` |

При конфликте имён приоритет у проектных субагентов.

## Формат файла

```markdown
---
name: my-agent
description: >
  Одна чёткая зона ответственности. Use when ... Use proactively when ...
model: inherit
readonly: true
is_background: false
---

# Роль

Ты субагент `my-agent`, вызванный через Task(my-agent).

## Алгоритм
1. ...
2. ...

## Выход
Структурированный отчёт: что сделано, что передать следующему агенту.

## Запреты
- ...
```

## Поля frontmatter

| Поле | Обязательно | Значения | Зачем |
|------|-------------|----------|-------|
| `name` | Да | `kebab-case`, латиница | ID для `Task(name)` и `/name` |
| `description` | **Критично** | 1–3 предложения + триггеры | Agent решает, делегировать ли |
| `model` | Нет | `inherit` или slug модели | Разная «мощность» под задачу |
| `readonly` | Нет | `true` / `false` | `true` = без правок файлов и shell |
| `is_background` | Нет | `true` / `false` | Фоновый vs блокирующий |

## Как вызывать

```text
Task(my-agent)
/ my-agent сделай X
Use the my-agent subagent to ...
```

Субагент **не видит** историю чата — родитель передаёт контекст в prompt.

## Subagent vs Skill vs Rule vs Command

| Артефакт | Когда |
|----------|-------|
| **Subagent** | Долгая задача, изоляция контекста, параллель, независимая проверка |
| **Skill** | Один повторяемый workflow, без отдельного контекста |
| **Rule** | Постоянные стандарты («всегда пиши по-русски») |
| **Command** | Явный slash-вызов сценария (`/t-800-factory`) |
| **Hook** | Реакция на событие (sessionStart, subagentStop, afterFileEdit) |

## Паттерны

### Verifier (проверка)
`readonly: true`, description: «Use after tasks marked done».

### Orchestrator (лид)
Координирует цепочку: architect → builder → integrator → auditor.

### Specialist (узкий эксперт)
Одна зона: «только SEO-мета», «только валидация registry».

## Антипаттерны (из официальной docs)

- Расплывчатые description («помогает с кодом»)
- Промпт на 2000+ слов
- 50+ агентов без категорий и роутинга
- Дублирование: subagent там, где хватит skill
- Skill вместо subagent для mentor-ролей с readonly

## Чеклист перед публикацией

- [ ] `name` уникален в реестре
- [ ] `description` содержит конкретные триггеры
- [ ] Промпт < 500 строк, структурирован
- [ ] `readonly` соответствует роли
- [ ] Запись в `registry/agents-registry.json`
- [ ] Строка в `docs/T-800-AGENTS.md`
- [ ] Routing rule обновлён (если нужна автоделегация)
- [ ] `scripts/validate-agents.ps1` проходит
- [ ] `scripts/audit-agent-graph.ps1` без ошибок

## Официальная ссылка

https://cursor.com/ru/docs/subagents
