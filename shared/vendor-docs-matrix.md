# Vendor Docs Matrix (мастодонты + cookbooks)

Матрица для `Task(t-800-research-vendor-docs)`.  
Отличает вендор-доки / cookbooks от Context7 и prompt-craft.

## Канонические вендоры (мастодонты)

| Vendor | Docs / API | Cookbook / идеи | Что искать |
|--------|------------|-----------------|------------|
| **OpenAI (GPT)** | [platform.openai.com/docs](https://platform.openai.com/docs) | [cookbook.openai.com](https://cookbook.openai.com/) | models, Responses API, tools, Agents SDK, structured outputs, **рецепты** (RAG, evals, agents) |
| **Anthropic (Claude)** | [platform.claude.com/docs](https://platform.claude.com/docs) / [docs.anthropic.com](https://docs.anthropic.com) | Claude prompting best practices + Anthropic cookbook / courses | XML prompts, tool use, prompt caching, agentic patterns, computer use |
| **Google (Gemini)** | [ai.google.dev/gemini-api/docs](https://ai.google.dev/gemini-api/docs) | [ai.google.dev](https://ai.google.dev) cookbooks / prompting strategies | Gemini models, grounding, function calling, multimodal, Nano Banana |
| **Perplexity** | [docs.perplexity.ai](https://docs.perplexity.ai/) | API guides + sonar models | search-augmented chat, citations, sonar / online models |
| **Kie.AI** | [docs.kie.ai](https://docs.kie.ai/market/quickstart) | market model cards | createTask, recordInfo, image/video/audio models, credits |
| **Cursor** | [cursor.com/docs](https://cursor.com/docs) | Agent prompting, skills, subagents | Agent, skills, rules, MCP, hooks — **приоритет над community** |

Опционально по задаче: GRS AI, Railway, Make, Notion API — только если явно в brief.

## Обязательные «идеи»-хабы (не только API reference)

При DEEP и теме agents / prompting / automation vendor-docs **обязан** заглянуть минимум в релевантные cookbooks:

| Hub | URL | Зачем |
|-----|-----|--------|
| OpenAI Cookbook | https://cookbook.openai.com/ | Готовые паттерны GPT: agents, tools, evals, RAG |
| Claude prompting | https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices | Как правильно писать под Claude |
| Gemini prompting | https://ai.google.dev/gemini-api/docs/prompting-strategies | Стратегии промптов Gemini |
| Perplexity docs | https://docs.perplexity.ai/ | Search API / sonar — если нужен research-агент или citations |
| Cursor Agent prompting | https://cursor.com/docs/agent/prompting | Как промптить именно Cursor Agent |

**Правило:** API reference = факты (модели, лимиты). Cookbook = **идеи и паттерны** → в `adaptation_plan` под Cursor, не копировать notebook целиком.

## Когда какую строку открывать

| Сигнал в задаче | Вендоры |
|-----------------|---------|
| GPT / OpenAI / Responses / Structured Outputs | OpenAI docs + **Cookbook** |
| Claude / Anthropic / Opus / Sonnet | Claude docs + prompting guide |
| Gemini / Google AI / Nano Banana | Gemini docs + prompting strategies |
| Perplexity / sonar / citations search | Perplexity docs |
| Kie / createTask / market models | Kie.AI |
| Cursor skill/agent/rule | Cursor docs (всегда сверять) |
| «лучшие практики промптов» / multi-model | OpenAI Cookbook + Claude + Gemini (+ Perplexity если search) |
| Неясно | `open_questions` пользователю + 2–3 мастодонта по умолчанию |

**Не always-on все строки** — но в DEEP при multi-model / prompting теме минимум **3 мастодонта** (обычно GPT + Claude + Gemini).

## vs Context7 (`t-800-research-docs`)

| | vendor-docs | research-docs (Context7) |
|--|-------------|---------------------------|
| Источник | WebFetch docs + cookbooks | MCP Context7 |
| Когда | Модели, vendor API, **cookbooks/идеи** | Конкретная library/SDK/package |
| Budget | 4–8 страниц в DEEP (вкл. cookbooks) | ≤5 query-docs DEEP |
| Выход | `vendor_docs_brief` | `docs_brief` |

Можно вызвать **оба**.

## vs prompt-craft (`t-800-prompt-craft`)

| | vendor-docs | prompt-craft |
|--|-------------|--------------|
| Фокус | Факты + cookbook **паттерны** (с URL) | Стиль frontmatter/body агента |
| Выход | brief + open_questions + `idea_seeds[]` | `prompt_spec` |
| Не делает | Писать agents/*.md | Тянуть полные API reference |

## Выход: `vendor_docs_brief`

```yaml
vendor_docs_brief:
  vendors: [openai, anthropic, gemini, perplexity, kie, cursor]
  rows:
    - vendor: openai
      kind: docs|cookbook|blog
      url: "https://cookbook.openai.com/..."
      fetched: "YYYY-MM-DD"
      takeaway: "..."
  idea_seeds:           # паттерны из cookbooks для factory/prompt-craft
    - source: "OpenAI Cookbook / ..."
      pattern: "..."
      adapt_for_cursor: "..."
  open_questions: []    # модели / провайдер — для пользователя
```

## Запреты

- Подменять Context7 для package docs
- Копировать cookbook notebooks / статьи целиком
- Писать `prompt_spec` (это prompt-craft)
- Always-on на все вендоры без сигнала (кроме DEEP multi-model минимума 3 мастодонта)
- Игнорировать OpenAI Cookbook / Claude / Gemini guides при теме «промпты / агенты»
