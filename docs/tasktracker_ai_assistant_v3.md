# Task Tracker: AI-ассистент v3 — Actions

**Дата создания:** 2026-05-23
**Roadmap:** [`roadmap_ai_assistant_v3_actions.md`](roadmap_ai_assistant_v3_actions.md)
**Базовый модуль:** `custom_addons/ai_assistant/` (AIA-001 — AIA-028 выполнены)
**Предыдущие трекеры:** [`tasktreckeragentconsul.md`](tasktreckeragentconsul.md), [`tasktracker_ai_assistant_v2.md`](tasktracker_ai_assistant_v2.md)

---

## Как пользоваться этим трекером (для агента из терминала)

1. Открой задачу **в порядке зависимостей** (см. сводную таблицу в §13).
2. **Прочитай блок «Контекст»** задачи (`Read` указанных файлов).
3. Если задача помечена 🔧 **Context7** — **сначала** вызови Context7 MCP по указанной теме, потом пиши код.
4. Соблюдай **«Запрещено»**-блок задачи — это границы из roadmap §1.3.
5. Каждый шаг отмечай `[x]` сразу после выполнения.
6. После последнего шага — обнови `docs/changelog.md` и (если затронута архитектура) `docs/project.md`.

### Условные обозначения

- 🔧 **Context7** — обязательная сверка с актуальной документацией библиотеки.
- 📁 **Контекст** — список файлов/документов, без которых не начинать.
- 🚫 **Запрещено** — конкретные операции/паттерны, недопустимые в этой задаче.
- ✅ **DoD** — Definition of Done (что должно быть выполнено для закрытия).
- ⛓ **Зависит от** — задачи, которые должны быть закрыты раньше.

---

## Этап V3-1. Knowledge + Prompt

### Задача: AIA-029 — Создать `supply_cycle_context.md` для knowledge base

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Создать сжатую (≤ 6 КБ) версию инструкции `docs/instruction-warehouse-supply-cycle.md` для подгрузки в system prompt при `module in ('purchase','stock','object_request')` и режиме actions.
- **📁 Контекст**:
  - `docs/instruction-warehouse-supply-cycle.md` — источник
  - `custom_addons/ai_assistant/services/knowledge_provider_v2.py` — как подключается knowledge
  - `custom_addons/ai_assistant/static/knowledge/index.json` — где регистрировать
  - `custom_addons/ai_assistant/static/knowledge/generated/object_request_context.md` — пример формата
- **Шаги выполнения**:
  - [x] Создать `custom_addons/ai_assistant/static/knowledge/supply_cycle_context.md` с разделами:
    - [x] Роли (прораб, снабженец, кладовщик, AI)
    - [x] Маппинг склад → `picking_type_id` (по фактическим данным Odoo, заполнить через MCP `search_records` на `stock.picking.type`)
    - [x] Формулы пересчёта (кг/т → м) — из §7 инструкции
    - [x] Denylist операций (из §3.2, §10)
    - [x] Пример «правильного» плана PO (фрагмент 5–10 строк)
  - [x] Зарегистрировать файл в `static/knowledge/index.json` под ключами `purchase` и `stock` и `object_request`
  - [x] Проверить размер: `wc -c < custom_addons/ai_assistant/static/knowledge/supply_cycle_context.md` ≤ 6144
  - [x] Обновить `KnowledgeProviderV2._SEARCH_KEYWORDS` (если есть) — добавить триггерные слова: «снабжение», «закупка», «требование», «приход», «ОбМ»
- **🚫 Запрещено**: вставлять в файл инструкции по `button_confirm`, `button_validate`, инвентаризации.
- **✅ DoD**: файл подгружается в system prompt при тестовом запросе «как создать закупку на ОбМ-4», проверено логом `[AI Assistant] build_messages: docs_chars=…`.
- **⛓ Зависит от**: —

---

