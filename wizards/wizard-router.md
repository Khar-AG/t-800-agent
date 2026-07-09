# Wizard Router — куда вести новичка

## Схема выбора

```mermaid
flowchart TD
    start[Что вы хотите?]
    understand[Понять проект]
    change[Внести правку]
    automate[Автоматизация]
    error[Исправить ошибку]
    mcp[Подключить сервис]
    canvas[Сделать отчёт или поделиться]

    start --> understand
    start --> change
    start --> automate
    start --> error
    start --> mcp
    start --> canvas
```

## Маршруты

| Намерение | Режим Cursor | Wizard |
|-----------|--------------|--------|
| Понять проект | Ask | `wizard-first-project.md` |
| Маленькая правка | Agent после Ask | `wizard-first-project.md` |
| Большая задача | Plan | `wizard-first-project.md` |
| Автоматизация | Plan → Agent | `wizard-automation.md` |
| Ошибка | Debug | `wizard-fix-error.md` |
| Внешний сервис | Plan | `wizard-connect-mcp.md` |
| Отчёт / дашборд | Agent + Canvas | `wizard-share-canvas.md` |
