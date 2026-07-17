# T800-SYSTEM-MAP.md

Карта системы для внешнего архитектора (проектирование / усиление **loop engineering**).  
Сгенерировано: 2026-07-17 (обновлено под **1.17.0**). Источник истины: checkout `t-800-agent` (git `Khar-AG/t-800-agent`), память `../t-800-memory/`.  
Версия плагина на момент карты: **1.17.0**.  
Правило документа: факты (файл / кто пишет / кто читает / авто|руками). Без маркетинга.

---

## 1. Система в цифрах

| Метрика | Значение | Источник |
|---------|----------|----------|
| Версия | `1.17.0` | `.cursor-plugin/plugin.json` |
| Display name | T-800 Agent | там же |
| GitHub | `https://github.com/Khar-AG/t-800-agent` | `shared/release-channel.json` |
| Branch релиза | `main` | `shared/release-channel.json` |
| Agents (Task-субагенты) | **43** файла `agents/t-800-*.md` = **43** в `registry/agents-registry.json` (вкл. `t-800-loop-conductor`) | ls + registry |
| Commands | **17** (`commands/*.md`, вкл. `/t800-loop`) | ls |
| Skills | **1** (`skills/t-800-knowledge-base/SKILL.md`) | find |
| Rules (plugin) | **5** `rules/*.mdc` | ls |
| Shared contracts | **30+** (`shared/*.md` + `release-channel.json`; вкл. `lesson-schema-contract`) | ls |
| Scripts | **40+** (`.py`/`.sh`/`.ps1`; + loop v2: report/lessons/classifier/golden/queue/dispatcher) | ls scripts |
| Templates | **10+** (вкл. `loop-policy.json.template`) | ls templates |
| Loop v2 artifacts | `runs/<id>/`, `loop-queue.md`, `.loop-paused`, `golden/`, `telemetry/`, `docs/examples/self-golden/` | loop-engineering-contract |
| KB markdown cards | **~76** (без raw HTML bulk) | find knowledge-base |
| LOC (md/py/sh/ps1/json/mdc/yaml, без `.cursor/agents` mirror) | **~17429+** (карта; пересчитать при аудите) | wc |
| Размер checkout | **~21M** (многое — `knowledge-base/raw/` HTML) | du |
| Agents body size | ~2735+ строк суммарно по `agents/*.md` | wc |
| Hooks | `sessionStart` (один; dispatcher внутри bootstrap), `beforeFileEdit` | `hooks.json` |
| Tests | ручные `tests/TEST-SCENARIOS.md` + fixtures `tests/fixtures/loop/` + golden self-check; нет CI unit-suite | файл |
| Хостинг | локальный Cursor plugin: `~/.cursor/plugins/local/t-800-agent/` | install scripts |
| Деплой | `bash scripts/install-plugin.sh` → copy в plugins/local; автообновление с GitHub на `sessionStart` | INSTALL + auto-update-contract |

### Стек

| Слой | Технология |
|------|------------|
| Артефакты Cursor | Markdown agents/commands/skills, `.mdc` rules, `hooks.json` |
| Оркестрация | Cursor Agent + `Task(subagent_type=…)` (лиды отделов) |
| Machine gates | Bash + Python3 (`t800_run_gate.py`, `t800_doctor.py`, `t800_plugin_audit.py`, `t800_factory_bypass_gate.py`) |
| Registry | JSON `registry/agents-registry.json` |
| KB sync | PowerShell `scripts/sync-docs.ps1` (Windows-канон в контракте; macOS — ручной/частичный) |
| Память прогона | Markdown + JSON в `{memory_path}/` целевого проекта |
| Язык UX | русский (контракты/промпты), идентификаторы — English kebab-case |

### Категории агентов (registry)

| Отдел | Лид | Leaf / специалисты (сводка) |
|-------|-----|------------------------------|
| System / Mentor | — (Директор по slash) | onboard, operator, system-auditor, plugin-auditor, intake-clarifier, maintainer, cursor-kb-curator, **loop-conductor** (`/t800-loop`) |
| Research | `t-800-research-lead` | strategist, github, repo-miner, community, clawhub, vendor-docs, docs, news, synthesizer; adjacent: prompt-craft |
| Brains | `t-800-brain-lead` | agents, context, cloud, dev, admin, security, tools, teya |
| Factory | `t-800-factory` | architect, artifact-hooks, artifact-scripts, mcp-wiring, builder, integrator, prompt-auditor, auditor |
| Cloud Hub | `t-800-cloud-hub-lead` | analyst, prompt, pack, smoke |

---

## 2. Анатомия одного прогона

### 2.1 `/t800-start` (CREATE / крупное изменение)

Канон: `commands/t800-start.md` + `shared/department-orchestration-contract.md` + `shared/loop-engineering-contract.md`.

| # | Шаг | Кто | Вход | Выход / артефакты |
|---|-----|-----|------|-------------------|
| 0 | Discovery | Директор (main Agent) запускает scripts | workspace path | JSON: `plugin_root`, `memory_path`, `profile`, `artifact_surface` (`scripts/discover-target-project.sh`, опц. `list-target-plugins.sh`) |
| 0a | STATE init | Директор | `memory_path` | `{memory}/STATE.md` через `bash scripts/t800_loop_state.sh init`; **Read** STATE |
| 0b | Intake? | `Task(t-800-intake-clarifier)` | неоднозначный brief (модели/MCP/surface/readonly) | 2–5 вопросов пользователю **или** `skipped`; fragment опц.; `t800_loop_state.sh touch --stage intake` |
| 1 | Scout | `Task(t-800-scout)` | задача + surface | `scout_report` (+ fragment `fragments/t-800-scout.md`); touch `scout` |
| 2 | Research mode test | Директор | сложность / «только KB» / «быстрый обзор» | режим `DEEP` \| `LIGHT` \| `SKIP` (контракт loop) |
| 2a | Research | `Task(t-800-research-lead)` | mode + scout | **Внутри lead АВТО:** strategist → fan-out specialists → synthesizer → `research_brief` + coverage_matrix; fragments по специалистам; touch `research` |
| 2b | Prompt craft? | `Task(t-800-prompt-craft)` | если artifact ∈ {agent, skill, command} | `prompt_spec`; touch `prompt_craft` или skip |
| 3 | Brain | `Task(t-800-brain-lead)` | scout + research + prompt_spec? + target_context | **Внутри АВТО** 1–2 domain brains → `brief_for_factory`; touch `brain` |
| 4 | Factory | `Task(t-800-factory)` | `brief_for_factory` | **Внутри АВТО:** architect → companions? → builder → integrator → prompt-auditor? → auditor; пишет файлы на `artifact_surface`; `factory-briefs/<slug>.yaml`; fragments; обновляет `run-manifest.json` |
| 4r | Repair ≤2 | factory lead | auditor FAIL | builder/integrator → re-audit; 3-й FAIL → escalate пользователю |
| 5 | Machine gate | Директор / scripts | memory + опц. plugin_root | `python3 scripts/t800_run_gate.py …`; validate/audit/verify когда применимо; STATE Gates/Completed/Lessons |
| 6 | Progress UI | Директор | после каждого отдела | одна строка `T-800 ▸ [■■■□□] n/5 …` (не файл, текст чата; опц. fragment progress) |

