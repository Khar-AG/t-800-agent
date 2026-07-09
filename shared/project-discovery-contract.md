# T-800 — обнаружение целевого проекта

Отдел **универсален**: он не привязан к одному плагину. Перед любой сборкой агентов определи **куда писать код** и **где хранить память прогона**.

## Два корня (не путать)

| Понятие | Что это | Пример |
|---------|---------|--------|
| **workspace_root** | Папка, открытая в Cursor сейчас | `Мой сайт/`, `TeyaPlugin/` |
| **plugin_root** | Git/checkout плагина, куда пишутся `agents/`, `skills/`, `commands/` | `$TEYA_PLUGIN_ROOT`, `t-800-agent/` |
| **memory_path** | Папка памяти **этого** workspace или сессии | `teya-memory/`, `plugin-memory/`, `{slug}-memory/` |

**Закон:** память прогона T-800 живёт в **memory_path целевого контекста**, не «всегда в t-800-memory».  
`t-800-memory/` — только если workspace **разрабатывает сам T-800 Agent** (см. marker ниже).

## Алгоритм (BOOT каждого `/t800-start`)

0. **Выбор плагина:** `list-target-plugins.sh` + текст пользователя (`shared/target-selection-contract.md`)
1. Запусти discovery:
   ```bash
   bash scripts/discover-target-project.sh --workspace "<WORKSPACE_ROOT>"
   ```
2. Если `needs_user_question: true` или несколько плагинов без указания в тексте — **один** вопрос: «Для какого плагина?» (список из `known-plugins.json`)
3. Прочитай `memory_path/run-manifest.json` (если есть) — контекст прошлых прогонов.
4. Передай в factory YAML-блок `target_context` (см. `shared/t-800-factory-contract.md`).

## Маркер проекта (рекомендуется для новых плагинов)

Файл в **корне workspace** (или рядом с `.cursor-plugin/`):

```text
project-memory.marker.json
```

```json
{
  "slug": "my-plugin",
  "memory_dir": "my-plugin-memory",
  "plugin_root": ".",
  "release_handoff": null
}
```

| Поле | Назначение |
|------|------------|
| `slug` | Короткое имя плагина |
| `memory_dir` | Папка памяти относительно workspace |
| `plugin_root` | `.` или подпапка с `.cursor-plugin/plugin.json` |
| `release_handoff` | Команда release (например `/teya-release-sync`) или null |

T-800 **не создаёт** marker в чужих проектах без запроса. Для нового плагина — `bash scripts/init-project-memory.sh`.

## Авто-распознавание (без marker)

| Сигнал | profile | plugin_root | memory_dir |
|--------|---------|-------------|------------|
| `plugin-memory/` + `.cursor-plugin/plugin.json` + teya gates | `teya-plugin-dev` | workspace | `plugin-memory/` |
| `teya-memory/` в workspace | `teya-client` | `$TEYA_PLUGIN_ROOT` (env) | `teya-memory/` |
| `.cursor-plugin/plugin.json` + `{name}-memory/` | `generic-plugin` | workspace или marker | `{name}-memory/` |
| Marker `t-800-agent` / memory `t-800-memory` | `self-t800` | `t-800-agent/` | `t-800-memory/` |

## Сценарии оператора

### A. Разработка Teya Plugin (отдельная папка TeyaPlugin)

- workspace = TeyaPlugin
- plugin_root = workspace
- memory = `plugin-memory/` + эфемерно `.teya-plugin-run/`
- Release: `/teya-release-sync`

### B. Клиентский сайт — правка агентов Teya

- workspace = клиент (`teya-memory/`)
- plugin_root = `$TEYA_PLUGIN_ROOT` (git checkout, **не** `~/.cursor/plugins/local/teya`)
- memory прогона = `teya-memory/fragments/` + `run-manifest.json`
- После integrator: handoff release-sync в TeyaPlugin workspace

### C. Новый плагин Foo

- Создать workspace, `init-project-memory.sh --slug foo`
- Получить `foo-memory/run-manifest.json`, `factory-briefs/`

### D. Разработка T-800 Agent

- workspace = `T-800 AGENT/`
- marker или convention: `t-800-memory/`, plugin_root = `t-800-agent/`

## Запреты

- Не писать артефакты Teya в `~/.cursor/plugins/local/teya` (перезаписывается sync)
- Не assume `target_plugin=t-800-agent` без discovery
- Не смешивать `plugin-memory/` (TeyaPlugin repo) и `teya-memory/` (клиент)

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `discover-target-project.sh` | JSON: workspace, plugin_root, memory_path, profile |
| `list-target-plugins.sh` | Список checkout'ов из `~/.t800/known-plugins.json` |
| `init-project-memory.sh` | Scaffold memory для нового плагина |

Контракт памяти: `shared/project-memory-contract.md`
