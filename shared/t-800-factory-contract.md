# Контракт handoff между агентами T-800 Factory

Каждый субагент отдела возвращает ответ в этом формате.

## Обязательные поля

```yaml
status: ok | needs_input | blocked
stage: architect | builder | integrator | auditor | lead
agent_id: null  # для нового агента — предлагаемый name
```

## Артефакты

```yaml
artifacts:
  - path: agents/my-agent.md
    type: subagent
  - path: commands/my-agent.md
    type: command
  - path: rules/routing-my.mdc
    type: rule
```

## Handoff следующему агенту

```yaml
handoff:
  summary: "Спецификация готова, нужно создать файлы"
  context:
    name: my-agent
    readonly: true
    category: content
    description: "..."
    calls: []
    calledBy: ["t-800-factory"]
  open_questions: []
```

## registry_patch (для integrator)

```json
{
  "id": "my-agent",
  "file": "agents/my-agent.md",
  "category": "content",
  "readonly": true,
  "calls": [],
  "calledBy": ["t-800-factory"],
  "description": "..."
}
```

## Запреты

- Не пропускать auditor перед финальным отчётом пользователю
- Не менять `name` после builder без повторного architect
- Не добавлять в registry без существующего файла
