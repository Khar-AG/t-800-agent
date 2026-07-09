---
title: "Teya — 7 частей Task-промпта"
audience: advanced
last_synced: 2026-07-06
---

# 7 частей Task (выжимка Teya)

Полный контракт: `$TEYA_PLUGIN_ROOT/shared/task-prompt-discipline.md`

1. **РОЛЬ** — агент + skill
2. **РЕЖИМ** — если есть режимы
3. **ВХОДЫ** — пути от PROJECT_ROOT / TEYA_PLUGIN_ROOT
4. **ЗАДАЧА** — нумерованные шаги
5. **ВЫХОДЫ** — файлы + fragment с маркером `=== ИМЯ ===`
6. **КРИТЕРИИ** — PASS условия
7. **ЗАПРЕТЫ** — не Task(), не production без разрешения

Статусы: только `PASS` | `WARN` | `BLOCKER`
