# Cloud Hub — EXAMPLE patterns (anonymized)

**Метка:** `EXAMPLE_CORPUS` — учебные паттерны полей.  
**Не** копировать как официальный Cursor Automations API.  
**Нет** реальных секретов, host production, имён клиентов.

## Job pack field patterns

| Field | Role |
|-------|------|
| `requestId` | Корреляция запроса Client↔Hub |
| `task` | Краткое ТЗ / описание задания |
| `command_ref` | Ссылка на command/skill из checkout Hub |
| `callbackUrl` | App-level URL результата (не official Automations callback API) |
| `payload` | Произвольный объект данных задания |

## Minimal example (fake)

```json
{
  "requestId": "req_example_001",
  "task": "Run documented command from checkout",
  "command_ref": "example-command",
  "callbackUrl": "https://app.example.com/hooks/result",
  "payload": {
    "note": "generic placeholder only"
  }
}
```

## Auth notes (not official schema)

- Automations inbound webhook auth — см. UI + `shared/cloud-hub-setup-contract.md` (UI-derived Bearer caveat).
- Cloud Agents API outbound — см. official api/webhooks (HMAC и т.п.) — **другой** канал.

## Forbidden in this folder

- Реальные API keys / `crsr_` tokens
- Имена конкретных клиентских проектов
- Product field dumps как «закон Cursor»
