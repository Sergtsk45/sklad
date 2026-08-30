# Roadmap: AI-ассистент v3 — Actions (исполнение из чата в Odoo)

**Дата:** 2026-05-23
**Статус:** Проект (к реализации)
**Базируется на:**
- `custom_addons/ai_assistant/` v2 (AIA-001 — AIA-028, Vision + Knowledge готовы)
- `custom_addons/object_request/` v19.0.1.1.0 (OR/выдача/закупка, wizards готовы)
- `custom_addons/custom_product_search/` (`ai_search_products()`)
- `docs/instruction-warehouse-supply-cycle.md` (целевой процесс)
- `docs/technical-debt.md` (TD-001 / TD-002 / TD-003 — ограничения)
- `docs/datamodelspecobjectrequest.md` (модель `object.request`)

**Связанный tasktracker:** [`tasktracker_ai_assistant_v3.md`](tasktracker_ai_assistant_v3.md)

---

## 0. Как пользоваться этим документом (для агента в терминале)

Этот roadmap — единственный «источник правды» для разработки v3. Любой агент (Cursor / CLI / другой) перед началом любой задачи должен:

1. Прочитать **§1 (цели и границы)** — чтобы не вылезать за scope.
2. Прочитать **§2 (allowlist/denylist tools)** — это контракт безопасности, его нельзя нарушать.
3. Найти в **`tasktracker_ai_assistant_v3.md`** свою задачу (AIA-029…AIA-050) и прочитать её **полностью**.
4. Подтянуть указанные **«Контекст»** файлы (через Read).
5. Где задача помечена **🔧 Context7** — вызвать Context7 MCP для актуальной документации **до** кодинга.
6. Соблюдать стандарты из `CLAUDE.md` (snake_case, ранние return, длина методов, тесты).

### Ключевые контекстные пути

| Зачем | Путь |
|---|---|
| Архитектура чата (v1/v2) | `custom_addons/ai_assistant/` |
| Контроллер чата | `custom_addons/ai_assistant/controllers/chat_controller.py` |
| OpenRouter клиент | `custom_addons/ai_assistant/services/openrouter_client.py` |
| Prompt builder | `custom_addons/ai_assistant/services/prompt_builder.py` |
| Response guard | `custom_addons/ai_assistant/services/response_guard.py` |
| Knowledge base | `custom_addons/ai_assistant/static/knowledge/` |
| Модуль требований | `custom_addons/object_request/` |
| Wizard закупки (образец логики) | `custom_addons/object_request/wizards/purchase_wizard.py` |
| Wizard выдачи (образец логики) | `custom_addons/object_request/wizards/issue_preview_wizard.py` |
| Поиск товаров для AI | `custom_addons/custom_product_search/models/product_product.py::ai_search_products` |
| Бизнес-процесс (allowlist) | `docs/instruction-warehouse-supply-cycle.md` §3, §8 |
| Запреты | `docs/instruction-warehouse-supply-cycle.md` §10, `docs/technical-debt.md` TD-003 |
| Модель `object.request` | `docs/datamodelspecobjectrequest.md` |

### Когда использовать Context7

🔧 **Обязательно** Context7-запросы перед задачами:

- **OpenRouter Function Calling / Tools API** — для AIA-031, AIA-032 (формат `tools`, обработка `tool_calls`, parallel tools, finish_reason). Используется библиотекой: `openrouter` / `openai-compatible function calling`.
- **OpenAI Python SDK function calling** (как референс схемы) — Odoo шлёт сырые HTTP, но схема `tools[]` совместима с OpenAI; нужны актуальные правила JSON Schema 2020-12 для tool parameters.
- **Odoo 19 ORM** (`stock.picking`, `purchase.order`, `stock.move.line`, `mail.thread.message_post`, `ir.config_parameter`) — для AIA-033…AIA-038. **Только методы**, без `state=done`, без `button_validate`/`button_confirm` в этом релизе.
- **OWL 2 / Odoo 19 web framework** — для AIA-041, AIA-042 (кнопки подтверждения и карточки результатов в чате).
- **JSON Schema (draft 2020-12)** — для AIA-031 (валидация аргументов tools перед вызовом).

