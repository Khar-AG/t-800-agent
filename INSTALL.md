# T-800 Agent — установка v1.13.0

## Рекомендуемый способ

См. [`docs/СЦЕНАРИЙ-СТАРТА.md`](docs/СЦЕНАРИЙ-СТАРТА.md)  
Обновление со старой версии: [`docs/ОБНОВЛЕНИЕ.md`](docs/ОБНОВЛЕНИЕ.md)

Плагин **v1.13.0** — **36** субагентов + fix/doctor/run_gate: `/t800-fix`, `/t800-doctor`, `/t800-plugin-audit` → fix-pack, loop engineering.

## Ручная установка / обновление

```bash
cd t-800-agent
bash scripts/install-plugin.sh
bash scripts/verify-install.sh
```

→ **Reload Window**

## Команды

| Команда | Зачем |
|---------|--------|
| `/t800-doctor` | Здоровье системы / плагина |
| `/t800-plugin-audit` | Карта одного плагина (inventory/graph/orphans) |
| `/t800-fix` | Правка по fix-pack |
| `/t800-audit` | Разбор лишних rules системы Cursor |
| `/t800-update` | Инструкция обновления |
| `/t800-start` | Создать артефакт |
| `/t800-bootstrap` | Первый старт |
