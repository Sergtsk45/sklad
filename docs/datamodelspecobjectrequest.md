---
title: Data Model Spec - Требование на комплектацию объекта
created: 2026-03-15
status: Draft for implementation
scope: Odoo 19, models, fields, relations, constraints
---

## Цель документа

Зафиксировать модель данных для кастомного Odoo 19 модуля `Требование на комплектацию объекта`.

Документ описывает:

- состав моделей;
- набор полей;
- типы полей Odoo;
- связи между моделями;
- вычисляемые поля;
- ограничения и SQL/python constraints;
- наследование стандартных моделей Odoo;
- рекомендации для MVP и для этапа 2.

Этот документ является продолжением:

- `docs/roadmapobjectrequest.md`
- `docs/functionalspecobjectrequest.md`

## Базовые решения

## 1. Решение по модели объекта

Ранее выбор между `project.project` и отдельной моделью был открыт.  
Для **MVP** рекомендуется использовать **отдельную легковесную модель объекта**, а не зависеть от `project.project`.

### Рекомендуемая модель

- `object.request.project`

### Почему отдельная модель лучше для MVP

- модуль не зависит от приложения `Project`;
- объект строительства в твоем процессе не обязан быть проектом Odoo в полном смысле;
- проще ввести собственные поля:
  - код объекта
  - адрес
  - заказчик
  - дата начала/окончания
  - активность
- проще потом связать с `project.project`, если это потребуется.

### Допустимый компромисс

Если позже понадобится интеграция с приложением `Project`, можно добавить:

- `project_project_id = fields.Many2one('project.project')`

Но в первом релизе это лучше не делать обязательным.

## 2. Выбор модели пользователя

Для ролевых полей рекомендуется использовать:

- `res.users`

Поля:

- `foreman_user_id`
- `buyer_user_id`
- `warehouse_user_id`
- `approver_user_id`

### Почему не `hr.employee`

- HR-модуль сейчас не является базовой зависимостью;
- права доступа и реальные действия удобнее привязывать к пользователю Odoo;
- при необходимости позже можно добавить связанные поля на `hr.employee`.

## 3. Товары и поставщики

Используются стандартные сущности Odoo:

- товар: `product.product`
- шаблон товара: `product.template`
- поставщик: `res.partner`
- supplier info / vendor info: `product.supplierinfo`

Модуль не должен дублировать их собственным справочником.

## Зависимости модуля

Для data model spec предполагаются зависимости:

- `base`
- `mail`
- `contacts`
- `stock`
- `purchase`
- `product`

Опционально позже:

- `project`
- `hr`

## Набор моделей

Рекомендуемый состав:

1. `object.request.project` - справочник объектов
2. `object.request` - шапка документа требования
3. `object.request.line` - строки документа
4. `object.request.import.wizard` - transient wizard для Excel
5. `object.request.line.stock` - распределение строки по складам
6. `object.request.issue.preview.wizard` - transient wizard предпросмотра выдач по складам
7. `object.request.purchase.wizard` - transient wizard для подготовки закупки
8. расширение `stock.picking`
9. расширение `purchase.order`

## Модель 1. `object.request.project`

### Назначение

Справочник объектов строительства / проектов, к которым относятся документы требований.

### Технические параметры

- `_name = 'object.request.project'`
- `_description = 'Project Object for Supply Request'`
- `_inherit = ['mail.thread', 'mail.activity.mixin']`
- `_order = 'name asc'`

### Поля

- `name = fields.Char(required=True, tracking=True)`
  - отображаемое наименование объекта
- `code = fields.Char(index=True, tracking=True)`
  - внутренний код объекта; генерируется sequence `object.request.project.code` в формате `O001`, `O002`, ...
- `company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)`
- `warehouse_id = fields.Many2one('stock.warehouse', readonly=True, copy=False)`
  - склад объекта, создаётся автоматически при создании объекта
- `partner_id = fields.Many2one('res.partner')`
  - заказчик / контрагент объекта
- `address = fields.Char()`
  - строковый адрес для MVP
- `comment = fields.Text()`
- `active = fields.Boolean(default=True)`
- `request_ids = fields.One2many('object.request', 'project_id')`
- `request_count = fields.Integer(compute='_compute_request_count')`

### Required fields в MVP

- `name`

### Склад объекта

При создании объекта модуль создаёт связанный `stock.warehouse`:

