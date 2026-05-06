# Odoo 19 Product Search — техническое задание для Cursor

## Цель

Сделать устойчивый поисковик товаров для Odoo 19, который находит товары даже при проблемах в названии:

- двойные и тройные пробелы: `кран  шаровый  Ду50`
- разный регистр: `ДУ50`, `ду50`, `Ду50`
- разные варианты написания: `Ду50`, `ДУ 50`, `DN50`, `50мм`
- поиск по части названия: `кран шар`, `шаровый ду50`
- поиск по SKU / internal reference / barcode
- дальнейшее расширение под склад, интернет-магазин и ИИ-ассистента

Важно: ядро Odoo не менять. Реализовать отдельным кастомным addon.

---

## Исходный стек проекта

- Odoo: 19.0
- Основные модули: `stock`, `product`, `sale`, в перспективе `website_sale`, `purchase`
- Кастомный модуль: ИИ-ассистент / справочник по руководству
- IDE: Cursor
- LLM API: OpenRouter API
- База данных: PostgreSQL
- Рекомендуемое расширение БД: `pg_trgm`
- Подход: Odoo addon + PostgreSQL fuzzy search + нормализация товарных названий

---

## Главная проблема

В базе товар может быть сохранён так:

```text
кран  шаровый  Ду50
```

А пользователь ищет так:

```text
кран шаровый Ду50
```

Стандартный поиск может не найти товар, если поиск идёт по строке без нормализации или ожидает точное совпадение последовательности символов.

Нужно сделать слой поиска, который сначала нормализует данные и запрос, а затем ищет по нормализованным полям и fuzzy-индексам.

---

## Репозитории и готовые решения, которые применяем

### 1. OCA/server-tools

GitHub:

```text
https://github.com/OCA/server-tools
```

Использовать модуль:

```text
base_search_fuzzy
```

Назначение:

- включает fuzzy search на базе PostgreSQL trigram
- даёт возможность использовать trigram-поиск
- не заменяет полностью стандартный поиск Odoo, а предоставляет базовый механизм для кастомных addon

Важно: на момент подготовки ТЗ в OCA/server-tools видна ветка 18.0 с `base_search_fuzzy`. Для Odoo 19 нужно проверить наличие ветки 19.0 или портировать модуль с 18.0.

---

### 2. OCA/search-engine

GitHub:

```text
https://github.com/OCA/search-engine
```

Назначение:

- база для более продвинутого search-engine подхода
- полезно для будущей интеграции интернет-магазина
- можно рассматривать на втором этапе

На первом этапе не обязательно внедрять полностью.

---

### 3. OCA/product-attribute

GitHub:

```text
https://github.com/OCA/product-attribute
```

Назначение:

- модули вокруг товаров, атрибутов, справочников, альтернативных кодов
- полезно, если появятся синонимы, технические характеристики, аналоги, бренды, типоразмеры

На первом этапе использовать как источник практик и возможных зависимостей, но основную задачу решать своим addon.

---

## Рекомендуемая архитектура

```text
custom_product_search/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── product_template.py
│   └── product_product.py
├── data/
│   └── cron.xml                    # опционально
├── security/
│   └── ir.model.access.csv         # если появятся свои модели
├── views/
│   └── product_views.xml           # опционально
└── README.md
```

---

## Что должен делать custom addon

### 1. Добавить нормализованные поля

На `product.template`:

```python
x_search_name = fields.Char(
    string='Normalized Search Name',
    compute='_compute_x_search_name',
    store=True,
    index=True,
)
```

На `product.product`:

```python
x_search_name = fields.Char(
    string='Normalized Search Name',
    compute='_compute_x_search_name',
    store=True,
    index=True,
)
```

---

### 2. Нормализовать текст

Нормализация должна делать:

- `strip()`
- lowercase
- замену `ё` → `е`
- замену неразрывных пробелов на обычные
- сворачивание любых повторных пробелов в один
- нормализацию `ду 50` → `ду50`
- нормализацию `dn 50` → `dn50`
- удаление лишних спецсимволов только осторожно, чтобы не сломать артикулы

Пример функции:

```python
import re


def normalize_product_search_text(value):
    if not value:
        return ''

    value = str(value)
    value = value.replace('\u00A0', ' ')
    value = value.replace('ё', 'е').replace('Ё', 'Е')
    value = value.lower()
    value = re.sub(r'\s+', ' ', value)
    value = value.strip()

    # Ду 50 -> ду50, DN 50 -> dn50
    value = re.sub(r'\bду\s+(\d+)\b', r'ду\1', value, flags=re.IGNORECASE)
    value = re.sub(r'\bdn\s+(\d+)\b', r'dn\1', value, flags=re.IGNORECASE)

    return value
```

---

### 3. Переопределить `_name_search()`

Цель: чтобы поиск в Many2one, складских операциях, заказах и формах работал мягко.

Искать по:

- `default_code`
- `barcode`
- `name`
- `x_search_name`
- `product_tmpl_id.x_search_name`

Пример логики:

```python
@api.model
def _name_search(self, name='', domain=None, operator='ilike', limit=100, order=None):
    domain = domain or []

    if not name:
        return super()._name_search(name=name, domain=domain, operator=operator, limit=limit, order=order)

    normalized = normalize_product_search_text(name)

    search_domain = expression.OR([
        [('default_code', 'ilike', name)],
        [('barcode', '=', name)],
        [('name', 'ilike', name)],
        [('x_search_name', 'ilike', normalized)],
        [('product_tmpl_id.x_search_name', 'ilike', normalized)],
    ])

    final_domain = expression.AND([domain, search_domain])
    return self._search(final_domain, limit=limit, order=order)
```

В Odoo 19 сигнатуру `_name_search()` обязательно сверить с текущим исходным кодом. Если отличается — адаптировать.

---

### 4. Добавить PostgreSQL `pg_trgm`

Для fuzzy-поиска и ускорения.

SQL:

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

GIN индекс:

```sql
CREATE INDEX IF NOT EXISTS product_template_x_search_name_trgm_idx
ON product_template
USING gin (x_search_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS product_product_x_search_name_trgm_idx
ON product_product
USING gin (x_search_name gin_trgm_ops);
```

В идеале делать через `post_init_hook` в Odoo addon.

---

## Важное решение по OCA/base_search_fuzzy

### Не полагаться только на него

`base_search_fuzzy` полезен, но сам по себе не обязан автоматически изменить весь backend-поиск товаров.

Правильная схема:

```text
base_search_fuzzy
+
custom_product_search
```

`base_search_fuzzy` даёт инфраструктуру fuzzy search, а `custom_product_search` решает конкретную бизнес-задачу поиска товаров.

---

## Этапы реализации

### Этап 1 — MVP

Сделать кастомный addon:

- нормализованное поле `x_search_name`
- compute/store/index
- override `_name_search()` для `product.product`
- поиск по пробелам, регистру, `Ду50` / `Ду 50`
- тесты вручную в складских документах

Результат:

```text
кран шаровый ду50
```

должен находить:

```text
кран  шаровый  Ду50
```

---

### Этап 2 — PostgreSQL fuzzy

Добавить:

- `pg_trgm`
- GIN indexes
- опционально OCA `base_search_fuzzy`
- проверку скорости на каталоге товаров

---

### Этап 3 — синонимы и технические обозначения

Добавить свою модель:

```text
product.search.alias
```

Поля:

- `name`
- `normalized_name`
- `product_id`
- `product_tmpl_id`
- `active`

Примеры алиасов:

```text
ду50 -> dn50
ду 50 -> dn50
кран шар -> кран шаровый
50мм -> ду50
```

---

### Этап 4 — интернет-магазин

Для `website_sale`:

- расширить website search domain
- использовать `x_search_name`
- добавить поиск по SKU и barcode, если нужно
- добавить фильтрацию по наличию на складе
- позже рассмотреть OCA/search-engine

---

### Этап 5 — ИИ-ассистент

ИИ-ассистент не должен первым делом искать напрямую в БД через LLM.

Правильная схема:

```text
User query
↓
normalize query
↓
Odoo product search service
↓
результаты товаров
↓
LLM только объясняет и уточняет
```

