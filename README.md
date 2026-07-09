# T-800 Agent

<p align="center">
  <img src="assets/t800-cover.png" alt="T-800 Agent cover" width="920"/>
</p>

<p align="center">
  <strong>Цех Skynet для Cursor</strong> — создавай и правь субагентов, skills, rules, commands и hooks правильно.<br/>
  Публичный плагин с <strong>полуавтообновлением с GitHub</strong>.
</p>

<p align="center">
  <a href="https://github.com/Khar-AG/t-800-agent/releases"><img alt="version" src="https://img.shields.io/github/v/release/Khar-AG/t-800-agent?include_prereleases&label=version&color=red"/></a>
  <a href="https://github.com/Khar-AG/t-800-agent"><img alt="stars" src="https://img.shields.io/github/stars/Khar-AG/t-800-agent?style=social"/></a>
  <img alt="agents" src="https://img.shields.io/badge/agents-36-blue"/>
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green"/>
</p>

---

## Что это

**T-800 Agent** — плагин для [Cursor](https://cursor.com): отдел, который помогает не «набросать промпт», а собрать артефакты Cursor по конвейеру:

```text
System → Research → Brains → Factory
```

| Отдел | Зачем |
|-------|--------|
| **System** | onboard, audit, doctor, update |
| **Research** | сам выбирает, где искать (GitHub, ClawHub, cookbooks…) |
| **Brains** | сверка с документацией Cursor |
| **Factory** | сборка agent / skill / rule / command / hook |

Память прогонов пишется в **целевой проект**, не в чужой канон плагина.

---

## Быстрый старт

### 1. Установка (первый раз)

```bash
git clone https://github.com/Khar-AG/t-800-agent.git
cd t-800-agent
bash scripts/install-plugin.sh
bash scripts/verify-install.sh
```

В Cursor: **Developer: Reload Window** → `/t800-bootstrap`

### 2. Обновление (потом — без zip в чате)

```text
/t800-update
```

или в терминале:

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh
```

Скрипт:

1. читает версию с GitHub (`main`);
2. сравнивает с локальной;
3. если новее — скачивает архив ветки и запускает `install-plugin.sh`;
4. просит **Reload Window**.

Проверка без установки:

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh --check
```

---

## Команды

| Команда | Зачем |
|---------|--------|
| `/t800-bootstrap` | Первый запуск + глобальное правило по согласию |
| `/t800-start` | Создать skill / agent / rule / command / hook |
| `/t800-fix` | Точечная правка по fix-pack |
| `/t800-doctor` | Здоровье установки |
| `/t800-audit` | Разбор «жира» Cursor (rules/skills) |
| `/t800-plugin-audit` | Карта одного плагина (граф, orphans) |
| **`/t800-update`** | Обновление с GitHub |
| `/t800-onboard` | Что установлено |

---

## Структура

```text
t-800-agent/
├── agents/           # 36 субагентов
├── commands/         # slash-команды
├── rules/            # routing rules
├── scripts/          # install, update, audit, gates
├── shared/           # контракты + release-channel.json
├── knowledge-base/   # KB Cursor
└── .cursor-plugin/plugin.json
```

Канал обновлений: [`shared/release-channel.json`](shared/release-channel.json)

---

## Для автора релиза

После правок в этом репозитории:

```bash
# bump version в .cursor-plugin/plugin.json
bash scripts/install-plugin.sh
bash scripts/verify-install.sh
git add -A && git commit -m "Release vX.Y.Z" && git push origin main
# опционально: gh release create vX.Y.Z
```

Команда у команды: `/t800-update` — подтянет `main`.

---

## Лицензия

MIT — см. [LICENSE](LICENSE)

---

*T-800 Agent · цех сборки субагентов Skynet*
