---
title: "Subagents — узкие помощники"
source: https://cursor.com/ru/docs/subagents
audience: beginner
tier: 2
last_synced: 2026-07-02
---

## Простыми словами

**Субагент** — отдельный помощник с своим «окном памяти». Главный Agent отдаёт ему подзадачу и получает краткий ответ.

## Встроенные (не настраивать)

| Субагент | Зачем |
|----------|-------|
| **Explore** | Искать по проекту |
| **Bash** | Команды в терминале |
| **Browser** | Работа с веб-страницей |

## Свои субагенты

Файл `.cursor/agents/имя.md` или `~/.cursor/agents/имя.md`:

```markdown
---
name: moy-pomoshchnik
description: Проверяет текст на ошибки. Use proactively.
readonly: true
---
```

## Когда subagent, когда skill

| Subagent | Skill |
|----------|-------|
| Долгое исследование | Одна быстрая операция |
| Нужна изоляция контекста | Не нужен отдельный контекст |
| Параллельные задачи | Один шаг |

## Пошагово

1. Создайте `.cursor/agents/verifier.md`
2. Перезапустите Cursor (если глобально — после копирования в `~/.cursor/agents/`)
3. Попросите Agent: «используй verifier для проверки»

## Официальная ссылка

https://cursor.com/ru/docs/subagents
