# Changelog базы знаний T-800

Формат: дата — что изменилось — источник.

## 1.15.2 — 2026-07-09

- Подробный README: возможности, все команды, сценарии, **примеры промптов** (audit Cursor, doctor, plugin-audit, start/fix)
- Docs: НАЧАЛО-РАБОТЫ, ПОЛНАЯ-ИНСТРУКЦИЯ, ОБНОВЛЕНИЕ, СЦЕНАРИЙ-СТАРТА — без «обновляй zip каждый раз»; акцент на `/t800-bootstrap` и автообновление
- Описание плагина: старт через `/t800-start`, не через ручной update

## 1.15.1 — 2026-07-09

- Версию с GitHub читаем через **API** (`Accept: application/vnd.github.raw+json`), не через CDN `raw.githubusercontent.com` (у raw бывает лаг после push)
- Fallback на raw с cache-buster, если API недоступен
- Исправлено: после релиза 1.15.0 auto-check мог видеть старую 1.14.0 и уходить в fail-open

## 1.15.0 — 2026-07-09

- **Автопроверка версии** на `sessionStart`: `t800-auto-version-check.sh` + hook JSON `additional_context`
- При новой версии на GitHub — автоустановка, затем Reload + продолжение задачи
- Контракт: `shared/auto-update-contract.md`; TTL-кэш 6ч; `T800_SKIP_AUTO_UPDATE=1`
- `/t800-update` — ручной fallback к автохуку

## 1.14.0 — 2026-07-09

- Публичный GitHub: https://github.com/Khar-AG/t-800-agent
- `scripts/t800-update-from-github.sh` — сравнение версий + автоустановка с `main`
- `/t800-update` переписан под GitHub (не только zip)
- `shared/release-channel.json` — канон канала обновлений
- README + обложка `assets/t800-cover.png` + LICENSE MIT

## 1.13.1 — 2026-07-09

- `t800_plugin_audit.py`: orphans = **нет в registry** (не «нет в command-chains»)
- `soft_unreferenced` — info без WARN (leaf brains/factory — норма)
- Smoke: self-audit T-800 → PASS при полной registry sync

## 1.13.0 — 2026-07-09

- **`/t800-fix`** + `shared/fix-pipeline-contract.md` + `templates/fix-pack.md.template` — PATCH по fix-pack (SKIP/LIGHT research)
- **`/t800-doctor`** + `scripts/t800_doctor.py` — scripts-only health
- **`scripts/t800_run_gate.py`** — канонический machine gate (STATE + optional validate/audit)
- **`scripts/t800_audit_to_fixpack.py`** — audit → `{memory}/fix-packs/<slug>.md`
- Handoff: plugin-audit / system-audit → fix-pack → `/t800-fix`
- Factory: `mode: PATCH`; loop-engineering ссылается на run_gate
- Roster **36** без новых leaf/research/brain агентов

## 1.12.1 — 2026-07-09

- **No user-home mirrors:** `install-plugin` пишет только в `~/.cursor/plugins/local/t-800-agent`
- Убрано копирование agents/commands/rules/skills в `~/.cursor/{agents,commands,rules,skills}`
- Optional allowlisted cleanup старых `t-800-*` зеркал в user-home (не трогает `t-800-mandatory-routing.mdc`)
- `verify-install` / `health-check` проверяют PLUGIN paths; global mandatory-routing = WARN
- KEEP: `install-global-routing-rule.sh` + `/t800-bootstrap` (consent)
- Docs/KB/README/SKILL/TEST синхронизированы с plugin-local каноном

## 1.12.0 — 2026-07-09

- **Loop engineering** (Habr / Osmani / Anthropic evaluator-optimizer) — без новых агентов
- `shared/loop-engineering-contract.md` — STATE.md, machine gates, repair budget 2, research mode test
- `templates/STATE.md.template` + `scripts/t800_loop_state.sh` (init/touch)
- `/t800-start` + `/t800-plugin-audit`: init/read STATE; «готово» только с machine evidence
- Factory: repair ≤2 → escalate; auditor отчёт `machine_gates` + `ralph_wiggum_risk`
- Roster **36** без изменений

## 1.11.0 — 2026-07-09

- **`/t800-plugin-audit`** + `t-800-plugin-auditor` — аудит одного плагина (inventory, graph, orphans, alwaysApply)
- `scripts/t800_plugin_audit.py` — machine SoT → `{memory_path}/audits/<run-id>/`
- Контракт: `shared/plugin-audit-contract.md` (не путать с `/t800-audit` и `/teya-run-audit`)
- MEMORY LAW: runtime-карта чужого плагина **не** в knowledge-base T-800
- Roster **35 → 36**; category `system`