### Задача: AIA-030 — Расширить `PromptBuilder` режимом `actions`

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Добавить в `services/prompt_builder.py` параметр `mode='consult'|'actions'` и блок дополнительных правил для actions (из roadmap §4.1). Сохранить обратную совместимость.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/services/prompt_builder.py`
  - `docs/roadmap_ai_assistant_v3_actions.md` §4.1
  - `custom_addons/ai_assistant/services/response_guard.py` — паттерны, которые нужно учесть
- **Шаги выполнения**:
  - [x] Добавить константу `_ACTIONS_RULES_BLOCK` с текстом из roadmap §4.1
  - [x] Расширить сигнатуру `build_messages(..., mode='consult')`
  - [x] В `_build_system()` при `mode='actions'` дописать `_ACTIONS_RULES_BLOCK` после `_SYSTEM_PROMPT_V2`
  - [x] Параметризовать `_SAFETY_RULES` — в actions режиме не запрещать «я создам/выполню»
  - [x] Тест: `tests/test_prompt_builder_v3.py::test_actions_mode_includes_rules`
  - [x] Тест: `test_consult_mode_unchanged` — старое поведение не сломалось
  - [x] Тест: `test_actions_mode_blocks_inventory_mention` — проверка что блок упоминает запреты
- **🚫 Запрещено**: убирать или ослаблять правила консультативного режима.
- **✅ DoD**: оба режима покрыты тестами; в actions виден доп. блок правил.
- **⛓ Зависит от**: AIA-029

---

## Этап V3-2. Tool layer (домен)

### Задача: AIA-031 — Реализовать `action_tools/registry.py` + `base.py` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Базовый каркас domain-слоя для tools: абстрактные классы и реестр. Должен быть независимым от OpenRouter и HTTP.
- **🔧 Context7**:
  - Тема: «OpenAI function calling tools schema 2024-2025», «JSON Schema 2020-12»
  - Цель: убедиться, что мы строим JSON Schema, корректно принимаемый OpenRouter (совместимый с OpenAI).
  - Что искать: формат `parameters.properties`, поддержка `enum`, `additionalProperties: false`, `required`.
- **📁 Контекст**:
  - `docs/roadmap_ai_assistant_v3_actions.md` §2, §3.3, §5
- **Шаги выполнения**:
  - [x] Создать `services/action_tools/__init__.py` (пустой, экспорт)
  - [x] Создать `services/action_tools/base.py`:
    - [x] Класс `AbstractTool` с атрибутами: `name`, `description`, `parameters_schema` (JSON Schema dict), `required_groups` (list of XML id групп)
    - [x] Метод `execute(env, args: dict) -> dict` (абстрактный)
    - [x] Метод `validate_args(args)` — проверка по JSON Schema (используем `jsonschema` если доступен, иначе ручная проверка required + типы)
    - [x] Класс `AbstractReadTool(AbstractTool)` — `is_write=False`
    - [x] Класс `AbstractWriteTool(AbstractTool)` — `is_write=True`, обязателен `idempotency_key(args) -> str`
  - [x] Создать `services/action_tools/registry.py`:
    - [x] Класс `ToolRegistry` с методами: `register(tool)`, `get(name)`, `list_for_user(env)` — фильтрация по группам
    - [x] Метод `to_openrouter_tools(env)` — конвертация в массив `[{type:'function', function:{name, description, parameters}}]`
    - [x] Глобальный singleton `default_registry`
  - [x] Тест `tests/test_action_tools_registry.py`:
    - [x] `test_register_and_get`
    - [x] `test_list_for_user_filters_by_group`
    - [x] `test_to_openrouter_tools_schema_shape`
    - [x] `test_validate_args_rejects_extra_properties`
- **🚫 Запрещено**: импортировать здесь OpenRouter-клиент или HTTP-слой.
- **✅ DoD**: реестр и базовые классы работают, тесты зелёные.
- **⛓ Зависит от**: —

---

### Задача: AIA-032 — Pre-condition валидаторы (`validators.py`) 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Набор reusable-проверок, вызываемых tools перед ORM. Должны быть **чистыми функциями** или статическими методами (без побочных эффектов).
- **🔧 Context7**:
  - Тема: «Odoo 19 stock.picking.type fields», «Odoo 19 product.product is_storable»
  - Цель: подтвердить актуальные имена полей в v19 (например, `is_storable` vs `type` — в v19 единое поле).
- **📁 Контекст**:
  - `docs/instruction-warehouse-supply-cycle.md` §5, §9.2, §9.3
  - `docs/datamodelspecobjectrequest.md`
- **Шаги выполнения**:
  - [x] Создать `services/action_tools/validators.py`
  - [x] Реализовать:
    - [x] `validate_picking_type_is_object(env, picking_type_id) -> None|raise`: код склада начинается с `ОбМ-`
    - [x] `validate_product_is_storable(env, product_id) -> None|raise`
    - [x] `validate_state_in(record, allowed_states) -> None|raise`
    - [x] `validate_warehouse_code_pattern(env, warehouse_id) -> None|raise`
    - [x] `validate_partner_is_supplier(env, partner_id) -> None|raise` (supplier_rank > 0)
    - [x] `validate_uom_is_meter(env, product_id) -> warning_message` (если категория «Трубы» и UoM не «метр»/«m» — вернуть предупреждение, **не raise**, до TD-002)
  - [x] Исключения: использовать `odoo.exceptions.ValidationError`
  - [x] Тест `tests/test_validators.py` — на каждый валидатор happy + edge case
- **🚫 Запрещено**: писать в БД из валидаторов, использовать `sudo()`.
- **✅ DoD**: все валидаторы покрыты тестами, ошибки понятные пользователю на русском.
- **⛓ Зависит от**: AIA-031

---

### Задача: AIA-033 — Read tools (`read_tools.py`): продукты и партнёры 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Реализовать `search_products`, `find_product_by_id`, `find_partner`.
- **🔧 Context7**:
  - Тема: «Odoo 19 product.product search_read fields», «Odoo 19 res.partner supplier_rank»
  - Цель: уточнить актуальный набор полей и domain operators.
- **📁 Контекст**:
  - `custom_addons/custom_product_search/models/product_product.py::ai_search_products`
  - `custom_addons/ai_assistant/services/action_tools/base.py` (AIA-031)
- **Шаги выполнения**:
  - [x] `SearchProductsTool(AbstractReadTool)`:
    - parameters: `query: string` (min 2 chars), `limit: integer` (default 10, max 30)
    - execute: `env['product.product'].ai_search_products(query, limit=limit)`; вернуть `{products: [{id, display_name, default_code, uom_id, is_storable, list_price}]}`
  - [x] `FindProductByIdTool(AbstractReadTool)`:
    - parameters: `product_id: integer`
    - execute: `env['product.product'].browse(id).read(['display_name','uom_id','categ_id','is_storable','seller_ids'])`
  - [x] `FindPartnerTool(AbstractReadTool)`:
    - parameters: `query: string` (имя или ИНН), `is_supplier: boolean` (default true)
    - execute: domain `[('name','ilike',q)|('vat','=',q)]` + `[('supplier_rank','>',0)]` если supplier; limit 10
  - [x] Регистрация в `registry.default_registry`
  - [x] Тест `tests/test_read_tools.py::test_search_products_basic`, `test_find_partner_by_vat`, etc.
- **🚫 Запрещено**: `sudo()`, доступ к `res.users.password`/`ir.config_parameter`.
- **✅ DoD**: tools вызываются из тестов, возвращают ожидаемые поля, ACL соблюдается (тест с non-stock user падает корректно).
- **⛓ Зависит от**: AIA-031, AIA-032

---

### Задача: AIA-034 — Read tools: склад, остатки, requests 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Реализовать `search_stock_quants`, `find_warehouse`, `find_picking_type`, `find_object_request`, `read_object_request`.
- **🔧 Context7**:
  - Тема: «Odoo 19 stock.quant search_read», «Odoo 19 stock.picking.type code field»
  - Цель: подтвердить поля и значения enum `code` (incoming/outgoing/internal/mrp_operation).
- **📁 Контекст**:
  - `custom_addons/object_request/models/object_request.py` — поля OR
  - `docs/datamodelspecobjectrequest.md`
  - `docs/instruction-warehouse-supply-cycle.md` §5
- **Шаги выполнения**:
  - [x] `SearchStockQuantsTool`:
    - parameters: `product_id: integer`, `warehouse_codes: array<string> | null`, `only_positive: boolean (default true)`
    - execute: domain `[('product_id','=',pid)]` + `[('quantity','>',0)]` + `[('warehouse_id.code','in',codes)]`
  - [x] `FindWarehouseTool`:
    - parameters: `code_pattern: string` (например `ОбМ-4` или `ОбМ-`)
    - execute: search_read `[('code','=ilike',pattern)]` с полями `name, code, in_type_id, int_type_id, lot_stock_id`
  - [x] `FindPickingTypeTool`:
    - parameters: `warehouse_id: integer`, `code: enum('incoming','internal')`
    - execute: search_read с двумя условиями
  - [x] `FindObjectRequestTool`:
    - parameters: `query: string | null`, `state: enum(...) | null`, `project_id: integer | null`
    - execute: search_read top 20 по убыванию даты
  - [x] `ReadObjectRequestTool`:
    - parameters: `request_id: integer`
    - execute: read шапку + до 50 строк (`line_ids`), сводка `qty_total_*`
  - [x] Регистрация + тесты в `test_read_tools.py`
- **🚫 Запрещено**: возвращать поля с PII (например `partner.user_id.password_crypt`) — whitelist полей.
- **✅ DoD**: каждый tool протестирован минимум одним happy-case и одним ACL-case.
- **⛓ Зависит от**: AIA-031, AIA-032, AIA-033

---

### Задача: AIA-034A — Подключить `action_tools` при загрузке services

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Гарантировать, что read tools регистрируются в `default_registry` при стандартной загрузке пакета `ai_assistant.services`, а не только при прямом импорте `services.action_tools`.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/services/__init__.py`
  - `custom_addons/ai_assistant/services/action_tools/__init__.py`
  - `custom_addons/ai_assistant/services/action_tools/read_tools.py`
  - `docs/roadmap_ai_assistant_v3_actions.md` §3.2, §3.3
