# Odoo Schema: `object_request_raw`

> Сгенерировано из `/tmp/akaidoo_raw/object_request_raw.md` скриптом `extract_schema.py`.  
> Модели: 40, полей всего: 389.

## `PurchaseOrderExt` ← purchase.order
Файл: `custom_addons/object_request/models/purchase_order_ext.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `is_object_request_purchase` | Boolean | — | Закупка по требованию |
| `object_request_project_id` | Many2one | object.request.project | Объект требования |
| `object_request_ids` | Many2many | object.request | Требования на комплектацию |
| `object_request_count` | Integer | — | Требований |

## `ResCompany` ← res.company
Файл: `odoo/addons/stock/models/res_company.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `internal_transit_location_id` | Many2one | stock.location |  |

## `ResPartner` ← res.partner
Файл: `odoo/addons/purchase/models/res_partner.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `buyer_id` | Many2one | res.users |  |
| `property_stock_customer` | Many2one | stock.location |  |
| `property_stock_supplier` | Many2one | stock.location |  |

## `ResUsers` ← res.users
Файл: `odoo/addons/resource/models/res_users.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `resource_ids` | One2many | resource.resource |  |
| `resource_calendar_id` | Many2one | resource.calendar |  |

## `StockPickingInherit` ← stock.picking
Файл: `custom_addons/object_request/models/stock_picking_inherit.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `is_object_request_issue` | Boolean | — | Выдача по требованию |
| `object_request_project_id` | Many2one | object.request.project | Объект требования |
| `object_request_ids` | Many2many | object.request | Требования на комплектацию |
| `object_request_count` | Integer | — | Требований |

## `account.analytic.account` ← mail.thread
*Analytic Account*  
Файл: `odoo/addons/analytic/models/analytic_account.py`  

*Полей нет (абстрактная модель или наследование)*  

## `account.analytic.distribution.model` ← analytic.mixin
*Analytic Distribution Model*  
Файл: `odoo/addons/analytic/models/analytic_distribution_model.py`  

*Полей нет (абстрактная модель или наследование)*  

## `analytic.mixin`
*Analytic Mixin*  
Файл: `odoo/addons/analytic/models/analytic_mixin.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `analytic_distribution` | Json | — |  |
| `analytic_precision` | Integer | — |  |
| `distribution_analytic_account_ids` | Many2many | account.analytic.account |  |

## `barcode.nomenclature`
*Barcode Nomenclature*  
Файл: `odoo/addons/barcodes/models/barcode_nomenclature.py`  

*Полей нет (абстрактная модель или наследование)*  

## `barcode.rule`
*Barcode Rule*  
Файл: `odoo/addons/barcodes/models/barcode_rule.py`  

*Полей нет (абстрактная модель или наследование)*  

