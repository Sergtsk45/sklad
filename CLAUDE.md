# project_Odoo

## Проект
Odoo 19 ERP — локальная разработка и деплой на VPS через Docker Compose.
Стек: Python / Odoo 19 / PostgreSQL 15 / Docker Compose

## Команды

- **Запуск стека**: `docker compose -f docker-compose.local.yml up -d`
- **Остановка**: `docker compose -f docker-compose.local.yml down`
- **Рестарт Odoo**: `docker compose -f docker-compose.local.yml restart odoo`
- **Логи Odoo**: `docker compose -f docker-compose.local.yml logs -f odoo`
- **Shell в контейнер**: `docker exec -it odoo19-local bash`
- **Обновить модуль**: `docker exec odoo19-local odoo -u <module> -d odoo19_local --stop-after-init`
- **Тесты (модуль)**: `docker exec odoo19-local odoo --test-enable -u <module> -d odoo19_local --stop-after-init`
- **Тесты (конкретный класс)**: `docker exec odoo19-local odoo --test-enable --test-tags <tag> -d odoo19_local --stop-after-init`
- **Lint**: `docker exec odoo19-local python -m flake8 /mnt/extra-addons`
- **Установить зависимости**: `docker exec odoo19-local pip install -r /mnt/extra-addons/<module>/requirements.txt`

## Структура проекта

```
project_Odoo/
  odoo/               # исходники Odoo 19 (не трогаем)
  custom_addons/      # НАШИ модули (главное место для изменений)
    <module>/
      __init__.py
      __manifest__.py
      models/
      views/
      security/
      tests/
        __init__.py
        test_*.py
  config/
    odoo.local.conf   # локальный конфиг (не коммитить с секретами)
  docs/               # документация проекта
  docker-compose.local.yml
  .env                # секреты (не коммитить)
```

## Стандарты кода (Odoo)

- **Именование**: snake_case для методов/полей, PascalCase для классов моделей
- **Модели**: наследовать от `models.Model`, `models.TransientModel`, `models.AbstractModel`
- **Поля**: определять на уровне класса, не в `__init__`
- **Методы**: `@api.model`, `@api.depends`, `@api.constrains`, `@api.onchange` — стандартные декораторы
- **Импорты**: сначала stdlib, затем odoo (`from odoo import models, fields, api`)
- **Обработка ошибок**: `raise UserError(...)` для пользовательских ошибок, `raise ValidationError(...)` для валидации
- **Максимальная длина функции**: 50 строк, метода: 30 строк
- Не оставлять `_logger.debug` / `print` для отладки в prod-коде
- Использовать ранний return вместо глубокой вложенности

## Тестирование

- **Фреймворк**: Odoo built-in test runner (unittest)
- **Паттерн именования**: `test_*.py`
- **Расположение**: `<module>/tests/` (обязательно `__init__.py`)
- **Базовые классы**: `odoo.tests.common.TransactionCase` (откат после каждого теста), `SavepointCase`
- **Тег**: `@tagged('post_install', '-at_install')` для post-install тестов
- Покрытие: писать тесты на все публичные методы моделей и edge cases
- Один assert на логическую проверку, понятные имена тестов

## Git

- **Формат коммитов**: conventional commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`)
- **Ветки**: `feature/*`, `fix/*`, `refactor/*`
- **Перед коммитом**: flake8 должен проходить, тесты изменённых модулей должны быть зелёными
- **Никогда не коммитить**: `.env`, `config/*.conf` с паролями, `docker/traefik/acme/*`, дампы БД

## Документация

- **Путь**: `docs/`
- Обновлять `docs/changelog.md` при каждом значимом изменении
- Обновлять `docs/tasktracker.md` при работе с задачами
- Docstring для публичных методов моделей
