# /t800-plugin-audit — аудит одного Cursor-плагина

**Зачем:** карта agents / skills / commands / rules / hooks внутри `--plugin-root` (граф, orphans, alwaysApply) — без dump в KB T-800.

Loop / STATE: `shared/loop-engineering-contract.md`.

## Шаги

### 0. Discovery + STATE

```bash
bash scripts/discover-target-project.sh --workspace "<WORKSPACE>" --plugin-root "<PLUGIN_ROOT>"
bash scripts/t800_loop_state.sh init --memory-path "<memory_path>"
# Read STATE.md — blockers / lessons прошлого аудита
```

Запомни `memory_path` целевого проекта. Runtime-отчёты → **только** `{memory_path}/audits/`.

### 1. Machine SoT (обязателен)

```bash
python3 scripts/t800_plugin_audit.py \
  --plugin-root "<PLUGIN_ROOT>" \
  --out "<memory_path>/audits/t800-plugin-audit-$(date +%Y%m%d-%H%M)" \
  [--strict-alwaysapply large]
```

Пишет: `inventory.json`, `scorecard.json`, `graph.md`, `audit-machine-summary.md`.

**Без `inventory.json` или при fail скрипта — не «готово»** (machine gate).

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "plugin-audit" --message "machine SoT: inventory.json"
```

### 2. Narrative

```
Task(t-800-plugin-auditor)
```

Передай: `plugin_root`, `out` (run-id dir), `memory_path`, уровень strict.

Агент читает JSON → `audit-summary.md` + `fragments/t-800-plugin-auditor.md`.

### 3. Fix-pack draft (после narrative)

```bash
python3 scripts/t800_audit_to_fixpack.py \
  --audit-dir "<memory_path>/audits/<run-id>" \
  --memory-path "<memory_path>" \
  [--slug from-audit-$(date +%Y%m%d)]
```

Скрипт печатает путь `{memory_path}/fix-packs/<slug>.md`.  
Дальше для правок: **`/t800-fix`** (не полный `/t800-start`, если список файлов уже в pack).

### 4. Закрытие STATE

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "plugin-audit" --message "narrative готов; fix-pack draft; gates pass"
```

Обнови в STATE.md секции Completed / Lessons / Gates (plugin-audit inventory = pass|fail).

## Отличия от `/t800-audit`

| | `/t800-plugin-audit` | `/t800-audit` |
|--|----------------------|---------------|
| Объект | Один плагин | Вся система Cursor (global+local) |
| Агент | `t-800-plugin-auditor` | `t-800-system-auditor` |
| Скрипт | `t800_plugin_audit.py` | `audit-cursor-setup` + `audit-cursor-bloat` |
| Выход | `{memory}/audits/<run-id>/` | диалог keep/narrow/remove |
| Цель | карта + orphans + scorecard | почистить bloat контекста |

Не путать с `/teya-run-audit` (качество прогона Teya).

Контракт: `shared/plugin-audit-contract.md`.

## Связанные команды

| Команда | Когда |
|---------|--------|
| `/t800-audit` | Разбор rules всей системы Cursor |
| `/t800-onboard` | Быстрый обзор «что установлено» |
| `/t800-fix` | PATCH по fix-pack после `t800_audit_to_fixpack` |
| `/t800-doctor` | Быстрое здоровье (scripts-only) |
| `/t800-start` | Создать новый артефакт (не узкий PATCH) |

**Закон:** не полный plugin audit из main chat без `Task(t-800-plugin-auditor)`. Machine SoT обязателен.