## `barcodes.barcode_events_mixin`
*Barcode Event Mixin*  
Файл: `odoo/addons/barcodes/models/barcode_events_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `html.field.history.mixin`
*Field html History*  
Файл: `odoo/addons/html_editor/models/html_field_history_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `object.request` ← mail.thread, mail.activity.mixin
*Object Supply Request*  
Файл: `custom_addons/object_request/models/object_request.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — | Номер документа |
| `project_id` | Many2one | object.request.project | Объект |
| `foreman_user_id` | Many2one | res.users | Прораб |
| `need_date` | Date | — | Дата потребности |
| `priority` | Selection | 0,1,2,3 | Приоритет |
| `comment` | Text | — | Комментарий |
| `state` | Selection | draft,in_progress,closed,cancelled | Статус |
| `active` | Boolean | — |  |
| `line_ids` | One2many | object.request.line | Строки |
| `source_file_name` | Char | — | Имя файла |
| `source_file_checksum` | Char | — | Контрольная сумма |
| `imported_at` | Datetime | — | Дата импорта |
| `imported_by_user_id` | Many2one | res.users | Импортировал |
| `matching_state` | Selection | all_matched,partial,requires_mapping | Статус сопоставления |
| `approval_state` | Selection | not_required,pending,approved,rejected | Согласование |
| `buyer_user_id` | Many2one | res.users | Снабженец |
| `warehouse_user_id` | Many2one | res.users | Кладовщик |
| `approver_user_id` | Many2one | res.users | Согласующий |
| `issue_picking_ids` | Many2many | stock.picking | Выдачи |
| `issue_picking_count` | Integer | — |  |
| `purchase_order_ids` | Many2many | purchase.order | Закупки |
| `purchase_order_count` | Integer | — |  |
| `line_count` | Integer | — | Строк |
| `line_problem_count` | Integer | — |  |
| `line_matched_count` | Integer | — |  |
| `line_to_issue_count` | Integer | — |  |
| `line_to_buy_count` | Integer | — |  |
| `line_fully_supplied_count` | Integer | — |  |
| `qty_total_requested` | Float | — |  |
| `qty_total_to_issue` | Float | — |  |
| `qty_total_to_buy` | Float | — |  |
| `qty_total_issued` | Float | — |  |
| `qty_total_reserved` | Float | — |  |
| `company_id` | Many2one | res.company | Компания |
| `currency_id` | Many2one | res.currency |  |

## `object.request.excel.parser`
*Сервис парсинга и автосопоставления строк Excel*  
Файл: `custom_addons/object_request/models/excel_parser.py`  

*Полей нет (абстрактная модель или наследование)*  

## `object.request.line`
*Object Supply Request Line*  
Файл: `custom_addons/object_request/models/object_request_line.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `request_id` | Many2one | object.request |  |
| `sequence` | Integer | — | № |
| `source_row_no` | Integer | — | Строка Excel |
| `supplier_article` | Char | — | Артикул поставщика |
| `name_raw` | Char | — | Наименование (из файла) |
| `uom_raw` | Char | — | Ед. изм. (из файла) |
| `qty_requested` | Float | — | Запрошено |
| `price_raw` | Float | — | Цена (из файла) |
| `comment` | Text | — | Комментарий |
| `supplier_raw` | Char | — | Поставщик (из файла) |
| `zone` | Char | — | Зона |
| `floor` | Char | — | Этаж |
| `section` | Char | — | Участок |
| `product_id` | Many2one | product.product | Товар |
| `product_tmpl_id` | Many2one | product.template |  |
| `uom_id` | Many2one | uom.uom | Ед. изм. |
| `preferred_vendor_id` | Many2one | res.partner | Предпочтительный поставщик |
| `allowed_substitute_ids` | Many2many | product.product | Допустимые замены |
| `matching_required` | Boolean | — | Требует сопоставления |
| `matching_state` | Selection | matched,requires_mapping,manual_review | Статус сопоставления |
| `matching_note` | Text | — | Примечание по сопоставлению |
| `manual_vendor_required` | Boolean | — | Требует выбора поставщика |
| `procurement_mode` | Selection | manual,issue,buy,mixed | Способ обеспечения |
| `qty_to_issue` | Float | — | К выдаче |
| `qty_to_buy` | Float | — | К закупке |
| `qty_reserved` | Float | — | Зарезервировано |
| `issue_reserved` | Boolean | — | Резерв создан |
| `qty_issued` | Float | — | Выдано |
| `stock_qty_on_hand` | Float | — | Остаток на складе |
| `stock_check_date` | Datetime | — | Дата проверки остатка |
| `is_cancelled` | Boolean | — | Отменена |
| `line_state` | Selection | draft,requires_mapping,ready,partially_issued,fully_supplied,cancelled | Статус строки |
| `issue_picking_id` | Many2one | stock.picking | Выдача |
| `issue_move_id` | Many2one | stock.move | Движение |
| `purchase_order_id` | Many2one | purchase.order | Закупка |
| `purchase_order_line_id` | Many2one | purchase.order.line | Строка закупки |
| `company_id` | Many2one | res.company |  |
| `currency_id` | Many2one | res.currency |  |
| `has_substitutes` | Boolean | — |  |
| `is_fully_matched` | Boolean | — |  |
| `is_ready_for_issue` | Boolean | — |  |
| `is_ready_for_purchase` | Boolean | — |  |