## 1.10.1 — 2026-07-09

- Контракт отделов: `shared/department-orchestration-contract.md`
- Директор → только лиды; Research/Brains/Factory **авто** fan-out специалистов
- Progress-бар между отделами (5 этапов); без новых research/brain агентов
- Обновлены: t800-start, research-lead, brain-lead, factory, mandatory-routing

## 1.10.0 — 2026-07-09

- `/t800-audit` + `t-800-system-auditor` — интерактивный разбор rules/skills (alwaysApply, bloat)
- `scripts/audit-cursor-bloat.sh` — оценка «жира» контекста
- `/t800-update` + `docs/ОБНОВЛЕНИЕ.md` — промпт обновления со старых версий
- Roster **34 → 35**

## 1.9.0 — 2026-07-09

- Автономный поиск: `t-800-research-strategist` (куда искать) + `t-800-research-synthesizer` (лучший вариант)
- Контракт: `shared/search-strategy-contract.md`
- Roster **32 → 34**; research-lead: strategist → fan-out → synthesizer
- Пользователь не обязан перечислять сайты — отдел сам выбирает GitHub/Reddit/ClawHub/Context7/cookbooks

## 1.8.1 — 2026-07-09

- Vendor mastodons: **OpenAI Cookbook**, Claude prompting, Gemini strategies, **Perplexity**, Kie, Cursor
- `t-800-research-vendor-docs` → `idea_seeds[]`; DEEP multi-model → min 3 мастодонта
- `prompt-craft` потребляет idea_seeds; matrix + Perplexity

## 1.8.0 — 2026-07-09

- Roster **27 → 32**: `t-800-research-clawhub`, `t-800-research-repo-miner`, `t-800-research-vendor-docs`, `t-800-research-news`, `t-800-intake-clarifier`
- Контракты: `shared/deep-research-contract.md`, `shared/clawhub-research-contract.md`, `shared/vendor-docs-matrix.md`
- Research-lead **DEEP MODE** default + coverage_matrix FAIL incomplete
- `/t800-start`: step 0b intake-clarifier; fan-out ClawHub / repo-miner / vendor / news
- Context7: trigger any API/SDK/MCP name; deep budget ≤5 (LIGHT ≤3)
- Gaps D1–D7 CLOSED (см. `17-team-capability-audit/team-roster-gaps.md`)

## 1.7.0 — 2026-07-09

- Roster **21 → 27**: `t-800-research-docs`, `t-800-prompt-craft`, `t-800-artifact-hooks`, `t-800-artifact-scripts`, `t-800-mcp-wiring`, `t-800-prompt-auditor`
- Контракты: `shared/research-docs-contract.md`, `shared/prompt-craft-contract.md`
- Цепочка `/t800-start`: scout → research-lead (+docs если library) → prompt-craft? → brain → factory (companions → prompt-auditor → auditor)
- Context7 **не** always-on; hooks.json → object map `{version, hooks:{event:[...]}}`
- Gaps G1–G7 CLOSED (см. `17-team-capability-audit/team-roster-gaps.md`)

## 2026-07-08 — v1.6.0 docs: сценарий старта 4 шага

- `docs/СЦЕНАРИЙ-СТАРТА.md` — канонический онбординг через Cursor Agent
- Обновлены README, INSTALL, НАЧАЛО-РАБОТЫ, share/T-800-ИНСТРУКЦИЯ.md

## 2026-07-08 — v1.6.0 First-run bootstrap + точность исполнения

- Команда `/t800-bootstrap` — аудит → объяснение → глобальное rule **по согласию**
- Скрипты: `first-run-status.sh`, `t800-state.sh`, `install-global-routing-rule.sh`
- `~/.t800/state.json` — флаг первого запуска
- Глобальное `t-800-mandatory-routing.mdc` **не** копируется при install — только bootstrap
- Контракты: `first-run-contract.md`, `execution-quality-contract.md`

## 2026-07-08 — v1.5.0 Onboard для новичков

- Команда `/t800-onboard` + агент `t-800-onboard`
- Скрипт `audit-cursor-setup.sh` — global vs local inventory

## 2026-07-06 — v1.4.0 Universal department + web research

