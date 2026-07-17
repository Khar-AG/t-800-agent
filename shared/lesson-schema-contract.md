# Lesson Schema Contract (v1.0)

Канон одной записи в `{memory_path}/runs/<run_id>/lessons.json`.  
Потребители: `t800_lessons_export.py`, `t800_risk_classifier.py`,
`t800_lessons_to_fixpack.py`, `Task(t-800-loop-conductor)`.

## Корневой документ

```yaml
schema_version: "1.0"   # обязателен
run_id: string
generated_at: ISO8601
memory_path: string
lesson_count: int
lessons: [Lesson, ...]
```

## Lesson — поля

| Поле | Тип | Обязательно | Описание |
|------|-----|-------------|----------|
| `id` | string | да | Стабильный slug урока в рамках run |
| `severity` | `low` \| `medium` \| `high` | да | Человеческая тяжесть симптома (≠ risk_class) |
| `class` | string | да | Категория: `state_lesson`, `gate_fail`, `auditor`, … |
| `agent_id` | string \| null | да | Кто породил урок; `null` если из STATE |
| `evidence` | string[] | да | Пути/якоря доказательств (не пустой при export) |
| `symptom` | string | да | Что сломалось / чему научились |
| `proposed_patch` | object | да | Предлагаемый патч |
| `proposed_patch.files` | string[] | да | Относительные пути файлов (может быть `[]`) |
| `proposed_patch.change` | string | да | Кратко что изменить |
| `risk_class` | string | да | До classifier: **`unset`**. После — только скрипт |
| `recurrence_of` | string \| null | да | `id` предыдущего урока или `null` |

Опционально: `source` (например `STATE.md`).

## risk_class

Допустимые значения **после** classify:

`LOW` | `MEDIUM` | `HIGH` | `BLOCK_CANDIDATE`

Правила:

- До `t800_risk_classifier.py` поле = `unset` (не пустая строка, не `null` в каноне export).
- **Только** `scripts/t800_risk_classifier.py` назначает класс (denylist wins).
- LLM / агент / conductor **не** ставят `LOW`.

Контракт loop: `shared/loop-engineering-contract.md`.

## Минимальный пример

```json
{
  "schema_version": "1.0",
  "run_id": "example",
  "generated_at": "2026-07-17T12:00:00Z",
  "memory_path": "/path/to/memory",
  "lesson_count": 1,
  "lessons": [
    {
      "id": "state-1-example",
      "severity": "medium",
      "class": "state_lesson",
      "agent_id": null,
      "evidence": ["STATE.md##Lessons#1"],
      "symptom": "gate fail без machine evidence",
      "proposed_patch": {
        "files": ["scripts/t800_run_gate.py"],
        "change": "проверить exit code до «готово»"
      },
      "risk_class": "unset",
      "recurrence_of": null
    }
  ]
}
```

## Версия

- Введён: 2026-07-17 · Loop Engineering **v2** · schema **1.0**
