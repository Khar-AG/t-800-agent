---
title: "permissions.json"
source: https://cursor.com/docs/reference/permissions
audience: beginner
tier: 3
last_synced: 2026-07-02
---

## Простыми словами

Файл с белыми списками: какие MCP и терминальные команды разрешены без лишних вопросов.

## Когда вам это нужно

Повторяете одни и те же безопасные команды (npm test, git status) и устали подтверждать.

## Ключевые поля (концептуально)

- `terminalAllowlist` — разрешённые команды
- `mcpAllowlist` — разрешённые MCP-инструменты
- `autoRun` — что можно без подтверждения

## Важно для новичка

Начните с **Auto-review** в UI. `permissions.json` — когда уже понимаете, что делаете.

## Официальная ссылка

https://cursor.com/docs/reference/permissions