- `name = "{object.name} склад"`
- `code = object.code`
- `company_id = object.company_id`

Склад объекта используется как склад приёмки закупок, создаваемых из требования. При архивации объекта архивируется и склад; при разархивации активность склада восстанавливается.

Переименование `name` и изменение `code` после создания запрещены для обычных пользователей. Администратор может изменить `name`; в этом случае имя связанного склада синхронизируется.

### SQL constraints

- уникальность `code`, если код заполнен

Пример логики:

- `unique(code)` при `code is not null`

### Индексы

- `code`
- `active`

## Модель 2. `object.request`

### Назначение

Главный документ `Требование на комплектацию объекта`.

### Технические параметры

- `_name = 'object.request'`
- `_description = 'Object Supply Request'`
- `_inherit = ['mail.thread', 'mail.activity.mixin']`
- `_order = 'create_date desc, id desc'`
- использовать `ir.sequence` для поля `name`

### Основные поля

- `name = fields.Char(required=True, copy=False, readonly=True, default='New', tracking=True)`
  - номер документа
- `project_id = fields.Many2one('object.request.project', required=True, tracking=True, index=True)`
  - объект
- `foreman_user_id = fields.Many2one('res.users', required=True, tracking=True, index=True)`
  - прораб
- `need_date = fields.Date(required=True, tracking=True, index=True)`
  - дата потребности
- `priority = fields.Selection([
    ('0', 'Низкий'),
    ('1', 'Обычный'),
    ('2', 'Высокий'),
    ('3', 'Критический')
  ], default='1', required=True, tracking=True, index=True)`
- `comment = fields.Text()`
- `state = fields.Selection([
    ('draft', 'Черновик'),
    ('in_progress', 'В работе'),
    ('closed', 'Закрыто'),
    ('cancelled', 'Отменено')
  ], default='draft', required=True, tracking=True, index=True)`

### Склад в шапке

В актуальной multi-warehouse схеме у `object.request` нет полей:

- `warehouse_id`
- `check_warehouse_ids`
- `stock_check_confirmed`

Прораб не выбирает склад при создании требования. Расчёт наличия выполняется автоматически по всем активным складам компании, а план выдачи хранится на уровне `object.request.line.stock`.

### Поля источника импорта

- `source_file_name = fields.Char()`
- `source_file_checksum = fields.Char(index=True)`
- `imported_at = fields.Datetime(readonly=True)`
- `imported_by_user_id = fields.Many2one('res.users', readonly=True)`

### Поля процесса

- `matching_state = fields.Selection([
    ('all_matched', 'Все сопоставлено'),
    ('partial', 'Есть проблемы'),
    ('requires_mapping', 'Требует сопоставления')
  ], compute='_compute_matching_state', store=True, index=True)`

- `approval_state = fields.Selection([
    ('not_required', 'Не требуется'),
    ('stub', 'Заглушка'),
    ('pending', 'Ожидает согласования'),
    ('approved', 'Согласовано'),
    ('rejected', 'Отклонено')
  ], default='stub', tracking=True)`

- `line_ids = fields.One2many('object.request.line', 'request_id', copy=True)`
- `line_count = fields.Integer(compute='_compute_line_count')`

### Агрегатные счетчики

- `line_problem_count = fields.Integer(compute='_compute_line_counters', store=True)`
- `line_matched_count = fields.Integer(compute='_compute_line_counters', store=True)`
- `line_to_issue_count = fields.Integer(compute='_compute_line_counters', store=True)`
- `line_to_buy_count = fields.Integer(compute='_compute_line_counters', store=True)`
- `line_fully_supplied_count = fields.Integer(compute='_compute_line_counters', store=True)`

### Количественные агрегаты

- `qty_total_requested = fields.Float(compute='_compute_qty_totals', store=True)`
- `qty_total_to_issue = fields.Float(compute='_compute_qty_totals', store=True)`
- `qty_total_to_buy = fields.Float(compute='_compute_qty_totals', store=True)`
- `qty_total_issued = fields.Float(compute='_compute_qty_totals', store=True)`

### Связи с документами Odoo

- `issue_picking_ids = fields.Many2many(
    'stock.picking',
    'object_request_stock_picking_rel',
    'request_id',
    'picking_id',
    string='Issue Pickings'
  )`

- `issue_picking_count = fields.Integer(compute='_compute_issue_picking_count')`

