# T-800 — поверхности артефактов (не только плагины)

Отдел создаёт **любые** Cursor-артефакты. Плагин — одна из поверхностей.

## Поверхности (`artifact_surface`)

| ID | Куда пишет builder | Когда |
|----|-------------------|-------|
| `cursor-plugin` | `{plugin_root}/agents`, `skills/`, `commands/`, `rules/` | Разработка Cursor-плагина (git checkout) |
| `cursor-workspace` | `{workspace}/.cursor/rules`, `.cursor/skills`, `.cursor/commands`, `.cursor/agents` | Текущий проект пользователя |
| `cursor-user` | `~/.cursor/rules`, `~/.cursor/skills`, `~/.cursor/commands` | Глобально на машине |

## Выбор (Директор)

1. Пользователь сказал «для проекта / в этом репо» → `cursor-workspace`
2. «Глобально / для всех проектов / user rules» → `cursor-user`
3. Назвал плагин или открыт plugin repo → `cursor-plugin`
4. Неясно → **один вопрос:** «Куда сохранить: плагин, текущий проект или глобально?»

## Память прогона

| surface | memory_path |
|---------|-------------|
| cursor-plugin | `plugin-memory/`, `teya-memory/`, `{slug}-memory/` (discovery) |
| cursor-workspace | `{workspace}/.cursor/t800-memory/` или marker |
| cursor-user | `~/.cursor/t800-memory/` |

Создание: `bash scripts/init-project-memory.sh --workspace . --slug workspace --surface workspace`

## Integrator

- **cursor-plugin** — registry, install-plugin, teya release-sync
- **cursor-workspace** — только `.cursor/` в workspace, без plugin registry
- **cursor-user** — только `~/.cursor/`, предупреди про Reload Window

## Запреты

- Не assume plugin, если задача «сделай rule для этого проекта»
- Не писать в `~/.cursor/plugins/local/*` install-копии как в git

См. `shared/target-selection-contract.md`, `shared/project-discovery-contract.md`
