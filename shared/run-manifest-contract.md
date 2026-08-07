# Run Manifest Contract (v1.13+)

Два манифеста прогона в `{memory_path}` — у них **разные владельцы**.

## 1. Корневой `run-manifest.json`

- **Владелец:** текущий прогон `/t800-start` (CREATE/крупное изменение).
- Пишется шагами конвейера (scout → research → brain → factory).
- Используется `scripts/t800_run_gate.py --strict-create` (завершённый шаг factory).
- **Правило:** `/t800-fix` прогоны его **не трогают**.

## 2. Архивный `run-manifest.archive.<slug>.json`

- **Владелец:** прогон `/t800-fix` по fix-pack `<slug>` (slug = имя pack без даты `-YYYY-MM-DD`).
- **Кто пишет:**
  - `scripts/t800_loop_state.sh touch --stage fix|factory` — создаёт/обновляет архив после записи STATE;
  - `scripts/t800_run_gate.py` — при PASS дописывает шаг `run_gate` с exit code.
- **Кто читает:** teya-run-auditor при машинной сверке chains релизного окна.
  Отсутствие архива у старого прогона — **WARN, не FAIL** (graceful).

### Схема (минимальная)

```json
{
  "run_id": "<slug fix-pack без даты>",
  "slug": "<slug>",
  "fix_pack": "fix-packs/<имя pack>.md",
  "created_at": "YYYY-MM-DD HH:MM",
  "updated_at": "YYYY-MM-DD HH:MM",
  "stages": [
    { "stage": "fix", "ts": "YYYY-MM-DD HH:MM", "verdict": "recorded|pass|fail", "message": "..." },
    { "stage": "run_gate", "ts": "YYYY-MM-DD HH:MM", "verdict": "pass", "exit_code": 0 }
  ],
  "files": ["scripts/t800_loop_state.sh"],
  "fragment": "fragments/t-800-factory.md",
  "run_gate": null
}
```

| Поле | Источник |
|------|----------|
| `run_id` / `slug` | имя fix-pack файла без расширения и без даты на конце |
| `fix_pack` | относительный путь к pack в `{memory_path}` |
| `stages[]` | по одной записи на стадию (`research`/`brain`/`factory`/`fix`/`run_gate`); повторный touch **заменяет** запись той же стадии |
| `verdict` | из message touch: `pass`/`fail` по ключевым словам, иначе `recorded` |
| `files[]` | секция `### files` pack-а (строки `- \`path\``) |
| `fragment` | work report фабрики (default `fragments/t-800-factory.md`) |
| `run_gate` | `null` до первого PASS gate; затем `{exit_code, ts, verdict}` |

## Инварианты

- Имя архива: строго `run-manifest.archive.<slug>.json` (glob `run-manifest.archive.*.json`).
- Один архив на fix-pack; серия из ≥2 fix-прогонов подряд — у каждого свой архив.
- Запись архива **best-effort**: ошибка записи не ломает gate / touch (WARN в stderr).
- Комментарии и докстринги в коде — на русском.

## Связанные

- `shared/fix-pipeline-contract.md` — закон обязательности для серий fix-прогонов
- `shared/loop-engineering-contract.md` — STATE / gates
- `scripts/t800_loop_state.sh`, `scripts/t800_run_gate.py` — реализация

## Версия

- Введён: 2026-08-07 · fix-pack `t800-fix-per-run-manifest-2026-08-07`
