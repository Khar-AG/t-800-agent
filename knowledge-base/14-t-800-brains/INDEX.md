---
title: "Отдел Мозги — карта библиотекарей"
audience: advanced
tier: 4
last_synced: 2026-07-06
---

# Мозги T-800 Agent

Доменные субагенты с полной локальной KB Cursor. Вызываются через `t-800-brain-lead`.

| Task | Домен | KB |
|------|-------|-----|
| `t-800-brain-agents` | Agent, режимы, prompting | `02-agent-i-rezhimy/` |
| `t-800-brain-context` | Rules, skills, subagents, MCP | `03-kontekst/` |
| `t-800-brain-cloud` | Cloud, automations, hooks | `10-cloud-automation/` |
| `t-800-brain-dev` | CLI, SDK, API | `12-advanced-dev/` |
| `t-800-brain-admin` | Teams, billing, integrations | `11-team-admin/` |
| `t-800-brain-security` | Security, Run Modes | `04-bezopasnost/` |
| `t-800-brain-tools` | Terminal, Browser, Search | `09-tools/` |
| `t-800-brain-teya` | Teya Pro plugin | `15-teya-pro-plugin/` |

## Разведчик

`t-800-scout` — проверка обновлений на cursor.com vs `manifest.json`.

## Цепочка

```
t-800-scout → t-800-brain-lead → domain brain(s) → t-800-factory
```

## Синхронизация KB

`Task(t-800-maintainer)` + `scripts/sync-docs.ps1` — обновление карточек из официальных URL.
