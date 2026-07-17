# Self-golden example (T-800)

Минимальный golden smoke для Loop Engineering v2.

## Проверка

Из корня плагина:

```bash
python3 scripts/t800_golden_check.py \
  --expected docs/examples/self-golden/expected.json \
  --root .
```

Exit `0` = PASS, `1` = FAIL. stdout — JSON.

## Обновить хеши (maintainer)

```bash
python3 scripts/t800_golden_check.py \
  --expected docs/examples/self-golden/expected.json \
  --root . \
  --write-hashes
```

## Смысл

Фиксируем наличие ключевых файлов loop v2 и (опционально) sha256 —
регрессия удаления скриптов/шаблонов ловится machine gate, не словами агента.
