# Plugin Audit Contract (v1.11)

Контракт машинного + narrative аудита **чужого Cursor-плагина** (agents / skills / commands / rules / hooks).

## Scope vs соседние команды

| Команда | Объект | Цель | Куда пишет |
|---------|--------|------|------------|
| **`/t800-plugin-audit`** | Один плагин (`--plugin-root`) | Инвентарь, граф команд↔агенты, orphans, alwaysApply scorecard | `{target memory_path}/audits/<run-id>/` |
| **`/t800-audit`** | Вся система Cursor (global + local workspace) | Диалог keep/narrow/remove по bloat rules/skills | fragment system-auditor; без карты чужого плагина в KB |
| **`/teya-run-audit`** | Прогон Teya (`run-manifest`) | Post-run 4/4 качество оркестрации | `teya-memory/` клиента |

Не путать: plugin-audit ≠ cursor-bloat audit ≠ Teya post-run audit.

## Write paths (MEMORY LAW)

После `bash scripts/discover-target-project.sh --workspace "<ROOT>" [--plugin-root "<PLUGIN>"]`:

| Артефакт | Путь |
|----------|------|
| Machine SoT | `{memory_path}/audits/<run-id>/inventory.json` |
| Scorecard | `{memory_path}/audits/<run-id>/scorecard.json` |
| Graph | `{memory_path}/audits/<run-id>/graph.md` |
| Machine summary | `{memory_path}/audits/<run-id>/audit-machine-summary.md` |
| Narrative | `{memory_path}/audits/<run-id>/audit-summary.md` |
| Fragment | `{memory_path}/fragments/t-800-plugin-auditor.md` |
| Fix-pack draft (опц.) | `{memory_path}/fix-packs/<slug>.md` — через `scripts/t800_audit_to_fixpack.py` |

`run-id` — например `t800-plugin-audit-YYYYMMDD-HHMM` или явный `--out`.  
Fix-pack разрешён в `{memory_path}/fix-packs/` (не в KB). Дальше: `/t800-fix` (`shared/fix-pipeline-contract.md`).

### Запреты записи

- **Не** класть карту чужого плагина в `t-800-agent/knowledge-base/`
- **Не** писать runtime-отчёт в `t-800-memory/audits/`, если целевой проект другой (Teya → `plugin-memory/` / `teya-memory/`)
- **Не** silent prune / удаление agents/skills/commands целевого плагина
- Скрипт пишет **только** в `--out`

Артефакты **самого** T-800 (команда, агент, скрипт, контракт) живут в `t-800-agent/`.

## alwaysApply thresholds (large plugins)

Для плагинов с большим числом rules (`--strict-alwaysapply large`):

| Уровень | Условие | Exit |
|---------|---------|------|
| soft | `alwaysApply: true` count **≥ 10** | WARN в scorecard, exit 0 |
| hard | `alwaysApply: true` count **≥ 20** | FAIL в scorecard, exit **non-zero** |

Без `--strict-alwaysapply large` пороги только информационные (не валят exit).

## Machine JSON = Source of Truth

Агент `t-800-plugin-auditor`:

1. Запускает / читает `scripts/t800_plugin_audit.py` → JSON в `--out`
2. Строит narrative **только** из machine SoT (+ точечный Read для пояснений)
3. Пишет `audit-summary.md` + fragment в memory целевого проекта

Не выдумывать counts «на глаз», если есть `inventory.json`.

## Exit codes скрипта

| Code | Когда |
|------|--------|
| 0 | OK (включая soft WARN) |
| 1 | broken / missing `plugin.json` (или `.cursor-plugin/plugin.json`) |
| 2 | hard alwaysApply fail (`--strict-alwaysapply large` и count ≥ 20) |

## Оркестрация

```text
discover → python3 scripts/t800_plugin_audit.py → Task(t-800-plugin-auditor)
```

**Закон:** полный plugin audit не из main chat без `Task(t-800-plugin-auditor)`.

## Версия

- Обновлён: 2026-07-09 · T-800 **1.13.0** (fix-packs handoff)
- Введён: 2026-07-09 · T-800 **1.11.0**
- Связанные: `project-memory-contract.md`, `department-orchestration-contract.md`, `fix-pipeline-contract.md`, `commands/t800-plugin-audit.md`
