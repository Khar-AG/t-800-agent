---
title: "Масштабирование 100+ субагентов"
audience: advanced
tier: 4
last_synced: 2026-07-06
---

# Масштабирование плагина с 100+ субагентами

## Принципы

1. **Категории** — не 100 плоских агентов, а 8–15 категорий по 5–15 агентов
2. **Реестр** — `registry/agents-registry.json` + скрипты аудита
3. **Роутинг в два уровня** — category rule → конкретный agent
4. **Узкая специализация** — один агент = одна ответственность
5. **Factory pipeline** — новых агентов только через T-800 Factory

## Структура папок (рекомендация)

```
agents/
  factory/          # отдел создания (опционально подпапки)
  content/
  marketing/
  ...
registry/
  agents-registry.json
  categories.json
rules/
  routing-content.mdc
  routing-factory.mdc
commands/
  t-800-factory.md
scripts/
  validate-agents.ps1
  audit-agent-graph.ps1
  register-agent.ps1
```

> Cursor читает `agents/*.md` на верхнем уровне. Для подпапок — копировать плоским списком в install или держать плоскую структуру с префиксами: `content-seo.md`, `mkt-landing.md`.

## Именование

| Паттерн | Пример |
|---------|--------|
| `{category}-{role}` | `content-seo-meta` |
| `{plugin}-{role}` | `t-800-operator`, `t-800-factory` |
| Без пробелов, kebab-case | `my-agent` |

## description для масштаба

Плохо: `Helps with marketing`

Хорошо: `Writes Russian SEO meta titles 50-60 chars. Use when user asks for meta for landing pages. Do NOT use for full article writing.`

Включайте **Use when** и **Do NOT use when**.

## install-plugin.ps1

Копировать **все** `agents/t-800-*.md`, не хардкодить имена. Индекс: `docs/T-800-AGENTS.md`.

## Валидация в CI

```powershell
.\scripts\validate-agents.ps1
.\scripts\audit-agent-graph.ps1
.\scripts\verify-install.ps1
```

## Когда НЕ добавлять subagent

- Задача < 3 шагов → skill
- Только напоминание → rule
- Явный разовый сценарий → command

## Официальное предупреждение

> «Не создавайте десятки общих субагентов» — cursor.com/ru/docs/subagents

Решение: категории + чёткие description + T-800 Factory.