## `object.request.project` ← mail.thread, mail.activity.mixin
*Project Object for Supply Request*  
Файл: `custom_addons/object_request/models/object_request_project.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — | Наименование |
| `code` | Char | — | Код объекта |
| `partner_id` | Many2one | res.partner | Заказчик |
| `address` | Char | — | Адрес |
| `comment` | Text | — | Комментарий |
| `active` | Boolean | — |  |
| `request_ids` | One2many | object.request | Требования |
| `request_count` | Integer | — | Количество требований |

## `onboarding.onboarding`
*Onboarding*  
Файл: `odoo/addons/onboarding/models/onboarding_onboarding.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.onboarding.step`
*Onboarding Step*  
Файл: `odoo/addons/onboarding/models/onboarding_onboarding_step.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.progress`
*Onboarding Progress Tracker*  
Файл: `odoo/addons/onboarding/models/onboarding_progress.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.progress.step`
*Onboarding Progress Step Tracker*  
Файл: `odoo/addons/onboarding/models/onboarding_progress_step.py`  

*Полей нет (абстрактная модель или наследование)*  

## `purchase.bill.line.match`
*Purchase Line and Vendor Bill line matching view*  
Файл: `odoo/addons/purchase/models/purchase_bill_line_match.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `pol_id` | Many2one | purchase.order.line |  |
| `aml_id` | Many2one | account.move.line |  |
| `product_id` | Many2one | product.product |  |
| `purchase_order_id` | Many2one | purchase.order |  |
| `account_move_id` | Many2one | account.move |  |

