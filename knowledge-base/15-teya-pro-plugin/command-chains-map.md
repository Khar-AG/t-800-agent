---
title: "Teya — command chains и docs"
audience: advanced
last_synced: 2026-07-06
---

# COMMAND_AGENTS и документация

При новой slash-команде в Teya:

1. Файл в `$TEYA_PLUGIN_ROOT/commands/<name>.md`
2. Запись в `scripts/teya_docs_build.py` → `COMMAND_AGENTS`
3. Пересборка: `python3 scripts/teya_docs_build.py`

При новом агенте в команде:

- Проверить `shared/command-chains.json`
- `description` в frontmatter читается в live docs

## Проверка

```bash
python3 scripts/teya_plugin_smoke.py
python3 scripts/teya_release_sync_gate.py  # в TeyaPlugin workspace
```
