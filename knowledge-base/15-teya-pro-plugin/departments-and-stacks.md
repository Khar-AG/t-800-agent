---
title: "Teya — отделы и стэки"
audience: advanced
last_synced: 2026-07-06
---

# Manager vs Leaf

| Тип | Примеры | Task() |
|-----|---------|--------|
| Manager | teya-site-manager, director | Оркестрирует |
| Leaf | excalibur-geo-qa, *-reviewer | Не вызывает Task |

Контракт: `$TEYA_PLUGIN_ROOT/shared/cross-department-helper-contract.md`

## Отделы (ориентир)

- Site / Visual / Content / Presentation / Promotion
- Aurora team (WP build)
- Post-Run (auditor, plugin-engineer, knowledge-curator)

Новый агент Teya — указать стэк и отдел в architect spec.

Инвентарь: `python3 scripts/teya_plugin_inventory.py`
