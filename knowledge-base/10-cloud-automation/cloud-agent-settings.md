---
title: "Cloud Agent Settings — настройки облачных агентов"
source: https://cursor.com/docs/cloud-agent/settings
audience: intermediate
tier: 2
last_synced: 2026-07-02
---

# Cloud Agent Settings

## Простыми словами

Cloud Agent Settings — настройки того, как облачные агенты работают с репозиториями, окружениями, секретами и командными правилами.

## Когда вам это нужно

- Cloud Agent не видит нужный репозиторий
- Нужны environment variables
- Нужно ограничить доступы
- Команда хочет единый режим работы

## Что важно новичку

Секреты нельзя хранить в Git. Всё, что похоже на API key, token, password, должно жить в защищённых настройках, а не в файлах проекта.

## Мини-чеклист

- Репозиторий подключён
- Ветка выбрана правильно
- Secrets заданы в безопасном месте
- Rules/skills доступны Cloud Agent
- После запуска проверяется diff/PR

## Официальная ссылка

https://cursor.com/docs/cloud-agent/settings
