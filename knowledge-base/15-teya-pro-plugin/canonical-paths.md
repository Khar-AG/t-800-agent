---
title: "Teya — канонические пути"
source: https://cursor.com/docs/subagents
audience: advanced
last_synced: 2026-07-06
---

# TEYA_PLUGIN_ROOT — куда писать

| Путь | Роль |
|------|------|
| `$TEYA_PLUGIN_ROOT` (git checkout) | **Единственное** место правок |
| `~/.cursor/plugins/local/teya` | Установка Cursor; перезаписывается `sync_plugin.sh` |
| GitHub `backup` → `main` | SSOT для удалённых агентов |
| Railway `teya-pro-docs` | Живая методичка |

## Резолв пути

```bash
python3 "$TEYA_PLUGIN_ROOT/scripts/teya_plugin_root.py"
```

Настройка: `~/.teya/teya.env.global`:

```bash
TEYA_PLUGIN_ROOT=/absolute/path/to/TeyaPlugin
```

## Закон integrator

При `target_plugin=teya-pro` писать только в:
- `$TEYA_PLUGIN_ROOT/agents/`
- `$TEYA_PLUGIN_ROOT/skills/`
- `$TEYA_PLUGIN_ROOT/commands/`
- `$TEYA_PLUGIN_ROOT/rules/`

**Запрещено:** `~/.cursor/plugins/local/teya` как destination правок.