## `purchase.order` ← portal.mixin, product.catalog.mixin, mail.thread, mail.activity.mixin, account.document.import.mixin
*Purchase Order*  
Файл: `odoo/addons/purchase/models/purchase_order.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `priority` | Selection | 0,1 |  |
| `origin` | Char | — |  |
| `partner_ref` | Char | — |  |
| `date_order` | Datetime | — |  |
| `date_approve` | Datetime | — |  |
| `partner_id` | Many2one | res.partner | Vendor |
| `dest_address_id` | Many2one | res.partner | Dropship Address |
| `currency_id` | Many2one | res.currency |  |
| `state` | Selection | draft,sent,to approve,purchase,cancel | Status |
| `locked` | Boolean | — |  |
| `lock_confirmed_po` | Selection | company_id.po_lock |  |
| `order_line` | One2many | purchase.order.line | Order Lines |
| `acknowledged` | Boolean | — |  |
| `note` | Html | — |  |
| `partner_bill_count` | Integer | — |  |
| `invoice_count` | Integer | — | Bill Count |
| `invoice_ids` | Many2many | account.move | Bills |
| `invoice_status` | Selection | no,to invoice,invoiced | Billing Status |
| `date_planned` | Datetime | — | Expected Arrival |
| `date_calendar_start` | Datetime | — |  |
| `amount_untaxed` | Monetary | — | Untaxed Amount |
| `tax_totals` | Binary | — |  |
| `amount_tax` | Monetary | — | Taxes |
| `amount_total` | Monetary | — | Total |
| `amount_total_cc` | Monetary | — | Total in currency |
| `fiscal_position_id` | Many2one | account.fiscal.position | Fiscal Position |
| `tax_country_id` | Many2one | res.country |  |
| `tax_calculation_rounding_method` | Selection | company_id.tax_calculation_rounding_method | Tax calculation rounding method |
| `payment_term_id` | Many2one | account.payment.term |  |
| `incoterm_id` | Many2one | account.incoterms |  |
| `product_id` | Many2one | product.product | Product |
| `user_id` | Many2one | res.users | Buyer |
| `company_id` | Many2one | res.company |  |
| `company_currency_id` | Many2one | ? | Company Currency |
| `country_code` | Char | — | Country code |
| `company_price_include` | Selection | company_id.account_price_include |  |
| `currency_rate` | Float | — | Currency Rate |
| `duplicated_order_ids` | Many2many | purchase.order |  |
| `receipt_reminder_email` | Boolean | — |  |
| `reminder_date_before_receipt` | Integer | — |  |
| `is_late` | Boolean | — |  |
| `show_comparison` | Boolean | — |  |
| `purchase_warning_text` | Text | — |  |

## `purchase.order.line` ← analytic.mixin
*Purchase Order Line*  
Файл: `odoo/addons/purchase/models/purchase_order_line.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Text | — | Description |
| `translated_product_name` | Text | — |  |
| `sequence` | Integer | — | Sequence |
| `product_qty` | Float | — | Quantity |
| `product_uom_qty` | Float | — | Total Quantity |
| `date_planned` | Datetime | — | Expected Arrival |
| `discount` | Float | — | Discount (%) |
| `tax_ids` | Many2many | account.tax | Taxes |
| `allowed_uom_ids` | Many2many | uom.uom |  |
| `product_uom_id` | Many2one | uom.uom | Unit |
| `product_id` | Many2one | product.product | Product |
| `product_type` | Selection | product_id.type |  |
| `price_unit` | Float | — | Unit Price |
| `price_unit_product_uom` | Float | — | Unit Price Product UoM |
| `price_unit_discounted` | Float | — |  |
| `price_subtotal` | Monetary | — | Subtotal |
| `price_total` | Monetary | — | Total |
| `price_tax` | Float | — | Tax |
| `order_id` | Many2one | purchase.order | Order Reference |
| `company_id` | Many2one | res.company | Company |
| `state` | Selection | order_id.state |  |
| `invoice_lines` | One2many | account.move.line | Bill Lines |
| `qty_invoiced` | Float | — | Billed Qty |
| `qty_received_method` | Selection | manual | Received Qty Method |
| `qty_received` | Float | — |  |
| `qty_received_manual` | Float | — |  |
| `qty_to_invoice` | Float | — | To Invoice Quantity |
| `qty_received_at_date` | Float | — | Received |
| `qty_invoiced_at_date` | Float | — | Billed |
| `amount_to_invoice_at_date` | Float | — | Amount |
| `partner_id` | Many2one | res.partner | Partner |
| `currency_id` | Many2one | ? | Currency |
| `date_order` | Datetime | — | Order Date |
| `date_approve` | Datetime | — | Confirmation Date |
| `tax_calculation_rounding_method` | Selection | company_id.tax_calculation_rounding_method | Tax calculation rounding method |
| `display_type` | Selection | line_section,line_subsection,line_note |  |
| `is_downpayment` | Boolean | — |  |
| `selected_seller_id` | Many2one | product.supplierinfo |  |
| `product_template_attribute_value_ids` | Many2many | ? |  |
| `product_no_variant_attribute_value_ids` | Many2many | product.template.attribute.value | Product attribute values that do not create variants |
| `purchase_line_warn_msg` | Text | — |  |
| `parent_id` | Many2one | purchase.order.line | Parent Section Line |
| `technical_price_unit` | Float | — |  |

## `resource.calendar`
*Resource Working Time*  
Файл: `odoo/addons/resource/models/resource_calendar.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.attendance`
*Work Detail*  
Файл: `odoo/addons/resource/models/resource_calendar_attendance.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.leaves`
*Resource Time Off Detail*  
Файл: `odoo/addons/resource/models/resource_calendar_leaves.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.mixin`
*Resource Mixin*  
Файл: `odoo/addons/resource/models/resource_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.resource`
*Resources*  
Файл: `odoo/addons/resource/models/resource_resource.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `user_id` | Many2one | res.users |  |

## `stock.lot` ← mail.thread, mail.activity.mixin
*Lot/Serial*  
Файл: `odoo/addons/stock/models/stock_lot.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `ref` | Char | — |  |
| `product_id` | Many2one | product.product |  |
| `product_uom_id` | Many2one | uom.uom |  |
| `quant_ids` | One2many | stock.quant |  |
| `product_qty` | Float | — |  |
| `note` | Html | — | Description |
| `display_complete` | Boolean | — |  |
| `company_id` | Many2one | res.company |  |
| `delivery_ids` | Many2many | stock.picking | Transfers |
| `delivery_count` | Integer | — |  |
| `partner_ids` | Many2many | res.partner |  |
| `location_id` | Many2one | stock.location |  |

