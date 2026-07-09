# Discovery — шпаргалка

```bash
bash scripts/discover-target-project.sh --workspace "."
bash scripts/init-project-memory.sh --workspace "." --slug my-plugin
```

| profile | memory | plugin_root |
|---------|--------|-------------|
| teya-client | teya-memory/ | TEYA_PLUGIN_ROOT |
| teya-plugin-dev | plugin-memory/ | workspace |
| generic-plugin | {slug}-memory/ | workspace |
| self-t800 | t-800-memory/ | t-800-agent/ |

Если `needs_user_question: true` — спросить путь plugin_root один раз.
