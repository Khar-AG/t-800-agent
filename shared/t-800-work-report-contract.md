# T-800 — контракт Work Report (fragment)

Каждый субагент T-800 пишет fragment после работы.

## Путь

`{memory_path}/fragments/t-800-<agent-id>.md`

`memory_path` — из discovery (`scripts/discover-target-project.sh`).

Для прогона factory: также `{memory_path}/run-manifest.json` → `steps[]`.

## Шаблон

```markdown
=== T-800 FACTORY-ARCHITECT (spec) ===

**Статус:** PASS | WARN | BLOCKER
**Агент:** t-800-factory-architect
**Этап:** architect

## Сделано
- ...

## Артефакты
- agents/my-agent.md (planned)

## Handoff
summary: ...
registry_patch: ...

## kb_usage
- knowledge-base/13-agent-factory/subagent-creation-guide.md

## kb_write
- (предложения в Brain — опционально)

## Блокеры
- (пусто или список)
```

## Обязательные поля

- `Статус` — PASS/WARN/BLOCKER
- `Handoff` — для следующего агента в цепочке
- При BLOCKER — причина и что нужно от оператора

## Запреты

- Пустой fragment при «готово»
- PASS без созданных артефактов (для builder/integrator)