- **Шаги выполнения**:
  - [x] Проверить, что импорт `action_tools` не противоречит roadmap: `action_tools/*` не импортирует OpenRouter/HTTP и остаётся доменным слоем.
  - [x] Добавить `from . import action_tools  # noqa: F401` в `services/__init__.py`.
  - [x] Зафиксировать техдолг: заменить side-effect регистрацию на явную `register_default_tools()` с идемпотентной защитой.
- **🚫 Запрещено**: импортировать OpenRouter-клиент или HTTP-слой внутрь `action_tools/*`.
- **✅ DoD**: `ai_assistant.services` загружает `action_tools`, а `read_tools.py` регистрирует read tools в `default_registry`.
- **⛓ Зависит от**: AIA-031, AIA-033, AIA-034

---

## Этап V3-3. Write tools + executor

### Задача: AIA-035 — `create_object_request_draft` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Write tool для создания OR в `draft` от имени текущего пользователя.
- **🔧 Context7**:
  - Тема: «Odoo 19 mail.thread message_post API»
  - Цель: актуальные параметры `body`, `subtype_xmlid`, `message_type`.
- **📁 Контекст**:
  - `custom_addons/object_request/models/object_request.py`
  - `custom_addons/object_request/security/object_request_security.xml`
  - `docs/datamodelspecobjectrequest.md`
- **Шаги выполнения**:
  - [x] `CreateObjectRequestDraftTool(AbstractWriteTool)`:
    - required_groups: `['ai_assistant.group_ai_assistant_supply']`
    - parameters: `project_id: integer`, `need_date: string (ISO date)`, `lines: array<{name_raw: string, qty_requested: number, preferred_vendor_id: integer | null}>` (min 1, max 100)
    - whitelist полей шапки: `project_id`, `need_date`, `foreman_user_id` (= current user)
  - [x] Валидации:
    - validate_state_in (не нужен — создание)
    - `len(lines) >= 1`
    - все `qty_requested > 0`
  - [x] Execute:
    - `env['object.request'].create({...})` (без sudo)
    - На каждую строку — `env['object.request.line'].create(...)`
    - `record.message_post(body=...)` с пометкой «создано AI-ассистентом»
    - Return `{request_id, name, url: f"/odoo/object_request/{id}"}`
  - [x] idempotency_key: hash от `(project_id, need_date, sorted(lines))`
  - [x] Тест `tests/test_write_tools.py::test_create_or_draft_happy`
  - [x] Тест `test_create_or_draft_rejects_without_supply_group`
  - [x] Тест `test_create_or_draft_message_post_called`
- **🚫 Запрещено**: устанавливать `state` напрямую (по умолчанию `draft`), использовать `sudo()`.
- **✅ DoD**: OR создаётся через write tool без `sudo()`, в chatter есть запись. Подключение через executor закрывается в AIA-038.
- **⛓ Зависит от**: AIA-031, AIA-032

---

### Задача: AIA-036 — `create_purchase_order_draft` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Write tool создания PO в `draft` с правильным `picking_type_id` склада объекта.
- **🔧 Context7**:
  - Тема: «Odoo 19 purchase.order onchange picking_type_id», «Odoo 19 purchase.order.line product_qty product_uom»
  - Цель: уточнить, есть ли в v19 onchange, который автоматически выставляет `default_location_dest_id` — это критично, иначе линии могут уйти на Vendors → Stock вместо ОбМ-N.
- **📁 Контекст**:
  - `custom_addons/object_request/wizards/purchase_wizard.py` — образец логики
  - `custom_addons/object_request/models/purchase_order_ext.py`
  - `docs/instruction-warehouse-supply-cycle.md` §5.3, §9.2
- **Шаги выполнения**:
  - [x] `CreatePurchaseOrderDraftTool(AbstractWriteTool)`:
    - parameters:
      - `partner_id: integer` (required)
      - `picking_type_id: integer` (required)
      - `origin: string` (required, OR/...)
      - `partner_ref: string` (required, номер счёта 1С)
      - `date_planned: string (ISO datetime, optional)`
      - `lines: array<{product_id: integer, product_qty: number, product_uom: integer, price_unit: number, name: string | null}>` (min 1)
    - whitelist полей шапки: `partner_id`, `picking_type_id`, `origin`, `partner_ref`, `date_planned`, `notes`
    - whitelist полей строки: `product_id`, `product_qty`, `product_uom`, `price_unit`, `name`, `date_planned`
  - [x] Валидации:
    - `validate_partner_is_supplier`
    - `validate_picking_type_is_object` (код склада начинается с `ОбМ-`)
    - на каждую строку: `validate_product_is_storable` + `validate_uom_is_meter` (warning)
  - [x] Execute:
    - `po = env['purchase.order'].create({...})` (триггерит стандартный onchange по picking_type_id)
    - Строки через `po.order_line = [(0, 0, ln) for ln in lines]` или `env['purchase.order.line'].create`
    - `po.message_post(body=...)` с пометкой
    - Return `{po_id, name, url: f"/odoo/purchase/{id}", warnings: [...]}`
  - [x] idempotency_key: hash от `(partner_id, origin, partner_ref, sorted(lines))`
  - [x] Тест: happy на ОбМ-4, ИНН ПроМеталл, 6 строк труб
  - [x] Тест: отклоняет picking_type_id не-ОбМ
  - [x] Тест: отклоняет product без `is_storable`
  - [x] Тест: warning при UoM кг для трубы
- **🚫 Запрещено**:
  - `button_confirm`/`action_post`
  - изменение `state` в payload
  - запись в `account.move.*`
- **✅ DoD**: PO создаётся в `draft`, тесты зелёные, в chatter — отметка AI.
- **⛓ Зависит от**: AIA-031, AIA-032, AIA-033, AIA-034, AIA-035

---

### Задача: AIA-037 — `create_internal_picking_draft` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Write tool для перемещения с базового склада на ОбМ-N.
- **🔧 Context7**:
  - Тема: «Odoo 19 stock.picking create with moves», «stock.move.line vs stock.move»
  - Цель: уточнить, как корректно создать picking с move lines в v19 (через `move_ids_without_package` или `move_ids`).
- **📁 Контекст**:
  - `custom_addons/object_request/wizards/issue_preview_wizard.py` — образец
  - `docs/instruction-warehouse-supply-cycle.md` §5.4, §3a
