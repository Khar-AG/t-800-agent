# /t800-update — обновление T-800 с GitHub

**Автомат:** при каждом **новом чате** hook `sessionStart` сам сравнивает версию с GitHub и при необходимости ставит обновление (`shared/auto-update-contract.md`).  
**Вручную:** эта команда — если нужно обновить прямо сейчас или автопроверка была пропущена.

Канал: `shared/release-channel.json` → **Khar-AG/t-800-agent** (`main`).

## Авто (по умолчанию)

При старте сессии Cursor:

1. `hooks/t-800-session-bootstrap.sh` → `t800-auto-version-check.sh`
2. если на GitHub версия новее — скачивание + `install-plugin.sh`
3. агенту в контекст: «обновлено → Reload Window → продолжи задачу»

Отключить: `export T800_SKIP_AUTO_UPDATE=1`

## Вручную в чате

```text
/t800-update
```

Директор:

```bash
bash "$HOME/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh"
# или
bash "$HOME/.cursor/plugins/local/t-800-agent/scripts/t800-auto-version-check.sh" --force
```

## Только проверка

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh --check
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-auto-version-check.sh --check-only
```

## После обновления

1. **Developer: Reload Window** (обязательно — иначе в памяти сессии старые агенты)
2. Продолжить исходную задачу пользователя
3. Версия:

```bash
python3 -c "import json; print(json.load(open('$HOME/.cursor/plugins/local/t-800-agent/.cursor-plugin/plugin.json'))['version'])"
```

## Закон

Не говори «готово» без успешного обновления/UP_TO_DATE и напоминания про **Reload Window**, если файлы на диске менялись.
