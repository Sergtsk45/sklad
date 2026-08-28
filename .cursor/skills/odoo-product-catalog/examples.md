# Примеры вызовов (Odoo MCP / XML-RPC)

Имя MCP-сервера и id полей — из **текущей** базы. Ниже — шаблоны.

## Поиск алиаса по артикулу

```text
search_records(
  model="product.supplierinfo",
  domain=[["product_code", "=", "SQ0905-1003"]],
  fields=["id", "partner_id", "product_tmpl_id", "product_code",
          "product_name", "price"]
)
```

## Поиск шаблона по типоразмеру

```text
search_records(
  model="product.template",
  domain=[
    "&",
    ["name", "ilike", "профильн"],
    ["name", "ilike", "40×20"]
  ],
  fields=["id", "name", "categ_id", "uom_id", "is_storable", "seller_ids"],
  # context: lang каталога, active_test=false при охоте на дубли
)
```

## Резолв категории и UoM

```text
search_records(
  model="product.category",
  domain=[["complete_name", "ilike", "Трубы"]],
  fields=["id", "name", "complete_name"]
)

search_records(
  model="uom.uom",
  domain=[["name", "=", "шт."]],
  fields=["id", "name"]
)
```

## Создание карточки + алиас

```text
create_record(
  model="product.template",
  values={
    "name": "Труба стальная профильная 15×15×1,5 мм, длина 6 м",
    "categ_id": <id>,
    "uom_id": <шт.>,
    "type": "consu",
    "is_storable": true,
    "purchase_ok": true,
    "sale_ok": false,
    "standard_price": 388.5,
    "list_price": 388.5
  }
)

create_record(
  model="product.supplierinfo",
  values={
    "product_tmpl_id": <id>,
    "partner_id": <id поставщика>,
    "product_code": false,
    "product_name": "Труба профильная 15*15*1,5 L 6",
    "price": 388.5,
    "min_qty": 1.0
  }
)
```

## Запись name с языком (если MCP без lang)

XML-RPC / shell:

```python
# псевдокод
execute_kw(..., "product.template", "write",
           [[tmpl_id], {"name": normalized}],
           {"context": {"lang": "ru_RU"}})
execute_kw(..., "product.template", "write",
           [[tmpl_id], {"name": normalized}],
           {"context": {"lang": "en_US"}})
```

## Цена: кг в счёте → шт. на карточке

```text
price_per_uom = round(line_amount_with_vat / qty_in_card_uom, 2)
# пример: 18910.80 ₽ / 17 шт = 1112.40 ₽/шт
# в product_name можно оставить «103 ₽/кг» из счёта
```