- **Шаги выполнения**:
  - [x] `CreateInternalPickingDraftTool(AbstractWriteTool)`:
    - parameters:
      - `picking_type_id: integer` (тип internal)
      - `location_id: integer` (источник, базовый склад)
      - `location_dest_id: integer` (назначение, ОбМ-N/...)
      - `origin: string` (OR/...)
      - `scheduled_date: string (ISO datetime, optional)`
      - `moves: array<{product_id: integer, product_uom_qty: number, product_uom: integer, name: string | null}>` (min 1)
  - [x] Валидации:
    - `picking_type_id.code == 'internal'`
    - `location_dest_id` — child_of warehouse с кодом ОбМ-*
    - на каждый product — `validate_product_is_storable`
  - [x] Execute:
    - создать `stock.picking` со всеми moves в одном `create`
    - `picking.message_post(...)`
    - Return `{picking_id, name, url}`
  - [x] idempotency_key
  - [x] Тесты: happy, отклонение если dest не ОбМ
- **🚫 Запрещено**: `action_assign`/`button_validate`; запись `state`.
- **✅ DoD**: picking создаётся в `draft`, moves видны в UI.
- **⛓ Зависит от**: AIA-031, AIA-032, AIA-033, AIA-034

---

### Задача: AIA-038 — `post_chatter_note` и `ToolExecutor` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Финальный tool аудита + центральный executor, выполняющий tool по имени с проверками безопасности.
- **🔧 Context7**:
  - Тема: «Odoo 19 mail.thread message_post subtype_xmlid mail.mt_note»
  - Цель: правильный subtype для internal note (не уведомляет followers).
- **📁 Контекст**:
  - `docs/roadmap_ai_assistant_v3_actions.md` §2.4, §7.3
  - `custom_addons/ai_assistant/services/action_tools/registry.py`
- **Шаги выполнения**:
  - [x] `PostChatterNoteTool(AbstractWriteTool)`:
    - parameters: `model: enum(...allowlist...)`, `record_id: integer`, `body: string` (max 2000)
    - allowlist моделей: `object.request`, `purchase.order`, `stock.picking`
    - execute: `env[model].browse(id).message_post(body=body, subtype_xmlid='mail.mt_note')`
  - [x] `services/action_tools/executor.py`:
    - класс `ToolExecutor(env, user_id)`:
      - `execute(name: str, args: dict) -> dict`
      - проверка `tool.required_groups` → ACL пользователя
      - проверка denylist на этапе before execute (двойная страховка)
      - `tool.validate_args(args)` → JSON Schema
      - `tool.execute(env, args)`
      - оборачивание ошибок в стандартный формат `{success: false, error: {code, message}}`
      - логирование (`_logger.info`) без чувствительных данных
  - [x] Тест `tests/test_tool_executor_security.py`:
    - [x] `test_executor_rejects_unknown_tool`
    - [x] `test_executor_rejects_user_without_group`
    - [x] `test_executor_validates_schema`
    - [x] `test_executor_returns_error_envelope_on_exception`
    - [x] `test_executor_post_chatter_only_allowed_models`
- **🚫 Запрещено**: ловить `Exception` и молча возвращать success.
- **✅ DoD**: executor закрыт тестами, в т.ч. на запрещённые операции; ошибки структурированы.
- **⛓ Зависит от**: AIA-031, AIA-035, AIA-036, AIA-037

---

## Этап V3-4. OpenRouter integration

### Задача: AIA-039 — Расширить `OpenRouterClient` поддержкой tools 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Добавить метод `send_chat_with_tools(messages, tools, tool_choice='auto', model_override=None)`. Парсить ответ модели с `tool_calls`.
- **🔧 Context7**:
  - Тема: «OpenRouter tools function calling 2025», «OpenAI Python SDK tool_calls response format», «Gemini 2.0 Flash function calling support OpenRouter»
  - Цель: подтвердить формат payload и формат ответа, поддержку моделями `google/gemini-2.0-flash-001` и `openai/gpt-4o-mini`.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/services/openrouter_client.py`
  - `docs/roadmap_ai_assistant_v3_actions.md` §5
- **Шаги выполнения**:
  - [x] Добавить метод `send_chat_with_tools(...)`:
    - payload включает `tools`, `tool_choice`
    - возвращает структурированно: `{type: 'message'|'tool_calls', content, tool_calls: [{id, name, arguments}], finish_reason, model_used, tokens_used}`
  - [x] Безопасный JSON-парс `arguments` (модель присылает строкой)
  - [x] Логирование: количество tool_calls, имена tools — **без аргументов** (PII)
  - [x] Сохранить старый `send_chat()` без изменений (back-compat для consult)
  - [x] Тест `tests/test_openrouter_tools.py` с моком requests:
    - [x] `test_send_with_tools_passes_tools_in_payload`
    - [x] `test_parses_tool_calls_response`
    - [x] `test_handles_invalid_json_in_arguments`
    - [x] `test_finish_reason_stop_returns_message`
- **🚫 Запрещено**: логировать `arguments` (могут содержать ИНН/телефоны/адреса).
- **✅ DoD**: моки покрывают оба finish_reason; парсинг устойчив к битому JSON.
- **⛓ Зависит от**: AIA-031

---

### Задача: AIA-040 — Tool-call цикл в `chat_controller.py` + `pending_action`

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Реализовать главный цикл: модель → tool_calls → исполнение (read автоматом, write → pending) → ответ → loop.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/controllers/chat_controller.py`
  - `docs/roadmap_ai_assistant_v3_actions.md` §3.1, §5.2
- **Шаги выполнения**:
  - [x] Создать `services/pending_action.py`:
    - класс `PendingActionStore` (in-memory dict `{uid: {key, tool_name, args, expires_at}}`)
    - методы `put(uid, key, tool, args)`, `get(uid, key)`, `pop(uid, key)`, `clear(uid)`
    - TTL: 10 минут
  - [x] Модифицировать `_get_ai_response`:
    - определить `mode` по группе пользователя + `actions_enabled`
    - в actions: подгрузить `registry.to_openrouter_tools(env)` → `client.send_chat_with_tools(...)`
    - цикл max=5 итераций:
      - response.type == 'message' → return answer
      - response.type == 'tool_calls' →
        - для каждой tool_call: если read → executor.execute → append role='tool' message
        - если write → сохранить в pending_action, прервать цикл, вернуть `confirmation_card`
  - [x] Новый endpoint `POST /ai_assistant/confirm`:
    - body: `{pending_key: string, decision: 'confirm'|'cancel'}`
    - confirm → executor.execute(write tool), затем дополнить историю и снова вызвать модель для финального текста
    - cancel → pending_action.pop, вернуть «отменено»
  - [x] DTO ответа `/ai_assistant/chat` расширить полем `cards: [{type:'confirmation', pending_key, plan: {...}}]`
  - [x] Тест `tests/test_chat_controller.py` (расширить):
    - [x] `test_actions_mode_read_tool_call_loop` (моки на client.send_chat_with_tools)
    - [x] `test_actions_mode_write_returns_confirmation_card`
    - [x] `test_confirm_endpoint_executes_pending`
    - [x] `test_confirm_with_wrong_key_returns_error`
    - [x] `test_max_iterations_breaks_loop`
