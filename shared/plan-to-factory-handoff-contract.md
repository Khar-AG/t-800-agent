# Plan → Factory Handoff Contract (v1.0)

Контракт перехода от **утверждённого плана** (CreatePlan / Plan mode) к **Implement**.  
Цель: не повторять инцидент Zen Intel — когда в плане был `/t800-start` / factory, а Implement сразу правил файлы в main chat.

Связано: `rules/t-800-mandatory-routing.mdc`, `shared/fix-pipeline-contract.md`, `shared/department-orchestration-contract.md`.

## Закон

Если в **approved plan** есть любой из маркеров:

| Маркер в плане | Значение |
|----------------|----------|
| `factory-brief` / `factory-briefs/` | Нужен конвейер factory |
| `/t800-start` | CREATE через T-800 |
| `/t800-fix` | PATCH через T-800 |
| `Task(t-800-factory)` | Прямой handoff на factory |
| CREATE/PATCH `agents/` · `skills/` · `commands/` · `rules/` · `hooks` | Cursor-артефакты |

то **первый шаг Implement** — команда `/t800-start` или `/t800-fix` (и `Task(t-800-factory)` внутри лида), **не** `Write` / `StrReplace` / правки файлов в main chat.

```text
CreatePlan (approved, содержит factory) 
  → Implement стартует с /t800-start|/t800-fix
  → scout? → research? → brain → factory → auditor → t800_run_gate
  → НЕ: main chat правит agents/*.md напрямую
```

## Анти-паттерн (запрещён)

```text
CreatePlan → user "Implement the plan" → Agent mode Write agents/foo.md
```

Это обход T-800. Machine gates:

- `scripts/t800_factory_bypass_gate.py`
- `scripts/t800_run_gate.py --strict-create`
- hook `hooks/before-artifact-edit.sh` (v1: WARN)

## Обязанности Директора

1. Перед первой правкой артефакта — проверить план на маркеры выше.
2. Если маркер есть — делегировать `Task(t-800-factory)` / запустить `/t800-fix` по fix-pack; **не** писать файлы сам.
3. Обычный код (не cursor-artifacts) можно править без factory.
4. После factory — `t800_run_gate.py` (для CREATE/production — с `--strict-create`).

## BLOCKER

| Ситуация | Действие |
|----------|----------|
| Plan требует factory, Implement начал file edits | **STOP** → переключить на `/t800-start`\|`/t800-fix` |
| Нет fix-pack / brief, но нужны agents/skills | Создать brief / pack, затем factory |
| Пользователь явно сказал «без T-800 / руками» | Зафиксировать в STATE Lessons; gates всё равно могут FAIL |

## Версия

- Введён: 2026-07-14 · инцидент Zen Intel (factory bypass)
- Enforcement: rules (advisory) + hooks WARN + machine gates FAIL
