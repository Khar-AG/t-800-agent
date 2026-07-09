# Аудит памяти Teya Pro (эталон для универсального отдела)

**Дата:** 2026-07-06  
**Источник:** `TEYA_PLUGIN_ROOT/shared/memory-protocol.md`, `plugin-memory-contract.md`, клиент `Мой сайт/teya-memory/`

## Вердикт

Teya — **зрелая двухслойная память**. T-800 отдел должен **встраиваться** в неё, а не создавать параллельную `t-800-memory` в Teya-проектах.

## Слои

| Слой | Папка | Назначение |
|------|-------|------------|
| Клиент | `teya-memory/` | Сайт, дизайн, WP, блог, fix-pack, fragments всех Teya-агентов |
| Плагин (dev) | `plugin-memory/` | HANDOFF, ROADMAP, PLUGIN_LOG между сессиями разработки Teya |
| Прогон | `run-manifest.json` | Один `/teya-*` или factory trace |

## Сильные стороны

1. **Единый источник правды** — все субагенты читают/пишут `teya-memory/`
2. **fragments/** — один файл на агента, без гонок
3. **run-manifest.json** — machine gate (`teya_control_department_gate.py`)
4. **project-mode.json** — маршрут static vs WP
5. **plugin-memory/** — durable BOOT для TeyaPlugin workspace
6. **Контракты** — memory-protocol, work-report, control-department

## Риски / пробелы

| # | Проблема | Рекомендация для T-800 |
|---|----------|------------------------|
| 1 | `TEYA_PLUGIN_ROOT` часто не задан | Discovery + вопрос оператору |
| 2 | Клиент vs Plugin — разные memory | Discovery profile `teya-client` vs `teya-plugin-dev` |
| 3 | 400+ файлов в teya-memory клиента | Factory читает только manifest + brief + mode |
| 4 | Нет marker для сторонних плагинов | `project-memory.marker.json` + `init-project-memory.sh` |

## Как T-800 должен работать с Teya

| Действие | Куда |
|----------|------|
| Создать агента Teya | `$TEYA_PLUGIN_ROOT/agents/` |
| Fragment factory | `teya-memory/fragments/t-800-factory-*.md` (клиент) или native Teya post-run (plugin dev) |
| Бриф | `teya-memory/factory-briefs/` или `{memory}/factory-briefs/` |
| Release | Handoff `/teya-release-sync` — **не** из клиентского workspace |

## Образец для нового плагина Foo

Минимум (создаёт `init-project-memory.sh`):

```text
foo-memory/
├── run-manifest.json
├── factory-briefs/
├── fragments/
└── README.md
project-memory.marker.json
```

Полный аналог Teya не обязателен на старте — расширять по мере зрелости плагина.

## Связанные карточки

- `knowledge-base/15-teya-pro-plugin/canonical-paths.md`
- `shared/project-memory-contract.md`
