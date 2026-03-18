---
title: Rules & структура проекта под Odoo 19 (Cursor → VPS)
created: 2026-03-15
scope: docker, odoo19, traefik, git-deploy, volumes
---

## Цель

Организовать один и тот же код и конфигурацию так, чтобы:

- локально в Cursor (WSL2/Ubuntu) можно было быстро запускать Odoo 19 в Docker;
- на VPS (Ubuntu 22.04) работал тот же стек (Docker Compose), но с доменом и HTTPS;
- изменения делались только в Cursor, затем деплоились на VPS через git (`pull` + рестарт контейнера);
- данные (PostgreSQL + filestore Odoo) жили в Docker volumes и не терялись при пересоздании контейнеров.

## Важное правило по кастомизации Odoo

Рекомендуемая стратегия — **не править ядро Odoo**, а делать изменения через **свои модули** в `custom_addons/`.

- 90% задач решается через: наследование моделей, расширение views, actions, security, QWeb, JS assets.
- если всё же нужно менять ядро — фиксировать это отдельным патчем/веткой и понимать, что обновления Odoo станут сложнее.

## Рекомендуемая структура репозитория

Ниже — “эталонная” структура, которую удобно держать и локально, и на VPS.

```
<project-root>/
  odoo/                       # исходники Odoo (git submodule или subtree, ветка 19.0)
  custom_addons/              # твои модули (главное место для изменений)
    your_module_1/
    your_module_2/

  config/
    odoo.conf                 # НЕ коммитить с секретами (см. шаблон в docs/deploy.md)

  docker/
    traefik/
      acme/                   # хранение сертификатов (volume/папка, права 600)

  docker-compose.yml          # основной стек (Traefik + Odoo + Postgres)
  .env                        # окружение (секреты, домен, email LE) — не коммитить

  docs/
    rulesworkproject.md
    deploy.md
    project.md                # описание архитектуры (по необходимости)
    changelog.md              # журнал изменений
    tasktracker.md            # статусы задач
```

### Что где хранится

- **Код Odoo**: `odoo/` (ветка `19.0` из [`odoo/odoo`](https://github.com/odoo/odoo)).
- **Твой код**: `custom_addons/` (это то, что ты обычно деплоишь).
- **Данные**:
  - PostgreSQL — Docker volume (например, `odoo-db-data`).
  - Filestore Odoo (`/var/lib/odoo`) — Docker volume (например, `odoo-web-data`).
- **Секреты/переменные**: `.env` на каждой среде свой (dev/prod).
- **Конфиг Odoo**: `config/odoo.conf`, лучше хранить как:
  - `config/odoo.conf.example` (в git, без секретов),
  - `config/odoo.conf` (на машине, с секретами/паролями, в `.gitignore`).

## Workflow разработки и деплоя

### Локально (Cursor/WSL2)

- Поднять стек через `docker compose up -d`.
- Код монтируется в контейнер:
  - `./custom_addons` → `/mnt/extra-addons`
  - `./config/odoo.conf` → `/etc/odoo/odoo.conf`
- Для разработки:
  - менять код в Cursor;
  - при необходимости — рестарт Odoo контейнера;
  - обновлять модуль через команду `-u <module>` (см. `docs/deploy.md`).

### VPS (Ubuntu 22.04)

- Код лежит в `/opt/<project>` (или другом каталоге).
- Данные — в volumes (не зависят от git).
- Домен `skladtsk.duckdns.org` ведёт на VPS.
- Traefik получает сертификат Let’s Encrypt и проксирует HTTPS → Odoo.

### Деплой изменений (из Cursor на VPS)

Рекомендуемый “чистый” процесс:

1) В Cursor:
   - изменения в `custom_addons/` (и/или конфиге без секретов);
   - `git commit` → `git push`.
2) На VPS:
   - `git pull`;
   - `docker compose up -d` (или `restart odoo`).
3) Если это изменение логики модуля:
   - выполнить `-u your_module` (upgrade) и только потом полноценно проверять UI.

## Практические соглашения (чтобы не ломать прод)

- **Никогда не коммитить**: `.env`, `config/odoo.conf` с паролями, `docker/traefik/acme/*`, дампы БД.
- **Стабильность prod**:
  - любые изменения в `custom_addons/` сопровождай обновлением модуля (`-u`) на целевой БД;
  - перед крупными изменениями делать бэкап (см. `docs/deploy.md`).
- **Разделяй dev/prod настройки**:
  - разные `.env` (пароли, db name, email LE);
  - одинаковый `docker-compose.yml`, но разные значения переменных.

