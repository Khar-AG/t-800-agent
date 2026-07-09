# T-800 — профили целевого проекта

**Не привязывайся к «нашему» плагину.** Сначала discovery, потом профиль.

```bash
bash scripts/discover-target-project.sh --workspace "<WORKSPACE>"
```

Контракты: `shared/project-discovery-contract.md`, `shared/project-memory-contract.md`

## Профили (после discovery)

| profile | plugin_root (куда писать agents/skills) | memory (отчёты прогона) | Release |
|---------|-------------------------------------------|-------------------------|---------|
| `teya-plugin-dev` | workspace TeyaPlugin | `plugin-memory/` | `/teya-release-sync` |
| `teya-client` | `$TEYA_PLUGIN_ROOT` | `teya-memory/` в клиенте | handoff → TeyaPlugin → release-sync |
| `generic-plugin` | workspace или marker | `{slug}-memory/` | по README / marker |
| `self-t800` | `t-800-agent/` | `t-800-memory/` | `install-plugin.sh` + Reload |
| `marker` | из `project-memory.marker.json` | из marker | из marker |

## Устаревшие ID (миграция брифов)

| Старый `target_plugin` | Новый |
|--------------------------|-------|
| `teya-pro` | `teya-plugin-dev` или `teya-client` (по discovery) |
| `t-800-agent` | `self-t800` |
| `generic-plugin` | без изменений |

## teya-client (правка Teya из клиента)

1. Discovery: `teya-memory/` в workspace
2. `plugin_root` = `$TEYA_PLUGIN_ROOT` (git checkout)
3. **Запрещено** писать в `~/.cursor/plugins/local/teya`
4. Fragments factory → `teya-memory/fragments/t-800-*.md`
5. Handoff: «Открой TeyaPlugin → `/teya-release-sync`»

## teya-plugin-dev

1. workspace = TeyaPlugin git
2. Читать BOOT: `plugin-memory/HANDOFF.md`
3. Run manifest эфемерно: `.teya-plugin-run/` (нативный Teya) **или** доп. traces в `plugin-memory/` по контракту Teya

## generic-plugin

1. Нет memory → `bash scripts/init-project-memory.sh --slug <name>`
2. Integrator пишет в `agents/`, `skills/`, `commands/` относительно `plugin_root`

## Выбор (architect)

Discovery `needs_user_question: true` → один вопрос:

«Укажите папку git checkout плагина (plugin_root) или откройте workspace плагина.»

Не угадывать путь молча.

## TEYA_PLUGIN_ROOT

`~/.teya/teya.env.global` или `teya-memory/teya.env.local` — только для Teya.