🚫 **Не нужен** Context7 для:

- работы внутри уже существующего кода ассистента (он в репо);
- bash/docker команд (есть в `CLAUDE.md`);
- знания об инструкции снабжения (она в репо).

---

## 1. Цель и границы v3

### 1.1 Цель

Дать AI-ассистенту в Odoo (модуль `ai_assistant`) возможность **выполнять ограниченный набор действий** из инструкции `instruction-warehouse-supply-cycle.md` **прямо из чата**, без перехода в основной UI на этапе подготовки документов:

- создавать **черновики** `object.request`, `purchase.order`, `stock.picking` (incoming/internal);
- наполнять строки документов с правильным `picking_type_id` склада объекта;
- искать остатки и товары для решения «с базы / закупка»;
- логировать действия в chatter создаваемых записей.

### 1.2 Что **остаётся** только консультацией

- Любые вопросы по интерфейсу/документации Odoo (как было в v1/v2).
- Подсказки «как сделать в UI».

### 1.3 Что **не делаем** в v3 (явно за границей)

| Запрет | Почему | Где зафиксировано |
|---|---|---|
| **`button_confirm`** на `purchase.order` через AI | TD-003 не закрыт | `docs/technical-debt.md` TD-003 |
| **`button_validate`** на `stock.picking` через AI | TD-003 не закрыт; «остатки только через Validate в UI» | `instruction-warehouse-supply-cycle.md` §8.1, §10 |
| **`update_record({state:'done'})`** на pickings | даёт «done, но quants=0» | `instruction-warehouse-supply-cycle.md` §8.2 |
| Использование **инвентаризации** (`stock.quant.write` / `stock.quant.action_apply_inventory`) | прямой запрет процесса | `instruction-warehouse-supply-cycle.md` §3.2 |
| Создание **vendor bill** (`account.move`) | оплата ведётся в **1С** | `instruction-warehouse-supply-cycle.md` §3.2, §3.3 |
| Любые операции с `res.users`, `res.groups`, `ir.model.*`, `ir.ui.*` | вне scope | этот документ §2 |
| Пересчёт **кг→м** в плане закупки | workflow рассчитывает метры до подтверждения, user approval остаётся обязательным | `docs/technical-debt.md` TD-002 |

### 1.4 Критерии приёмки v3

| # | Критерий |
|---|---|
| К1 | Пользователь группы «AI Assistant Supply» в чате просит «создай PO по счёту УТ-1132 на ОбМ-4», ассистент показывает план, после подтверждения создаёт **PO в `draft`** на `picking_type_id` ОбМ-4 с `origin = OR/…`, `partner_ref = УТ-1132`, строками в метрах. |
| К2 | Ассистент **никогда** не вызывает `button_confirm`/`button_validate` и не пишет `state` напрямую. Это покрыто тестом. |
| К3 | Все write-операции ассистента логируются в `mail.thread` созданной записи через `message_post`. |
| К4 | Пользователь без группы Supply видит ассистента только в режиме консультации (старое поведение v2). |
| К5 | Feature flag `ai_assistant.actions_enabled` (default: **off**) — на проде включается админом явно. |
| К6 | Все tools имеют JSON Schema; ассистент не может вызвать tool с произвольной моделью/полем. |
| К7 | Подтверждение write-операций — через **кнопку в UI чата** (не только «да» в тексте). |
| К8 | E2E-тест: OR/2026/05/0007 → PO черновик на ОбМ-4 → ссылка возвращается в чат. |

---

## 2. Allowlist и Denylist tools

Это **контракт безопасности** — он же и список tools, которые увидит LLM в `tools[]`.

### 2.1 Read tools (без подтверждения)