**Кто кого вызывает (закон):** Директор зовёт **только лидов**. Leaf (`t-800-research-github`, `t-800-factory-builder`, …) — **только внутри лида**. Обход лида = нарушение `department-orchestration-contract` (advisory + social; machine gate не ловит «кто вызвал Task»).

### 2.2 `/t800-fix` (PATCH по fix-pack)

Канон: `commands/t800-fix.md` + `shared/fix-pipeline-contract.md`.

| # | Шаг | Кто | Вход | Выход |
|---|-----|-----|------|-------|
| 0 | Discovery + STATE | Директор + scripts | workspace | `memory_path`, `STATE.md` |
| 1 | Read fix-pack | Директор | `{memory}/fix-packs/<slug>.md` | список `files[]`, `changes[]`, `research_mode`, `success_criteria` |
| 2 | Research | SKIP/LIGHT default; DEEP только если pack требует | pack | обычно skip; иначе LIGHT research-lead |
| 3 | Brain | `Task(t-800-brain-lead)` | pack + mode PATCH | `brief_for_factory` с `mode: PATCH` |
| 4 | Factory PATCH | `Task(t-800-factory)` | только `files[]` | правки **только** listed paths |
| 5 | Run gate | `t800_run_gate.py` | memory | JSON summary stdout + exit 0/1 |
| 6 | STATE | Директор + `t800_loop_state.sh touch` | gate result | Completed / Gates / Lessons |

### 2.3 Соседние прогоны (кратко)

| Команда | Цепочка | Пишет куда |
|---------|---------|------------|
| `/t800-loop` | discover → `Task(t-800-loop-conductor)` → `t800_loop_queue_write.py` → HITL → `/t800-fix` | `{memory}/loop-queue.md`, `runs/`, lessons; уважает `.loop-paused` |
| `/t800-plugin-audit` | discover → `t800_plugin_audit.py` → `Task(t-800-plugin-auditor)` → опц. `t800_audit_to_fixpack.py` | `{memory}/audits/<run-id>/`, fragment, опц. fix-pack |
| `/t800-audit` | `Task(t-800-system-auditor)` (+ `audit-cursor-bloat.sh`) | fragment; **диалог** keep/narrow/remove; не карта чужого плагина в KB |
| `/t800-doctor` | `python3 scripts/t800_doctor.py` | `{memory}/audits/<run-id>/doctor.json` + `doctor-report.md` |
| `/t800-cloud-hub` | `Task(t-800-cloud-hub-lead)` → selective analyst/prompt/pack/smoke | `{memory}/cloud-hub/*` (dual-write contract) |
| `/t800-bootstrap` | audit + согласие → `install-global-routing-rule.sh` | global `~/.cursor/rules/t-800-mandatory-routing.mdc` |
| `/t800-update` | `t800-update-from-github.sh` | перезапись `~/.cursor/plugins/local/t-800-agent` |
| `/t-800-factory` | только factory (если brain уже дал контекст) | как шаг 4 `/t800-start` |

### 2.4 Пример реальных путей (self-t800 в этом workspace)

| Ключ | Путь |
|------|------|
| workspace | `/Users/andrejharcenko/Desktop/Мои разработки на коде/Cursor/T-800 AGENT` |
| plugin_root (dev) | `…/T-800 AGENT/t-800-agent` |
| plugin_root (runtime Cursor) | `~/.cursor/plugins/local/t-800-agent` |
| memory_path | `…/T-800 AGENT/t-800-memory` |
| profile | `self-t800` / marker (`project-memory.marker.json`) |

---

## 3. Память и артефакты

Контракт: `shared/project-memory-contract.md`.  
**Закон:** канон памяти — у **целевого** проекта (`teya-memory/`, `plugin-memory/`, `{slug}-memory/`). Писать STATE чужого плагина в `t-800-memory/` как канон **запрещено** (кроме profile `self-t800`).

### 3.1 Таблица файлов состояния

| Артефакт | Путь | Кто пишет | Кто читает | Формат | Живёт между прогонами? | При «новом проекте» / init |
|----------|------|-----------|------------|--------|------------------------|----------------------------|
| STATE | `{memory}/STATE.md` | Директор + `t800_loop_state.sh` | Директор, run_gate (наличие), люди | Markdown секции | Да (накапливает Lessons/Completed) | `t800_loop_state.sh init` или `init-project-memory.sh` |
| run-manifest | `{memory}/run-manifest.json` | factory / Директор (по контракту) | run_gate `--strict-create`, bypass_gate, люди | JSON steps[] | Да (история шагов; сейчас часто **мультирелизный лог**, не один run_id) | создаётся/дописывается на прогоне |
| Fragment агента | `{memory}/fragments/t-800-<agent>.md` | каждый Task-агент (ожидание контракта) | auditor, Директор, run_gate (factory fragment status) | Markdown ± YAML status | Да | не чистится автоматом |
| Factory brief | `{memory}/factory-briefs/<slug>.yaml` | factory / Директор | factory stages, run_gate `--factory-brief` | YAML | Да | новый slug на задачу |
| Fix-pack | `{memory}/fix-packs/<slug>.md` | человек / `t800_audit_to_fixpack.py` / `t800_lessons_to_fixpack.py` / Директор | `/t800-fix`, factory PATCH | Markdown секции | Да | из аудита, lessons (LOW), или руками |
| Run report | `{memory}/runs/<id>/report.json` | `t800_run_report.py` | conductor, classifier, люди | JSON | Да | новый `run_id` |
| Lessons | `{memory}/runs/<id>/lessons.json` | `t800_lessons_export.py` + `t800_risk_classifier.py` | `/t800-loop`, fixpack scripts | JSON (`lesson-schema`) | Да | после report |
| Loop queue | `{memory}/loop-queue.md` | **только** `t800_loop_queue_write.py` (не агент Write) | Директор, `/t800-loop` | Markdown | Да | handoff conductor |
| Loop pause (kill switch) | `{memory}/.loop-paused` | человек / HITL | dispatcher, `/t800-loop` | empty file | Да | `touch` / удалить |
| Golden expected | `{memory}/golden/` или `docs/examples/self-golden/expected.json` | maintainer (`--write-hashes` HITL) | `t800_golden_check.py` | JSON paths/hashes | Да | Prove phase |
| Plugin audit out | `{memory}/audits/<run-id>/inventory.json` (+ scorecard, graph, summaries) | `t800_plugin_audit.py` + plugin-auditor | `/t800-fix` handoff, run_gate `--require-plugin-audit-out` | JSON + MD | Да | новый `run-id` каталог |
| Doctor out | `{memory}/audits/<run-id>/doctor.json` | `t800_doctor.py` | человек / smoke | JSON + MD | Да | новый run |
| Cloud Hub pack | `{memory}/cloud-hub/*` | cloud-hub-* агенты | Hub Automations (человек копирует в Cursor UI) | MD/JSON | Да | dual-write contract |
| Progress fragment | `{memory}/fragments/t-800-run-progress.md` | опц. Директор | люди | YAML в MD | опц. | редко используется на практике |
| Project marker | `project-memory.marker.json` (workspace) | человек / init | discover script | JSON | Да | задаёт slug/memory_dir |
| Known plugins | `~/.t800/known-plugins.json` | list/discover helpers | Директор | JSON | Да (user home) | не в git плагина |

