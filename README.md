# T-800 Agent

<p align="center">
  <img src="assets/t800-cover.png" alt="T-800 Агент — обложка" width="920"/>
</p>

<p align="center">
  <strong>Цех Skynet для Cursor</strong><br/>
  Система помощи для работы с плагинами, субагентами, командами, skills и правилами.<br/>
  <em>«Я не тот Скайнет, о котором вы могли бы подумать.»</em>
</p>

<p align="center">
  <a href="https://github.com/Khar-AG/t-800-agent/releases"><img alt="version" src="https://img.shields.io/github/v/release/Khar-AG/t-800-agent?include_prereleases&label=version&color=red"/></a>
  <a href="https://github.com/Khar-AG/t-800-agent"><img alt="stars" src="https://img.shields.io/github/stars/Khar-AG/t-800-agent?style=social"/></a>
  <img alt="agents" src="https://img.shields.io/badge/субагентов-36-blue"/>
  <img alt="license" src="https://img.shields.io/badge/license-MIT-green"/>
</p>

---

## Зачем это нужно

В Cursor легко накопить хаос: десятки rules, skills, команд и субагентов «на глаз».  
**T-800 Agent** — плагин-отдел, который помогает **правильно создавать, править и разбирать** эту систему.

Он закрывает технический процесс вокруг Cursor:

- создание и правка **команд**, **skills**, **субагентов**, **правил**, **hooks**;
- **аудит Cursor** — что жрёт контекст, что лишнее;
- **аудит плагинов** — карта агентов, цепочки, слабые места;
- исследование свежих практик (GitHub, docs, cookbooks) перед сборкой;
- полуавтообновление плагина с GitHub — без zip в чатах.

```text
Система → Research → Мозги → Factory
```

| Этап | Что делает |
|------|------------|
| **Система** | Онбординг, doctor, аудит, обновление |
| **Research** | Сам ищет, где смотреть актуальное |
| **Мозги** | Сверяет с документацией Cursor |
| **Factory** | Собирает артефакт и проверяет machine gate |

---

## Что умеет

### Создание и правка артефактов Cursor
- субагенты (`agents/*.md`);
- skills (`.cursor/skills/`);
- slash-команды;
- rules;
- hooks и сопутствующие scripts.

Команды: **`/t800-start`** (создать) · **`/t800-fix`** (точечно поправить).

### Аудит Cursor
Разбор глобальных/локальных rules и skills: что нужно, что раздувает контекст, что можно сузить или убрать.  
Команда: **`/t800-audit`**.

### Аудит плагинов
Полная карта одного плагина: агенты, команды, skills, rules, граф связей, orphans, alwaysApply.  
Отчёт пишется в память **целевого** проекта (например `plugin-memory/audits/`), не в KB T-800.  
Команда: **`/t800-plugin-audit`** → при необходимости **`/t800-fix`**.

### Здоровье и обновление
- **`/t800-doctor`** — быстрая диагностика установки;
- **`/t800-update`** — сравнить версию с GitHub и обновиться;
- **`/t800-bootstrap`** / **`/t800-onboard`** — первый запуск и обзор.

---

## Быстрый старт

### Установка

```bash
git clone https://github.com/Khar-AG/t-800-agent.git
cd t-800-agent
bash scripts/install-plugin.sh
bash scripts/verify-install.sh
```

В Cursor: **Developer: Reload Window** → `/t800-bootstrap`

### Обновление (без zip в чате)

```text
/t800-update
```

или:

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh
```

Скрипт читает версию с `main`, сравнивает с локальной и при отличии ставит новую. Затем снова **Reload Window**.

Только проверка:

```bash
bash ~/.cursor/plugins/local/t-800-agent/scripts/t800-update-from-github.sh --check
```

---

## Основные команды

| Команда | Зачем |
|---------|--------|
| `/t800-bootstrap` | Первый запуск |
| `/t800-start` | Создать skill / agent / rule / command / hook |
| `/t800-fix` | Точечная правка |
| `/t800-doctor` | Здоровье установки |
| `/t800-audit` | Аудит Cursor (лишние rules/skills) |
| `/t800-plugin-audit` | Аудит одного плагина |
| `/t800-update` | Обновление с GitHub |
| `/t800-onboard` | Что установлено |

---

## Как устроена команда

36 субагентов в отделах System / Research / Brains / Factory.  
Директор зовёт **лидов**, специалисты запускаются внутри отдела автоматически.

Память прогонов — в **целевом проекте** (`teya-memory/`, `plugin-memory/`, `t-800-memory/`…), не как «канон чужого плагина» внутри T-800.

Канал обновлений: [`shared/release-channel.json`](shared/release-channel.json)

---

## Релиз для автора

```bash
# bump version в .cursor-plugin/plugin.json
bash scripts/install-plugin.sh
bash scripts/verify-install.sh
git add -A && git commit -m "Release vX.Y.Z" && git push origin main
# опционально: gh release create vX.Y.Z
```

У команды после этого достаточно `/t800-update`.

---

## Лицензия

MIT — см. [LICENSE](LICENSE)

---

*T-800 Agent · цех сборки субагентов Skynet для Cursor*