LLM через OpenRouter должен вызывать отдельный tool/service:

```python
search_products(query, limit=20, warehouse_id=None, only_available=True)
```

---

## Tool для ИИ-ассистента

Сделать сервисный метод:

```python
@api.model
def ai_search_products(self, query, limit=20, warehouse_id=None, only_available=False):
    normalized = normalize_product_search_text(query)

    domain = expression.OR([
        [('default_code', 'ilike', query)],
        [('barcode', '=', query)],
        [('name', 'ilike', query)],
        [('x_search_name', 'ilike', normalized)],
        [('product_tmpl_id.x_search_name', 'ilike', normalized)],
    ])

    if only_available:
        domain = expression.AND([domain, [('qty_available', '>', 0)]])

    products = self.search(domain, limit=limit)
    return products.read([
        'id',
        'display_name',
        'default_code',
        'barcode',
        'qty_available',
        'uom_id',
    ])
```

---

## Тестовые сценарии

Создать товар:

```text
кран  шаровый  Ду50
```

Проверить запросы:

```text
кран шаровый Ду50
кран шаровый ду50
кран  шаровый  Ду50
кран ду50
шаровый ду 50
ДУ50
ду 50
```

Все должны находить товар.

Дополнительно проверить:

```text
кран шар
шаров ду50
```

Для fuzzy/trigram этапа:

```text
кран шаровй ду50
кран шаровый д50
```

---

## Критерии готовности

### Backend

- поиск работает в списке товаров
- поиск работает в складских операциях
- поиск работает в заказах продаж
- поиск работает в закупках, если модуль установлен
- поиск не ломает стандартные права доступа Odoo

### Производительность

- на 10 000 товаров поиск отвечает быстро
- на 100 000 товаров нужен GIN/trigram индекс

### Архитектура

- ядро Odoo не изменено
- всё сделано в отдельном addon
- код совместим с будущим подключением `website_sale`
- есть отдельный метод для AI-поиска

---

## Что не делать

Не менять файлы:

```text
odoo/addons/product/
odoo/addons/stock/
odoo/addons/sale/
```

Не исправлять массово товары вручную как основное решение.

Не давать LLM прямой доступ к созданию/изменению товаров без сервисного слоя и прав.

Не строить поиск только на embeddings: для склада сначала нужны точные поля, SKU, barcode, остатки, склад.


---

## Команды для подготовки репозиториев

Пример структуры проекта:

```bash
git clone https://github.com/odoo/odoo.git -b 19.0 odoo
mkdir custom-addons
cd custom-addons
```

OCA server-tools:

```bash
git clone https://github.com/OCA/server-tools.git -b 18.0 oca-server-tools
```

Если ветка 19.0 уже доступна:

```bash
git clone https://github.com/OCA/server-tools.git -b 19.0 oca-server-tools
```

Проверить наличие модуля:

```bash
ls oca-server-tools/base_search_fuzzy
```

---

## Рекомендуемый addons_path

```ini
addons_path = /opt/odoo/odoo/addons,/opt/odoo/custom-addons,/opt/odoo/oca-server-tools
```

---

## Приоритет реализации

1. `custom_product_search` без внешних зависимостей
2. `pg_trgm` индексы
3. совместимость с OCA `base_search_fuzzy`
4. aliases для технических терминов
5. website_sale search
6. AI semantic/hybrid search

---

## Будущая гибридная схема поиска

```text
Exact search:
- barcode
- default_code

Normalized search:
- x_search_name

Fuzzy search:
- pg_trgm

Business filters:
- sale_ok
- purchase_ok
- qty_available
- warehouse/location

AI layer:
- OpenRouter explains results
- asks clarifying questions
- recommends alternatives
- never bypasses Odoo permissions
```

---

## Краткий итог

Для текущей задачи не нужно переписывать Odoo core.

Нужен отдельный addon:

```text
custom_product_search
```

И желательно подключить:

```text
OCA/server-tools/base_search_fuzzy
PostgreSQL pg_trgm
```

Главный принцип:

```text
поиск должен идти не только по name, а по нормализованному search_name + SKU + barcode + fuzzy index
```