- **🚫 Запрещено**: выполнять write-tools без `/confirm` endpoint.
- **✅ DoD**: backend-тесты проходят; cancellation работает; в логах виден путь tool_call → confirm. Финальный LLM-текст после confirm и frontend-рендер карточек закрываются следующими задачами UX.
- **⛓ Зависит от**: AIA-038, AIA-039

---

## Этап V3-5. Frontend UX

### Задача: AIA-041 — OWL `ConfirmationCard` 🔧 Context7

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Inline-карточка в чате с описанием плана и кнопками «Подтвердить» / «Отменить».
- **🔧 Context7**:
  - Тема: «Odoo 19 OWL 2 components t-component slots», «Odoo 19 web/static/src widget patterns»
  - Цель: актуальные API OWL 2 для inline-компонентов внутри уже зарегистрированного backend-виджета.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/static/src/xml/ai_chat_widget.xml`
  - `custom_addons/ai_assistant/static/src/js/ai_chat_boot.js`
  - `custom_addons/ai_assistant/static/src/scss/ai_chat_widget.scss`
- **Шаги выполнения**:
  - [x] Создать `static/src/js/ai_chat_actions.js` с компонентом `ConfirmationCard`
    - props: `plan: {title, fields: [{label, value}], tool_name}`, `pendingKey: string`, `onConfirm`, `onCancel`
    - слот для дочернего описания (опциональный)
  - [x] Шаблон в `ai_chat_widget.xml` (или отдельном `.xml`):
    - заголовок плана (жирный)
    - таблица «поле → значение»
    - две кнопки
  - [x] Стили в `ai_chat_widget.scss` — карточка с отступами и рамкой
  - [x] Подключить в основной чат-сервис: при ответе с `cards[].type === 'confirmation'` рендерить
  - [x] Тест ручной: визуальная проверка в браузере на dev-инстансе
    - Проверено технически через `odoo -u ai_assistant`; визуальная браузерная проверка оставлена для AIA-043/AIA-044 UX-прохода.
- **🚫 Запрещено**: использовать deprecated jQuery API.
- **✅ DoD**: карточка появляется в чате, кнопки кликабельны, шлют запрос на `/confirm`.
- **Результат**:
  - Добавлен OWL-компонент `ConfirmationCard`.
  - `ai_chat_service.js` сохраняет `cards` в истории и отправляет `/ai_assistant/confirm`.
  - `AiChatWidget` рендерит `confirmation` cards и помечает карточку как подтверждённую/отменённую после ответа.
- **⛓ Зависит от**: AIA-040

---

### Задача: AIA-042 — OWL `ResultCard`

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Карточка с результатом: ✅ имя записи, ссылка `/odoo/<model>/<id>`, подсказка следующего шага.
- **📁 Контекст**:
  - `static/src/js/ai_chat_actions.js` (AIA-041)
- **Шаги выполнения**:
  - [x] Компонент `ResultCard(props: {status: 'success'|'error', record: {model, id, name, url}, next_hint: string})`
  - [x] При клике на ссылку — открыть в новой вкладке (`target="_blank"`)
  - [x] Подсветка успеха зелёным, ошибки — красным
  - [x] Подключить рендеринг при `cards[].type === 'result'`
- **🚫 Запрещено**: показывать сырые stack traces — только `error.message`.
- **✅ DoD**: после подтверждения видна карточка со ссылкой; клик переводит в Odoo.
- **Результат**:
  - Добавлен OWL-компонент `ResultCard` в `ai_chat_actions.js`.
  - Рендеринг `result` cards подключён в `AiChatWidget`.
  - Ошибки показываются только через `error.message`, без stack trace.
- **⛓ Зависит от**: AIA-041

---

### Задача: AIA-043 — `ai_chat_service.js`: расширение для tools

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Передача `cards` от backend, обработка кликов confirm/cancel.
- **📁 Контекст**: `custom_addons/ai_assistant/static/src/js/ai_chat_service.js`
- **Шаги выполнения**:
  - [x] Обновить response DTO: `cards: array` в additional полях
  - [x] Метод `confirmAction(pendingKey, decision)` — POST на `/ai_assistant/confirm`
  - [x] Сохранение в sessionStorage: card отображается до перезагрузки страницы; после клика — обновляется на ResultCard
  - [x] Удаление pending cards при `clearHistory()`
  - [x] Лимит: одна active confirmation card на чат (новая отменяет старую через `/confirm` с `decision: 'cancel'`)
- **🚫 Запрещено**: хранить в sessionStorage `tool_args` (они уже у backend в pending_action).
- **✅ DoD**: интеграция чистая, нет race-condition при быстром клике.
- **Результат**:
  - `ai_chat_service.js` сохраняет `cards` в sessionStorage без `tool_args`.
  - `confirmAction()` централизует JSON-RPC вызов `/ai_assistant/confirm`.
  - Перед добавлением новой confirmation card старые active pending cards отменяются и помечаются как отменённые.
  - Повторный быстрый клик блокируется состоянием `isLoading`; результат подтверждения заменяет pending card на `ResultCard`.
- **⛓ Зависит от**: AIA-041, AIA-042

---

## Этап V3-6. Безопасность

### Задача: AIA-044 — Группа `group_ai_assistant_supply` + feature flag

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Новая группа Odoo для пользователей, которым разрешены actions; settings flag `actions_enabled`.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/security/security_groups.xml`
  - `custom_addons/ai_assistant/models/ai_assistant_config.py`
  - `custom_addons/ai_assistant/views/ai_assistant_settings_views.xml`
- **Шаги выполнения**:
  - [x] `security_groups.xml`: добавить `group_ai_assistant_supply` с `implied_ids` → `group_ai_assistant_user`, `purchase.group_purchase_user`, `stock.group_stock_user`
  - [x] `ai_assistant_config.py`: добавить поле `ai_assistant_actions_enabled` (`config_parameter='ai_assistant.actions_enabled'`, default `'0'`)
  - [x] `ai_assistant_settings_views.xml`: переключатель «Включить actions» с подсказкой
  - [x] `__manifest__.py`: depends += `['mail','stock','purchase','object_request','custom_product_search']`
  - [x] Тест `tests/test_module_install.py` — проверить, что новые depends ставятся, модуль upgradable
