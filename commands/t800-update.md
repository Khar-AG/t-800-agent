# /t800-update — обновление T-800 с GitHub

**Полуавтомат:** сравнить версию на GitHub с локальной → при отличии скачать и установить.

Канал: `shared/release-channel.json` → репозиторий **Khar-AG/t-800-agent** (ветка `main`).

## В чате (рекомендуется)

```text
/t800-update
```

или:

```text
Обнови T-800 Agent с GitHub.
```

Директор обязан:

```bash
bash "$HOME/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh"
```

Если плагин ещё не в `plugins/local` — клонировать репо и `install-plugin.sh`, затем снова update.

## Только проверка

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh --check
# exit 0 = актуально; exit 10 = есть обновление
```

## Принудительно

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh --force
```

## После обновления

1. **Developer: Reload Window**
2. `/t800-doctor` или `/t800-onboard`
3. Показать локальную версию:

```bash
python3 -c "import json; print(json.load(open('$HOME/.cursor/plugins/local/t-800-agent/.cursor-plugin/plugin.json'))['version'])"
```

## Старый способ (zip)

Если нет сети к GitHub — положите zip и попросите Agent разархивировать + `install-plugin.sh` (legacy).

## Закон

Не говори «готово» без успешного скрипта (или явного UP_TO_DATE) и напоминания про **Reload Window**.