- `purchase_order_ids = fields.Many2many(
    'purchase.order',
    'object_request_purchase_order_rel',
    'request_id',
    'purchase_id',
    string='Purchase Orders'
  )`

- `purchase_order_count = fields.Integer(compute='_compute_purchase_order_count')`

### Ролевые поля

- `buyer_user_id = fields.Many2one('res.users', tracking=True)`
  - снабженец, ведущий документ
- `warehouse_user_id = fields.Many2one('res.users', tracking=True)`
  - ответственный кладовщик
- `approver_user_id = fields.Many2one('res.users', tracking=True)`
  - заглушка под согласующего

### Служебные поля

- `company_id = fields.Many2one('res.company', required=True, default=lambda self: self.env.company, index=True)`
- `currency_id = fields.Many2one('res.currency', related='company_id.currency_id', store=True)`
- `active = fields.Boolean(default=True)`

### Required fields в MVP

- `name`
- `project_id`
- `foreman_user_id`
- `need_date`
- `priority`
- `state`
- `company_id`

### Readonly by state

После перехода в `closed` и `cancelled`:

- все бизнес-поля readonly

После перехода в `in_progress`:

- `project_id`
- `foreman_user_id`
- `need_date`

лучше сделать readonly, чтобы документ не менял смысл по ходу обработки.

Состав строк после перехода в `in_progress` (и далее в `closed`/`cancelled`)
фиксируется на сервере и в UI:

- нельзя создавать и удалять `object.request.line`;
- нельзя менять `qty_requested`;
- сопоставление, `qty_to_issue` и `qty_to_buy` остаются доступны в `in_progress`.

Поле `state` не копируется (`copy=False`): дубликат документа всегда стартует
как черновик.

### Python constraints

- документ должен содержать хотя бы одну строку перед переводом в `in_progress`
- документ нельзя закрыть, если есть строки в невалидном состоянии

### SQL constraints

- уникальный номер `name`

### Индексы

- `project_id`
- `state`
- `need_date`
- `priority`
- `matching_state`
- `company_id`

## Модель 3. `object.request.line`

### Назначение

Строка требования на комплектацию объекта.

### Технические параметры

- `_name = 'object.request.line'`
- `_description = 'Object Supply Request Line'`
- `_order = 'request_id, sequence, id'`

### Связь с шапкой

- `request_id = fields.Many2one('object.request', required=True, ondelete='cascade', index=True)`

### Поля импорта

- `sequence = fields.Integer(default=10, index=True)`
  - номер строки / номер п/п
- `source_row_no = fields.Integer(index=True)`
  - реальный номер строки Excel
- `supplier_article = fields.Char(index=True)`
- `name_raw = fields.Char(required=True, index=True)`
- `uom_raw = fields.Char()`
- `qty_requested = fields.Float(required=True, digits='Product Unit of Measure')`
- `price_raw = fields.Float(digits='Product Price')`
- `comment = fields.Text()`
- `supplier_raw = fields.Char(index=True)`

### Поля размещения внутри объекта

- `zone = fields.Char(index=True)`
- `floor = fields.Char(index=True)`
- `section = fields.Char(index=True)`

Для MVP рекомендованы именно `Char`, а не отдельные справочники:

- проще импорт;
- меньше зависимостей;
- позже можно нормализовать в отдельные модели.

### Поля номенклатуры

- `product_id = fields.Many2one('product.product', index=True)`
- `product_tmpl_id = fields.Many2one('product.template', related='product_id.product_tmpl_id', store=True, index=True)`
- `uom_id = fields.Many2one('uom.uom')`
- `preferred_vendor_id = fields.Many2one('res.partner', domain="[('supplier_rank', '>', 0)]", index=True)`
- `allowed_substitute_ids = fields.Many2many(
    'product.product',
    'object_request_line_substitute_rel',
    'line_id',
    'product_id',
    string='Allowed Substitutes'
  )`

### Поля сопоставления

- `matching_required = fields.Boolean(default=False, index=True)`
- `matching_state = fields.Selection([
    ('matched', 'Сопоставлено'),
    ('requires_mapping', 'Требует сопоставления'),
    ('manual_review', 'Требует проверки')
  ], default='matched', required=True, index=True)`
- `matching_note = fields.Text()`
- `manual_vendor_required = fields.Boolean(default=False, index=True)`

### Поля складской и закупочной обработки

