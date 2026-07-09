# T-800 — дисциплина Task-промптов

Каждый Task в конвейере T-800 обязан содержать **7 частей**. Без любой части — субагент останавливается с `BLOCKER`.

## 7 обязательных частей

```text
1. РОЛЬ          — «Ты — t-800-factory-architect. Следуй shared/t-800-factory-contract.md»
2. РЕЖИМ         — architect | builder | integrator | auditor | scout | brain
3. ВХОДЫ         — точные пути: factory-brief, scout_report, spec YAML, TEYA_PLUGIN_ROOT
4. ЗАДАЧА        — нумерованные шаги, не абзац
5. ВЫХОДЫ        — файлы + fragment в {memory_path}/fragments/
6. КРИТЕРИИ      — проверяемые условия PASS
7. ЗАПРЕТЫ       — не skip auditor, не писать в ~/.cursor/plugins/local/teya
```

## Fragment (обязателен)

Путь: `{memory_path}/fragments/t-800-<agent-id>.md` (memory_path из discovery)

Маркер: `=== T-800 <AGENT> (<STAGE>) ===`

Формат: `shared/t-800-work-report-contract.md`

## Статусы

Только: `PASS` | `WARN` | `BLOCKER`

## Правила Директора

- Один Task = одна роль = одна запись в `{memory_path}/run-manifest.json`
- Не бандлить architect+builder в один Task
- После Task — проверить fragment и артефакты на диске

## Связь с Teya

При profile `teya-client` или `teya-plugin-dev` в ВХОДЫ добавлять:
- `$TEYA_PLUGIN_ROOT/shared/agent-quality-contract.md`
- `$TEYA_PLUGIN_ROOT/shared/task-prompt-discipline.md`