### 3.2 KB / «Brain proposals» аналог Teya

| Артефакт | Путь | Роль |
|----------|------|------|
| UPDATE-QUEUE | `knowledge-base/UPDATE-QUEUE.md` | Очередь **карточек docs Cursor** после sync — **не** очередь патчей промптов агентов |
| manifest | `knowledge-base/manifest.json` | SHA/свежесть URL docs |
| CHANGELOG KB | `knowledge-base/CHANGELOG.md` | история версий плагина + KB |
| HEALTH-REPORT | `knowledge-base/HEALTH-REPORT.md` | вывод health-check (пути относительные с 1.15.3) |
| Skill KB | `skills/t-800-knowledge-base/SKILL.md` | как читать KB |

**НЕТ** в T-800 отдельного `Brain proposals/` для автопатчей промптов агентов (как у Teya post-run → plugin-engineer). Ближайшее: Lessons в `STATE.md` + fix-pack + `/t800-fix`.

### 3.3 Что делает «новый сайт» аналог

У T-800 нет `/teya-new-site`. Аналоги:

| Действие | Что происходит с памятью |
|----------|--------------------------|
| `bash scripts/init-project-memory.sh --workspace … --slug …` | создаёт `{slug}-memory/` каркас (STATE template, dirs) |
| Новый workspace + marker | discover выбирает другой `memory_path` |
| `t800_loop_state.sh init` | пересоздаёт/инициализирует STATE (не wipe всего memory) |
| Смена профиля на Teya | писать в `teya-memory/` / `plugin-memory/`, **не** плодить `t-800-memory/` в клиенте |

---

## 4. Gates и верификация (критично)

### 4.1 Таблица gates

| Gate | Что проверяет | Авто / человек | При провале | Ретраи | Где логика | Машиночитаемый вердикт? |
|------|---------------|----------------|-------------|--------|------------|-------------------------|
| `t800_run_gate.py` | наличие `STATE.md`; опц. inventory; опц. validate-agents; опц. `--strict-create` (manifest factory + fragment factory status + brief done) | Авто (exit code) | стоп «готово»; Директор должен чинить | budget 2 на уровне **контракта** (не внутри скрипта) | `scripts/t800_run_gate.py` | **Да:** JSON `{ok, checks, error}` на stdout |
| `t800_factory_bypass_gate.py` | изменённые agents/skills/commands/rules/hooks без completed factory в manifest | Авто | FAIL exit 1 | нет авто-retry | `scripts/t800_factory_bypass_gate.py` | **Да:** JSON summary |
| `validate-agents.sh/.ps1` | frontmatter, name=filename, description; WARN если >200 строк | Авто | exit 1 | repair через factory | `scripts/validate-agents.sh` | Частично: текст OK/FAIL + exit; **нет** единого JSON |
| `audit-agent-graph.sh/.ps1` | симметрия calls/calledBy, registry | Авто | exit ≠0 | repair | `scripts/audit-agent-graph.*` | Текст + exit |
| `verify-install.sh/.ps1` | файлы плагина в plugins/local; контракты/скрипты на месте; readonly флаги | Авто | exit ≠0 | reinstall | `scripts/verify-install.*` | Текст + exit |
| `health-check.sh/.ps1` | установка + validate + graph + manifest freshness | Авто | FAIL в HEALTH-REPORT | install+verify | `scripts/health-check.*` | MD report + exit |
| `t800_doctor.py` | discovery, counts, alwaysApply, последние audits | Авто | отчёт; exit по логике скрипта | — | `scripts/t800_doctor.py` | **Да:** `doctor.json` |
| `t800_plugin_audit.py` | inventory/graph/orphans/alwaysApply | Авто | exit 1/2 | — | `scripts/t800_plugin_audit.py` | **Да:** `inventory.json`, `scorecard.json` |
| `factory-auditor` (агент) | prompt-auditor ok + scripts + registry + quality | Агент readonly + scripts | `status: blocked` → factory repair | ≤2 в factory lead | `agents/t-800-factory-auditor.md` | **Частично:** YAML в ответе/fragment (`status`, `machine_gates`, `ralph_wiggum_risk`); не единый schema-файл |
| `prompt-auditor` | качество промпта agent/skill/command | Агент | blocked ship | через factory | `agents/t-800-prompt-auditor.md` | YAML в fragment/ответе |
| `beforeFileEdit` hook | правка Cursor-артефактов | Hook | **WARN allow** (не hard-deny v1) | — | `hooks/before-artifact-edit.sh` | JSON stdout `{continue, permission, userMessage}` |
| Mandatory routing rule | запрет Write артефактов вне factory | Advisory rule | социальный / gate scripts если запущены | — | `rules/t-800-mandatory-routing.mdc` (+ global copy после bootstrap) | Нет (текст правила) |
| Research coverage_matrix | полнота DEEP research | Агент synthesizer/lead | FAIL incomplete → не идти дальше (контракт) | человек/повтор research | `shared/deep-research-contract.md` | Обычно в fragment/research_brief YAML — **не** отдельный gate script |
| alwaysApply hard (≥20) | bloat rules | `t800_plugin_audit.py --strict-alwaysapply large` | exit 2 | человек | plugin-audit-contract | scorecard JSON |

### 4.2 Анти–Ralph Wiggum

Контракт явно запрещает «готово» без machine evidence.  
`ralph_wiggum_risk: true` в отчёте auditor, если скрипты не запускались.

### 4.3 Единый отчёт прогона?

**Нет единого schema «run-report.json» на весь `/t800-start`.**  
Сейчас: разрозненные STATE (MD), run-manifest (JSON), fragments (MD), stdout JSON отдельных скриптов, YAML auditor. Свести можно скриптом, но **готового агрегатора нет**.

### 4.4 Repair budget (контракт vs код)

| Слой | max_repair_attempts=2 |
|------|------------------------|
| Контракт loop / factory agent | Да, описано |
| `t800_run_gate.py` | **Не** считает ретраи; только pass/fail |
| Автоматический цикл без Директора | **Нет** — Директор/factory lead должен сам вызвать повторный Task |

---

## 5. Текущий цикл обратной связи

### 5.1 Честная схема «как есть» (не Teya post-run 4/4)

```text
прогон /t800-start|/t800-fix|/t800-plugin-audit
  → machine gate (scripts) + factory-auditor
  → STATE.md Lessons / Gates   (пишет Директор руками по шаблону)
  → [разрыв] человек читает Lessons / audit
  → опц. t800_audit_to_fixpack.py → fix-packs/<slug>.md
  → человек запускает /t800-fix
  → factory PATCH промптов/контрактов
  → run_gate
  → git commit + bump version + push main
  → sessionStart auto-update у пользователей
```

