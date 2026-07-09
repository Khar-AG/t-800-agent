# /t800-bootstrap — первый запуск T-800

**Запускайте один раз** при установке плагина или для новичка в чате.

## Цепочка

### 1. Статус

```bash
bash scripts/first-run-status.sh
```

Если `needs_bootstrap: false` — достаточно `/t800-onboard`.

### 2. Аудит + объяснение

```
Task(t-800-onboard)
```

Передай: `first_run: true`, уровень новичок.

### 3. Глобальное правило (после согласия)

Спроси пользователя **один раз**:

«Установить глобальное правило: все subagents, skills, commands, rules и hooks создаются только через T-800 (`/t800-start`)? Работает во всех проектах.»

При **да**:

```bash
bash scripts/install-global-routing-rule.sh --yes
```

При **нет** — запиши в `~/.t800/state.json` отказ; предложи позже повторить `/t800-bootstrap`.

### 4. Reload Window

Напомни перезагрузить Cursor.

---

**После bootstrap** в чате: `/t800-onboard` (аудит) и `/t800-start` (создание артефактов).
