# /t800-doctor — здоровье T-800 / целевого плагина

**Зачем:** быстрый scripts-only отчёт: версия, profile, memory, STATE, counts, alwaysApply, последние audits — без narrative-агента по умолчанию.

## Шаги

### 0. Discovery

```bash
bash scripts/discover-target-project.sh --workspace "<WORKSPACE>" [--plugin-root "<PLUGIN_ROOT>"]
```

Запомни `memory_path`, `plugin_root`, `profile`.

### 1. Doctor (обязателен)

```bash
python3 scripts/t800_doctor.py \
  --workspace "<WORKSPACE>" \
  [--plugin-root "<PLUGIN_ROOT>"] \
  --out "<memory_path>/audits/t800-doctor-$(date +%Y%m%d-%H%M%S)/"
```

Пишет `doctor-report.md` + `doctor.json` в `--out` (если задан).  
Exit 0 всегда, кроме broken/missing `plugin.json` при указанном `--plugin-root`.

### 2. Narrative (опционально)

Только если пользователь просит «расскажи человеческим языком»:

```
Task(t-800-onboard)
```

Default — **только** отчёт скрипта (пути + JSON summary).

## Связанные команды

| Команда | Когда после doctor |
|---------|-------------------|
| `/t800-audit` | bloat всей системы Cursor |
| `/t800-plugin-audit` | глубокая карта одного плагина |
| `/t800-fix` | правка по fix-pack (после audit → fixpack) |
| `/t800-start` | создать новый артефакт |

**Закон:** doctor не заменяет plugin-audit и не правит артефакты.