### 5.2 Переходы (авто / руками / потери)

| Переход | Авто? | Что теряется |
|---------|-------|--------------|
| Auditor FAIL → repair builder | **Полуавто** внутри factory lead (если lead соблюдает контракт) | Если Директор объявил «готово» раньше — урок не в STATE |
| Gate FAIL → escalate | **Руками** (Директор пишет Blockers) | Часто остаётся только в чате |
| Lessons → следующий прогон | **Руками** (Read STATE в начале) | Если init перезапишет / забудут Read — Lessons игнор |
| Audit → fix-pack | **Полуавто** (`t800_audit_to_fixpack.py`) | Draft часто с `(уточните пути вручную)` — см. реальные packs в memory |
| Fix-pack → `/t800-fix` | **Руками** (slash) | Нет автозапуска после аудита |
| PATCH промпта → регрессия поведения | **Частично** validate/graph/verify; **нет** golden E2E прогона агента | Семантические регрессии промпта скрипты не ловят |
| Lessons → KB / CHANGELOG | **Руками** maintainer | Повторяющиеся Lessons могут жить только в STATE |

### 5.3 Аналоги Teya post-run

| Teya | T-800 эквивалент | Статус |
|------|------------------|--------|
| `teya-run-auditor` | `t-800-plugin-auditor` + `t800_plugin_audit.py` / `t800_doctor` / factory-auditor | Есть, другая цель |
| `teya-post-run-retrospective` | секция **Lessons** в STATE + fragment | **Нет** отдельного агента ретро |
| `teya-plugin-engineer` | `/t800-fix` + `t-800-factory` PATCH | Есть, **не** авто после каждого прогона |
| `teya-knowledge-curator` | `t-800-cursor-kb-curator` + `t-800-maintainer` | Только **KB docs**, не промпты агентов |

### 5.4 Формат «урока»

Факт сегодня:

```markdown
## Lessons
- verify/health должны проверять PLUGIN paths, иначе патч install ломает gates
- consent mandatory-routing остаётся через /t800-bootstrap, не через install
```

(из реального `t-800-memory/STATE.md`)

Нет schema: severity / agent_id / proposed_patch / evidence_path / auto_applicable.

### 5.5 Кто правит промпты