| Tool | Модель | Метод | Назначение |
|---|---|---|---|
| `search_products` | `product.product` | `ai_search_products(query, limit)` | поиск номенклатуры по нормализованному имени |
| `find_product_by_id` | `product.product` | `read([id], fields)` | детали товара (UoM, is_storable, category) |
| `search_stock_quants` | `stock.quant` | `search_read(domain, fields)` | остатки по `product_id` и складам, с фильтром «положительные» |
| `find_warehouse` | `stock.warehouse` | `search_read` по `code` или `name` | резолв склада объекта в id и `in_type_id` |
| `find_picking_type` | `stock.picking.type` | `search_read` (`code in (incoming, internal)`, фильтр по `warehouse_id`) | resolve конкретного типа операции |
| `find_partner` | `res.partner` | `search_read` (`supplier_rank>0` для поставщиков) | поставщик по ИНН/имени |
| `find_object_request` | `object.request` | `search_read` по `name` / `project_id` / `state` | поиск OR пользователем |
| `read_object_request` | `object.request` | `read([id], fields)` + строки | полный контекст OR для разбора |

### 2.2 Write tools (требуют подтверждения через UI-кнопку)

| Tool | Создаёт | Ограничения |
|---|---|---|
| `create_object_request_draft` | `object.request` (state=`draft`) | обязательно `project_id`, `need_date`, ≥1 строка |
| `update_object_request_line` | `object.request.line` | только в OR со `state in ('draft','in_progress')` |
| `create_purchase_order_draft` | `purchase.order` (state=`draft`) | обязательно `partner_id`, `picking_type_id` склада ОбМ-*, `origin`, `partner_ref`, ≥1 строка |
| `add_purchase_order_line` | `purchase.order.line` | только в PO со `state='draft'` |
| `create_internal_picking_draft` | `stock.picking` (state=`draft`) типа internal | `location_id` базы → `location_dest_id` ОбМ-N; `origin` = OR |
| `add_picking_move` | `stock.move` + `stock.move.line` | только в picking `state in ('draft','confirmed','assigned')` |
| `post_chatter_note` | `mail.message` (subtype=note) | только на моделях из allowlist |

### 2.3 Жёсткий denylist (LLM не получает эти tools; tool_executor выбрасывает `AccessControlError`)

- `*.button_confirm`, `*.button_validate`, `*.action_done`, `*.action_post`.
- `stock.quant.write`, `stock.quant.create`, `stock.quant.unlink`.
- `stock.inventory.*`, `stock.quant.action_apply_inventory`.
- `account.move.*`, `account.payment.*`.
- `res.users.*`, `res.groups.*`, `ir.model.*`, `ir.ui.*`, `ir.config_parameter.write/create/unlink`.
- Любая запись `state` напрямую через `write({'state': ...})`.
- `unlink` на проведённых документах.

### 2.4 Правила tool_executor

1. **ACL Odoo соблюдается всегда** — вызовы идут через `request.env[...]` (не `sudo()`), от имени текущего пользователя.
2. **Проверка группы**: write-tools требуют `ai_assistant.group_ai_assistant_supply`.
3. **Whitelist полей**: для каждого write-tool — явный список разрешённых полей (нельзя «протащить» `state`, `company_id` через `**kwargs`).
4. **Pre-condition валидаторы** (Python, до вызова ORM):
   - `picking_type_id.warehouse_id.code` начинается с `ОбМ-` для `create_purchase_order_draft`;
   - `product_id.is_storable=True` для строк, попадающих на склад;
   - `state` целевой записи в разрешённом множестве.
5. **Post-action хук**: после `create()` — обязательный `message_post` через `post_chatter_note` (имя пользователя + сводка действия).
6. **Лимиты**: не более 1 write-tool на одно сообщение пользователя без явного подтверждения; не более 5 итераций tool-call цикла.

---

## 3. Архитектурные изменения

### 3.1 Картинка «было → станет»

