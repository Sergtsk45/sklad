# Codex CLI — Правила

## Общие требования
- Всегда отвечай на русском языке, независимо от языка запроса.
- Соблюдай структуру ответов, описанную в системных инструкциях Codex CLI.

## Контекст проекта
- Основной код живёт в `custom_addons/` и `odoo/`, ссылки на файлы давай относительными.
- Используй терминологию и артефакты из каталога `docs/`.

## Проект
- ERP Odoo 19, запуск и деплой через Docker Compose (локально и на VPS).
- Стек: Python, Odoo 19, PostgreSQL 15, Docker Compose.

## Базовые команды (локально)
- `docker compose -f docker-compose.local.yml up -d` — запустить стек.
- `docker compose -f docker-compose.local.yml down` — остановить.
- `docker compose -f docker-compose.local.yml restart odoo` — перезапустить сервис.
- `docker compose -f docker-compose.local.yml logs -f odoo` — логи.
- `docker exec -it odoo19-local bash` — shell в контейнере.
- `docker exec odoo19-local odoo -u <module> -d odoo19_local --stop-after-init` — обновить модуль.
- `docker exec odoo19-local odoo --test-enable -u <module> -d odoo19_local --stop-after-init` — тесты модуля.
- `docker exec odoo19-local python -m flake8 /mnt/extra-addons` — линтинг.

## Стандарты кода
- Модели наследуй от `models.Model`/`models.TransientModel`/`models.AbstractModel`.
- Используй snake_case для полей/методов, PascalCase для классов.
- Импорты: stdlib → odoo (`from odoo import models, fields, api`).
- Методы декорируй `@api.model`, `@api.depends`, `@api.constrains`, `@api.onchange` по назначению.
- Не превышай 50 строк на функцию и 30 на метод, избегай отладочных логов в проде.
- Ошибки пользователю показывай через `UserError`/`ValidationError`.

## Тестирование
- Используй unittest, размещай тесты в `<module>/tests/` с `__init__.py` и паттерном `test_*.py`.
- Базовые классы: `TransactionCase` или `SavepointCase`.
- Помечай интеграционные тесты тегами `@tagged('post_install', '-at_install')`.
- Покрывай публичные методы и граничные сценарии, держи ассерты осмысленными.

## Git
- Коммиты в стиле conventional commits (`feat:`, `fix:`, `refactor:` и т.д.).
- Перед коммитом прогоняй flake8 и тесты затронутых модулей.
- Не коммить `.env`, конфиги с секретами и данные Traefik/БД.

## Документация
- Основной каталог: `docs/`.
- Обновляй `docs/changelog.md` при значимых изменениях и `docs/tasktracker*.md` при работе по задачам.
