---
title: "Teya — чеклист качества агента"
audience: advanced
last_synced: 2026-07-06
---

# Чеклист agent-quality (выжимка Teya)

Полный контракт: `$TEYA_PLUGIN_ROOT/shared/agent-quality-contract.md`

## Минимум

- [ ] `name`, `description` (Use when + Do NOT use when), `model: inherit`, `readonly`
- [ ] Роль, что читать, задача, выходы, запреты
- [ ] Teya Brain retrieval + `kb_usage[]` в Work Report
- [ ] Fragment в `teya-memory/fragments/`

## Reviewer / Guardian

- [ ] `readonly: true` по инструкции (не правит production)
- [ ] Пишет findings / fix-pack
- [ ] Не ставит PASS при открытых BLOCKER

## Leaf-specialist

- [ ] Не запускает `Task()` сам
- [ ] `helper_needed` → Директор

## Docs

- [ ] Попал в `teya_docs_build.py` → COMMAND_AGENTS если есть slash-команда
