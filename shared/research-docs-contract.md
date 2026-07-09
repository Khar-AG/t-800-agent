# Research Docs Contract (Context7)

Контракт для `Task(t-800-research-docs)` и оркестрации через `t-800-research-lead`.

## Когда вызывать

- В задаче есть **конкретная** library / API / SDK / CLI / framework / **MCP server name** + (опционально) version
- Research-lead или factory brief ссылается на пакет (React, Prisma, Railway CLI, …)
- DEEP: любой явный API/SDK/MCP в теме — триггер docs (не always-on без имени)
- Нужны **живые** официальные фрагменты, а не локальная KB

## Когда НЕ вызывать

- Нет имени библиотеки/API/SDK/MCP
- Только вендор models/docs сайтов → `t-800-research-vendor-docs`
- Документация уже в контексте Task / scout_report
- Достаточно `t-800-brain-context`
- Пользователь сказал «только KB» / «без MCP»

**Context7 не always-on.**

## MCP-протокол

1. `GetMcpTools` для Context7 (`user-context7` или `plugin-context7-plugin-context7`)
2. `resolve-library-id` → точный `libraryId`
3. `query-docs` — узкий запрос
4. Budget: **≤ 5** `query-docs` в DEEP; **≤ 3** в LIGHT
5. Запрещён `CallMcpTool` без шага 1

## Выход: `docs_brief`

```yaml
docs_brief:
  libraryId: "/org/package"
  queries: ["..."]
  citations:
    - topic: "..."
      quote: "..."
      libraryId: "/org/package"
  unverified: []
  query_count: 0
  budget_mode: deep|light
```

Вложение:

```yaml
research_brief:
  docs: <docs_brief | null>
```

При отсутствии library: `status: skip`, `docs: null`.

## Запреты

- WebSearch / WebFetch как замена Context7 для lib docs
- Дублировать brain-context или vendor-docs
- Always-on Context7 в `/t800-start` без имён
- Создавать factory-артефакты из research-docs
