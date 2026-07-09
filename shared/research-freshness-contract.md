# T-800 — контракт свежести (research)

Любая идея из интернета **не попадает в factory** без проверки даты.

## Пороги

| Уровень | Возраст источника | Действие |
|---------|-------------------|----------|
| OK | ≤ 90 дней | Можно адаптировать |
| WARN | 91–180 дней | Только если нет свежее; пометка `stale_warning` |
| BLOCK | > 180 дней или дата неизвестна | Не копировать verbatim; искать свежее |

Официальный cursor.com/changelog — **исключение**: всегда OK если страница актуальна.

## Обязательные поля в research brief

```yaml
sources:
  - url: "..."
    published_or_updated: "YYYY-MM-DD"
    freshness: ok | warn | block
    takeaway: "..."
adaptation_notes: "что меняем под Cursor frontmatter / Task()"
```

## Инструменты агентов research

- `WebSearch` — первичный поиск
- `WebFetch` — прочитать README, SKILL.md, issue
- `gh` CLI — опционально, если доступен

## Запреты

- Не выдавать промпт «как есть» с Habr/GitHub без adaptation_notes
- Не скрывать возраст источника
- Не использовать один источник без cross-check (минимум 2 для нового skill)

## Кто применяет

`t-800-research-lead` → `t-800-factory-architect` → auditor проверяет `freshness` в brief
