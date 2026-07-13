# Cloud Hub Setup Contract

Универсальный закон **Blank Plugin-Checkout Hub** + Client TZ-builder для Cursor Automations.  
Отдел: `t-800-cloud-hub-*`. Команда: `/t800-cloud-hub` (алиас `/t800-hub-setup`).

## 1. Blank Plugin-Checkout Hub law

| Роль | Закон |
|------|--------|
| **Hub** | Thin Instructions; **пустые по смыслу до webhook**; умения = checkout плагина/репо (skills/commands/agents) |
| **Hub цикл** | `load_env` → materialize → resolve `command_ref` → execute → **app-level** callback → **STOP** |
| **Client** | Владеет полным **job_pack** TZ + git/publish; product-agnostic placeholders |
| **Repo** | No \| Single \| Multi — skill Hub требует **Single** (или Multi env) |

Hub не хранит постоянную «миссию продукта» в Instructions: контекст приходит с webhook/payload.

## 2. Secrets matrix

| Тип | Назначение | Заметки |
|-----|------------|---------|
| **EnvVar** | Имена переменных окружения Automation | Только имена в артефактах памяти, не значения |
| **Runtime** | Runtime secrets UI | **Runtime ≠ hard isolation** Terminal |
| **Build** | Build-time | Environment-scoped |

Secrets — environment-scoped. Учить оба UX: Dashboard «All repos» и scoped Secrets.

## 3. Auth (UI-derived caveats)

1. Сохранение webhook в UI → выдаются **URL + API key**.
2. Generate auth header в UI; community/практика Bearer `crsr_` — помечать как **UI-derived / community**, пока официальные docs не закрепят иначе.
3. Если отправитель не может выставить headers → middleware/proxy pattern.
4. **Не** выдавать Bearer/`crsr_` как цитату «из official automations.md», если там этого нет.

## 4. Automations inbound ≠ API HMAC

| Канал | Auth |
|-------|------|
| **Automations inbound** (webhook → agent) | UI key / Bearer (см. caveats выше) |
| **Cloud Agents API outbound** | HMAC / схемы из **api/webhooks** docs |

Не смешивать. Нет «HMAC для Automations inbound» как официального правила отдела.

## 5. Callbacks

**Нет** официального Automations inbound status-callback API.  
Результат — только **app-level `callbackUrl`** в job_pack (department schema), не invented Cursor primitive.

## 6. Permissions

Private | Team Visible | **Team Owned** — при Team Owned ключ **перевыпускается** (учесть в smoke).

## 7. Memory layout

Под каноническим `{memory_dir}` профиля (см. `project-memory-contract.md` + dual-write):

```text
{memory}/cloud-hub/
├── capability-map.md
├── hub-instructions.md
├── client-instructions.md
├── pack-schema.json
├── pack-schema-brief.md   # опционально
└── smoke-report.md
```

Dual-write ≠ duplicate roots: `shared/project-memory-dual-write-contract.md`.

## 8. Official URLs

- https://cursor.com/docs/cloud-agent/automations
- https://cursor.com/docs/cloud-agent/setup
- https://cursor.com/docs/cloud-agent/security-network
- https://cursor.com/docs/cloud-agent/settings
- https://cursor.com/docs/cloud-agent/api/webhooks

При расхождении с community — **docs > community**, caveats явно в smoke/Instructions.

## 9. FORBIDDEN

- Хардкод product / client_id / чужих имён клиентов в агентах и Instructions
- Клиентские секреты и job_pack в git / GitHub KB плагина T-800
- Invent официальных Automations auth / inbound JSON / status-callback schemas
- Копирование EXAMPLE_CORPUS / research dumps как «Cursor API»
- Specialist → specialist; depth > 2
- Вызов kb-curator на каждый hub-setup

## 10. Связанные артефакты

- Агенты: `t-800-cloud-hub-lead` (+ analyst, prompt, pack, smoke)
- KB cadence: `t-800-cursor-kb-curator` → `t-800-maintainer`
- Примеры паттернов: `docs/examples/cloud-hub/README.md` (EXAMPLE only)