## `stock.move`
*Stock Move*  
Файл: `odoo/addons/stock/models/stock_move.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `sequence` | Integer | — |  |
| `priority` | Selection | Priority,_compute_priority |  |
| `date` | Datetime | — |  |
| `date_deadline` | Datetime | — |  |
| `company_id` | Many2one | res.company |  |
| `product_id` | Many2one | product.product |  |
| `product_category_id` | Many2one | product.category |  |
| `never_product_template_attribute_value_ids` | Many2many | product.template.attribute.value | Never attribute Values |
| `description_picking` | Text | — | Description Of Picking |
| `description_picking_manual` | Text | — |  |
| `product_qty` | Float | — |  |
| `product_uom_qty` | Float | — |  |
| `allowed_uom_ids` | Many2many | uom.uom |  |
| `product_uom` | Many2one | uom.uom |  |
| `product_tmpl_id` | Many2one | product.template |  |
| `location_id` | Many2one | stock.location |  |
| `location_dest_id` | Many2one | stock.location |  |
| `location_final_id` | Many2one | stock.location |  |
| `location_usage` | Selection | Source Location Type | Source Location Type |
| `location_dest_usage` | Selection | Destination Location Type | Destination Location Type |
| `partner_id` | Many2one | res.partner |  |
| `move_dest_ids` | Many2many | stock.move |  |
| `move_orig_ids` | Many2many | stock.move |  |
| `picking_id` | Many2one | stock.picking |  |
| `state` | Selection | draft,waiting,confirmed,partially_available,assigned,done,cancel | Status |
| `picked` | Boolean | — |  |
| `price_unit` | Float | — |  |
| `origin` | Char | — |  |
| `procure_method` | Selection | make_to_stock,make_to_order | Supply Method |
| `scrap_id` | Many2one | stock.scrap |  |
| `procurement_values` | Json | — |  |
| `reference_ids` | Many2many | stock.reference | References |
| `rule_id` | Many2one | stock.rule |  |
| `propagate_cancel` | Boolean | — |  |
| `delay_alert_date` | Datetime | — |  |
| `picking_type_id` | Many2one | stock.picking.type |  |
| `is_inventory` | Boolean | — |  |
| `inventory_name` | Char | — |  |
| `move_line_ids` | One2many | stock.move.line |  |
| `package_ids` | One2many | stock.package | Packages |
| `origin_returned_move_id` | Many2one | stock.move |  |
| `returned_move_ids` | One2many | stock.move |  |
| `availability` | Float | — |  |
| `restrict_partner_id` | Many2one | res.partner |  |
| `route_ids` | Many2many | stock.route |  |
| `warehouse_id` | Many2one | stock.warehouse |  |
| `has_tracking` | Selection | product_id.tracking | Product with Tracking |
| `has_lines_without_result_package` | Boolean | — |  |
| `quantity` | Float | — |  |
| `show_operations` | Boolean | — |  |
| `picking_code` | Selection | picking_id.picking_type_id.code |  |
| `show_details_visible` | Boolean | — |  |
| `is_storable` | Boolean | — |  |
| `additional` | Boolean | — |  |
| `is_locked` | Boolean | — |  |
| `is_initial_demand_editable` | Boolean | — |  |
| `is_date_editable` | Boolean | — |  |
| `is_quantity_done_editable` | Boolean | — |  |
| `reference` | Char | — | Reference |
| `move_lines_count` | Integer | — |  |
| `display_assign_serial` | Boolean | — |  |
| `display_import_lot` | Boolean | — |  |
| `next_serial` | Char | — |  |
| `next_serial_count` | Integer | — |  |
| `orderpoint_id` | Many2one | stock.warehouse.orderpoint |  |
| `forecast_availability` | Float | — |  |
| `forecast_expected_date` | Datetime | — |  |
| `lot_ids` | Many2many | stock.lot | Serial Numbers |
| `reservation_date` | Date | — |  |
| `packaging_uom_id` | Many2one | uom.uom |  |
| `packaging_uom_qty` | Float | — |  |
| `show_quant` | Boolean | — |  |
| `show_lots_m2o` | Boolean | — |  |
| `show_lots_text` | Boolean | — |  |

## `stock.move.line`
*Product Moves (Stock Move Line)*  
Файл: `odoo/addons/stock/models/stock_move_line.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `picking_id` | Many2one | stock.picking |  |
| `move_id` | Many2one | stock.move |  |
| `company_id` | Many2one | res.company | Company |
| `product_id` | Many2one | product.product |  |
| `allowed_uom_ids` | Many2many | uom.uom |  |
| `product_uom_id` | Many2one | uom.uom |  |
| `product_category_name` | Char | — | Product Category |
| `quantity` | Float | — |  |
| `quantity_product_uom` | Float | — |  |
| `picked` | Boolean | — |  |
| `package_id` | Many2one | stock.package |  |
| `lot_id` | Many2one | stock.lot |  |
| `lot_name` | Char | — |  |
| `result_package_id` | Many2one | stock.package |  |
| `result_package_dest_name` | Char | — |  |
| `package_history_id` | Many2one | stock.package.history | Package History |
| `is_entire_pack` | Boolean | — |  |
| `date` | Datetime | — |  |
| `scheduled_date` | Datetime | — |  |
| `owner_id` | Many2one | res.partner |  |
| `location_id` | Many2one | stock.location |  |
| `location_dest_id` | Many2one | stock.location |  |
| `location_usage` | Selection | Source Location Type | Source Location Type |
| `location_dest_usage` | Selection | Destination Location Type | Destination Location Type |
| `lots_visible` | Boolean | — |  |
| `picking_partner_id` | Many2one | ? |  |
| `move_partner_id` | Many2one | ? |  |
| `picking_code` | Selection | picking_type_id.code |  |
| `picking_type_id` | Many2one | stock.picking.type |  |
| `picking_type_use_create_lots` | Boolean | — |  |
| `picking_type_use_existing_lots` | Boolean | — |  |
| `state` | Selection | move_id.state |  |
| `scrap_id` | Many2one | ? |  |
| `is_inventory` | Boolean | — |  |
| `is_locked` | Boolean | — |  |
| `consume_line_ids` | Many2many | stock.move.line |  |
| `produce_line_ids` | Many2many | stock.move.line |  |
| `reference` | Char | — |  |
| `tracking` | Selection | product_id.tracking |  |
| `origin` | Char | — | Source |
| `description_picking` | Text | — |  |
| `quant_id` | Many2one | stock.quant |  |
| `picking_location_id` | Many2one | ? |  |
| `picking_location_dest_id` | Many2one | ? |  |

