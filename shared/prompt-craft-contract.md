# Prompt Craft Contract

Контракт для `Task(t-800-prompt-craft)` и QA через `Task(t-800-prompt-auditor)`.

## Когда вызывать

- `artifact` ∈ {agent, skill, command}
- Нужен vendor-aware промпт (Claude / GPT / Gemini / Cursor Agent)
- Перед builder или при рефакторинге description/промпта

## Когда НЕ вызывать (skip)

- Только rule / hook / script без тела промпта
- Чисто механический rename без изменения текста

## Vendor matrix

| Vendor | Акцент в prompt_spec | Идеи из vendor-docs |
|--------|----------------------|---------------------|
| Claude | Чёткие роли, XML/секции, явные запреты, примеры | Claude prompting best practices |
| GPT | Пошаговый алгоритм, критерии done, output schema | **OpenAI Cookbook** patterns |
| Gemini | Контекст + ограничения, структурированные списки | Gemini prompting strategies |
| Perplexity | Citations, search-first, источники в ответе | docs.perplexity.ai / sonar |
| Cursor | Frontmatter 5 полей; Use when / Do NOT; Роль→Алгоритм→Выход→Запреты | cursor.com/docs/agent/prompting |

Default для T-800: **Cursor**.  
Если в входе есть `vendor_docs_brief.idea_seeds[]` — вплети 1–3 паттерна в `body_outline` / `anti_patterns_avoided` с attribution URL.

## Anti Description Trap

| Правильно | Неправильно |
|-----------|-------------|
| description = маршрутизация: зона + Use when + Do NOT | description = весь промпт агента |
| Тело файла = алгоритм и запреты | Дубль алгоритма в description |

## Cursor frontmatter (ровно 5 полей)

```yaml
name: ...
description: >
  ...
model: inherit
readonly: true|false
is_background: false
```

**Запрещено:** поле `tools:` в frontmatter субагента.

## Выход: `prompt_spec`

```yaml
prompt_spec:
  artifact: agent | skill | command
  vendor: claude | gpt | gemini | cursor
  frontmatter: { name, description, model, readonly, is_background }
  body_outline: []
  anti_patterns_avoided: []
```

## QA handoff

После builder/integrator:

1. `Task(t-800-prompt-auditor)` → `status: ok | blocked`
2. Critical: vague description, Description Trap, `tools:` в frontmatter
3. Только при `ok` → `Task(t-800-factory-auditor)`

Контракт качества: `shared/t-800-agent-quality-contract.md`.