- 20 агентов: research-lead, research-github, research-community
- artifact_surface: cursor-plugin | cursor-workspace | cursor-user
- research-freshness-contract (90 дней), GitHub/Reddit/Habr/X
- Цепочка: scout → research-lead → brain → factory

## 2026-07-06 — v1.3.0 Universal commands only

- Удалена `/t800-teya` — только `/t800-start` + текст задачи
- `list-target-plugins.sh`, `~/.t800/known-plugins.json`, `target-selection-contract.md`
- Выбор плагина: текст пользователя или один уточняющий вопрос

## 2026-07-06 — v1.2.0 Universal Project Memory

- Discovery: `discover-target-project.sh`, `init-project-memory.sh`
- Контракты: `project-discovery-contract.md`, `project-memory-contract.md`
- KB 16-universal-project-memory, аудит Teya memory
- Factory/brain/rules: memory_path из discovery, без hardcode target_plugin=t-800-agent
- `project-memory.marker.json` в workspace T-800 AGENT

## 2026-07-06 — v1.1.0 Department Hardening

- P0: verify-install, install.ps1/sh parity, docs/T-800-AGENTS, t800-start
- Bash gates: verify, validate, audit-graph, coverage, health
- Контракты: task-prompt, agent-quality, work-report, target-plugin-profiles
- Teya profile: KB 15-teya-pro-plugin, t-800-brain-teya, /t800-teya
- KB coverage 44/44 explicit (manifest-coverage-map)
- hooks.json эталон, t-800-memory/, factory example teya-test-scout-readonly

## 2026-07-02 (6)

- Добавлены `scripts/health-check.ps1` и команда `/t-800-health`
- Добавлены тестовые диалоги `tests/t-800-operator-dialogues.md` и `scripts/test-dialogues.ps1`
- Добавлена матрица маршрутизации `routing-test-cases.md`
- Добавлены учебные материалы `learning-path-7-days.md` и `typical-beginner-failures.md`
- Обновлены install/verify, INDEX и prompt `t-800-operator`

## 2026-07-02 (5)

- Добавлен maintainer-субагент `t-800-maintainer` для обслуживания KB, sync, coverage и verify
- Добавлен `scripts/audit-coverage.ps1` и отчёт `knowledge-base/COVERAGE-REPORT.md`
- Добавлены профили новичков и wizard-сценарии: первый проект, автоматизация, MCP, ошибка, Canvas
- Обновлены `agents/t-800-operator.md`, `INDEX.md`, `install-plugin.ps1`, `verify-install.ps1`, команды и rule обновления KB

## 2026-07-02 (4)

- Расширена база знаний до почти полной карты Cursor Docs/Help/Learn для T-800 Agent
- Добавлены P0-карточки: Ask Mode, Plan Mode, Debug Mode, Prompting, Agent Review, Terminal, Browser, Search, Security Run Modes
- Добавлены продвинутые разделы: Cloud Agents, Automations, Hooks, Teams/Dashboard, Pricing/Usage, Integrations, Bugbot/Security Agents, CLI, SDK, Cloud Agents API
- Обновлены `INDEX.md`, `agents/t-800-operator.md` и seed URL в `sync-docs.ps1`

## 2026-07-02 (3)

- Исправлена архитектура T-800 Agent: `t-800-operator` теперь полноценный субагент в `agents/t-800-operator.md`, а не skill-заглушка
- Удалён конфликтующий skill `t-800-operator`; оставлен только maintainer-skill `t-800-knowledge-base` с `disable-model-invocation: true`
- Добавлен `scripts/verify-install.ps1` для проверки установки
- Очищен `UPDATE-QUEUE.md` от mojibake и уже обработанных пунктов
- `sync-docs.ps1` переведён на ASCII-служебные строки, чтобы PowerShell 5 не портил кириллицу
- Sync проверен: 11/11 страниц OK, `docs/rules` закрыт существующей карточкой `03-kontekst/rules.md`

## 2026-07-02 (2)

- Добавлена карточка `02-agent-i-rezhimy/canvas-i-shared-canvases.md` (Canvas, Shared Canvases, Publish)
- Seed sync: `https://cursor.com/docs/agent/tools/canvas`
- Обновлены INDEX, glossarium, SKILL routing

## 2026-07-02

- Первая версия базы знаний (разделы 01–08, glossarium, playbooks)
- Добавлен `sync-docs.ps1` и контракт обновления
- Добавлено rule `t-800-knowledge-refresh`
