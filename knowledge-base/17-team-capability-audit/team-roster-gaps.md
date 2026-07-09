# Аудит команды T-800 — 2026-07-06

## v1.8.0 — gaps D1–D7 CLOSED (2026-07-09)

Roster: **27 → 32**. Deep Research Department.

| Gap | Пробел | Закрытие |
|-----|--------|----------|
| D1 | Нет ClawHub | `t-800-research-clawhub` + `shared/clawhub-research-contract.md` |
| D2 | GitHub поверхностный | `t-800-research-repo-miner` + handoff из github |
| D3 | Нет вендор-доков | `t-800-research-vendor-docs` + `shared/vendor-docs-matrix.md` |
| D4 | Нет news pass | `t-800-research-news` |
| D5 | Нет уточнений у новичка | `t-800-intake-clarifier` (step 0b `/t800-start`) |
| D6 | Research «тонкий» | `shared/deep-research-contract.md` — ≥8 sources, ≥2 mines, coverage_matrix |
| D7 | Context7 робкий | trigger API/SDK/MCP; deep budget ≤5 |

Аудит: `t-800-memory/audits/team-v1.8-deep-research-gaps.md`

## v1.7.0 — gaps G1–G7 CLOSED (2026-07-09)

Roster: **21 → 27**. Context7 условно (не always-on).

| Gap | Пробел | Закрытие |
|-----|--------|----------|
| G1 | Context7 / library docs | `t-800-research-docs` + `shared/research-docs-contract.md` |
| G2 | prompt-craft | `t-800-prompt-craft` + `shared/prompt-craft-contract.md` |
| G3 | hooks + scripts как типы | `t-800-artifact-hooks`, `t-800-artifact-scripts` |
| G4 | artifact-specialists | companions в architect/factory |
| G5 | MCP wiring | `t-800-mcp-wiring` |
| G6 | prompt QA | `t-800-prompt-auditor` перед factory-auditor |
| G7 | Context7 в `/t800-start` | условный вызов через research-lead (не always-on) |

История v1.4 ниже сохранена.

---

## Миссия (целевая)

Универсальный отдел Cursor: **не только плагины**, но и rules, skills, commands, subagents, hooks, scripts — с **актуальной** разведкой из интернета и адаптацией под Cursor.

## Рoster (было: 17 агентов)

| Блок | Агенты | Статус |
|------|--------|--------|
| Scout | `t-800-scout` | ✅ cursor.com + manifest |
| Brains | lead + 8 domain (+ teya) | ✅ локальная KB |
| Factory | lead + architect + builder + integrator + auditor | ✅ только plugin-bias |
| Mentor | `t-800-operator` | ✅ |
| Maintainer | `t-800-maintainer` | ✅ sync KB |
| **Research** | — | ❌ **пробел** |
| **Workspace surface** | — | ❌ **пробел** (только plugin_root) |
| **Freshness gate** | частично в scout | ⚠️ нет community/github |

## Gaps (P0 → P1)

| # | Пробел | Решение v1.4 |
|---|--------|----------------|
| G1 | Нет веб-разведки GitHub/Reddit/Habr | `t-800-research-github`, `t-800-research-community` |
| G2 | Нет оркестратора research | `t-800-research-lead` |
| G3 | Factory только в plugin checkout | `artifact_surface`: workspace / user-global |
| G4 | Устаревшие промпты без проверки даты | `shared/research-freshness-contract.md` (≤90 дней) |
| G5 | Цепочка без research | `/t800-start` → scout → **research-lead** → brain → factory |

## Новые агенты (v1.4)

| Task | Роль |
|------|------|
| `t-800-research-lead` | Оркестратор: GitHub + community, brief для factory |
| `t-800-research-github` | Репозитории, skills, rules, prompts |
| `t-800-research-community` | Reddit, Habr, X, свежие обсуждения |

## Поверхности записи (не только плагин)

| surface | Куда пишем |
|---------|------------|
| `cursor-plugin` | `{plugin_root}/agents|skills|commands|rules` |
| `cursor-workspace` | `{workspace}/.cursor/` |
| `cursor-user` | `~/.cursor/rules`, `~/.cursor/skills`, `~/.cursor/commands` |

Контракт: `shared/artifact-surfaces-contract.md`

## Рекомендуемая цепочка

```
/t800-start
  → t-800-scout
  → t-800-research-lead  (если нужна свежесть / внешние идеи)
  → t-800-brain-lead
  → t-800-factory
```

Research-lead **пропускается** только если пользователь явно сказал «только из локальной KB» или «не искать в интернете».
