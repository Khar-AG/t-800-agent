# Department Orchestration Contract (v1.12.0)

Контракт взаимодействия отделов T-800. **Новых агентов в Research/Brains не добавляем** — усиливаем логику вызовов и прогресс.  
Loop / STATE / machine gates: `shared/loop-engineering-contract.md`.

## Четыре отдела (+ system-adjacent)

| Отдел | Лид | Специалисты | Кто запускает |
|-------|-----|-------------|---------------|
| **System / Mentor** | — | onboard, system-auditor, **plugin-auditor**, operator, intake-clarifier, maintainer, **cursor-kb-curator**† | Директор по команде (`/t800-*`) |
| **Research** | `t-800-research-lead` | strategist, github, repo-miner, community, clawhub, vendor-docs, docs, news, synthesizer, prompt-craft* | Директор → **lead сам** fan-out |
| **Brains** | `t-800-brain-lead` | agents, context, cloud, dev, admin, security, tools, teya | Директор → **lead сам** выбирает 1–2 domain |
| **Factory** | `t-800-factory` | architect, hooks, scripts, mcp-wiring, builder, integrator, prompt-auditor, auditor | Директор → **lead сам** пайплайн |
| **Cloud Hub** (system-adjacent) | `t-800-cloud-hub-lead` | analyst, prompt, pack, smoke | Директор → `/t800-cloud-hub`; lead сам selective fan-out |
| **Loop** (system-adjacent) | — | **`t-800-loop-conductor`**‡ | Директор → `/t800-loop` (semi-manual; не research/brain leaf) |

† `t-800-cursor-kb-curator` — каденс living KB (`UPDATE-QUEUE` → maintainer); **не** на каждый hub-setup.  
‡ `t-800-loop-conductor` — **не** новый research/brain агент: только report/lessons → queue handoff; `risk_class` script-only.

\* `prompt-craft` — research-adjacent; вызывает Директор **или** factory lead после research (см. ниже).

## Закон: лиды оркестрируют, Директор не микроменеджит

| Делает Директор (main Agent / `/t800-start`) | Делает лид отдела |
|---------------------------------------------|-------------------|
| Выбор surface, discovery, порядок **отделов** | Выбор **специалистов внутри** отдела |
| Один `Task` на лид (research-lead, brain-lead, factory) | Вложенные `Task` специалистов (глубина ≤2) |
| Показ progress пользователю между отделами | Progress внутри отдела (опционально в fragment) |
| BLOCKER / вопросы пользователю | Не спрашивать пользователя без open_questions |

**Запрещено Директору:** вручную звать `t-800-research-github`, `t-800-brain-context`, `t-800-factory-builder` в обход лида — кроме отладки / явной просьбы.

## Каноническая цепочка `/t800-start`

```text
[0]  discovery (scripts) + surface
[0b] intake-clarifier?          ← только если неясно
[1]  scout                      ← всегда
[2]  research-lead DEEP|LIGHT|SKIP
       └─ АВТО: strategist → specialists → synthesizer
[2b] prompt-craft?              ← если agent|skill|command
[3]  brain-lead                 ← всегда перед factory
       └─ АВТО: 1–2 domain brains (+ teya если profile)
[4]  factory
       └─ АВТО: architect → companions? → builder → integrator
                → prompt-auditor? → auditor
[5]  machine gate + отчёт пользователю + следующий шаг
```

Специалисты Research/Brains/Factory **запускаются автоматом лидом** — пользователю и Директору не нужно перечислять их.

## Loop / STATE / gates / repair (v1.12)

Полный контракт: `shared/loop-engineering-contract.md`.

| Элемент | Правило |
|---------|---------|
| **STATE.md** | `{memory_path}/STATE.md` — init+Read в начале `/t800-start` и `/t800-plugin-audit`; touch после каждого отдела |
| **Machine gate** | «Готово» запрещено без auditor PASS **и** scripts exit 0 (когда применимо) |
| **Repair budget** | После auditor FAIL — до **2** циклов fix→re-audit; затем escalate |
| **Анти–Ralph** | Self-PASS без machine evidence запрещён |

