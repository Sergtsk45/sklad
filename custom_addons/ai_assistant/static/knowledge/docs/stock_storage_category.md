---
source: inventory_and_mrp/inventory/shipping_receiving/daily_operations/storage_category
module: stock
generated: 2026-03-24
---

# Storage categories

## Шаг за шагом

**Ключевые слова**: Склад app → Конфигурация → Настройки, Склад app → Конфигурация → Местонахождениеs, Склад app → Конфигурация → Putaway Rules

### Storage categories

1. Enable features in the settings
2. Define capacity limitations
3. Assign a category to storage locations
4. Add the storage category as an attribute to a :ref:`putaway rule

### Define storage category limitations

> **Примечание**: Weight limits can be combined with capacity by package or product (e.g. a maximum of one hundred products with a total weight of two hundred kilograms). While it is possible to limit capacity by product and package type at the same location, it may be more practical to store items in different amounts across various locations, as shown in the limit capacity by package  example.
> **Примечание**: Odoo does **not** automatically split quantities across multiple storage locations. If an incoming receipt contains several units or packages and the first recommended location exceeds its capacity, Odoo still routes all items to that same location instead of selecting another one with available space. *(Example: If a location can hold 10 units and 12 units arrive, all 12 are still assigned to that location.)*

### Limit capacity by package type

> **Примечание**: Odoo does **not** automatically split quantities across multiple storage locations. If an incoming receipt contains several units or packages and the first recommended location exceeds its capacity, Odoo still routes all items to that same location instead of selecting another one with available space. *(Example: If a location can hold 10 units and 12 units arrive, all 12 are still assigned to that location.)*

### Assign storage locations

**Навигация:**
- Склад app → Конфигурация → Местонахождениеs

> **Примечание**: On the storage category form, the :icon:`oi-arrows-v` **Местонахождениеs** smart button shows which storage locations the category has been assigned to.

### Create a putaway rule

**Навигация:**
- Склад app → Конфигурация → Putaway Rules

> **Примечание**: If products are not routing to secondary locations for a storage category and a product weight is defined, verify that the storage category's **Max Weight** value is set to a number greater than `0`.
