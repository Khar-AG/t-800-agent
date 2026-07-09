---
title: "Карта базы знаний T-800"
audience: beginner
last_synced: 2026-07-02
---

# База знаний T-800 Agent

Упрощённые выжимки из официальной документации Cursor на русском.

## С чего начать

| День | Что изучить | Файлы |
|------|-------------|-------|
| **День 1** | Установка, первая папка, Agent, Ask/Plan/Debug, Tab | `01-pervye-shagi/`, `02-agent-i-rezhimy/` |
| **Неделя 1** | Rules, Skills, diff, review, checkpoints, prompting | `03-kontekst/`, `02-agent-i-rezhimy/agent-review.md`, `prompting.md` |
| **Месяц 1** | Terminal, Browser, Search, MCP, subagents, Canvas | `09-tools/`, `03-kontekst/mcp-basics.md`, `canvas-i-shared-canvases.md` |
| **Позже** | Cloud Agents, Automations, Teams, CLI, SDK, API | `10-cloud-automation/`, `11-team-admin/`, `12-advanced-dev/` |

## Профили и wizards

- [Профили новичков](../profiles/beginner-profiles.md)
- [Cursor за 7 дней](learning-path-7-days.md)
- [Типичные проблемы новичков](typical-beginner-failures.md)
- [Wizard Router](../wizards/wizard-router.md)
- [Первый проект](../wizards/wizard-first-project.md)
- [Первая автоматизация](../wizards/wizard-automation.md)
- [Подключить MCP](../wizards/wizard-connect-mcp.md)
- [Исправить ошибку](../wizards/wizard-fix-error.md)
- [Canvas и Shared Canvas](../wizards/wizard-share-canvas.md)

## Разделы

### 01 — Первые шаги
- [Установка и вход](01-pervye-shagi/ustanovka-i-vhod.md)
- [Первая папка](01-pervye-shagi/pervaya-papka.md)
- [Tab — автодополнение](01-pervye-shagi/tab-avtodopolnenie.md)

### 02 — Agent и режимы
- [Что такое Agent](02-agent-i-rezhimy/chto-takoe-agent.md)
- [Agents Window](02-agent-i-rezhimy/agents-window.md)
- [Таблица режимов](02-agent-i-rezhimy/rezhimy-tablica.md)
- [Ask Mode](02-agent-i-rezhimy/ask-mode.md)
- [Plan Mode](02-agent-i-rezhimy/plan-mode.md)
- [Debug Mode](02-agent-i-rezhimy/debug-mode.md)
- [Design Mode](02-agent-i-rezhimy/design-mode.md)
- [Prompting](02-agent-i-rezhimy/prompting.md)
- [Agent Review](02-agent-i-rezhimy/agent-review.md)
- [Контрольные точки](02-agent-i-rezhimy/kontrolnye-tochki.md)
- [Очередь сообщений](02-agent-i-rezhimy/ochered-soobscheniy.md)
- [Canvas и Shared Canvases](02-agent-i-rezhimy/canvas-i-shared-canvases.md)

### 03 — Контекст
- [Rules](03-kontekst/rules.md)
- [Skills](03-kontekst/skills.md)
- [Subagents](03-kontekst/subagents.md)
- [MCP — основы](03-kontekst/mcp-basics.md)
- [@file и контекст](03-kontekst/ssylki-kontekst.md)

### 04 — Безопасность
- [Run Mode](04-bezopasnost/run-mode.md)
- [Security и Run Modes](04-bezopasnost/security-run-modes.md)
- [permissions.json](04-bezopasnost/permissions.md)
- [Что не давать агенту](04-bezopasnost/chto-ne-davat-agentu.md)

### 05 — Практика
- [Plan Mode workflow](05-praktika/plan-mode-workflow.md)
- [Ревью diff](05-praktika/review-diff.md)
- [Troubleshooting](05-praktika/troubleshooting.md)
- [Cursor за 7 дней](learning-path-7-days.md)
- [Типичные проблемы новичков](typical-beginner-failures.md)

### 06 — Облако и API (позже)
- [Cloud Agents](06-oblako-i-api/cloud-agents.md)
- [API — обзор](06-oblako-i-api/api-overview.md)