```
v2 (сейчас):                          v3 (целевое):

POST /ai_assistant/chat               POST /ai_assistant/chat
  └─ ContextResolver                    ├─ ContextResolver
  └─ KnowledgeProviderV2                ├─ KnowledgeProviderV2 + supply context
  └─ PromptBuilder (system v2)          ├─ PromptBuilder v3 (actions mode)
  └─ OpenRouterClient.send_chat          ├─ OpenRouterClient.send_chat_with_tools
        (messages only)                   │     ▲             │
  └─ ResponseGuard (filter)               │     │             ▼
                                          │     │   ToolExecutor
                                          │     │     ├─ search_products
                                          │     │     ├─ search_stock_quants
                                          │     │     ├─ find_warehouse
                                          │     │     ├─ create_purchase_order_draft
                                          │     │     └─ post_chatter_note
                                          │     │             │
                                          │     └─── tool_results
                                          └─ ResponseGuard v3 (actions-aware)

Confirmation flow:
  user msg → LLM proposes plan → frontend renders "Подтвердить/Отмена" card
                                       │
                                       └── user clicks → POST /ai_assistant/confirm
                                                          └─ ToolExecutor (write)
```

### 3.2 Новые / изменённые файлы

```
custom_addons/ai_assistant/
  __manifest__.py                              # +depends: stock, purchase, object_request, custom_product_search, mail
  controllers/
    chat_controller.py                         # MODIFIED: + tool-call loop, + /confirm endpoint
  services/
    openrouter_client.py                       # MODIFIED: + send_chat_with_tools, parse tool_calls
    prompt_builder.py                          # MODIFIED: + actions mode system prompt
    response_guard.py                          # MODIFIED: + actions-aware режим
    action_tools/                              # NEW package
      __init__.py
      registry.py                              # реестр tools, JSON Schema, метаданные
      base.py                                  # AbstractTool, AbstractWriteTool
      read_tools.py                            # search_products, search_stock_quants, find_*
      write_tools.py                           # create_*, add_*, post_chatter_note
      validators.py                            # pre-condition Python-валидаторы
      executor.py                              # ToolExecutor с ACL и аудитом
    pending_action.py                          # NEW: in-memory очередь подтверждаемых действий
  models/
    ai_assistant_config.py                     # MODIFIED: + actions_enabled, max_tool_iters
    ai_assistant_audit.py                      # NEW: модель аудита tool-вызовов (опционально, см. AIA-048)
  security/
    security_groups.xml                        # MODIFIED: + group_ai_assistant_supply
    ir.model.access.csv                        # MODIFIED: + ai_assistant.audit
  static/
    src/js/
      ai_chat_service.js                       # MODIFIED: + tool_calls rendering, confirm card
      ai_chat_actions.js                       # NEW: ConfirmationCard, ResultCard OWL компоненты
    src/xml/
      ai_chat_widget.xml                       # MODIFIED: + слоты для карточек
    src/scss/
      ai_chat_widget.scss                      # MODIFIED: + стили карточек
    knowledge/
      supply_cycle_context.md                  # NEW: сжатая инструкция для system prompt
  tests/
    test_action_tools_registry.py              # NEW
    test_read_tools.py                         # NEW
    test_write_tools.py                        # NEW
    test_tool_executor_security.py             # NEW: запрещённые операции
    test_openrouter_tools.py                   # NEW: парсинг tool_calls
    test_prompt_builder_v3.py                  # NEW
    test_e2e_supply_cycle.py                   # NEW: E2E УТ-1132
```

### 3.3 Слои и зависимости (SRP)

```
Controllers      → chat_controller (HTTP)
Application      → tool_executor, pending_action, openrouter_client
Domain           → action_tools/* (read_tools, write_tools, registry, base, validators)
Infrastructure   → ORM Odoo, OpenRouter HTTP
```

`action_tools/*` **не знает** про OpenRouter и HTTP. `openrouter_client` **не знает** про конкретные tools — только про их регистрацию (см. AIA-031).

---

## 4. Промпт-инженерия v3

### 4.1 Новый system prompt (дополнение к v2)

В `prompt_builder.py` — режимы:

- `mode='consult'` (старый, по умолчанию для пользователей без группы Supply).
- `mode='actions'` (новый, для группы Supply при `actions_enabled=True`).

Дополнение к system prompt в `actions` режиме:

```
РЕЖИМ ДЕЙСТВИЙ.

Ты можешь подготавливать ЧЕРНОВИКИ документов снабжения в Odoo:
- object.request (требование прораба)
- purchase.order (черновик заказа поставщику)
- stock.picking (черновик внутреннего перемещения или incoming)

ОБЯЗАТЕЛЬНЫЕ ПРАВИЛА:
1. Перед любым write-tool сначала сформулируй ПЛАН в формате:
   "Я создам:
    - <модель>: <поля>
    - …
    Подтверди для выполнения."
2. После плана дождись сигнала подтверждения от системы (не от текста пользователя).
3. НЕ вызывай button_confirm, button_validate, не пиши state, не используй инвентаризацию.
4. PO всегда с picking_type_id склада объекта (ОбМ-1…ОбМ-N), origin=OR/…,
   partner_ref=номер счёта поставщика (для 1С).
5. Для труб — UoM «метр». Если счёт пришёл в кг/тоннах/хлыстах, workflow
   показывает пересчёт в метры и записывает только подтверждённый результат.
6. После успешного write-tool вызывай post_chatter_note с пометкой
   «создано AI-ассистентом по запросу <user>» в записи.

ОГРАНИЧЕНИЯ:
- Bull bill, оплаты, бухгалтерия — в 1С, не в Odoo.
- Confirm PO и Validate приёмки — выполняет снабженец в UI.
```

### 4.2 Knowledge: `supply_cycle_context.md`

Сжатая (≤ 6 КБ) версия `docs/instruction-warehouse-supply-cycle.md`:

- роли;
- маппинг склад → `picking_type_id` (ОбМ-1…4, БАЗА, Офис);
- формулы пересчёта (кг/т → м);
- denylist операций;
- пример «правильного» плана PO.

Подгружается `KnowledgeProviderV2` всегда, когда модуль контекста = `purchase` / `stock` / `object_request` **и** `mode='actions'`.

### 4.3 Изменения в `ResponseGuard`

В `actions` режиме — фильтр «я создам/выполнил» **отключается** (это валидное поведение). Вместо него:

- режется упоминание `state=`, `button_confirm`, `button_validate`, `inventory.action_apply`;
- режется упоминание `account.move`, `account.payment`;
- prompt injection защита остаётся.

---

## 5. OpenRouter tools / function calling

### 5.1 Формат запроса (🔧 Context7)

OpenRouter принимает tools в OpenAI-совместимом формате:

```json
{
  "model": "google/gemini-2.0-flash-001",
  "messages": [...],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search_stock_quants",
        "description": "Поиск остатков по товару на складах…",
        "parameters": {
          "type": "object",
          "properties": {
            "product_id": {"type": "integer"},
            "warehouse_codes": {
              "type": "array",
              "items": {"type": "string"}
            },
            "only_positive": {"type": "boolean", "default": true}
          },
          "required": ["product_id"],
          "additionalProperties": false
        }
      }
    }
  ],
  "tool_choice": "auto"
}
```

🔧 **Context7-задача** (AIA-031): сверить актуальную спецификацию OpenRouter и OpenAI Python SDK function calling (parallel tool calls, формат `tool_calls[]` в response, `finish_reason='tool_calls'`).

### 5.2 Цикл обработки

```
1. Send: messages + tools + tool_choice='auto'
2. Receive: assistant message with tool_calls=[{id, name, arguments}]
3. Determine: read tools → execute immediately
              write tools → save to pending_action, return ConfirmationCard, STOP
4. Append tool results as role='tool' messages, loop GOTO 1
5. Max iterations: 5 (анти-цикл)
6. finish_reason='stop' → final answer to user
```

### 5.3 Лимиты OpenRouter

- Размер `tools[]` влияет на стоимость токенов: 8 tools × ~150 токенов описания ≈ 1.2K дополнительных input tokens на каждый вызов.
- Для текстовой модели `google/gemini-2.0-flash-001` — function calling **поддерживается** (по состоянию на 2026); в задаче AIA-031 — проверить.

---

## 6. UX в чате (frontend)

### 6.1 Поток сообщений

