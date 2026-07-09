# Deep Research Contract (v1.9)

Контракт для `Task(t-800-research-lead)` в режиме **DEEP** (default для `/t800-start`, кроме «только KB» / «без интернета»).

## Режим

| Режим | Когда |
|-------|--------|
| **DEEP** | Default `/t800-start` и любая задача на skill/agent/automation |
| **LIGHT** | Явно «быстрый обзор» / «без deep» |
| **SKIP** | «только KB» / «без интернета» |

## Автономия поиска (v1.9)

Отдел **сам** выбирает площадки. См. `shared/search-strategy-contract.md`.

Порядок DEEP:

1. `t-800-research-strategist` → `search_plan`
2. Fan-out specialists по плану
3. `t-800-research-synthesizer` → сравнение → один оптимальный вариант
4. `coverage_matrix`

## Intake gate

Перед тяжёлой разведкой, если неоднозначны модели / MCP / surface / integrations:

```
Task(t-800-intake-clarifier)
```

Статус `asked` → дождаться ответов. `skipped` → продолжать.

## Минимумы DEEP (FAIL если не закрыты)

| Требование | Минимум |
|------------|---------|
| `search_plan` от strategist | обязателен |
| `synthesis` с сравнением ≥2 семейств | обязателен |
| Источники с датами | ≥ 8 (`freshness` ok\|warn; block не в счёт) |
| GitHub deep-mines | ≥ 2 если канал github/repo-miner = must |
| ClawHub pass | если strategist поставил clawhub must / тема skills marketplace |
| Vendor docs **или** Context7 | если в плане must / в задаче API·модели·SDK·MCP |
| adaptation_plan | из `synthesis.merge_plan` |
| open_questions | если модели/API неоднозначны |

## coverage_matrix (обязателен в research_brief)

```yaml
coverage_matrix:
  strategist: pass|fail
  synthesizer: pass|fail
  github_shallow: pass|fail|skip
  repo_mines: pass|fail|skip
  community: pass|fail|skip
  clawhub: pass|fail|skip
  vendor_docs: pass|fail|skip
  context7_docs: pass|fail|skip
  news: pass|fail|skip
  sources_count: 0
  verdict: pass|fail
```

`verdict: fail` → не отдавать factory как ok.

## Fan-out специалистов

| Специалист | Роль |
|------------|------|
| `t-800-research-strategist` | **Сам** выбирает куда искать → `search_plan` |
| `t-800-research-github` | Топ-репо по плану |
| `t-800-research-repo-miner` | Deep mine ≥2 repos |
| `t-800-research-community` | Reddit/Habr/X/HN |
| `t-800-research-clawhub` | clawhub.ai |
| `t-800-research-vendor-docs` | Cookbooks GPT/Claude/Gemini/Perplexity/Kie/Cursor |
| `t-800-research-docs` | Context7 |
| `t-800-research-news` | Changelog/HN/blogs |
| `t-800-research-synthesizer` | Сравнение → один оптимальный вариант |

## Запреты

- Считать DEEP закрытым без coverage_matrix / без synthesis
- Пропускать strategist или synthesizer в DEEP
- Ждать список сайтов от пользователя
- Always-on Context7
- Копировать чужие skills целиком
- Clone репо без явной просьбы пользователя