## `stock.package`
*Package*  
Файл: `odoo/addons/stock/models/stock_package.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `location_id` | Many2one | stock.location |  |
| `location_dest_id` | Many2one | stock.location |  |
| `move_line_ids` | One2many | stock.move.line |  |
| `picking_ids` | Many2many | stock.picking |  |

## `stock.package.history`
*Stock Package History*  
Файл: `odoo/addons/stock/models/stock_package_history.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `company_id` | Many2one | res.company |  |
| `location_id` | Many2one | stock.location |  |
| `location_dest_id` | Many2one | stock.location |  |
| `move_line_ids` | One2many | stock.move.line | Move Lines |
| `package_id` | Many2one | stock.package |  |
| `package_name` | Char | — |  |
| `package_type_id` | Many2one | stock.package.type |  |
| `parent_orig_id` | Many2one | stock.package |  |
| `parent_orig_name` | Char | — |  |
| `parent_dest_id` | Many2one | stock.package |  |
| `parent_dest_name` | Char | — |  |
| `outermost_dest_id` | Many2one | stock.package |  |
| `picking_ids` | Many2many | stock.picking | Transfers |

## `stock.package.type`
*Stock package type*  
Файл: `odoo/addons/stock/models/stock_package_type.py`  

*Полей нет (абстрактная модель или наследование)*  

