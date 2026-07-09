# T-800 — контракт памяти целевого проекта

Память — **у каждого плагина/проекта своя**. T-800 отдел только **находит** её и **пишет** артефакты прогона, не подменяя нативную систему целевого плагина.

## Эталон: Teya Pro (аудит)

Teya реализовала память в двух слоях:

| Слой | Папка | Где | Горизонт |
|------|-------|-----|----------|
| Клиентский проект | `teya-memory/` | workspace клиента | Весь цикл сайта/блога/фиксов |
| Разработка плагина | `plugin-memory/` | TeyaPlugin git | Межсессионный HANDOFF, ROADMAP, PLUGIN_LOG |
| Один прогон | `run-manifest.json` | `teya-memory/` или `.teya-plugin-run/` | Одна команда `/teya-*` |

Ключевые артефакты Teya (см. `TEYA_PLUGIN_ROOT/shared/memory-protocol.md`):

- `run-manifest.json` — шаги Task, verdict
- `fragments/<agent>.md` — один файл на агента за этап
- `work-reports/` — развёрнутые отчёты
- `01-handoff.md` — склейка Директором
- `project-mode.json`, `site.inv` — режим и intake

**Вывод для T-800:** при работе **на Teya** не создавать параллельную `t-800-memory/` в клиенте — писать в **нативную** `teya-memory/` или `plugin-memory/`.

## Что пишет конвейер T-800 в memory_path

| Артефакт | Путь | Когда |
|----------|------|-------|
| **STATE прогона** | `{memory}/STATE.md` | Init в начале `/t800-start` / `/t800-plugin-audit`; touch после отделов |
| Бриф factory | `{memory}/factory-briefs/<slug>.yaml` | Старт factory |
| Manifest прогона | `{memory}/run-manifest.json` | Каждый `/t800-start` |
| Fragment этапа | `{memory}/fragments/t-800-<agent>.md` | После каждого Task factory |
| Audit отдела | `{memory}/audits/t-800-<topic>.md` | По запросу (readonly study) |

Шаблон STATE: `templates/STATE.md.template`. Скрипт: `scripts/t800_loop_state.sh`. Контракт: `shared/loop-engineering-contract.md`.

Префикс `t-800-` в fragments — **маркер отдела**, не целевого плагина. Целевой плагин (Teya) сохраняет свои имена (`teya-*`, `aura-*`).

## Структура memory (минимум для нового плагина)

```text
{memory_dir}/
├── STATE.md           # loop: Last run / In progress / Gates
├── run-manifest.json
├── factory-briefs/
├── fragments/
├── audits/            # опционально
└── README.md          # создаёт init-project-memory.sh
```

## Чтение перед Task

1. `{memory}/STATE.md` — blockers, lessons, last gates (обязательно)
2. `{memory}/run-manifest.json` — что уже делали
3. `{memory}/factory-briefs/*.yaml` — активные брифы
4. Для Teya client: также `project-mode.json`, `TEYA_TASKS.md`
5. Для TeyaPlugin dev: `plugin-memory/HANDOFF.md`, хвост `PLUGIN_LOG.md`

## profile → memory (канон)

| profile | memory_dir | plugin_root |
|---------|------------|-------------|
| `teya-client` | `teya-memory/` | `$TEYA_PLUGIN_ROOT` |
| `teya-plugin-dev` | `plugin-memory/` (+ run in `.teya-plugin-run/`) | workspace |
| `generic-plugin` | marker или `{slug}-memory/` | marker или workspace |
| `self-t800` | `t-800-memory/` | `t-800-agent/` |

## Если memory отсутствует

```bash
bash scripts/init-project-memory.sh --workspace "<ROOT>" --slug "<slug>"
```

Или спросить оператора: «Создать папку памяти `{slug}-memory/` для этого плагина?»

## Связанные контракты Teya (живое чтение)

При `profile` teya-* читать из `$TEYA_PLUGIN_ROOT/shared/`:

- `memory-protocol.md`
- `plugin-memory-contract.md`
- `agent-work-report-contract.md`
- `client-project-plugin-canonical-path-contract.md`

Карточки KB: `knowledge-base/15-teya-pro-plugin/`, аудит: `knowledge-base/16-universal-project-memory/teya-memory-audit.md`
