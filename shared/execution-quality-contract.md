# T-800 — контракт точности исполнения

Снижает «ручную сборку» и пропуски в конвейере.

## Gates (обязательны)

| # | Gate | Кто |
|---|------|-----|
| G1 | `first-run-status.sh` при `/t800-bootstrap` | Директор |
| G2 | `discover-target-project.sh` + surface | factory lead |
| G3 | `research_brief` если нужна свежесть | research-lead |
| G4 | fragment в `{memory_path}/fragments/` каждый Task | все субагенты |
| G5 | `validate-agents` + `audit-agent-graph` | auditor |
| G6 | Глобальное routing rule после bootstrap | install script |

## Запреты main Agent

- Не писать `agents/*.md`, `SKILL.md`, `commands/*.md`, `rules/*.mdc` без `Task(t-800-factory)`
- Исключение: `install-global-routing-rule.sh` по bootstrap с согласия

## Точность Task-промптов

7 частей (`shared/t-800-task-prompt-discipline.md`) + в ВХОДЫ:

- `target_context` JSON
- `artifact_surface`
- `research_brief` (если есть)
- пути audit/first-run отчётов

## Readonly sandbox

research-*, brain-*, architect, auditor, onboard — `readonly: true`

## Метрика «круто исполнено»

- [ ] Есть fragment PASS
- [ ] Артефакт на диске в правильной surface
- [ ] registry обновлён (если plugin)
- [ ] Пользователю дан следующий шаг одной фразой