```bash
bash scripts/t800_loop_state.sh init --memory-path "<memory_path>"
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "<dept>" --message "..."
```

## Progress (прогресс для человека)

После **каждого** завершённого отдела Директор пишет пользователю **одну строку статуса** (не эссе):

```text
T-800 ▸ [■■■□□] 3/5 Research готов (synthesis: high) → дальше Brain…
```

### Шкала этапов (5 клеток)

| # | Этап | Когда считать done |
|---|------|-------------------|
| 1 | Intake/Scout | scout_report есть (intake skipped|answered) |
| 2 | Research | research_brief + coverage pass + synthesis |
| 3 | Prompt craft | prompt_spec **или** skip (не agent/skill/command) |
| 4 | Brain | brief_for_factory готов |
| 5 | Factory | auditor PASS **и** machine scripts exit 0 + пути файлов |

Формат fragment (опционально, Директор или lead):

```yaml
# {memory_path}/fragments/t-800-run-progress.md
progress:
  run_id: "..."
  stage: intake|scout|research|prompt_craft|brain|factory|done
  bar: "[■■■□□]"
  stage_n: 3
  stage_total: 5
  last_message: "Research готов…"
  blockers: []
```

Внутри Research lead может писать подэтапы в свой fragment (`strategist done → fan-out 4/6 → synthesizer`).

## Handoff между отделами (что обязательно передать)

| Из | В | Обязательный пакет |
|----|---|-------------------|
| intake | scout/research | `intake_brief` |
| scout | research + brain | `scout_report` |
| research | prompt-craft + brain + factory | `research_brief` (search_plan, synthesis, coverage_matrix, adaptation_plan) |
| prompt-craft | brain + factory | `prompt_spec` |
| brain | factory | `brief_for_factory` (+ вложенный research_brief, target_context) |
| factory stages | next | `shared/t-800-factory-contract.md` handoff |

**Brain без research:** допустимо только при SKIP research («только KB») — тогда `research_brief: null`, brain опирается на KB + scout.

**Factory без brain:** **запрещено** для создания артефактов.

## Авто-маршрутизация внутри лидов

### Research-lead

1. Всегда `strategist` в DEEP/LIGHT  
2. Fan-out **только** каналы из `search_plan` (`must` обязательны)  
3. `github` must → после shallow **авто** `repo-miner` на top_repos  
4. Всегда `synthesizer` в DEEP (и в LIGHT если ≥2 источника)  
5. Не звать Context7, если канала `docs` нет в плане  

### Brain-lead

1. Прочитать `research_brief.synthesis` + `recommended_artifact`  
2. Выбрать domain brains по типу артефакта:

| artifact / тема | Domain brains |
|-----------------|---------------|
| subagent / agent modes | brain-agents (+ context) |
| skill / rule / MCP | brain-context |
| hook / automation | brain-cloud |
| CLI / SDK | brain-dev |
| security / readonly / permissions | brain-security |
| terminal/browser tools в промпте | brain-tools |
| profile teya-* | brain-teya **обязательно** |

3. Максимум **2** domain за прогон (кроме teya + один Cursor domain)  
4. Собрать `brief_for_factory` — не дублировать весь research, а **сверить** с KB и официальными URL  

### Factory-lead

1. architect всегда  
2. companions **авто** по типу: hook → artifact-hooks; script → artifact-scripts; MCP в spec → mcp-wiring  
3. builder → integrator всегда  
4. prompt-auditor **авто** если agent|skill|command  
5. factory-auditor всегда; FAIL → не «готово»  
6. Factory done = auditor `status: ok` **и** machine scripts (`validate-agents` / `audit-agent-graph` / `verify-install` когда применимо) exit 0  
7. Repair: до 2 циклов builder/integrator → re-audit; 3-й FAIL → escalate (`loop-engineering-contract`)  