### 07 — Курсы Learn
- [Работа с агентами](07-learn-kursy/working-with-agents.md)

### 08 — FAQ Help
- [Agent FAQ](08-help-faq/agent-faq.md)
- [Tab FAQ](08-help-faq/tab-faq.md)
- [Тарифы и лимиты](08-help-faq/pricing-i-limity.md)

### 09 — Tools
- [Terminal tool](09-tools/terminal.md)
- [Browser tool](09-tools/browser.md)
- [Search tool](09-tools/search.md)

### 10 — Cloud и автоматизация
- [Cloud Agents setup](10-cloud-automation/cloud-agents-setup.md)
- [Cloud Agent Settings](10-cloud-automation/cloud-agent-settings.md)
- [Automations](10-cloud-automation/automations.md)
- [Hooks](10-cloud-automation/hooks.md)

### 11 — Команда и администрирование
- [Teams и Dashboard](11-team-admin/teams-dashboard.md)
- [Pricing, usage limits и модели](11-team-admin/pricing-usage-limits.md)
- [Integrations](11-team-admin/integrations.md)
- [Bugbot и Security Agents](11-team-admin/bugbot-security-agents.md)

### 12 — Продвинутый dev-слой
- [Cursor CLI](12-advanced-dev/cli.md)
- [Cursor SDK](12-advanced-dev/sdk.md)
- [Cloud Agents API](12-advanced-dev/cloud-agent-api.md)

### Универсальная память проектов
- [16-universal-project-memory/INDEX.md](16-universal-project-memory/INDEX.md)

### Справочник
- [Карта покрытия manifest](00-meta/manifest-coverage-map.md)
- [Глоссарий](glossarium.md)
- [Changelog](CHANGELOG.md)
- [Очередь обновлений](UPDATE-QUEUE.md)
- [Отчёт покрытия](COVERAGE-REPORT.md)
- [Health report](HEALTH-REPORT.md)
- [Manifest (свежесть)](manifest.json)

## Обновление базы

Если в Cursor появилось что-то новое:

1. `.\scripts\sync-docs.ps1`
2. `.\scripts\audit-coverage.ps1`
3. `UPDATE-QUEUE.md` → упростить для новичков
4. `CHANGELOG.md` → записать изменение
5. `.\scripts\install-plugin.ps1`
6. `.\scripts\verify-install.ps1`

## Playbooks

- [00 — Первый раз](../playbooks/00-pervyy-raz.md)
- [01 — Первая автоматизация](../playbooks/01-pervaya-avtomatizaciya.md)
- [02 — Подключить MCP](../playbooks/02-podklyuchit-mcp.md)
- [03 — Создать субагента](../playbooks/03-sozdat-subagenta.md)
- [04 — Откат и безопасность](../playbooks/04-otkat-i-bezopasnost.md)
- [05 — T-800 Factory: создать субагента](../playbooks/05-t-800-factory-workflow.md)

### 13 — T-800 Factory (продвинутый)
- [Карта раздела](13-agent-factory/INDEX.md)
- [Гайд по созданию субагентов](13-agent-factory/subagent-creation-guide.md)
- [Subagent vs Skill vs Rule](13-agent-factory/agent-vs-skill-vs-command.md)
- [Граф связей](13-agent-factory/relationship-graph.md)
- [Масштаб 100+](13-agent-factory/scaling-100-plus.md)
- [Hooks и скрипты](13-agent-factory/hooks-and-scripts.md)
- Реестр: `../registry/agents-registry.json`

### 14 — Мозги T-800
- [Карта библиотекарей](14-t-800-brains/INDEX.md)

### 15 — Teya Pro (для конвейера)
- [Карта раздела](15-teya-pro-plugin/INDEX.md)
- [Канонические пути](15-teya-pro-plugin/canonical-paths.md)
- [Чеклист качества агента](15-teya-pro-plugin/agent-quality-checklist.md)
- [Release handoff](15-teya-pro-plugin/plugin-release-handoff.md)

## Официальные источники

- https://cursor.com/ru/docs
- https://cursor.com/ru/learn
- https://cursor.com/ru/help
- https://cursor.com/ru/docs/api
