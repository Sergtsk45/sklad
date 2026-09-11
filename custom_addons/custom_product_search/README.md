# custom_product_search

`custom_product_search` улучшает поиск товаров в Odoo 19 без изменения core Odoo.

Модуль добавляет stored computed поле `x_search_name` на `product.template` и `product.product`, нормализует названия товаров и расширяет backend-поиск вариантов товаров через актуальный для Odoo 19 метод `name_search()`.

## Что нормализуется

- пробелы в начале и конце строки;
- регистр символов;
- `ё` -> `е`;
- NBSP -> обычный пробел;
- повторные пробелы -> один пробел;
- `ду 50` -> `ду50`;
- `dn 50` -> `dn50`.

Пример:

```text
кран  шаровый  Ду50 -> кран шаровый ду50
```

## Где работает поиск

- backend UI для товаров;
- Many2one-поля на `product.product`, включая складские документы;
- сервисный метод для AI-ассистента:

```python
env['product.product'].ai_search_products(
    query='кран ду50',
    limit=20,
    warehouse_id=None,
    only_available=False,
)
```

Метод не использует `sudo()` для поиска и чтения данных, поэтому сохраняет стандартные ACL и record rules Odoo.

## PostgreSQL индексы

При установке addon выполняется `post_init_hook`:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS product_template_x_search_name_trgm_idx
ON product_template
USING gin (x_search_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS product_product_x_search_name_trgm_idx
ON product_product
USING gin (x_search_name gin_trgm_ops);
```

Если в базе нет прав на `CREATE EXTENSION`, установку нужно выполнить пользователем PostgreSQL с соответствующими правами или заранее включить `pg_trgm`.

## Совместимость с OCA base_search_fuzzy

Модуль не зависит от `base_search_fuzzy` и работает самостоятельно. Если `base_search_fuzzy` установлен, `custom_product_search` не конфликтует с ним: нормализованное поле и GIN trigram-индексы остаются отдельным совместимым слоем для поиска товаров.

## Установка и обновление

```bash
docker compose -f docker-compose.local.yml up -d
docker exec odoo19-local odoo -u custom_product_search -d odoo19_local --stop-after-init
docker compose -f docker-compose.local.yml restart odoo
```

## Тесты

```bash
docker exec odoo19-local odoo --test-enable -u custom_product_search -d odoo19_local --stop-after-init
```

## Ручные тестовые сценарии

Создайте товар:

```text
кран  шаровый  Ду50
```

Проверьте поиск в товарах, складских документах и заказах продаж:

```text
кран шаровый Ду50
кран шаровый ду50
кран  шаровый  Ду50
кран ду50
шаровый ду 50
ДУ50
ду 50
```

Ожидаемый результат: товар `кран  шаровый  Ду50` находится во всех сценариях.

Дополнительно проверьте поиск по:

```text
default_code
barcode
артикул поставщика (product.supplierinfo.product_code)
```

Пример: товар с каноническим именем «Отвод ПП…» и vendor code `00-00036296`
должен находиться по запросу `00-00036296`.

## Ограничения MVP

- Синонимы вида `ду50 -> dn50` пока не добавлены как отдельная модель.
- Website search будет расширяться отдельным этапом при подключении `website_sale`.
- Trigram-индексы ускоряют `ilike`, но явный fuzzy-порог похожести не включен в MVP.
