# Project Architecture

## Назначение

Проект содержит локальную разработку Odoo 19 ERP с кастомными addon в `custom_addons/`. Ядро Odoo в `odoo/` не изменяется.

## Основные компоненты

- `odoo/` — исходники Odoo 19, используются как upstream core.
- `custom_addons/ai_assistant/` — встроенный AI-ассистент через OpenRouter API.
- `custom_addons/object_request/` — модуль требований на комплектацию объектов.
- `custom_addons/custom_product_search/` — нормализованный поиск товаров для backend UI, складских документов и AI-сервисного слоя.
- `docs/` — проектная документация, changelog и tasktracker.

## custom_product_search

Модуль расширяет стандартные модели `product.template` и `product.product`:

- добавляет stored computed indexed поле `x_search_name`;
- нормализует названия товаров: регистр, `ё`, NBSP, повторные пробелы, `ду 50`/`dn 50`;
- расширяет `product.product.name_search()` с актуальной сигнатурой Odoo 19;
- добавляет `post_init_hook` для `pg_trgm` и GIN trigram-индексов;
- предоставляет `ai_search_products(query, limit=20, warehouse_id=None, only_available=False)`.

```mermaid
flowchart TD
    UserQuery[User query] --> Normalize[normalize_product_search_text]
    ProductData[product.template/product.product name] --> Compute[x_search_name stored fields]
    Normalize --> NameSearch[product.product.name_search]
    Compute --> NameSearch
    NameSearch --> Backend[Backend UI and stock documents]
    Normalize --> AISearch[ai_search_products]
    Compute --> AISearch
    AISearch --> OpenRouter[AI assistant tool layer]
```

## object_request

Модуль ведёт требования на комплектацию объектов. Склад не выбирается в шапке требования: при создании объекта автоматически создаётся связанный `stock.warehouse`, который используется как склад приёмки закупок. Выдача планируется на уровне строки требования через распределение `object.request.line.stock` по всем активным складам компании.

```mermaid
flowchart TD
    Project[Объект object.request.project] --> ProjectWh[Склад объекта stock.warehouse]
    Foreman[Прораб] --> Request[Требование object.request]
    Request --> Lines[Строки object.request.line]
    Lines --> Check[Рассчитать наличие]
    Check --> StockRows[Распределение object.request.line.stock]
    StockRows --> Split[Авто-разбивка / ручная правка]
    Split --> IssuePlan[К выдаче по складам]
    Split --> BuyPlan[К закупке]
    IssuePlan --> Preview[Wizard предпросмотра выдач]
    Preview --> PickA[stock.picking склад A]
    Preview --> PickB[stock.picking склад B]
    PickA --> Reserve[Резерв / факт выдачи]
    PickB --> Reserve
    Reserve --> SyncIssued[Синхронизация qty_reserved / qty_issued]
    BuyPlan --> PurchaseWizard[Wizard закупки]
    ProjectWh --> PurchaseWizard
    PurchaseWizard --> PO[purchase.order с приёмкой на склад объекта]
```

Ключевые правила:

- `object.request` не хранит `warehouse_id`, `check_warehouse_ids`, `stock_check_confirmed`.
- `action_check_stock` создаёт/обновляет `object.request.line.stock` по всем активным складам компании.
- `action_auto_split` использует положительный остаток склада объекта первым, затем остальные склады по доступному остатку; дефицит переносится в закупку.
- `object.request.issue.preview.wizard` создаёт по одному `stock.picking` на каждый включённый склад.
- `object.request.purchase.wizard` по умолчанию принимает закупку на `project.warehouse_id.in_type_id`.
- Excel-импорт `object.request.import.wizard` определяет колонки по заголовкам,
  а не по фиксированным позициям. Поддержаны стандартный формат
  `Артикул / Наименование / Ед. / Кол-во` и формат УУТЭ
  `Наименование / Обозначение / Единица измерения / Количество`, где
  `Обозначение` используется как артикул поставщика.
- Production-объекты снабжения: `O001` — Ломоносова 164 (warehouse id `10`) и `O002` — Б. Хмельницкого, 112 (warehouse id `16`).
- Новые объектные склады создаются только через `Комплектация объектов → Объекты`; ручное создание `stock.warehouse` для объектов запрещено регламентом.
- Legacy-запросы `ОбМ-2` и `ОбМ-4` временно поддерживаются AI Assistant как aliases на `O001` и `O002`.

## Правила безопасности

- Кастомные addon не меняют Odoo core.
- Поиск товаров выполняется через стандартные ORM `search`, `search_fetch`, `read`.
- `ai_search_products()` не использует `sudo()` для поиска и чтения результатов, чтобы сохранить ACL и record rules текущего пользователя.
- Секреты OpenRouter и конфиги с паролями не фиксируются в документации и git.

## ai_assistant v3 actions

AI Assistant v3 добавляет ограниченный tool layer для снабжения. Tools работают
через allowlist, denylist, JSON schema validation, frontend confirmation cards,
rate limits и audit. AI создаёт только черновики и заметки; Confirm/Validate
остаются ручными действиями пользователя в Odoo UI.

Сценарий контрагентов расширяет тот же tool layer:

- `create_partner_draft` создаёт нового `res.partner` только после поиска
  дубликата по ИНН и выбора категории.
- `update_partner_draft` дополняет существующего контрагента только по пустым
  полям, не меняет ИНН, добавляет тег категории и повышает ранги.
- `add_partner_bank_draft` и `add_partner_contact_draft` работают через
  плоские валидируемые параметры; denylist executor для сырых `bank_ids`,
  `child_ids`, `category_id` не ослаблен.
- Категории `Поставщик`, `Заказчик`, `Покупатель`, `Подрядчик` централизованы
  в validators и синхронизированы с workflow `.cursor/skills/odoo-add-partner`.

```mermaid
flowchart TD
    Chat[OWL chat widget] --> Controller[ai_assistant chat_controller]
    Controller --> OpenRouter[OpenRouter tools/function calling]
    Controller --> ToolLayer[action_tools registry + ToolExecutor]
    ToolLayer --> ReadTools[read tools]
    ToolLayer --> WriteTools[write draft tools]
    ToolLayer --> Pending[pending_action confirmation store]
    ToolLayer --> Audit[ai_assistant.audit]
    ReadTools --> ProductSearch[custom_product_search.ai_search_products]
    ReadTools --> OdooRead[Odoo ORM read/search]
    ReadTools --> FindPartner[find_partner — res.partner по ИНН/названию]
    WriteTools --> OR[object.request draft]
    WriteTools --> PO[purchase.order draft]
    WriteTools --> Picking[stock.picking internal draft]
    WriteTools --> Chatter[mail.thread message_post]
    WriteTools --> PartnerCreate[create_partner_draft / update_partner_draft]
    WriteTools --> PartnerBank[add_partner_bank_draft — res.partner.bank]
    WriteTools --> PartnerContact[add_partner_contact_draft — дочерний контакт]
    Pending --> ConfirmCard[ConfirmationCard / ResultCard]
    Controller --> CategoryChips[chips выбора категории контрагента]
```
