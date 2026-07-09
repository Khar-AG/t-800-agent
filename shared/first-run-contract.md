# T-800 — первый запуск (bootstrap)

## Закон

1. **Первый раз** — `/t800-bootstrap`, не `/t800-start` для создания артефактов.
2. Порядок: аудит → объяснение → **согласие** → глобальное rule.
3. Rule **не** ставится без явного «да» пользователя.

## Скрипты

| Скрипт | Назначение |
|--------|------------|
| `first-run-status.sh` | `needs_bootstrap` |
| `install-global-routing-rule.sh --yes` | `~/.cursor/rules/t-800-mandatory-routing.mdc` |
| `t800-state.sh` | `~/.t800/state.json` |

## Глобальное правило

Файл: `~/.cursor/rules/t-800-mandatory-routing.mdc`  
`alwaysApply: true` — во **всех** проектах.

Содержание: subagents/skills/commands/rules/hooks → только через `/t800-start` и конвейер T-800.

## Повтор

Пользователь отказал → позже снова `/t800-bootstrap`.

Уже установлено → `first-run-status.sh` → `needs_bootstrap: false`.
