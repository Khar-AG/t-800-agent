# Search Strategy Contract (v1.9)

Контракт для `Task(t-800-research-strategist)` → fan-out → `Task(t-800-research-synthesizer)`.

## Закон автономии

Research **сам** решает, куда идти. Пользователь может подсказать («посмотри Kie»), но **не обязан** перечислять сайты.

Запрещено:
- Ждать список URL от пользователя
- Искать только там, куда «явно сказали»
- Пропускать стратега в DEEP MODE

## Pipeline

```
intake? → scout → research-lead
  1) Task(t-800-research-strategist)  → search_plan
  2) fan-out по search_plan.channels   → findings
  3) Task(t-800-research-synthesizer) → synthesis (лучший вариант)
  4) research_brief + coverage_matrix
→ prompt-craft? → brain → factory
```

## Topic → каналы (подсказки стратегу)

| Тема / сигнал | Каналы (приоритет) |
|---------------|-------------------|
| Cursor skill / subagent / rule | github, repo-miner, clawhub, community, cursor(scout), news |
| Промпты / multi-model | vendor-docs (Cookbook/Claude/Gemini/Perplexity), prompt-craft later |
| Library / SDK / npm / API package | research-docs (Context7), github, vendor-docs если vendor API |
| Kie / GRS / image-video market | vendor-docs (Kie), Context7 если SDK, clawhub, github |
| Scrapers / crawlers / posting | github + repo-miner, community, news |
| PDF / sheets / docs automation | github, clawhub, vendor-docs, community |
| Security / malware skills | news, community, clawhub (vet), github |
| Breaking change / «что нового» | news, vendor-docs, cursor changelog |
| Неясно | strategist: широкий план + open_questions; min github+community+vendor OR clawhub |

Стратег **может добавить** каналы вне таблицы, если тема того требует (с обоснованием в `why`).

## search_plan (выход стратега)

```yaml
search_plan:
  topic: "..."
  intent_artifact: skill|agent|command|rule|hook|mix
  mode: deep|light
  channels:
    - id: github|repo-miner|community|clawhub|vendor-docs|docs|news|custom
      priority: must|should|nice
      why: "..."
      queries: ["..."]          # что искать
      sites_or_hubs: ["..."]    # github.com, clawhub.ai, cookbook.openai.com, …
      specialist: t-800-research-...
  compare_axes: ["freshness", "cursor_fit", "security", "completeness"]
  skip_channels: [{id: "...", why: "..."}]
  open_questions: []
```

`must` каналы обязательны для coverage. `should` — стремиться закрыть в DEEP.

## synthesis (выход синтезатора)

```yaml
synthesis:
  recommended_approach: "..."      # один оптимальный путь
  why_best: "..."
  runners_up: []                   # отвергнутые альтернативы + почему слабее
  merge_plan: "что взять из A + B"
  conflicts: []                    # противоречия источников
  confidence: high|medium|low
  sources_ranked: []               # url + score
```

Синтезатор **сравнивает** ≥2 независимых источника перед `recommended_approach`.  
Если источник один — `confidence: low` + open_question.

## Связь с DEEP minima

`shared/deep-research-contract.md` остаётся в силе.  
Стратег **не отменяет** ≥8 sources / ≥2 mines — он выбирает *куда*, lead проверяет *достаточно ли*.

## Запреты

- Стратег не WebFetch сам тонны страниц — только план (допускается 1–2 probe search)
- Синтезатор не вызывает новых specialists (добор — через lead)
- Не выдавать synthesis без сравнения