- `procurement_mode = fields.Selection([
    ('manual', 'Ручное решение'),
    ('issue', 'Выдать'),
    ('buy', 'Закупить'),
    ('mixed', 'Частично выдать / частично закупить')
  ], default='manual', index=True)`

- `stock_qty_on_hand = fields.Float(digits='Product Unit of Measure')`
- `stock_check_date = fields.Datetime()`
- `qty_to_issue = fields.Float(digits='Product Unit of Measure')`
- `qty_to_buy = fields.Float(digits='Product Unit of Measure')`
- `qty_reserved = fields.Float(digits='Product Unit of Measure')`
- `qty_issued = fields.Float(digits='Product Unit of Measure')`

### Статусы строки

- `line_state = fields.Selection([
    ('draft', 'Черновик'),
    ('requires_mapping', 'Требует сопоставления'),
    ('ready', 'Готово к обработке'),
    ('partially_issued', 'Частично выдано'),
    ('fully_supplied', 'Полностью обеспечено'),
    ('cancelled', 'Отменено')
  ], default='draft', required=True, index=True, tracking=True)`

### Связи со стандартными документами

- `issue_picking_id = fields.Many2one('stock.picking', index=True)`
- `issue_move_id = fields.Many2one('stock.move', index=True)`
- `purchase_order_id = fields.Many2one('purchase.order', index=True)`
- `purchase_order_line_id = fields.Many2one('purchase.order.line', index=True)`

### Служебные поля

- `company_id = fields.Many2one('res.company', related='request_id.company_id', store=True, index=True)`
- `currency_id = fields.Many2one('res.currency', related='request_id.currency_id', store=True)`

### Required fields в MVP

- `request_id`
- `name_raw`
- `qty_requested`

`product_id` не должен быть обязательным, потому что строка может быть импортирована как несопоставленная.

### Compute fields

Рекомендуемые вычисляемые поля:

- `display_name`
  - через Odoo default
- `has_substitutes = fields.Boolean(compute='_compute_has_substitutes')`
- `is_fully_matched = fields.Boolean(compute='_compute_matching_flags', store=True)`
- `is_ready_for_issue = fields.Boolean(compute='_compute_readiness_flags', store=True)`
- `is_ready_for_purchase = fields.Boolean(compute='_compute_readiness_flags', store=True)`

### Onchange поведение

- при выборе `product_id`:
  - если `uom_id` пустой, подставить UoM товара
  - если `preferred_vendor_id` пустой, можно предложить первого vendor info, но не сохранять насильно
- при изменении `qty_requested`:
  - валидировать `qty_to_issue` и `qty_to_buy`
- при изменении `qty_to_issue` / `qty_to_buy`:
  - обновлять `procurement_mode`

### SQL constraints

- `qty_requested > 0`
- `qty_to_issue >= 0`
- `qty_to_buy >= 0`
- `qty_issued >= 0`

### Python constraints

- `qty_to_issue + qty_to_buy <= qty_requested`
- нельзя указать `preferred_vendor_id`, если поставщик не vendor
- `issue_move_id` не должен принадлежать другому документу

### Индексы

- `request_id`
- `product_id`
- `preferred_vendor_id`
- `line_state`
- `matching_required`
- `matching_state`
- `manual_vendor_required`
- `source_row_no`

## Модель 4. `object.request.import.wizard`

### Назначение

Transient model для загрузки Excel и создания документа.

### Технические параметры

- `_name = 'object.request.import.wizard'`
- `_description = 'Object Request Import Wizard'`
- transient model

### Поля

- `file = fields.Binary(required=True)`
- `file_name = fields.Char(required=True)`
- `project_id = fields.Many2one('object.request.project', required=True)`
- `foreman_user_id = fields.Many2one('res.users', required=True)`
- `need_date = fields.Date(required=True)`
- `priority = fields.Selection([...], required=True, default='1')`
- `comment = fields.Text()`
- `parse_result_json = fields.Text(readonly=True)`
- `line_preview_count = fields.Integer(readonly=True)`
- `problem_line_count = fields.Integer(readonly=True)`

### Примечание

Wizard является UI-моделью и не должен хранить результат как бизнес-истину.  
После завершения импорта данные должны жить только в `object.request` и `object.request.line`.

## Модель 4a. `object.request.line.stock`

### Назначение

Хранит рассчитанный остаток, план выдачи, резерв и созданные складские документы по паре строка требования / склад.

### Технические параметры

