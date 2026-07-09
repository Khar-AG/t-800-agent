---
title: "Teya — handoff release-sync"
audience: advanced
last_synced: 2026-07-06
---

# После правок Teya Plugin

Контракт: `$TEYA_PLUGIN_ROOT/shared/client-project-plugin-release-contract.md`

## Из клиентского workspace

T-800 factory правит `$TEYA_PLUGIN_ROOT` → в отчёте:

**Следующий шаг:** открыть **TeyaPlugin workspace** → `/teya-release-sync`

## Release sync публикует

- GitHub `backup` → `main`
- Railway `teya-pro-docs`
- Factory MCP (по контракту teya-docs-sync)

## Не писать «готово»

Пока release-sync не выполнен — плагин не опубликован для удалённых агентов.