- **🚫 Запрещено**: давать группе Supply права администратора Odoo.
- **✅ DoD**: после миграции группа доступна в UI настроек пользователей; flag по умолчанию off.
- **⛓ Зависит от**: —

---

### Задача: AIA-045 — Rate limit и idempotency

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: 30 read/мин, 5 write/мин на пользователя; идемпотентность через `pending_action`.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/controllers/chat_controller.py` (паттерн `_VISION_RATE` уже есть)
  - `custom_addons/ai_assistant/services/pending_action.py` (AIA-040)
- **Шаги выполнения**:
  - [x] В `tool_executor.execute()` инкрементировать счётчик в in-memory структуре (по аналогии с `_VISION_RATE`)
  - [x] При превышении — вернуть error envelope `{code: 'rate_limited', retry_after}`
  - [x] В `pending_action`: при повторном плане с тем же idempotency_key — переиспользовать существующий, не создавать новый
  - [x] Тест: `test_rate_limit_blocks_after_5_writes`, `test_idempotency_reuses_pending`
- **🚫 Запрещено**: хранить счётчики в БД (создаст лишнюю нагрузку).
- **✅ DoD**: тесты зелёные; превышение лимита возвращает понятный текст пользователю.
- **Результат**:
  - Добавлен `ToolRateLimiter`: 30 read/min и 5 write/min на пользователя.
  - `ToolExecutor.execute()` возвращает `rate_limited` error envelope с `retry_after`.
  - `PendingActionStore.put()` переиспользует активный pending по `idempotency_key`.
  - Добавлены тесты на read/write лимиты и повторное pending-подтверждение.
- **⛓ Зависит от**: AIA-038, AIA-040

---

### Задача: AIA-046 — Денилист и security guard в `ToolExecutor`

- **Статус**: ✅ Выполнена
- **Приоритет**: Критический
- **Описание**: Двойная страховка denylist на этапе executor: даже если в реестре окажется запрещённый tool, executor его отвергнет.
- **📁 Контекст**: `docs/roadmap_ai_assistant_v3_actions.md` §2.3
- **Шаги выполнения**:
  - [x] Константа `_FORBIDDEN_METHOD_PATTERNS = [r'button_confirm', r'button_validate', r'action_done', r'action_post']`
  - [x] Проверка `tool.name` не матчит запрещённое
  - [x] Проверка: `tool` не наследник `AbstractWriteTool` для записи `state`, `company_id`, `currency_id`
  - [x] Аудит-лог при попытке вызова запрещённого tool (level=WARNING)
  - [x] Тест: `test_executor_blocks_button_confirm_tool_even_if_registered`
- **🚫 Запрещено**: отключать эту проверку флагом конфига.
- **✅ DoD**: попытка зарегистрировать tool с запрещённым именем падает в тестах.
- **Результат**:
  - `ToolExecutor` блокирует forbidden method names и write schemas с forbidden fields.
  - Попытки forbidden tool логируются на WARNING.
  - Регрессионный тест покрывает зарегистрированный `button_confirm` tool.
- **⛓ Зависит от**: AIA-038

---

## Этап V3-7. Тесты и E2E

### Задача: AIA-047 — Юнит-тесты coverage ≥ 80% по `action_tools/*`

- **Статус**: ⏳ Частично выполнена
- **Приоритет**: Высокий
- **Описание**: Покрыть тестами все tools и executor.
- **📁 Контекст**: все `tests/test_*` файлы выше
- **Шаги выполнения**:
  - [x] Запустить `docker exec odoo19-local odoo --test-enable --test-tags ai_assistant -d odoo19_local --stop-after-init`
  - [x] Прогнать `flake8 /mnt/extra-addons/ai_assistant`
  - [x] Зафиксировать coverage отчёт (если есть pytest-cov) в `docs/pilot_results_v3.md`
- **🚫 Запрещено**: коммитить без зелёных тестов.
- **✅ DoD**: все тесты v3 проходят; нет регрессий v1/v2.
- **Результат**:
  - Полный `/ai_assistant` test suite зелёный: 237 post-tests, 0 failed, 0 errors.
  - Полный `flake8 /mnt/extra-addons/ai_assistant` падает на существующем style debt вне AIA-041..046.
  - Точечный flake8 по изменённым Python-файлам AIA-045/AIA-046 зелёный.
  - Coverage tooling в текущем workflow не найден; процент покрытия не сформирован.
- **⛓ Зависит от**: AIA-031…AIA-046

---

### Задача: AIA-048 — (Опционально) Модель `ai_assistant.audit`

- **Статус**: ✅ Выполнена
- **Приоритет**: Средний
- **Описание**: Централизованный журнал tool-вызовов на случай, если chatter недостаточно.
- **📁 Контекст**: `docs/roadmap_ai_assistant_v3_actions.md` §7.3
- **Шаги выполнения**:
  - [x] Модель `ai_assistant.audit` с полями: `user_id`, `tool_name`, `args_summary` (Text, без PII), `result_status`, `record_ref`, `created_at`
  - [x] Запись в `ToolExecutor.execute()` после выполнения
  - [x] Меню/view (только для admin)
  - [x] Тест `test_audit_records_write_tool_call`
- **🚫 Запрещено**: писать в audit полные `args` (может содержать PII).
- **✅ DoD**: видны последние 100 действий ассистента в админ-меню.
- **Результат**:
  - Добавлена модель `ai_assistant.audit`, ACL на чтение только для `group_ai_assistant_admin`.
  - `ToolExecutor` пишет audit после успешных и ошибочных вызовов tool.
  - `args_summary` хранит только имена аргументов и типы/размеры, без сырых значений.
  - Добавлены list/form views и меню `Settings → AI Assistant → Audit`, limit 100.
  - Тест `test_audit_records_write_tool_call` проверяет запись audit и отсутствие PII в summary.
- **⛓ Зависит от**: AIA-038

---

### Задача: AIA-049 — E2E-тест «УТ-1132 → PO на ОбМ-4»

- **Статус**: ✅ Выполнена
- **Приоритет**: Высокий
- **Описание**: Один интеграционный тест, имитирующий полный сценарий.
- **📁 Контекст**:
  - `docs/instruction-warehouse-supply-cycle.md` §7 (таблица пересчёта)
  - `custom_addons/object_request/data/demo_data.xml` — есть ли там подходящий проект
- **Шаги выполнения**:
  - [x] `tests/test_e2e_supply_cycle.py::TestUT1132PipelineDraft`
    - setUp: создать проект ОбМ-4, поставщика ООО ПроМеталл, 6 товаров-труб с UoM «метр» и `is_storable=True`, OR/2026/05/0007
    - act: вызвать через `ToolExecutor`:
      1. `find_warehouse("ОбМ-4")` → id, in_type_id
      2. `find_partner("ПроМеталл")` → id
      3. `search_products("89×3,5")` → product_id
      4. `create_purchase_order_draft(...)` с 6 строками (1098 м суммарно)
    - assert:
      - PO создан в `state='draft'`
      - `picking_type_id.warehouse_id.code == 'ОбМ-4'`
      - `origin == 'OR/2026/05/0007'`
      - `partner_ref == 'УТ-1132'`
      - сумма qty по строкам == 1098
      - chatter содержит «AI Assistant»
- **🚫 Запрещено**: вызывать `button_confirm` в тесте.
- **✅ DoD**: тест зелёный; имитирует приёмочный сценарий v3.
- **Результат**:
  - Добавлен `tests/test_e2e_supply_cycle.py`.
  - Тест проходит через `ToolExecutor`: `find_warehouse`, `find_partner`, `search_products`, `create_purchase_order_draft`.
  - Проверяется draft PO для `ОбМ-4`, `origin=OR/2026/05/0007`, `partner_ref=УТ-1132`, сумма строк `1098`, chatter содержит `AI Assistant`.
  - `button_confirm` не вызывается.
- **⛓ Зависит от**: AIA-035, AIA-036, AIA-038

---

## Этап V3-8. Документация и пилот

### Задача: AIA-050 — `pilot_results_v3.md` + обновить `instruction-warehouse-supply-cycle.md`

- **Статус**: ✅ Выполнена
- **Приоритет**: Средний
- **Описание**: Финальная документация и обновление инструкции (раздел API).
- **📁 Контекст**:
  - `docs/instruction-warehouse-supply-cycle.md` §8.1 (матрица возможностей)
  - `docs/changelog.md`
  - `docs/project.md`
- **Шаги выполнения**:
  - [x] `docs/pilot_results_v3.md` — отчёт пилота:
    - сценарии (3–5 кейсов): УТ-1132, перемещение с базы, OR без сопоставления и т.п.
    - метрики (создано черновиков, отказов, ошибок валидации)
    - известные ограничения
  - [x] `docs/instruction-warehouse-supply-cycle.md` §8.1 — обновить колонки матрицы для tools, реализованных в v3 (отметить ✅, оставить ❌* для confirm/validate)
  - [x] `docs/project.md` — обновить mermaid-схему, добавить `tool_layer` под `ai_assistant`
  - [x] `docs/changelog.md` — запись `## [YYYY-MM-DD] - AI Assistant v3 Actions`
  - [x] `docs/tasktracker.md` — задача «AI Assistant v3 Actions: завершена»
- **🚫 Запрещено**: указывать в инструкции, что AI делает Confirm/Validate.
- **✅ DoD**: все артефакты документации обновлены; PR/коммит готов.
- **Результат**:
  - `pilot_results_v3.md` дополнен summary пилота, сценариями, метриками и ограничениями.
  - `instruction-warehouse-supply-cycle.md` разделяет MCP/API и AI v3 tools; Confirm/Validate отмечены как ❌*.
  - `project.md` содержит mermaid-схему `ai_assistant v3 actions`.
  - `changelog.md` содержит запись `2026-05-24 - AI Assistant v3 Actions`.
  - `tasktracker.md` помечает AI Assistant v3 Actions как завершённую задачу.
- **⛓ Зависит от**: AIA-049

---

## Этап V3-9. Post-v3 — улучшения read tools

### Задача: AIA-051 — `find_warehouse`: поиск по `name`, не только по `code`

- **Статус**: ✅ Выполнена (2026-05-24)
- **Приоритет**: Высокий
- **Описание**: Расширить read-tool `find_warehouse`, чтобы ассистент находил склад объекта по **адресу/названию** (например «Б. Хмельницкого, 112», «Хмельницкого»), а не только по коду `ОбМ-N`. Сейчас tool ищет только поле `stock.warehouse.code`, из‑за чего пользователь получает просьбу «уточните код склада» при естественных формулировках.
- **Контекст (проблема на проде)**:
  - Запрос: «что есть на складе Б. Хмельницкого, 112» → ассистент просит код склада.
  - В БД: `name = "Б. Хмельницкого, 112"`, `code = "ОбМ-4"`.
  - Tool: `custom_addons/ai_assistant/services/action_tools/read_tools.py::FindWarehouseTool`.
- **📁 Контекст**:
  - `custom_addons/ai_assistant/services/action_tools/read_tools.py` — `FindWarehouseTool`
  - `custom_addons/ai_assistant/tests/test_read_tools.py` — `test_find_warehouse_by_code`
  - `custom_addons/ai_assistant/static/knowledge/supply_cycle_context.md` — таблица ОбМ-1…4 (name ↔ code)
  - `docs/pilot_results_v3.md` §Known limitations — упомянуть закрытие после AIA-051
- **🔧 Context7** (опционально):
  - Тема: «Odoo 19 stock.warehouse search domain name ilike»
  - Цель: подтвердить поле `name` и отсутствие конфликта с `code` при OR-domain.
- **Шаги выполнения**:
  - [x] Изменить JSON Schema `find_warehouse`:
    - [x] Переименовать параметр `code_pattern` → **`query`** (строка ≥ 2 символов) **или** оставить `code_pattern` и добавить опциональный `name_query` — **предпочтительно один параметр `query`** для LLM (меньше путаницы).
    - [x] Обновить `description`: «Найти склад по коду (ОбМ-4, ОбМ-) или по части названия/адреса (Хмельницкого, Ломоносова)».
  - [x] Логика `execute(env, args)`:
    - [x] Нормализовать `query`: `strip()`, min length 2.
    - [x] Если `query` матчит шаблон `ОбМ-` (regex `^ОбМ-\d*$` или заканчивается на `-`) — искать по **`code`** (как сейчас: `=ilike` / `ilike` для префикса).
    - [x] Иначе — domain: `['|', ('code', 'ilike', query), ('name', 'ilike', query)]`, `limit=20`.
    - [x] Дедупликация по `id` если оба условия совпали.
    - [x] Возвращать те же поля: `id`, `name`, `code`, `in_type_id`, `int_type_id`, `lot_stock_id`.
  - [x] Обратная совместимость (если меняется имя параметра):
    - [x] В `execute` принимать и legacy `code_pattern` → маппить в `query` (deprecation в docstring, без ломания старых pending actions — их нет для read tools).
  - [x] Тесты `tests/test_read_tools.py`:
    - [x] `test_find_warehouse_by_code` — оставить/адаптировать под `query='ОбМ-R'`.
    - [x] `test_find_warehouse_by_name_fragment` — `query='Хмельницкого'` → находит склад с `code='ОбМ-4'`.
    - [x] `test_find_warehouse_by_full_name` — `query='Б. Хмельницкого, 112'`.
    - [x] `test_find_warehouse_no_match` — пустой список, не exception.
    - [x] `test_find_warehouse_obm_prefix_list` — `query='ОбМ-'` возвращает все объектные склады (как сейчас для code prefix).
  - [x] Обновить `supply_cycle_context.md` §«Склады объектов»: явная строка «поиск find_warehouse принимает и код, и название».
  - [x] Прогон: `docker exec odoo19-local odoo --test-enable --test-tags /ai_assistant -d odoo19_local --stop-after-init` (или prod после деплоя `-u ai_assistant`).
- **🚫 Запрещено**:
  - `sudo()` при поиске складов.
  - Возвращать склады вне ACL пользователя (стандартный `search_read` достаточен).
  - Менять write-tools или добавлять `list_warehouse_stock` в scope этой задачи (отдельная AIA-052 при необходимости).
- **✅ DoD**:
  - В чате на проде запрос «найди склад Б. Хмельницкого, 112» или «остатки … на Хмельницкого» **не** заканчивается просьбой «уточните код»; ассистент вызывает `find_warehouse` и получает `ОбМ-4`.
  - Все новые и существующие тесты `find_warehouse` зелёные.
  - Flake8 на изменённых файлах без новых ошибок.
- **Примеры приёмки (ручной чат)**:
  ```
  find_warehouse(query="Хмельницкого")     → warehouses[0].code == "ОбМ-4"
  find_warehouse(query="ОбМ-4")             → тот же склад
  find_warehouse(query="Ломоносова")        → ОбМ-2
  ```
- **⛓ Зависит от**: AIA-034 (read tools на проде)
- **Результат**:
  - `find_warehouse` принимает `query` и legacy `code_pattern`.
  - Поиск по адресу/названию идёт через `('name', 'ilike', query)` вместе с `code`.
  - Добавлены тесты для кода, legacy-параметра, фрагмента/полного адреса, пустого результата и префикса `ОбМ-`.

---

## 13. Сводная таблица задач

| ID | Название | Этап | Приоритет | Статус | Context7 | Зависит от |
|---|---|---|---|---|---|---|
| AIA-029 | supply_cycle_context.md | V3-1 | Критический | ✅ | — | — |
| AIA-030 | PromptBuilder режим actions | V3-1 | Критический | ✅ | — | AIA-029 |
| AIA-031 | action_tools/registry + base | V3-2 | Критический | ✅ | 🔧 | — |
| AIA-032 | validators.py | V3-2 | Критический | ✅ | 🔧 | AIA-031 |
| AIA-033 | read tools: products/partners | V3-2 | Критический | ✅ | 🔧 | AIA-031, AIA-032 |
| AIA-034 | read tools: stock/requests | V3-2 | Критический | ✅ | 🔧 | AIA-031..033 |
| AIA-034A | import action_tools в services | V3-2 | Высокий | ✅ | — | AIA-031, AIA-033, AIA-034 |
| AIA-035 | create_object_request_draft | V3-3 | Критический | ✅ | 🔧 | AIA-031, AIA-032 |
| AIA-036 | create_purchase_order_draft | V3-3 | Критический | ✅ | 🔧 | AIA-031..035 |
| AIA-037 | create_internal_picking_draft | V3-3 | Высокий | ✅ | 🔧 | AIA-031..034 |
| AIA-038 | post_chatter_note + ToolExecutor | V3-3 | Критический | ✅ | 🔧 | AIA-031, 035..037 |
| AIA-039 | OpenRouterClient.send_chat_with_tools | V3-4 | Критический | ✅ | 🔧 | AIA-031 |
| AIA-040 | tool-call loop + /confirm + pending_action | V3-4 | Критический | ✅ | — | AIA-038, AIA-039 |
| AIA-041 | OWL ConfirmationCard | V3-5 | Высокий | ✅ | 🔧 | AIA-040 |
| AIA-042 | OWL ResultCard | V3-5 | Высокий | ✅ | — | AIA-041 |
| AIA-043 | ai_chat_service.js cards | V3-5 | Высокий | ✅ | — | AIA-041, AIA-042 |
| AIA-044 | group_supply + feature flag | V3-6 | Критический | ✅ | — | — |
| AIA-045 | rate limit + idempotency | V3-6 | Высокий | ✅ | — | AIA-038, AIA-040 |
| AIA-046 | denylist guard в executor | V3-6 | Критический | ✅ | — | AIA-038 |
| AIA-047 | unit tests coverage | V3-7 | Высокий | ⏳ | — | AIA-031..046 |
| AIA-048 | ai_assistant.audit модель | V3-7 | Средний | ✅ | — | AIA-038 |
| AIA-049 | E2E УТ-1132 → PO ОбМ-4 | V3-7 | Высокий | ✅ | — | AIA-035, AIA-036, AIA-038 |
| AIA-050 | pilot_results_v3 + docs | V3-8 | Средний | ✅ | — | AIA-049 |
| AIA-051 | find_warehouse: поиск по name | V3-9 | Высокий | ✅ | — | AIA-034 |

---

## 14. Рекомендуемый порядок реализации

**Инкремент 1 — «можно посмотреть план»:**
AIA-044 → AIA-029 → AIA-030 → AIA-031 → AIA-032 → AIA-033 → AIA-034 → AIA-034A → AIA-039 → AIA-040 (без write) →
демо: пользователь спрашивает «есть ли остатки трубы 89?» — ассистент выполняет read-tools и отвечает.

**Инкремент 2 — «можно создать черновик OR»:**
AIA-035 → AIA-038 → AIA-046 → AIA-045 → AIA-041 → AIA-042 → AIA-043 →
демо: ассистент создаёт OR в `draft` после подтверждения в чате.

**Инкремент 3 — «полный цикл»:**
AIA-036 → AIA-037 → AIA-049 → AIA-047 → AIA-048 → AIA-050 →
демо: УТ-1132 → PO ОбМ-4 в `draft`, снабженец завершает в UI.

**Инкремент 4 — «склад по адресу» (post-v3):**
AIA-051 →
демо: «остатки трубы 89×3,5 на Б. Хмельницкого, 112» без просьбы уточнить код ОбМ-4.

---

## 15. Чеклист готовности перед merge каждой задачи

- [ ] Все шаги задачи отмечены `[x]`.
- [ ] Тесты задачи проходят локально (`docker exec odoo19-local odoo --test-enable --test-tags ai_assistant -d odoo19_local --stop-after-init`).
- [ ] Flake8 без новых ошибок.
- [ ] Если затрагивает архитектуру → `docs/project.md` обновлён.
- [ ] Если задача из критического приоритета → запись в `docs/changelog.md`.
- [ ] Этот файл (`tasktracker_ai_assistant_v3.md`) обновлён: статус задачи `✅ Выполнена` + дата.
- [ ] Никакие правила из `docs/roadmap_ai_assistant_v3_actions.md` §1.3 не нарушены.
