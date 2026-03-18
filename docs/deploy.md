---
title: Deploy Odoo 19 (Docker) — skladtsk.duckdns.org
created: 2026-03-15
stack: traefik, odoo:19.0, postgres:15
mode: repo-bind-mount + volumes for data
---

## Что получится

- **Prod/VPS**: домен `skladtsk.duckdns.org` → Traefik (HTTPS Let’s Encrypt) → Odoo 19 контейнер.
- **Данные**: PostgreSQL и Odoo filestore — в **Docker volumes** (переживают `up/down`).
- **Код**: репозиторий монтируется в контейнер как bind‑mount; после `git pull` достаточно рестарта Odoo.

Ссылка на исходники Odoo: [`odoo/odoo`](https://github.com/odoo/odoo).

## Файлы, которые нужно иметь в корне проекта

- `docker-compose.yml` (ниже — готовый)
- `.env` (ниже — шаблон; **не коммитить**)
- `config/odoo.conf` (ниже — шаблон; **секреты не коммитить**)
- `custom_addons/` (твои модули)

---

## 1) `.env` (prod пример)

Создай файл `.env` рядом с `docker-compose.yml`.

```bash
# Domain / Let's Encrypt
ODOO_DOMAIN=skladtsk.duckdns.org
LETSENCRYPT_EMAIL=you@example.com

# Postgres
POSTGRES_DB=odoo19
POSTGRES_USER=odoo
POSTGRES_PASSWORD=CHANGE_ME_STRONG_PASSWORD

# Odoo "master password" (для Database Manager / бэкапов из UI)
ODOO_ADMIN_PASSWD=CHANGE_ME_STRONG_MASTER_PASSWORD

# Timezone (опционально)
TZ=Europe/Moscow
```

Важно:
- `POSTGRES_PASSWORD` и `ODOO_ADMIN_PASSWD` должны быть **сильными**.
- `.env` не коммить в git.

---

## 2) `config/odoo.conf` (шаблон)

Odoo в Docker будет читать конфиг из `/etc/odoo/odoo.conf`.

```ini
[options]
; === Security / proxy ===
proxy_mode = True

; "master password" (не хранить в git — только локально/на VPS)
admin_passwd = CHANGE_ME_STRONG_MASTER_PASSWORD

; === Addons ===
; Официальные addons уже внутри образа, а твои модули — в /mnt/extra-addons
addons_path = /usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons

; === DB (можно оставить, а можно полагаться на env HOST/USER/PASSWORD) ===
db_host = db
db_port = 5432
db_user = odoo
db_password = CHANGE_ME_STRONG_PASSWORD

; === Data dir (filestore) ===
data_dir = /var/lib/odoo

; === Logging (минимально) ===
log_level = info

; === Performance (prod базово; можно тюнить позже) ===
; workers = 2
; max_cron_threads = 1
; limit_time_cpu = 60
; limit_time_real = 120
```

Рекомендация по секретам:
- В git храни `config/odoo.conf.example` (с плейсхолдерами),
- А `config/odoo.conf` — держи только на машинах (Cursor/WSL2 и VPS).

---

## 3) `docker-compose.yml` (Traefik + Odoo + Postgres)

Скопируй этот файл как `docker-compose.yml` в корень проекта.

```yaml
services:
  traefik:
    image: traefik:v3.2
    container_name: traefik
    restart: unless-stopped
    command:
      - --api.dashboard=true
      - --providers.docker=true
      - --providers.docker.exposedbydefault=false
      - --entrypoints.web.address=:80
      - --entrypoints.websecure.address=:443
      - --entrypoints.web.http.redirections.entrypoint.to=websecure
      - --entrypoints.web.http.redirections.entrypoint.scheme=https
      - --certificatesresolvers.le.acme.email=${LETSENCRYPT_EMAIL}
      - --certificatesresolvers.le.acme.storage=/acme/acme.json
      - --certificatesresolvers.le.acme.httpchallenge=true
      - --certificatesresolvers.le.acme.httpchallenge.entrypoint=web
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - traefik-acme:/acme
    networks:
      - web

  db:
    image: postgres:15
    container_name: odoo-db
    restart: unless-stopped
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - TZ=${TZ}
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    networks:
      - internal

  odoo:
    image: odoo:19.0
    container_name: odoo
    restart: unless-stopped
    depends_on:
      - db
    environment:
      # Официальный образ Odoo использует эти переменные для подключения к БД:
      # HOST/USER/PASSWORD (см. Docker Hub / Odoo docs)
      - HOST=db
      - USER=${POSTGRES_USER}
      - PASSWORD=${POSTGRES_PASSWORD}
      - TZ=${TZ}
    volumes:
      # filestore / sessions / attachments
      - odoo-web-data:/var/lib/odoo

      # конфиг (секреты — вне git)
      - ./config/odoo.conf:/etc/odoo/odoo.conf:ro

      # твои модули (из репозитория)
      - ./custom_addons:/mnt/extra-addons:rw
    networks:
      - internal
      - web
    labels:
      - traefik.enable=true
      - traefik.http.routers.odoo.rule=Host(`${ODOO_DOMAIN}`)
      - traefik.http.routers.odoo.entrypoints=websecure
      - traefik.http.routers.odoo.tls=true
      - traefik.http.routers.odoo.tls.certresolver=le
      - traefik.http.services.odoo.loadbalancer.server.port=8069

networks:
  web:
    name: web
  internal:
    name: internal
    internal: true

volumes:
  traefik-acme:
  odoo-db-data:
  odoo-web-data:
```

Примечания:
- Postgres 15 выбран как безопасный “по умолчанию” для современных Odoo; при желании можно поднять/опустить версию, но фиксируй её.
- Если хочешь включить Traefik dashboard — лучше закрыть его basic‑auth и/или ограничить IP (пока не включал намеренно).

---

## 4) Команды запуска и обновления (VPS)

### Первый старт

```bash
cd /opt/<project-root>
docker compose pull
docker compose up -d
docker compose logs -f odoo
```

### Создание БД и установка только нужных модулей

Самый простой способ: через веб‑интерфейс при первом заходе на `https://skladtsk.duckdns.org`.

Минимальный набор модулей:
- `contacts`
- `crm`
- `sale_management`
- `purchase`
- `stock`

### Обновление кода (деплой из Cursor)

На VPS:

```bash
cd /opt/<project-root>
git pull
docker compose restart odoo
```

Если изменения касаются логики Odoo‑модуля, обычно нужно сделать upgrade модуля:

```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d ${POSTGRES_DB} -u your_module --stop-after-init
docker compose restart odoo
```

### Обновить несколько модулей разом

```bash
docker compose exec odoo odoo -c /etc/odoo/odoo.conf -d ${POSTGRES_DB} -u module_a,module_b --stop-after-init
docker compose restart odoo
```

### Посмотреть логи

```bash
docker compose logs -f odoo
docker compose logs -f db
docker compose logs -f traefik
```

---

## 5) Команды для dev (Cursor/WSL2)

Те же команды, только домен обычно не нужен. Можно:

- Локально обращаться по `http://localhost:8069` (без Traefik),
- или оставить Traefik и использовать hosts‑запись для домена (редко нужно).

Минимальный dev‑поток:

```bash
docker compose up -d
docker compose logs -f odoo
```

После изменений кода:

```bash
docker compose restart odoo
```

---

## 6) Бэкапы (рекомендуется)

### Бэкап PostgreSQL (pg_dump внутри контейнера)

```bash
docker compose exec db pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup_$(date +%F).sql
```

### Бэкап filestore (volume)

Filestore хранится в volume `odoo-web-data`. Для бэкапа volume обычно используют временный контейнер:

```bash
docker run --rm -v odoo-web-data:/data -v "$PWD":/backup alpine \
  sh -c "cd /data && tar -czf /backup/filestore_$(date +%F).tar.gz ."
```

---

## 7) Частые проблемы

### Let’s Encrypt не выдаёт сертификат

Проверь:
- DNS A‑запись `skladtsk.duckdns.org` указывает на IP VPS
- порты 80/443 доступны снаружи
- нет второго сервиса, который уже слушает 80/443

### Изменения в модуле не применились

Обычно нужен `-u your_module --stop-after-init`, затем рестарт Odoo.