### Cloud-hub-lead (system-adjacent)

1. Discovery `memory_path` → артефакты только в `{memory}/cloud-hub/`  
2. Selective fan-out: analyst | prompt | pack | smoke (не все без нужды)  
3. **Не** звать `t-800-cursor-kb-curator` на каждый run  
4. Контракт: `shared/cloud-hub-setup-contract.md`  

## Параллельность

| Где | Можно параллельно |
|-----|-------------------|
| Research fan-out | github ∥ community ∥ clawhub ∥ vendor ∥ docs ∥ news (после strategist) |
| repo-miner | после github (нужны URL) — не раньше |
| Brains | до 2 domain параллельно |
| Factory | companions после architect можно параллельно hooks+scripts+mcp |
| Отделы | **строго последовательно** scout → research → craft → brain → factory |

## Режимы research (тест режима + фраза)

Директор выбирает режим по **тесту** (`loop-engineering-contract`), не только по фразе пользователя:

| Режим | Тест режима | Фраза пользователя (override) | Что авто |
|-------|-------------|-------------------------------|----------|
| DEEP | новый домен / «изучи свежее» / сложный multi-source | (default) | полный strategist→…→synthesizer |
| LIGHT | мелкий твик, известный паттерн | «быстрый обзор» | strategist + урезанный fan-out |
| SKIP | тривиальный copy / offline | «только KB / без интернета» | research-lead не звать; brain сразу после scout |

## Команды вне factory-цепочки

| Команда | Отдел | Цепочка |
|---------|--------|---------|
| `/t800-bootstrap` | System | onboard (+ install rule по согласию) |
| `/t800-onboard` | System | onboard |
| `/t800-audit` | System | system-auditor (диалог bloat Cursor) |
| `/t800-plugin-audit` | System | plugin-auditor + `t800_plugin_audit.py` (карта плагина → `{memory}/audits/`) → опц. `t800_audit_to_fixpack` |
| `/t800-doctor` | System | `t800_doctor.py` (scripts-only; narrative onboard только по просьбе) |
| `/t800-fix` | Research?→Brains→Factory | fix-pack → research SKIP/LIGHT → brain → factory **PATCH** → `t800_run_gate.py` |
| `/t800-loop` | Loop (system-adjacent) | `t-800-loop-conductor` + scripts; semi-manual; queue → опц. `/t800-fix` |
| `/t800-update` | System | ручной fallback; авто = `sessionStart` → `t800-auto-version-check.sh` |
| `/t800-cloud-hub` (`/t800-hub-setup`) | Cloud Hub | только `t-800-cloud-hub-lead` → selective specialists; KB curator — отдельно |
| `/t-800-operator` | System | operator |
| `/t-800-health` | System | scripts health |
| `/t800-start` | все 4 | полная цепочка выше (создание; правка → `/t800-fix`) |

## Запреты

- Плодить новых research/brain агентов без отдельного решения (этот контракт = «хватит»)  
- Директор вызывает leaf-специалистов в обход лида  
- Factory без brain brief  
- Research DEEP без strategist/synthesizer  
- Молчать пользователю на длинном прогоне — минимум progress после каждого отдела  

## Версия

- Обновлён: 2026-07-17 · T-800 **1.17.0** (`/t800-loop`, loop-conductor system-adjacent)  
- Обновлён: 2026-07-09 · T-800 **1.13.0** (`/t800-fix`, `/t800-doctor`, run_gate)  
- Loop: 2026-07-09 · T-800 **1.12.0** (STATE / machine gates)  
- Введён отделы: 2026-07-09 · T-800 **1.11.0**  
- Связанные: `loop-engineering-contract.md`, `lesson-schema-contract.md`, `fix-pipeline-contract.md`, `deep-research-contract.md`, `search-strategy-contract.md`, `t-800-factory-contract.md`, `plugin-audit-contract.md`, `t800-start.md`