```
[User] Создай PO по счёту УТ-1132 на ОбМ-4 для ООО ПроМеталл
   ↓
[Assistant text] Сейчас проверю остатки и подберу склад…
[Tool call: search_stock_quants] ← без UI, просто индикатор "..."
[Tool result]
[Assistant text] Нашёл. Готов создать черновик:
[ConfirmationCard]
   ┌────────────────────────────────────────┐
   │ Создать purchase.order:                │
   │   Поставщик: ООО ПроМеталл             │
   │   Склад: Б. Хмельницкого 112 (ОбМ-4)   │
   │   Origin: OR/2026/05/0007              │
   │   Partner ref: УТ-1132                 │
   │   Строк: 6 (1098 м труб)               │
   │ [ Подтвердить ]   [ Отменить ]         │
   └────────────────────────────────────────┘
   ↓ (клик)
[POST /ai_assistant/confirm]
   ↓
[ResultCard]
   ┌────────────────────────────────────────┐
   │ ✅ Создан P00012                       │
   │   ссылка → /odoo/purchase/12           │
   │ Следующий шаг: Confirm в UI снабженца. │
   └────────────────────────────────────────┘
```

### 6.2 OWL компоненты (🔧 Context7)

- `ConfirmationCard` — карточка с описанием плана и кнопками. Использует Odoo 19 `Dialog` или inline-карточку (см. AIA-041).
- `ResultCard` — карточка с ссылкой на запись (`/odoo/<model>/<id>` — стандартный паттерн Odoo 19).

🔧 **Context7-задача** (AIA-041): сверить актуальные OWL 2 паттерны Odoo 19 для inline-карточек в backend chat-виджете (slots, t-component).

---

## 7. Безопасность

### 7.1 Группы

```xml
<record id="group_ai_assistant_supply" model="res.groups">
    <field name="name">Снабжение (actions)</field>
    <field name="sequence">15</field>
    <field name="privilege_id" ref="res_groups_privilege_ai_assistant"/>
    <field name="implied_ids" eval="[(4, ref('group_ai_assistant_user')),
                                      (4, ref('purchase.group_purchase_user')),
                                      (4, ref('stock.group_stock_user'))]"/>
</record>
```

### 7.2 Feature flag

`ir.config_parameter` `ai_assistant.actions_enabled`:
- `'0'` (default) — режим только консультация для всех;
- `'1'` — actions доступны пользователям группы Supply.

В UI Settings — переключатель с предупреждением «требует группы снабжения».

### 7.3 Аудит

Каждый write-tool вызывает `post_chatter_note`:

```
[AI Assistant] Создано пользователем admin через AI-чат
Tool: create_purchase_order_draft
Args: {partner_id: 19, picking_type_id: 8, origin: 'OR/2026/05/0007', ...}
```

Опционально (AIA-048) — отдельная модель `ai_assistant.audit` для централизованного журнала.

### 7.4 Rate limit

- 30 read-tool вызовов / минуту / пользователь;
- 5 write-tool вызовов / минуту / пользователь;
- 1 одновременная незавершённая `pending_action` на пользователя (новая отменяет старую).

---

## 8. Этапы (с привязкой к задачам AIA-029…AIA-050)

| Этап | Задачи | Что получаем |
|---|---|---|
| **V3-1 Knowledge + Prompt** | AIA-029, AIA-030 | supply_cycle_context + новый system prompt в режиме actions |
| **V3-2 Tool layer (домен)** | AIA-031, AIA-032, AIA-033, AIA-034 | registry, JSON schemas, read tools |
| **V3-3 Write tools + executor** | AIA-035, AIA-036, AIA-037, AIA-038 | create_object_request_draft, create_purchase_order_draft, internal picking, post_chatter_note |
| **V3-4 OpenRouter integration** | AIA-039, AIA-040 | send_chat_with_tools, цикл обработки tool_calls |
| **V3-5 Frontend UX** | AIA-041, AIA-042, AIA-043 | ConfirmationCard, ResultCard, /confirm endpoint |
| **V3-6 Безопасность** | AIA-044, AIA-045, AIA-046 | группа Supply, feature flag, rate limit |
| **V3-7 Тесты и E2E** | AIA-047, AIA-048, AIA-049 | unit + e2e УТ-1132 → PO на ОбМ-4 |
| **V3-8 Документация и пилот** | AIA-050 | pilot_results_v3.md, обновление инструкции |

