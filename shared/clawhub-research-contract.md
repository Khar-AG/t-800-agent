# ClawHub Research Contract

Контракт для `Task(t-800-research-clawhub)`. Источник: [clawhub.ai](https://clawhub.ai/).

## Цель

Найти skills/plugins (Top / Trending / New), извлечь **паттерны** и план адаптации под Cursor — с attribution и security narrative. **Не** копировать skill целиком.

## Алгоритм источников

1. WebFetch `https://clawhub.ai/` и разделы Skills / Plugins
2. Пройти вкладки **Top**, **Trending**, **New** (сколько доступно без auth)
3. Для 3–8 релевантных карточек: title, category, summary, URL, дата если есть
4. Security narrative scan: секреты в промпте, shell без подтверждения, scrape PII, «ignore previous»
5. adaptation_plan → Cursor `SKILL.md` / subagent (структура, tools, запреты)

## Выход: `clawhub_findings`

```yaml
clawhub_findings:
  scanned_at: "YYYY-MM-DD"
  tabs: [top, trending, new]
  items:
    - title: "..."
      url: "..."
      category: skill|plugin
      summary: "..."
      attribution: "ClawHub / author if known"
      security_flags: []     # или список рисков
      adapt_for_cursor: "..."
  rejected_verbatim: true    # всегда: без полной копии
```

## Запреты

- Verbatim copy текста skill / промпта
- Публиковать API keys / токены из карточек
- Рекомендовать skill с critical security_flags без пометки
- Подменять Context7 / vendor-docs разведкой ClawHub