- `_name = 'object.request.line.stock'`
- `_description = 'Object Request Line Stock'`
- `_order = 'line_id, id'`

### Поля

- `line_id = fields.Many2one('object.request.line', required=True, ondelete='cascade', index=True)`
- `warehouse_id = fields.Many2one('stock.warehouse', required=True, index=True)`
- `company_id = fields.Many2one('res.company', related='line_id.company_id', store=True)`
- `qty_on_hand = fields.Float(digits='Product Unit of Measure')`
  - доступный остаток на складе на момент последней проверки
- `qty_to_issue = fields.Float(digits='Product Unit of Measure')`
  - план выдачи с конкретного склада
- `qty_reserved = fields.Float(digits='Product Unit of Measure')`
  - зарезервированное количество по созданному picking
- `last_check_date = fields.Datetime()`
- `picking_id = fields.Many2one('stock.picking', index=True)`
- `move_id = fields.Many2one('stock.move', index=True)`

### Constraints

- `UNIQUE(line_id, warehouse_id)`
- сумма `qty_to_issue` по всем складам строки не может превышать `qty_requested - qty_issued`.

### Синхронизация с `object.request.line`

После create/write/unlink распределения строка требования пересчитывает:

- `stock_qty_on_hand = sum(stock_ids.qty_on_hand)`
- `stock_check_date = max(stock_ids.last_check_date)`
- `qty_to_issue = sum(stock_ids.qty_to_issue)`
- `qty_reserved = sum(stock_ids.qty_reserved)`
- `qty_to_buy = max(qty_requested - qty_issued - qty_to_issue, 0)`
- `procurement_mode`

Ручная правка `qty_to_issue` в распределении ставит `manual_plan_override=True` на строке.

## Модель 5. `object.request.issue.preview.wizard`

### Назначение

Transient model для предпросмотра и создания выдач по складам.

### Поля

- `request_id = fields.Many2one('object.request', required=True)`
- `group_ids = fields.One2many('object.request.issue.preview.group', 'wizard_id')`
- `group_count = fields.Integer(compute='_compute_group_count')`

### Группа выдачи `object.request.issue.preview.group`

- `wizard_id = fields.Many2one('object.request.issue.preview.wizard', required=True, ondelete='cascade')`
- `warehouse_id = fields.Many2one('stock.warehouse', required=True, readonly=True)`
- `picking_type_id = fields.Many2one('stock.picking.type', required=True)`
- `source_location_id = fields.Many2one('stock.location', required=True)`
- `destination_location_id = fields.Many2one('stock.location', required=True)`
- `scheduled_date = fields.Datetime(required=True)`
- `comment = fields.Text()`
- `included = fields.Boolean(default=True)`
- `stock_line_ids = fields.Many2many('object.request.line.stock')`
- `line_count = fields.Integer(compute='_compute_totals')`
- `qty_total = fields.Float(compute='_compute_totals')`

### Использование

- `default_get` группирует `object.request.line.stock` с `qty_to_issue > 0` по складам.
- пользователь может исключить группу склада через `included=False`.
- `action_create_issues()` создаёт по одному `stock.picking` на каждую включённую группу.
- для каждой строки распределения сохраняются `picking_id` и `move_id`.
- после `action_assign()` синхронизируются `qty_reserved` и `issue_reserved`.

## Модель 6. `object.request.purchase.wizard`

### Назначение

Transient model для подготовки черновиков закупки по дефициту.

### Поля

- `request_id = fields.Many2one('object.request', required=True)`
- `line_ids = fields.Many2many('object.request.line')`
- `group_by_vendor = fields.Boolean(default=True)`
- `create_draft_only = fields.Boolean(default=True)`
- `comment = fields.Text()`

### Использование

Wizard создаёт draft `purchase.order` по строкам с `qty_to_buy > 0`, группируя строки по поставщику. Тип приёмки (`picking_type_id`) по умолчанию берётся из `request.project_id.warehouse_id.in_type_id`; если у объекта нет склада, снабженец должен выбрать тип приёмки вручную.

## Расширение `stock.picking`

### Способ

Использовать `_inherit = 'stock.picking'`

### Новые поля

- `object_request_ids = fields.Many2many(
    'object.request',
    'object_request_stock_picking_rel',
    'picking_id',
    'request_id',
    string='Object Requests'
  )`
