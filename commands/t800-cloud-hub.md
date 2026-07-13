# Cloud Hub / Client Automation Setup

**Команда:** `/t800-cloud-hub`  
**Алиас:** `/t800-hub-setup` (тот же лид, тот же контракт)

**Обязательно** вызови только:

```
Task(t-800-cloud-hub-lead)
```

Специалистов (`analyst` / `prompt` / `pack` / `smoke`) **не** вызывай вручную — их оркестрирует лид (selective fan-out).

## Контекст для лида

Передай:

- workspace / корень проекта;
- результат discovery (`profile`, `memory_path`, `plugin_root`) или попроси лида запустить discovery;
- цель: blank Hub + Client pack / schema / smoke / полный цикл;
- что уже есть в `{memory}/cloud-hub/` (если есть).

## Артефакты

Пишутся в **`{memory_path}/cloud-hub/`** по `shared/project-memory-dual-write-contract.md` + `shared/cloud-hub-setup-contract.md`:

- `capability-map.md`
- `hub-instructions.md`
- `client-instructions.md`
- `pack-schema.json`
- `smoke-report.md`

## Не в этой команде

- **Не** запускать `Task(t-800-cursor-kb-curator)` — каденс KB отдельно (scout / weekly / `/t800-update`).
- **Не** коммитить секреты и client job_pack в git плагина.

## Fallback

Если `Task(t-800-cloud-hub-lead)` недоступен:

```
Task(generalPurpose)
```

Промпт: полное содержимое `agents/t-800-cloud-hub-lead.md` из плагина T-800.

## UX

Ответы пользователю — на русском, без секретов в чате.
