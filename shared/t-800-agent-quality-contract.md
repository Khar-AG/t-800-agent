# T-800 — стандарт качества агента

Минимум для любого субагента, созданного конвейером.

## Frontmatter

| Поле | Обязательно | Правило |
|------|-------------|---------|
| `name` | Да | = имя файла, kebab-case |
| `description` | Да | Use when + Do NOT use when |
| `model` | Да | `inherit` по умолчанию |
| `readonly` | Да | reviewer/mentor/scout → `true`; builder/maintainer → `false` |
| `is_background` | Нет | `false` по умолчанию |

## Тело агента (секции)

1. **Роль** — одно предложение
2. **Что читать** — пути KB, contracts, registry
3. **Алгоритм** — 3–10 нумерованных шагов
4. **Выход** — YAML или список артефактов
5. **Связи** — calls / calledBy
6. **Запреты** — минимум 3 пункта

## Reviewer / Auditor

- `readonly: true` — не правят production (тема, deck, клиентский код)
- Пишут только отчёты и fragments
- PASS только при закрытых critical findings

## Orchestrator vs Leaf

| Тип | Примеры | Запуск Task() |
|-----|---------|---------------|
| Orchestrator | t-800-factory, t-800-brain-lead | Может вызывать специалистов |
| Leaf | factory-architect, brain-agents | Не вызывает Task() |

## Антипаттерны (auditor FAIL)

- Vague description: «helps with tasks»
- Subagent как skill (дубль t-800-operator)
- Промпт > 150 строк без причины
- name ≠ filename
- Нет записи в registry

## Teya Pro (дополнительно)

См. `knowledge-base/15-teya-pro-plugin/agent-quality-checklist.md`
