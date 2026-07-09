# T-800 Factory — создать или внедрить субагента

**Обязательно** вызови субагента через `Task(t-800-factory)`.

Передай контекст:
- идея нового агента (роль, задачи);
- категория в будущем плагине;
- readonly или с правками файлов;
- кто будет вызывать этого агента;
- что уже есть в `registry/agents-registry.json`.

**НЕ** создавай агента вручную в main chat — делегируй пайплайн Factory.

Если `Task(t-800-factory)` недоступен:

```
Task(generalPurpose)
```

Промпт: полное содержимое `agents/t-800-factory.md` + `registry/agents-registry.json` + `knowledge-base/13-agent-factory/INDEX.md`.
