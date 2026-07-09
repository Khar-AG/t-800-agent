# Auto Version Check Contract (v1.15)

Автопроверка версии T-800 при старте сессии Cursor — без ручного `/t800-update` каждый раз.

## Цель

1. При **новом чате** (`sessionStart`) сравнить локальную версию с GitHub (`release-channel.json`).
2. Если remote новее — **скачать и установить** (`t800-update-from-github.sh`).
3. Сообщить агенту через `additional_context`: обновлено → попросить **Reload Window** → **продолжить исходную задачу**.
4. Если версия та же / нет сети — **не мешать** работе (fail-open).

## Компоненты

| Файл | Роль |
|------|------|
| `hooks.json` → `sessionStart` | Триггер |
| `hooks/t-800-session-bootstrap.sh` | JSON stdout для Cursor |
| `scripts/t800-auto-version-check.sh` | Сравнение + apply |
| `scripts/t800-update-from-github.sh` | Скачивание архива + install |
| `shared/release-channel.json` | URL репозитория |

## Поведение

```text
sessionStart
  → t800-auto-version-check.sh --json
       → cache TTL (default 6ч) → skip network
       → curl plugin.json с GitHub (timeout короткий)
       → если remote > local → t800-update-from-github.sh
  → stdout JSON:
       additional_context (если updated/available/failed/bootstrap)
       env.T800_VERSION_STATUS / T800_PLUGIN_UPDATED
```

## Закон для Директора (агента)

Если в контексте сессии есть сигнал обновления:

1. Одной строкой сказать пользователю, что T-800 обновился.
2. Попросить **Developer: Reload Window**.
3. После Reload — продолжить **ту же** задачу пользователя (не сбрасывать прогресс без нужды).

## Отключение

```bash
export T800_SKIP_AUTO_UPDATE=1
```

Принудительная проверка (игнор TTL):

```bash
export T800_FORCE_VERSION_CHECK=1
bash scripts/t800-auto-version-check.sh
```

## Ограничения Cursor

- `sessionStart` — fire-and-forget: сессию не блокирует.
- Hook **не** умеет сам сделать Reload Window — только попросить пользователя/агента.
- Cloud Agents: `sessionStart` может не работать — там обновление вручную `/t800-update`.

## Версия

Введён: 2026-07-09 · T-800 **1.15.0**
