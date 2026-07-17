# /t800-start — универсальный запуск отдела T-800

**Единая команда.** Создание rules, skills, commands, subagents, hooks — для **плагина**, **текущего проекта** или **глобально**.

**Правка существующего** по списку файлов / после аудита → **`/t800-fix`** (fix-pack + PATCH), не полный DEEP-старт.  
Контракт: `shared/fix-pipeline-contract.md`.

## Закон оркестрации (Директор)

Контракт: `shared/department-orchestration-contract.md`.  
Loop / STATE / gates: `shared/loop-engineering-contract.md`.

1. Зовёшь **лидов отделов**, не leaf-специалистов (github, brain-context, builder…).
2. Специалисты Research / Brains / Factory запускаются **автоматом внутри лида**.
3. После каждого отдела — **одна строка progress** пользователю + `t800_loop_state.sh touch`.
4. Новых агентов в Research/Brains **не добавляем** — только эта цепочка.
5. «Готово» только при factory-auditor PASS **и** machine scripts exit 0 (когда применимо).

## 0. Куда пишем (surface + memory)

```bash
bash scripts/discover-target-project.sh --workspace "."
bash scripts/list-target-plugins.sh --workspace "."
```

Запомни `memory_path`. Затем:

```bash
bash scripts/t800_loop_state.sh init --memory-path "<memory_path>"
# Read STATE.md — blockers, lessons, last gates
```

| Пользователь сказал | artifact_surface |
|---------------------|------------------|
| «для этого проекта / в репо» | `cursor-workspace` → `.cursor/` |
| «глобально / user rules» | `cursor-user` → `~/.cursor/` |
| «для Teya / плагина X» | `cursor-plugin` → git checkout |

Если неясно — **один вопрос:** плагин, проект или глобально?

Контракты: `shared/artifact-surfaces-contract.md`, `shared/target-selection-contract.md`, `shared/project-memory-contract.md`

## 0b. Intake (уточнения до тяжёлой research)

Если неоднозначны модели / MCP / surface / readonly / integrations (Kie, GRS, …):

```
Task(t-800-intake-clarifier)
```

2–5 вопросов → дождаться ответов. Если всё ясно — `skipped`.  
Контракт: `shared/deep-research-contract.md` (intake gate).  
≠ `t-800-operator` (не обучение Cursor).

После отдела:

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "intake" --message "skipped|answered"
# Progress: T-800 ▸ [■□□□□] 1/5 …
```

## 1. Разведка (официальная)

```
Task(t-800-scout)
```

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "scout" --message "scout_report готов"
```

## 2. Веб-разведка — режим по тесту (не только фраза)

Перед вызовом выбери **DEEP | LIGHT | SKIP** по `shared/loop-engineering-contract.md` (Research mode test):

| Режим | Когда |
|-------|--------|
| DEEP | default: новый домен / «изучи свежее» / сложный multi-source |
| LIGHT | мелкий твик, известный паттерн, «быстрый обзор» |
| SKIP | «только KB», offline, тривиальный copy |

```
Task(t-800-research-lead)   # передай research_mode
```

Внутри lead (DEEP/LIGHT):

1. **`t-800-research-strategist`** — мозг: *куда* искать  
2. Fan-out специалистов по `search_plan`  
3. **`t-800-research-synthesizer`** — один оптимальный вариант  

| Специалист | Когда (решает strategist) |
|------------|---------------------------|
| `t-800-research-github` | код / skills / examples |
| `t-800-research-repo-miner` | deep dig ≥2 repos |
| `t-800-research-community` | Reddit / Habr / HN |
| `t-800-research-clawhub` | маркетплейс skills |
| `t-800-research-vendor-docs` | GPT Cookbook, Claude, Gemini, Perplexity, Kie… |
| `t-800-research-docs` | Context7 library/API |
| `t-800-research-news` | свежие changelog / blogs |

Минимумы DEEP: ≥8 источников, coverage_matrix PASS, synthesis с сравнением.  
Контракты: `shared/search-strategy-contract.md`, `shared/deep-research-contract.md`.

**Context7 не always-on** — только если strategist поставил канал `docs`.

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "research" --message "mode=DEEP|LIGHT|SKIP; synthesis готов|skipped"
```

## 2b. Prompt craft (условно)

Если artifact ∈ {agent, skill, command}:

```
Task(t-800-prompt-craft)
```

Контракт: `shared/prompt-craft-contract.md`.

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "prompt_craft" --message "prompt_spec|skip"
```

## 3. Нейросеть

```
Task(t-800-brain-lead)
```

Вход: intake_brief?, scout_report, research_brief (+ docs/vendor/clawhub?), prompt_spec?, target_context, artifact_surface.

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "brain" --message "brief_for_factory готов"
```

## 4. Конвейер

```
Task(t-800-factory)
```

Цепочка (отделы + loop):

```
[System]  intake? → scout
[Research] research-lead  ──АВТО──► strategist → specialists → synthesizer
[Craft]   prompt-craft?
[Brains]  brain-lead      ──АВТО──► 1–2 domain brains
[Factory] factory         ──АВТО──► architect → companions? → builder
                                    → integrator → prompt-auditor? → auditor
                                    → machine gates (validate/audit/verify)
                                    → repair ≤2 при FAIL
```

Progress: 5 этапов; этап 5 done = auditor PASS **и** machine scripts exit 0.

```bash
bash scripts/t800_loop_state.sh touch --memory-path "<memory_path>" --stage "factory" --message "auditor PASS + gates exit 0"
```

## 5. Закрытие (machine gate)

Не пиши «готово», если:

- factory-auditor `status` ≠ `ok`
- validate-agents / audit-agent-graph / verify-install (когда применимо) ≠ exit 0

Обнови STATE: Completed, Lessons, Gates.  
Repair budget: после 2 FAIL → escalate пользователю (`loop-engineering-contract`).

**Закрытие loop (рекомендуется):** после успешного прогона вызови **`/t800-loop`** — run report, lessons export, handoff в `loop-queue.md` (см. `shared/loop-engineering-contract.md` v2).

---

Примеры:

```
/t800-start
Найди свежие skill-паттерны (GitHub + ClawHub) и сделай skill для этого проекта.

/t800-start
Создай user rule: всегда отвечать на русском. Глобально.

/t800-start
Для Teya Plugin: subagent readonly для audit manifest. Модель и MCP уточни.
```

Реестр плагинов: `~/.t800/known-plugins.json`
