# T-800 — выбор цели (плагин + surface)

Отдел **универсален**: плагины, workspace `.cursor/`, глобальные user rules/skills.

## Алгоритм

1. Определи **artifact_surface** из текста (`shared/artifact-surfaces-contract.md`)
2. Если `cursor-plugin` — `list-target-plugins.sh` + выбор slug
3. `discover-target-project.sh` → memory_path
4. Factory + research → fragment в memory_path

## Surface (приоритет текста пользователя)

| Сигнал | surface | Куда |
|--------|---------|------|
| «этот проект», «в репозитории» | cursor-workspace | `{workspace}/.cursor/` |
| «глобально», «user rule» | cursor-user | `~/.cursor/` |
| «плагин Teya», checkout | cursor-plugin | `{plugin_root}/` |

## Вопросы (максимум 2)

1. Куда сохранить — **плагин / проект / глобально**? (если неясно)
2. Какой **плагин** из реестра? (если surface=plugin и count>1)

## Research

Если задача про «актуальное», «найди на GitHub», «как делают другие» → `Task(t-800-research-lead)` **до** factory.

## Реестр плагинов

`~/.t800/known-plugins.json` — только для surface `cursor-plugin`.

См. `shared/project-discovery-contract.md`, `shared/research-freshness-contract.md`