## `stock.quant`
*Quants*  
Файл: `odoo/addons/stock/models/stock_quant.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `product_id` | Many2one | product.product |  |
| `product_tmpl_id` | Many2one | product.template |  |
| `location_id` | Many2one | stock.location |  |
| `warehouse_id` | Many2one | stock.warehouse |  |
| `lot_id` | Many2one | stock.lot |  |
| `user_id` | Many2one | res.users |  |

## `stock.reference`
*Reference between stock documents*  
Файл: `odoo/addons/stock/models/stock_reference.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `move_ids` | Many2many | stock.move | Stock Moves |
| `picking_ids` | Many2many | stock.picking | Transfers |

## `stock.replenish.mixin`
*Product Replenish Mixin*  
Файл: `odoo/addons/stock/models/stock_replenish_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `stock.rule`
*Stock Rule*  
Файл: `odoo/addons/stock/models/stock_rule.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `location_dest_id` | Many2one | stock.location |  |
| `location_src_id` | Many2one | stock.location |  |
| `picking_type_id` | Many2one | stock.picking.type |  |
| `warehouse_id` | Many2one | stock.warehouse |  |

## `stock.warehouse`
*Warehouse*  
Файл: `odoo/addons/stock/models/stock_warehouse.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `active` | Boolean | — |  |
| `company_id` | Many2one | res.company |  |
| `partner_id` | Many2one | res.partner |  |
| `view_location_id` | Many2one | stock.location |  |
| `lot_stock_id` | Many2one | stock.location |  |
| `code` | Char | — |  |
| `route_ids` | Many2many | stock.route |  |
| `reception_steps` | Selection | one_step,two_steps,three_steps |  |
| `delivery_steps` | Selection | ship_only,pick_ship,pick_pack_ship |  |
| `wh_input_stock_loc_id` | Many2one | stock.location |  |
| `wh_qc_stock_loc_id` | Many2one | stock.location |  |
| `wh_output_stock_loc_id` | Many2one | stock.location |  |
| `wh_pack_stock_loc_id` | Many2one | stock.location |  |
| `mto_pull_id` | Many2one | stock.rule |  |
| `pick_type_id` | Many2one | stock.picking.type |  |
| `pack_type_id` | Many2one | stock.picking.type |  |
| `out_type_id` | Many2one | stock.picking.type |  |
| `in_type_id` | Many2one | stock.picking.type |  |
| `int_type_id` | Many2one | stock.picking.type |  |
| `qc_type_id` | Many2one | stock.picking.type |  |
| `store_type_id` | Many2one | stock.picking.type |  |
| `xdock_type_id` | Many2one | stock.picking.type |  |
| `reception_route_id` | Many2one | stock.route |  |
| `delivery_route_id` | Many2one | stock.route |  |
| `resupply_wh_ids` | Many2many | stock.warehouse |  |
| `resupply_route_ids` | One2many | stock.route |  |
| `sequence` | Integer | — |  |

## `stock.warehouse.orderpoint`
*Minimum Inventory Rule*  
Файл: `odoo/addons/stock/models/stock_orderpoint.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `warehouse_id` | Many2one | stock.warehouse |  |
| `location_id` | Many2one | stock.location |  |
| `product_tmpl_id` | Many2one | product.template |  |
| `product_id` | Many2one | product.product |  |
| `allowed_location_ids` | One2many | stock.location |  |