| Роль | Правит agents/*.md? |
|------|---------------------|
| factory-builder / integrator | Да (через factory) |
| factory-auditor / prompt-auditor / brains / research | Нет (readonly) |
| maintainer | KB + sync, не промпты агентов (по description) |
| Директор main chat | **Запрещено** правилом; hook WARN; bypass_gate FAIL если запущен |

Проверка «не сломало старое поведение»: structural gates да; behavioral golden tests — **НЕТ** (кроме ручных `tests/TEST-SCENARIOS.md`).

---

## 6. «Run auditor» в T-800

Отдельного `t-800-run-auditor` **нет**. Роли размазаны:

### 6.1 `run-manifest.json`

| Поле (факт) | Назначение |
|-------------|------------|
| `schema_version` | 1 |
| `steps[]` | `{agent, status, note?, at?, verdict?}` |
| `status` / `version` / dates | метаданные «проекта hardening», не строго один slash-run |

**Проблема:** текущий файл в `t-800-memory/run-manifest.json` — **кумулятивный лог релизов** (phase-0…v1.12.1), а не per-invocation manifest с `run_id`.  
`--strict-create` ищет любой step с `"factory"` в имени агента и ok-status — **не** привязывает к текущему chat run.

### 6.2 Как определяют причину сбоя

| Ситуация | Механизм |
|----------|----------|
| Structure/registry | factory-auditor + validate/graph |
| Install broken | verify-install / doctor |
| Orphans / alwaysApply | plugin-audit scorecard |
| Factory bypass | bypass_gate + hook WARN |
| Оркестрация (не вызвали lead) | **НЕТ** machine detector — только review чата / ручной audit |

### 6.3 Куда пишут / кто потребляет

| Выход | Потребитель |
|-------|-------------|
| `audits/<run-id>/*` | человек, `t800_audit_to_fixpack.py`, optionally run_gate |
| `fragments/t-800-factory-auditor.md` | Директор, strict-create косвенно через factory fragment |
| stdout JSON gates | CI/человек/smoke |
| STATE Gates table | следующий `/t800-start` (если Read) |

---

## 7. Релизный процесс

### 7.1 Как рождается версия

| Шаг | Кто | Авто? |
|-----|-----|-------|
| Изменения через factory / fix | factory | через `/t800-start`/`/t800-fix` |
| Bump `.cursor-plugin/plugin.json` version | человек или factory brief (часто в must_update) | Обычно **руками** в brief |
| `knowledge-base/CHANGELOG.md` | человек / maintainer / factory | Руками по факту |
| README / docs синхрон | factory / человек | Частично в brief |
| `git commit` + `git push origin main` | человек | Руками (user rule: не коммитить без просьбы) |
| GitHub Release tags | опц. | `releases_url` в channel; канон обновления — **ветка main zip**, не обязательно GitHub Release asset |
| Пользователи получают | `sessionStart` → `t800-auto-version-check.sh` → `t800-update-from-github.sh` | Авто (TTL 6ч), fail-open |
| Reload Window | **человек** | Hook не умеет Reload |

### 7.2 Docs build

| Teya `teya_docs_build.py` | T-800 |
|---------------------------|-------|
| Есть отдельный docs builder | **НЕТ** аналога |
| Sync официальных docs | `scripts/sync-docs.ps1` → raw + UPDATE-QUEUE |
| Install обновляет runtime | `install-plugin.sh` копирует plugin tree |

### 7.3 Тесты / smoke перед релизом

| Проверка | Статус |
|----------|--------|
| `verify-install.sh` | Да, ожидается |
| `validate-agents` + `audit-agent-graph` | Да |
| `t800_doctor.py` smoke | Использовался в v1.13 (см. memory audits) |
| `t800_run_gate.py` | Да после fix |
| `tests/TEST-SCENARIOS.md` | Ручные чеклисты; сценарий 6 = factory bypass |
| Авто CI на GitHub | **НЕТ ДАННЫХ** в репо (workflows не обнаружены в этой карте) |
| Стоимость/токены прогона | **НЕТ ДАННЫХ** (не логируется) |

### 7.4 Откат

| Способ | Как |
|--------|-----|
| Git | checkout предыдущего commit / revert на main |
| Runtime | поставить старый zip / предыдущий tree в `plugins/local` вручную |
| Auto-update | тянет **latest main** — откатиться = откатить main или отключить `T800_SKIP_AUTO_UPDATE=1` и руками поставить старую копию |
| Per-agent rollback | нет versioned agent store; только git history |

---

## 8. Болевые точки (топ реальных)

Источники: CHANGELOG 1.12–1.17.0, STATE Lessons, TEST scenarios 6–7, fix-pack drafts, контракты loop v2.

| # | Боль | Доказательство / симптом | Лечится сейчас? |
|---|------|--------------------------|-----------------|
| 1 | **Обход factory** (агенты пишутся из main/Plan Implement) | Инцидент Zen Intel → v1.16.1 bypass_gate + hook WARN + strict-create | Частично: WARN не hard-deny; gates надо **запускать** |
| 2 | **Self-PASS без scripts** (Ralph) | loop-contract + auditor `ralph_wiggum_risk` | Контрактом; enforcement = дисциплина Директора |
| 3 | **Lessons не замыкаются в патч** | STATE Lessons есть; авто `/t800-fix` нет | Нет closed loop |
| 4 | **fix-pack drafts сырые** | `fix-packs/final-smoke.md`: «уточните пути вручную» | Скрипт генерит draft, человек доводит |
| 5 | **run-manifest ≠ один прогон** | кумулятивный JSON с phase-0…v1.12 | Путает strict-create / аудиты истории |
| 6 | **Зеркала user-home** ломали модель установки | v1.12.1 no-mirror | Исправлено; VERIFY следит |
| 7 | **raw.githubusercontent CDN lag** | auto-update видел старую версию | v1.15.1 → GitHub Contents API |
| 8 | **DEEP research дорогой / неполный** | coverage_matrix FAIL; Context7 always-on запрещён | Режим LIGHT/SKIP; всё равно зависит от lead |
| 9 | **Директор зовёт leaf в обход lead** | department-contract запрещает | Нет machine detector |
| 10 | **Повторяющиеся install/path Lessons** | STATE: «verify/health должны проверять PLUGIN paths» | Патчились в 1.12.1; риск регресса при правке install |
| 11 | **Hook не блокирует** | before-artifact-edit allow+WARN | v1 hard-deny отложен |
| 12 | **Нет метрик прогонов** | нет duration/tokens/retry counters | Полный пробел для loop KPI |
| 13 | **KB UPDATE-QUEUE ≠ prompt patches** | путаница с Teya Brain proposals | Разные механизмы; легко спроектировать loop не туда |
| 14 | **Cloud Hub secrets / drift** | dual-write contract; smoke checklist | Процессный, не machine |
| 15 | **Дубли `.cursor/agents/` mirror** в plugin tree | файлы есть рядом с `agents/` | Риск рассинхрона; verify/install должны держать parity |

---

## 9. Метрики и логи

| Метрика | Логируется? | Где |
|---------|-------------|-----|
| Длительность прогона | **НЕТ** | — |
| Число ретраев repair | **НЕТ** (только текстовый budget в контракте) | — |
| Токены / $ | **НЕТ** | Cursor UI может показывать, плагин не пишет |
| Доля прогонов без человека | **НЕТ** | — |
| Exit codes gates | Да, если запущены | stdout/stderr + иногда JSON |
| Audit inventory | Да | `audits/<run-id>/` |
| STATE Last run timestamp | Да (руками/touch) | `STATE.md` |
| Auto-update cache | Да | TTL 6ч в auto-check script (локальный cache) |
| Hook WARN events | Только userMessage в момент edit | не агрегируется |

**Вывод для архитектора loop:** без нового telemetry-слоя evaluator-optimizer будет слепым по KPI.

---

## 10. Точки расширения (новый агент / команда / skill)

### 10.1 Новый субагент (канон)

| Шаг | Файл / действие |
|-----|-----------------|
| 1 | `/t800-start` → research → brain → `Task(t-800-factory)` |
| 2 | `agents/<name>.md` (+ часто `.cursor/agents/` mirror) |
| 3 | опц. `commands/<slash>.md` |
| 4 | опц. `rules/*-routing.mdc` |
| 5 | `registry/agents-registry.json` (integrator / `register-agent.ps1`) |
| 6 | `docs/T-800-AGENTS.md` запись |
| 7 | validate-agents + audit-agent-graph |
| 8 | factory-auditor `status: ok` |
| 9 | version bump + CHANGELOG + install/push |

Качество: `shared/t-800-agent-quality-contract.md` + `shared/t-800-factory-contract.md`.  
Валидатор структуры: `validate-agents.sh` (frontmatter) + auditor (семантика) + graph audit.

### 10.2 Новая команда

`commands/*.md` + wiring в README/docs + иногда rule routing; registry agents не всегда содержит commands (commands — отдельные md).

### 10.3 Новый skill

`skills/<id>/SKILL.md`; сейчас skill один. Conflict check: не дублировать субагента (кейс operator).

### 10.4 Новый hook

`hooks.json` + `hooks/*.sh`; companion `t-800-artifact-hooks`; cloud-safe (без секретов в argv).

### 10.5 Запрет без factory

Правило + bypass_gate + hook WARN. Для loop-отдела: любые новые агенты loop **только** через factory (контракт уже запрещает плодить research/brain ради loop).

---

## 11. Что уже есть из «loop engineering» (v1.12–1.17 Loop v2)

Не проектировать с нуля — **достраивать**:

| Компонент | Статус |
|-----------|--------|
| STATE.md | Есть |
| Machine gate канон | `t800_run_gate.py` |
| Repair budget 2 | Контракт + factory prompt |
| Research mode test | Контракт |
| Fix pipeline | `/t800-fix` + fix-packs |
| Audit → pack | `t800_audit_to_fixpack.py` |
| Anti-bypass | v1.16.1+ |
| **Loop Engineering v2** (1.17.0) | `/t800-loop`, `t-800-loop-conductor`, report→lessons→classify→queue; Anti-Ralph; `.loop-paused` kill switch |
| risk_class | **только** `t800_risk_classifier.py` (denylist wins; zero false LOW на fixtures) |
| Golden smoke (paths/hashes) | `t800_golden_check.py` + `docs/examples/self-golden/` |
| Post-run retrospective agent | **Нет** отдельного; роль conductor + lessons schema |
| Auto-apply low-risk prompt patches | **OFF** default (`loop-policy`); semi-manual HITL |
| Unified run JSON + metrics | Частично: `runs/<id>/report.json`; полный KPI telemetry — ещё gap |
| Golden E2E prompt regen | Частично: self-golden + fixtures; не полный autonomous client workspace |

Brief внедрения: `t-800-memory/factory-briefs/v1.12-loop-engineering.yaml` (+ контракт `shared/loop-engineering-contract.md` v2).

---

## Ответы архитектору

### 1. Может ли агент программно перезапустить команду (патч → тестовый прогон)?

**Частично / практически нет как у slash-command API.**

- Агент **может** снова вызвать `Task(t-800-factory)` / scripts (`t800_run_gate.py`, doctor, validate) в том же чате — это и есть repair-loop.
- Агент **не может** надёжно «нажать» `/t800-start` как UI-команду без участия человека в новом turn; нет публичного Cursor API «invoke slash» из плагина.
- Автозапуск полного DEEP `/t800-start` после maintainer-патча = **человек** или тот же Директор в том же диалоге по собственной инициативе.
- Cloud Automations — отдельный контур (`/t800-cloud-hub`), не замена локального factory loop.

### 2. Есть ли тестовый проект / эталонный бриф для smoke правок промптов?

**Частично.**

| Артефакт | Путь | Назначение |
|----------|------|------------|
| Readonly scout test brief | `docs/examples/teya-test-scout-readonly.md` | factory test |
| Briefs в memory | `t-800-memory/factory-briefs/teya-test-scout-readonly.yaml` и version briefs | история сборок |
| Manual scenarios | `tests/TEST-SCENARIOS.md` | оператор/mentor, bypass |
| Self-audit smoke | `t-800-memory/audits/t800-*-smoke-*` | doctor/audit/gate |

**Нет** выделенного «golden client workspace» с фиксированным брифом и ожидаемым деревом артефактов для регрессии **любого** prompt patch.

### 3. Вердикты gates → единый машиночитаемый отчёт?

**Сейчас нет.**  
Можно собрать: `t800_run_gate` JSON + `doctor.json` + `scorecard.json` + YAML auditor + STATE.  
Единого `run-report.json` writer’а нет. Форматы **разные** (JSON скриптов vs MD STATE vs YAML в fragments).

### 4. UPDATE-QUEUE и «Brain proposals»

| Механизм | Что это | Кто одобряет | Почему не авто для low-risk |
|----------|---------|--------------|------------------------------|
| `knowledge-base/UPDATE-QUEUE.md` | изменения **официальных docs Cursor** → карточки новичкам | человек / `t-800-maintainer` после curator | нужна упрощённая педагогика; не prompt-diff агентов |
| STATE Lessons | уроки прогона | Директор читает | нет severity/auto_apply |
| fix-packs | предложенный PATCH | человек запускает `/t800-fix` | files[] часто требуют ручной доводки; риск сломать routing |

Авто-одобрение низкорисковых правок **мешают:** (a) нет классификатора риска патча; (b) hook/gates не покрывают семантику; (c) policy «не плодить агентов / не silent prune»; (d) install/global rule требуют consent (`/t800-bootstrap`).

### 5. Стоимость полного `/t800-start` (токены/$)?

**НЕТ ДАННЫХ в плагине.**  
Порядок величины (экспертная оценка, не замер): DEEP research с fan-out 4–8 специалистов + brain + factory stages = **очень дорого** (часто $1–10+ и миллионы токенов в зависимости от модели/репо-майнинга), LIGHT/SKIP+PATCH — на порядки дешевле. Для дизайна loop закладывать **обязательный LIGHT/SKIP** на repair и метрики до автоматизации DEEP.

### 6. Низкорисковые vs высокорисковые правки промптов

**Низкорисковые (кандидат в авто после gate):**

- Опечатки, битые пути к contracts, уточнение Do NOT use when
- Добавление ссылки на существующий `shared/*.md`
- Синхронизация `description` с registry после graph FAIL
- Docs/CHANGELOG/README
- Fix-pack с 1 файлом leaf-агента без смены `calls`/`readonly`

**Высокорисковые (только человек):**

- Смена оркестрации лидов / department contract
- alwaysApply rules / mandatory-routing
- hooks.json behavior (особенно hard-deny)
- research-lead / factory-lead алгоритмы fan-out
- Любой новый агент / удаление агента
- profile Teya / dual-write / cloud-hub instructions
- Ослабление gates / repair budget / bypass
- Промпты, влияющие на деньги/секреты/production клиентских сайтов (через Teya surface)

---

## Приложение A — Карта команд → entrypoint

| Slash | Entry |
|-------|-------|
| `/t800-start` | `commands/t800-start.md` |
| `/t-800` | alias start |
| `/t800-fix` | `commands/t800-fix.md` |
| `/t800-loop` | `commands/t800-loop.md` |
| `/t800-plugin-audit` | `commands/t800-plugin-audit.md` |
| `/t800-audit` | `commands/t800-audit.md` |
| `/t800-doctor` | `commands/t800-doctor.md` |
| `/t800-bootstrap` | `commands/t800-bootstrap.md` |
| `/t800-update` | `commands/t800-update.md` |
| `/t800-cloud-hub` | `commands/t800-cloud-hub.md` |
| `/t800-onboard` | `commands/t800-onboard.md` |
| `/t-800-factory` | `commands/t-800-factory.md` |
| `/t-800-health` | `commands/t-800-health.md` |
| `/t-800-maintain` | `commands/t-800-maintain.md` |
| `/t-800-operator` | `commands/t-800-operator.md` |
| `/t-800-sync` | `commands/t-800-sync.md` |
| `/t-800-factory-validate` | `commands/t-800-factory-validate.md` |

## Приложение B — Ключевые контракты (читать архитектору)

1. `shared/loop-engineering-contract.md`
2. `shared/fix-pipeline-contract.md`
3. `shared/department-orchestration-contract.md`
4. `shared/project-memory-contract.md`
5. `shared/plan-to-factory-handoff-contract.md`
6. `shared/plugin-audit-contract.md`
7. `shared/t-800-factory-contract.md`
8. `shared/t-800-agent-quality-contract.md`
9. `shared/auto-update-contract.md`
10. `shared/knowledge-update-contract.md`
11. `shared/cloud-hub-setup-contract.md`
12. `shared/project-memory-dual-write-contract.md`

## Приложение C — Machine commands cheat-sheet

```bash
# discovery
bash scripts/discover-target-project.sh --workspace "<ROOT>"

# loop state
bash scripts/t800_loop_state.sh init --memory-path "<MEM>"
bash scripts/t800_loop_state.sh touch --memory-path "<MEM>" --stage factory --message "…"

# canonical gate
python3 scripts/t800_run_gate.py --memory-path "<MEM>" \
  --require-validate --plugin-root "<PLUGIN>" \
  --strict-create --factory-brief "<slug>"

# bypass gate
python3 scripts/t800_factory_bypass_gate.py \
  --plugin-root "<PLUGIN>" --memory-path "<MEM>" --git-diff

# doctor / audit
python3 scripts/t800_doctor.py --workspace "<ROOT>" --plugin-root "<PLUGIN>" --out "<MEM>/audits/<id>"
python3 scripts/t800_plugin_audit.py --plugin-root "<PLUGIN>" --out "<MEM>/audits/<id>"
python3 scripts/t800_audit_to_fixpack.py …   # см. --help скрипта

# structure
bash scripts/validate-agents.sh
bash scripts/audit-agent-graph.sh
bash scripts/verify-install.sh
```

## Приложение D — Честный gap для полного evaluator-optimizer

Чтобы loop стал «как задумано в задании Teya CLAUDE-SYSTEM-MAP», не хватает минимум:

1. **Run schema** — `run_id`, per-run manifest, не кумулятивный лог.
2. **Telemetry** — duration, retries, gate outcomes, model id.
3. **Retrospective agent или скрипт** — Lessons → structured findings JSON.
4. **Patch proposer** — diff промпта + risk class + evidence.
5. **Policy auto-apply** — allowlist low-risk + обязательный `t800_run_gate --strict-create`.
6. **Golden smoke workspace** — фиксированный brief + expected files hash.
7. **Hard-deny hook** (opt-in) — иначе bypass останется социальным.
8. **Запрет self-PASS** на уровне скрипта агрегатора «готово», а не только текста агента.

---

---

## Приложение E — Полный roster registry (43)

Источник: `registry/agents-registry.json` на **1.17.0**. `calls`/`calledBy` усечены если длинные.  
Добавлено с 1.16.1: `t-800-loop-conductor` (readonly, `/t800-loop`).

| id | category | readonly | calls | calledBy |
|----|----------|----------|-------|----------|
| `t-800-scout` | scout | True | maintainer, research-lead, cursor-kb-curator… | main-agent, factory |
| `t-800-intake-clarifier` | research | True | — | main-agent |
| `t-800-research-lead` | research | True | strategist + all research specialists | main-agent, factory, scout |
| `t-800-research-strategist` | research | True | — | research-lead |
| `t-800-research-synthesizer` | research | True | — | research-lead |
| `t-800-research-github` | research | True | — | research-lead |
| `t-800-research-repo-miner` | research | True | — | research-lead |
| `t-800-research-community` | research | True | — | research-lead |
| `t-800-research-clawhub` | research | True | — | research-lead |
| `t-800-research-vendor-docs` | research | True | — | research-lead |
| `t-800-research-docs` | research | True | — | research-lead |
| `t-800-research-news` | research | True | — | research-lead |
| `t-800-prompt-craft` | research | True | — | main-agent, factory |
| `t-800-brain-lead` | brains | True | all brain-* domains | main-agent, factory |
| `t-800-brain-agents` | brains | True | — | brain-lead |
| `t-800-brain-context` | brains | True | — | brain-lead |
| `t-800-brain-cloud` | brains | True | — | brain-lead |
| `t-800-brain-dev` | brains | True | — | brain-lead |
| `t-800-brain-admin` | brains | True | — | brain-lead |
| `t-800-brain-security` | brains | True | — | brain-lead |
| `t-800-brain-tools` | brains | True | — | brain-lead |
| `t-800-brain-teya` | brains | True | — | brain-lead |
| `t-800-factory` | factory | False | scout, research-lead, brain-lead, architect…auditor | main-agent |
| `t-800-factory-architect` | factory | True | artifact-hooks, artifact-scripts, mcp-wiring | factory |
| `t-800-factory-builder` | factory | False | — | factory |
| `t-800-factory-integrator` | factory | False | factory-auditor | factory |
| `t-800-factory-auditor` | factory | True | — | factory, integrator |
| `t-800-artifact-hooks` | factory | True | — | architect, factory |
| `t-800-artifact-scripts` | factory | True | — | architect, factory |
| `t-800-mcp-wiring` | factory | True | — | architect, factory |
| `t-800-prompt-auditor` | factory | True | — | factory |
| `t-800-onboard` | mentor | True | — | main-agent |
| `t-800-system-auditor` | mentor | True | — | main-agent |
| `t-800-plugin-auditor` | system | False | — | main-agent |
| `t-800-operator` | mentor | True | — | main-agent |
| `t-800-maintainer` | maintainer | False | — | main-agent, scout, cursor-kb-curator |
| `t-800-cloud-hub-lead` | cloud-hub | False | analyst, prompt, pack, smoke | main-agent |
| `t-800-cloud-hub-analyst` | cloud-hub | True | — | cloud-hub-lead |
| `t-800-cloud-hub-prompt` | cloud-hub | False | — | cloud-hub-lead |
| `t-800-cloud-hub-pack` | cloud-hub | False | — | cloud-hub-lead |
| `t-800-cloud-hub-smoke` | cloud-hub | False | — | cloud-hub-lead |
| `t-800-cursor-kb-curator` | maintainer | False | maintainer | main-agent, scout |
| `t-800-loop-conductor` | system | True | — | main-agent (`/t800-loop`) |

**Замечание для loop:** `t-800-plugin-auditor` в registry `readonly: False`, но контракт plugin-audit запрещает silent prune — агент пишет audits/fix-packs, не «чинит» плагин сам без `/t800-fix`.  
`t-800-loop-conductor` **readonly** — queue пишет только `t800_loop_queue_write.py`.

---

## Приложение F — Factory: внутренняя цепочка CREATE vs PATCH

### F.1 CREATE (`/t800-start` → factory)

| # | Агент | Пишет | Не пишет | Gate после |
|---|-------|-------|----------|------------|
| 1 | `t-800-factory-architect` | spec в fragment / handoff YAML | production agents | — |
| 1b | `t-800-artifact-hooks` | если тип hook | — | — |
| 1c | `t-800-artifact-scripts` | если нужны scripts | — | — |
| 1d | `t-800-mcp-wiring` | если MCP в spec | — | — |
| 2 | `t-800-factory-builder` | `agents/*.md`, skills, commands, rules, hooks по surface | вне surface | — |
| 3 | `t-800-factory-integrator` | registry, docs/T-800-AGENTS, install wiring | произвольный рефактор | — |
| 4 | `t-800-prompt-auditor` | fragment status | файлы агентов | обязателен для agent/skill/command |
| 5 | `t-800-factory-auditor` | fragment YAML `status` | файлы (readonly) | validate + graph |
| 6 | scripts | stdout | — | validate / graph / verify / run_gate |

### F.2 PATCH (`/t800-fix`)

То же, но:

- architect/builder **ограничены** `files[]` из fix-pack;
- research обычно SKIP;
- companions только если pack явно требует;
- без обновления pack писать вне списка = нарушение контракта (социальное + auditor finding, не отдельный path-lock script).

### F.3 Handoff YAML (минимум)

Из `shared/t-800-factory-contract.md`:

```yaml
status: ok | needs_input | blocked
stage: architect | builder | integrator | auditor | lead
artifacts: [{path, type}]
handoff: {summary, context, open_questions}
registry_patch: {id, file, category, readonly, calls, calledBy, description}
```

---

## Приложение G — Rules плагина (alwaysApply)

| Rule file | alwaysApply | Роль |
|-----------|-------------|------|
| `rules/t-800-mandatory-routing.mdc` | **true** | BLOCKER: артефакты только через factory; цепочка отделов; auto-update notice |
| `rules/t-800-factory-routing.mdc` | false | requestable: делегируй factory |
| `rules/t-800-operator-routing.mdc` | false | requestable: новички → operator |
| `rules/t-800-cloud-hub-routing.mdc` | false | hub setup |
| `rules/t-800-knowledge-refresh.mdc` | false | KB freshness |

Global copy после `/t800-bootstrap`: `~/.cursor/rules/t-800-mandatory-routing.mdc` (consent).  
Install **не** ставит его молча (Lesson в STATE + CHANGELOG 1.12.1).

---

## Приложение H — Инвентарь scripts (machine surface)

| Script | Назначение |
|--------|------------|
| `discover-target-project.sh` | JSON discovery memory/plugin/profile |
| `list-target-plugins.sh` | известные плагины |
| `init-project-memory.sh` | каркас memory |
| `t800_loop_state.sh` | STATE init/touch |
| `t800-state.sh` | legacy/adjacent state helper |
| `t800_run_gate.py` | канон machine gate |
| `t800_factory_bypass_gate.py` | анти-обход factory |
| `t800_doctor.py` | health JSON |
| `t800_plugin_audit.py` | inventory/scorecard |
| `t800_audit_to_fixpack.py` | audit → fix-pack draft |
| `t800_run_report.py` | агрегат → `{memory}/runs/<id>/report.json` |
| `t800_lessons_export.py` | lessons.json по schema |
| `t800_risk_classifier.py` | `risk_class` only (fixtures / patch-file) |
| `t800_lessons_to_fixpack.py` | LOW lessons → fix-pack drafts |
| `t800_loop_queue_write.py` | материализация `loop-queue.md` |
| `t800-loop-dispatcher.sh` | observe FS; уважает `.loop-paused` |
| `t800_golden_check.py` | path/hash golden (`--expected`, `--write-hashes`) |
| `validate-agents.sh/.ps1` | frontmatter agents |
| `audit-agent-graph.sh/.ps1` | registry graph |
| `audit-coverage.sh/.ps1` | KB coverage |
| `audit-cursor-bloat.sh` | alwaysApply fat |
| `audit-cursor-setup.sh` | setup audit |
| `verify-install.sh/.ps1` | post-install |
| `health-check.sh/.ps1` | aggregate health → HEALTH-REPORT |
| `install-plugin.sh/.ps1` | copy → plugins/local |
| `install-global-routing-rule.sh` | consent mandatory rule |
| `t800-auto-version-check.sh` | sessionStart version |
| `t800-update-from-github.sh` | zip/install from GitHub |
| `sync-docs.ps1` | Cursor docs → raw/UPDATE-QUEUE |
| `register-agent.ps1` | registry upsert |
| `first-run-status.sh` | bootstrap status |
| `fix-kb-frontmatter.ps1` | KB frontmatter repair |
| `test-dialogues.ps1` | dialogue tests (Windows) |

---

## Приложение I — `t800_loop_state.sh` поведение (факт)

| Команда | Эффект |
|---------|--------|
| `init --memory-path PATH` | создаёт dirs; копирует/заполняет `STATE.md` из `templates/STATE.md.template` |
| `touch --memory-path PATH --stage S --message M` | дописывает строку в In progress / Completed (реализация в скрипте) |
| Exit | 0 unless bad args |

**Не делает:** не пишет run-manifest; не запускает gates; не считает retries; не валидирует формат Lessons.

---

## Приложение J — `t800_audit_to_fixpack.py` (факт)

| Вход | `--audit-dir` (нужны scorecard/inventory), `--memory-path`, опц. `--slug` |
|------|--------------------------------------------------------------------------|
| Выход | `{memory}/fix-packs/<slug>.md` draft |
| Качество | Часто плейсхолдеры путей; P0 orphans / P1 alwaysApply секции |
| Дальше | Человек правит `files[]` → `/t800-fix` |

Реальные drafts: `t-800-memory/fix-packs/{final-smoke,smoke-from-self-audit,smoke-v1131-clean}.md`.

---

## Приложение K — Сравнение Teya post-run loop vs T-800 loop MVP

| Свойство | Teya Pro (эталон из задания) | T-800 **1.17.0** |
|----------|------------------------------|------------------|
| Триггер после прогона | post-run 4/4 | observe dispatcher + **semi-manual** `/t800-loop` (не stop/followup) |
| Ретроспектива | `teya-post-run-retrospective` | `t800_run_report` → lessons + `t-800-loop-conductor` |
| Патч промптов | `teya-plugin-engineer` | `/t800-fix` + factory (HITL queue) |
| Аудит прогона | `teya-run-auditor` + manifest | report.json + auditor/doctor/plugin-audit |
| Brain proposals | есть в Teya Brain | UPDATE-QUEUE только для docs KB |
| Machine gate «готово» | свои gates сайта/темы | `t800_run_gate.py` + golden + factory-auditor |
| Repair budget | свои ретраи отделов | max 2 на factory auditor |
| Релиз плагина | `/teya-release-sync` и т.п. | git push main + auto-update |
| Метрики токенов | НЕТ ДАННЫХ (типично) | НЕТ ДАННЫХ |

Вывод: T-800 **1.17** замыкает semi-manual loop (report→lessons→classify→queue→`/t800-fix`), но **auto-LOW OFF** и полного KPI-telemetry ещё нет.

---

## Приложение L — Profiles discovery → куда писать

| profile | memory_dir | plugin_root | Типичный кейс |
|---------|------------|-------------|---------------|
| `self-t800` | `t-800-memory/` | `t-800-agent/` | этот workspace |
| `teya-client` | `teya-memory/` | `$TEYA_PLUGIN_ROOT` | сайт клиента |
| `teya-plugin-dev` | `plugin-memory/` (+ `.teya-plugin-run/`) | checkout TeyaPlugin | разработка Teya |
| `generic-plugin` | marker / `{slug}-memory/` | marker/workspace | чужой плагин |
| `cursor-workspace` surface | memory проекта | — | rules/skills в `.cursor/` |
| `cursor-user` surface | — | `~/.cursor/` | user rules |

Cloud Hub подпапка: всегда внутри канонического memory (`shared/project-memory-dual-write-contract.md`).

---

## Приложение M — Пример реального STATE Gates (после v1.13)

Из `t-800-memory/STATE.md` (не выдумано):

| Gate | Результат |
|------|-----------|
| factory-auditor | ok (PATCH v1.13, no new leaf) |
| validate-agents | n/a this run |
| audit-agent-graph | n/a this run |
| verify-install | exit 0 |
| t800_run_gate | exit 0 |
| t800_doctor | exit 0 |
| plugin-audit inventory | smoke у parent |
| user-home t-800 mirrors | ABSENT |

Lessons там же про verify/health paths и bootstrap consent — **повторно появляются в дизайне**, значит loop их не «вылечил системно», а зафиксировал текстом.

---

## Приложение N — Рекомендуемый минимальный дизайн loop-отдела (не реализация)

Только ориентир архитектору; **не** создано в этой карте:

1. `run-manifest` per `run_id` (схема JSON) + writer из Директора.
2. `scripts/t800_run_report.py` — агрегатор gate JSON → `{memory}/runs/<run_id>/report.json`.
3. Structured Lessons schema (`findings[].risk`, `evidence`, `suggested_files`).
4. Команда `/t800-loop` или расширение `/t800-fix`: retrospective → draft pack → optional auto PATCH if risk=low.
5. Golden smoke: workspace fixture + expected hash list.
6. Opt-in `beforeFileEdit` hard-deny.
7. Запрет новых research/brain агентов сохранить (усиливать scripts, не roster).

---

## Приложение O — Файлы этой карты

| Файл | Роль |
|------|------|
| [`t-800-agent/T800-SYSTEM-MAP.md`](T800-SYSTEM-MAP.md) | **Канон** (корень git-репо плагина) |
| [`../T800-SYSTEM-MAP.md`](../T800-SYSTEM-MAP.md) | Указатель из workspace parent |

При расхождении с кодом верить: `.cursor-plugin/plugin.json`, `registry/agents-registry.json`, `knowledge-base/CHANGELOG.md`, скриптам в `scripts/`.

---

*Конец T800-SYSTEM-MAP.md. При устаревании сверять version + CHANGELOG; не дополнять маркетингom.*
