# Project Memory Dual-Write Contract

Дополнение к **`shared/project-memory-contract.md`** (истина по profile→`memory_dir`).  
Этот файл **не** создаёт конкурирующий корень памяти.

## Истина корня

| Правило | Смысл |
|---------|--------|
| Truth root | Только таблица profile → `memory_dir` в `project-memory-contract.md` |
| Dual-write | Писать cloud-hub артефакты **внутрь** канонического `memory_dir`, подпапка `cloud-hub/` |
| ≠ duplicate roots | Запрещено плодить вторую `t-800-memory/` «рядом» для тех же данных клиента |

## Профиль → cloud-hub путь

| profile | Куда писать cloud-hub |
|---------|------------------------|
| `self-t800` | `t-800-memory/cloud-hub/` |
| `generic-plugin` | `{slug}-memory/cloud-hub/` (или marker memory) |
| `teya-client` | **`teya-memory/cloud-hub/` native-first**; **не** создавать параллельную `t-800-memory/` в клиенте для cloud-hub данных |
| `teya-plugin-dev` | `plugin-memory/cloud-hub/` или run-scoped `.teya-plugin-run/cloud-hub/` |

Discovery: `scripts/discover-target-project.sh` → использовать его `memory_path`.

## Что можно dual-write

- Черновики Instructions Hub/Client
- `pack-schema.json`, smoke-report, capability-map
- Fragments прогона отдела в `{memory}/fragments/`

## FORBIDDEN в T-800 GitHub knowledge-base

- Client `job_pack` с боевыми данными
- Site/product secrets, API keys, webhook tokens
- Дампы полей чужого продукта как «шаблоны Cursor»
- Копирование клиентских Instructions из production в `knowledge-base/`

KB плагина — только **обобщённые** beginner-карточки и EXAMPLE patterns (см. `docs/examples/cloud-hub/`).

## Gitignore (guidance)

Если в client memory появляются секреты / локальные pack с ключами:

- Не коммитить `{memory}/cloud-hub/*secrets*`
- Локальные `.env`, raw webhook keys — вне git
- В отчётах агентов — только имена EnvVar

## Связь

- Layout файлов: `shared/cloud-hub-setup-contract.md` § Memory layout
- Канон памяти: `shared/project-memory-contract.md` § Cloud Hub artifacts