- `is_object_request_issue = fields.Boolean(default=False, index=True)`
- `object_request_project_id = fields.Many2one('object.request.project', index=True)`

### Зачем

- быстро открывать выдачи из документа;
- фильтровать складские документы, созданные из требований;
- печатать расходную накладную с контекстом объекта.

## Расширение `purchase.order`

### Способ

Использовать `_inherit = 'purchase.order'`

### Новые поля

- `object_request_ids = fields.Many2many(
    'object.request',
    'object_request_purchase_order_rel',
    'purchase_id',
    'request_id',
    string='Object Requests'
  )`
- `is_object_request_purchase = fields.Boolean(default=False, index=True)`
- `object_request_project_id = fields.Many2one('object.request.project', index=True)`

### Зачем

- видеть источник закупки;
- быстро открывать закупки из документа;
- группировать потребности по объекту.

## Вычисляемая логика статусов

## Статус документа `matching_state`

Рекомендуемая логика:

- `all_matched`
  - все строки сопоставлены
  - нет строк `requires_mapping`
- `partial`
  - есть и сопоставленные, и проблемные строки
- `requires_mapping`
  - все строки или хотя бы критичная часть требуют сопоставления

## Статус строки `line_state`

Рекомендуемая логика:

- `requires_mapping`
  - `product_id` не выбран
  - или строка специально помечена как проблемная
- `ready`
  - строка сопоставлена и может быть обработана
- `partially_issued`
  - `qty_issued > 0`, но меньше целевого количества
- `fully_supplied`
  - строка полностью закрыта выдачей или закупкой

### Важный момент

Для бизнеса показывать только понятные статусы, но технически хранить детализированное состояние.  
Это упростит переход ко 2 этапу.

## Рекомендации по трекингу и chatter

Для `object.request` желательно включить tracking у полей:

- `state`
- `project_id`
- `foreman_user_id`
- `need_date`
- `priority`
- `buyer_user_id`
- `warehouse_user_id`
- `approval_state`

Для `object.request.line` tracking можно ограничить, чтобы не засорять chatter.

## Рекомендации по ACL и record rules

На уровне данных надо закладывать будущие ACL:

- Прораб:
  - create/read/write свои документы
- Снабженец:
  - read/write все документы
- Кладовщик:
  - read документы
  - write только действия, связанные с выдачей
- Согласующий:
  - read
  - approve/reject позже

На уровне record rules удобнее фильтровать документы через `company_id` и ownership/role.

## Рекомендации по MVP vs этап 2

## В MVP хранить уже сейчас

Даже если логика пока не реализована, полезно сразу заложить поля:

- `stock_qty_on_hand`
- `stock_check_date`
- `qty_to_issue`
- `qty_to_buy`
- `qty_reserved`
- `preferred_vendor_id`
- `purchase_order_id`

Это позволит не ломать структуру модели позже.

## На этапе 2 активировать бизнес-логику

- автоматический расчет физического остатка;
- авторазбиение на выдачу и закупку;
- резервирование под требование;
- генерация draft RFQ / Purchase;
- согласование и отчеты.

## Что не хранить отдельной моделью в MVP

Не рекомендую в первом релизе создавать отдельные модели:

- зона
- этаж
- участок
- допустимая замена как отдельная сущность правил
- история согласования

Пока достаточно:

- `Char` для зоны/этажа/участка
- `Many2many` на разрешенные заменяющие товары
- `Selection` под согласование-заглушку

## Предлагаемые sequence и XML IDs

### Sequence

- `object.request.sequence`

Формат номера:

- `OR/%(year)s/%(month)s/%(seq)s`

### Важные XML IDs для будущей реализации

- `model_object_request`
- `model_object_request_line`
- `model_object_request_project`
- `action_object_request`
- `view_object_request_tree`
- `view_object_request_form`
- `view_object_request_line_tree`
- `wizard_object_request_import`

## Критерии готовности data model spec

- выбрана и зафиксирована модель объекта;
- перечислены все основные и transient модели;
- по каждой основной модели определены поля и типы;
- определены связи со стандартными моделями Odoo;
- определены ключевые compute fields и constraints;
- заложены поля под этап 2 без миграции структуры;
- документ пригоден как база для создания Python models и security.

## Следующий шаг

После этого документа логично подготовить:

1. `ACL / security matrix`
2. `wizard spec` для Excel-импорта
3. `state machine spec`
4. затем каркас Python-моделей и XML views
