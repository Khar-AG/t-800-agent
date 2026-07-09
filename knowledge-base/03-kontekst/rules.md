---
title: "Rules — постоянные инструкции"
source: https://cursor.com/ru/docs/context/rules
audience: beginner
tier: 2
last_synced: 2026-07-02
---

## Простыми словами

**Rules** — заметки для агента, которые он читает каждый раз (или когда нужно): «пиши по-русски», «не трогай папку dist».

## Когда вам это нужно

Хотите, чтобы Agent всегда помнил ваши стандарты без повторения в каждом сообщении.

## Типы правил

| Тип | Где | Для кого |
|-----|-----|----------|
| Project rules | `.cursor/rules/*.mdc` | Один проект |
| User rules | Settings → Rules | Все ваши проекты |
| Team rules | Dashboard команды | Вся команда |

## Типы применения

| Тип | Когда срабатывает |
|-----|-------------------|
| Always Apply | В каждом чате |
| Apply Intelligently | Agent сам решает по описанию |
| Apply to Specific Files | Когда открыт файл по шаблону |
| Apply Manually | Когда вы пишете `@имя-правила` |

## Пошагово

1. В Agent напишите `/create-rule` и опишите правило
2. Или создайте файл `.cursor/rules/moe-pravilo.mdc`
3. Добавьте frontmatter: `alwaysApply: true` или `description:` + `globs:`

## Частые ошибки

- Файл `.md` вместо `.mdc` в `.cursor/rules/` — **игнорируется**
- Слишком длинное правило — разбейте на несколько

## Официальная ссылка

https://cursor.com/ru/docs/context/rules
