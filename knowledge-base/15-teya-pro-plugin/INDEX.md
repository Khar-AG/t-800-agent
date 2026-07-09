---
title: "Teya Pro — карта раздела для T-800"
audience: advanced
tier: 5
last_synced: 2026-07-06
---

# Teya Pro Plugin — для конвейера T-800

T-800 **не копирует** весь vault Teya. Читает живые контракты из `$TEYA_PLUGIN_ROOT/shared/` когда целевой плагин — Teya (через `/t800-start` + текст или выбор из реестра).

## Документы

| Файл | Назначение |
|------|------------|
| [canonical-paths.md](canonical-paths.md) | TEYA_PLUGIN_ROOT, запрет local/teya |
| [agent-quality-checklist.md](agent-quality-checklist.md) | Минимум агента Teya |
| [task-prompt-7-parts.md](task-prompt-7-parts.md) | 7 частей Task-промпта |
| [plugin-release-handoff.md](plugin-release-handoff.md) | release-sync после правок |
| [command-chains-map.md](command-chains-map.md) | teya_docs_build, COMMAND_AGENTS |
| [departments-and-stacks.md](departments-and-stacks.md) | manager vs leaf, отделы |

## Субагент

`Task(t-800-brain-teya)` — доменный мозг при работе с Teya.

## Команда

**Закон:** нет project-specific slash-команд. Только `/t800-start` + «для Teya» в тексте или выбор из `~/.t800/known-plugins.json`.
