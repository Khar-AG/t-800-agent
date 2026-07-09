---
name: t-800-knowledge-base
description: >
  Карта KB плагина T-800 Agent для ОБНОВЛЕНИЯ базы знаний (sync, CHANGELOG).
  НЕ вызывать для ответов пользователю — для этого Task(t-800-operator).
disable-model-invocation: true
---

# T-800 — карта KB (только для maintainer)

Это **не** субагент. Пользователю отвечает **Task(t-800-operator)** → `agents/t-800-operator.md`.

Используй этот skill только когда:
- запускается `/t-800-sync`
- rule `t-800-knowledge-refresh` активен
- нужно обновить `knowledge-base/` после `sync-docs.ps1`

Контракт: `shared/knowledge-update-contract.md`

## Пути

- `knowledge-base/INDEX.md` — карта
- `knowledge-base/UPDATE-QUEUE.md` — очередь после sync
- `knowledge-base/manifest.json` — хеши страниц
- `scripts/sync-docs.ps1` — синхронизация
- `scripts/install-plugin.sh` — деплой в `~/.cursor/plugins/local/t-800-agent/` (без зеркал в user-home)
