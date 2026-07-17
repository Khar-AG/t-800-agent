# Тест-сценарии T-800 Agent

Ручная проверка после `bash scripts/install-plugin.sh` (или `.ps1`) и перезапуска Cursor.

**PASS install:** артефакты в `~/.cursor/plugins/local/t-800-agent/{agents,commands,rules,skills}` — **не** в `~/.cursor/agents` и т.п.

## Подготовка

1. `bash scripts/install-plugin.sh` (Windows: `.\scripts\install-plugin.ps1`)
2. `bash scripts/verify-install.sh` — verification passed
3. Перезапустить Cursor (Reload Window)
4. Открыть любой тестовый проект

---

## Сценарий 1 — Первый запуск

**Ввод пользователя:**
```
Я впервые в Cursor, что делать?
```

**Ожидание:**
- Главный агент делегирует именно `Task(t-800-operator)` (rule routing)
- Нельзя считать PASS, если главный агент просто отвечает «в стиле T-800 Agent»
- Ответ: суть + шаги + ссылка на playbook `00-pervyy-raz.md`
- Русский язык
- Не более 7 шагов за раз

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 2 — Режимы Plan vs Agent

**Ввод:**
```
Чем Plan отличается от Agent? Объясни как для новичка.
```

**Ожидание:**
- Таблица или mermaid-схема выбора режима
- Без правки файлов (t-800-operator readonly)
- Ссылка на `knowledge-base/02-agent-i-rezhimy/rezhimy-tablica.md` или help

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 3 — Автоматизация

**Ввод:**
```
Хочу автоматизировать публикации статей. С чего начать в Cursor?
```

**Ожидание:**
- Playbook 01 (rule + skill + Auto-review)
- **Не** рекомендует Run Everything
- Пошаговый чеклист

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 4 — Другой язык

**Ввод:**
```
Explain Agent mode in simple English.
```

**Ожидание:**
- Ответ на английском
- Предложение зафиксировать язык в user rules

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 5 — Опытный пользователь

**Ввод:**
```
Рефакторинг модуля auth без объяснений, просто сделай.
```

**Ожидание:**
- T-800 Agent **не** вызывается
- Главный агент работает в Agent без обучающего тона

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 6 — zen-intel-retro (factory bypass)

**Контекст:** инцидент Zen Intel — agents/skills собраны в main chat без `Task(t-800-factory)`.

**Проверка (machine, из `plugin_root` t-800-agent):**

```bash
# 1) Синтетика: «новый agent» без factory в manifest → FAIL
python3 scripts/t800_factory_bypass_gate.py \
  --plugin-root . \
  --memory-path /tmp/t800-empty-memory-$$ \
  --files agents/foo-scout.md
# ожидание: exit 1, FAIL … без завершённого шага t-800-factory

# 2) strict-create без factory step → FAIL (нужен memory с STATE.md, без factory completed)
python3 scripts/t800_run_gate.py \
  --memory-path "<memory_with_STATE_no_factory>" \
  --strict-create
# ожидание: exit 1

# 3) Обычный код не блокируется hook (before-artifact-edit allow без WARN на src/*.py)
```

**Ожидание поведения Директора:**
- Не `Write`/`StrReplace` в `agents/` · `skills/` · `commands/` · `rules/` · `hooks`
- Только `/t800-start` или `/t800-fix` → `Task(t-800-factory)`
- Plan с factory-brief → Implement по `shared/plan-to-factory-handoff-contract.md`

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 7 — /t800-loop + dispatcher + classifier

**Контекст:** Loop Engineering v2 — semi-manual закрытие прогона без stop/followup.

**Ввод пользователя:**
```
/t800-loop
```

**Ожидание поведения:**
- Директор зовёт `Task(t-800-loop-conductor)` (не полный DEEP `/t800-start`)
- Скрипты: report → lessons export → queue write; `risk_class` только из `t800_risk_classifier.py`
- Нет второго `sessionStart` hook — dispatcher внутри bootstrap

**Проверка (machine, из `plugin_root` t-800-agent):**

```bash
# 1) Pause: dispatcher уважает .loop-paused
MEMORY="<memory_path>"
touch "$MEMORY/.loop-paused"
bash scripts/t800-loop-dispatcher.sh --memory-path "$MEMORY"
# ожидание: exit 0 / skip с сообщением paused; без записи в queue

# 2) Classifier fixtures — zero false LOW
python3 scripts/t800_risk_classifier.py --fixture-dir tests/fixtures/loop
# или golden:
python3 scripts/t800_golden_check.py --expected docs/examples/self-golden/expected.json --root .
# ожидание: exit 0; ни один HIGH/MED fixture не классифицирован как LOW
```

**Статус:** [ ] PASS [ ] FAIL

---

## Сценарий 8 — KB provenance gate

**Цель:** machine gate не пускает orphan-файлы в `knowledge-base/` без manifest или manual provenance.

```bash
cd t-800-agent
python3 -m py_compile scripts/t800_kb_provenance_gate.py

python3 scripts/t800_kb_provenance_gate.py --fixture-dir tests/fixtures/kb-provenance/legal-sync
# ожидание: exit 0

python3 scripts/t800_kb_provenance_gate.py --fixture-dir tests/fixtures/kb-provenance/legal-manual
# ожидание: exit 0

python3 scripts/t800_kb_provenance_gate.py --fixture-dir tests/fixtures/kb-provenance/illegal-orphan
# ожидание: exit 1 + violations в JSON
```

**Ожидание:**
- legal-sync / legal-manual → exit 0
- illegal-orphan → exit 1
- `verify-install` lists `t800_kb_provenance_gate.py`

**Статус:** [ ] PASS [ ] FAIL

---

## Проверка установки (автоматическая)

| Файл | Путь | Проверено |
|------|------|-----------|
| Subagent | `%USERPROFILE%\.cursor\agents\t-800-operator.md` | PASS |
| Legacy skill | `%USERPROFILE%\.cursor\skills\t-800-operator\SKILL.md` | MUST NOT EXIST |
| Maintainer skill | `%USERPROFILE%\.cursor\skills\t-800-knowledge-base\SKILL.md` | PASS |
| Rule | `%USERPROFILE%\.cursor\rules\t-800-operator-routing.mdc` | PASS |
| Command | `%USERPROFILE%\.cursor\commands\t-800-operator.md` | PASS |
| KB INDEX | `knowledge-base/INDEX.md` | PASS |
| Playbook 00 | `playbooks/00-pervyy-raz.md` | PASS |
| Sync report | `knowledge-base/SYNC-REPORT.md` | PASS |

## Fallback (Cloud)

Если `Task(t-800-operator)` недоступен:
```
Task(generalPurpose) + full prompt from agents/t-800-operator.md
```

## Проверка конфликта skill/subagent

**Ожидание после установки:**

- `%USERPROFILE%\.cursor\agents\t-800-operator.md` существует
- `%USERPROFILE%\.cursor\skills\t-800-operator\SKILL.md` отсутствует
- `%USERPROFILE%\.cursor\skills\t-800-knowledge-base\SKILL.md` существует
- `/t-800-operator` не должен отвечать сам: он должен просить главный Agent вызвать `Task(t-800-operator)`