Детали по каждой задаче — в `docs/tasktracker_ai_assistant_v3.md`.

---

## 9. Риски и компромиссы

| Риск | Митигация |
|---|---|
| LLM «обходит» подтверждение и вызывает write-tool сам | Архитектурное решение: write-tools **никогда** не выполняются в первом цикле — только через `/confirm` endpoint. Это код, а не правило в промпте. |
| LLM придумывает несуществующий `picking_type_id` | Pre-condition валидатор отвергает; в промпте — обязательный шаг «сначала `find_warehouse`/`find_picking_type`». |
| Парсинг счёта в кг/тонн → метры с ошибкой → неверное `product_qty` | Пересчёт выполняется workflow до подтверждения; в PO попадает только подтверждённое значение, а при отсутствии `kg_per_meter` или длины хлыста workflow даёт ошибку. |
| Token blow-up при больших OR | `read_object_request` ограничивает выдачу 50 строк, далее пагинация. |
| Дрейф actions vs consult режимов | `prompt_builder` явно проверяет группу и `actions_enabled`; нет «незаметного» переключения. |
| Параллельные tool_calls создают дубликаты PO | Pending_action хранит idempotency key (hash от плана); повторный confirm на тот же key — no-op. |

---

## 10. Зависимости и порядок установки

```
ai_assistant (v3) depends on:
  - base, web, base_setup (уже)
  - mail (для message_post)
  - stock (для stock.picking/move/quant)
  - purchase (для purchase.order)
  - product (через stock)
  - object_request (для OR write-tools)
  - custom_product_search (для ai_search_products)
```

Команда обновления:

```bash
docker exec odoo19-local odoo -u ai_assistant -d odoo19_local --stop-after-init
```

Тесты:

```bash
docker exec odoo19-local odoo --test-enable --test-tags ai_assistant -d odoo19_local --stop-after-init
```

---

## 11. Что НЕ входит в v3 (отложено)

- Закрытие TD-003 (`button_confirm`/`button_validate` через AI) — отдельный roadmap v4.
- Дополнительная чистка справочника UoM и заполнение `kg_per_meter` по всей категории «Трубы» (TD-002 follow-up).
- Голосовой ввод действий.
- Multi-step plan execution без подтверждений между шагами.
- Сохранение истории в БД (остаётся sessionStorage).
- Telegram/мобильный клиент.
- Список **всех** позиций на складе без указания товара — отдельный tool (см. backlog **AIA-052** в трекере).

### 11.1. Post-v3 backlog (v3.1)

| ID | Улучшение | Статус |
|---|---|---|
| **AIA-051** | `find_warehouse`: поиск по `name` (`ilike`), не только `code` | ✅ выполнено, см. [`tasktracker_ai_assistant_v3.md`](tasktracker_ai_assistant_v3.md) |
| **AIA-052** | `get_warehouse_stock_link` — ссылка на отфильтрованный отчёт остатков по складу (`/odoo/stock-locations?...`) | ⏳ запланирована |
| **AIA-053** | `get_navigation_link` — навигационные ссылки в consult-режиме (Вариант 4: гибрид каталог + tool + knowledge + промпт) | ✅ выполнена (backend/knowledge MVP), см. [`tasktracker_ai_assistant_v3.md`](tasktracker_ai_assistant_v3.md) §AIA-053 |

---

## 12. История изменений

| Дата | Версия | Изменение |
|---|---|---|
| 2026-05-23 | 0.1 | Первая версия roadmap v3: actions в `ai_assistant`, без TD-003 |
| 2026-05-24 | 0.2 | Backlog AIA-051: `find_warehouse` по name |
| 2026-05-24 | 0.3 | AIA-051 выполнена: `find_warehouse(query)` ищет по коду и названию склада |
| 2026-05-24 | 0.4 | Backlog AIA-053: навигационные ссылки в consult-режиме (`get_navigation_link`, Вариант 4 — гибрид) |
| 2026-05-24 | 0.5 | AIA-053 выполнена: `NAVIGATION_CATALOG`, read-tool `get_navigation_link`, `navigation_map.md`, правила промпта и тесты |
