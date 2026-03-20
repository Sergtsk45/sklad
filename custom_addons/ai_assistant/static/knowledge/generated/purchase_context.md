# Odoo Schema: `purchase_raw`

> Сгенерировано из `/tmp/akaidoo_raw/purchase_raw.md` скриптом `extract_schema.py`.  
> Модели: 21, полей всего: 133.

## `AccountAnalyticAccount` ← account.analytic.account
Файл: `odoo/addons/purchase/models/analytic_account.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `purchase_order_count` | Integer | — |  |

## `AccountAnalyticApplicability` ← account.analytic.applicability
*Analytic Plan*  
Файл: `odoo/addons/purchase/models/analytic_applicability.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `business_domain` | Selection | purchase_order |  |

## `ResCompany` ← res.company
Файл: `odoo/addons/purchase/models/res_company.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `po_lock` | Selection | edit,lock | Purchase Order Modification |
| `po_double_validation` | Selection | one_step,two_step | Levels of Approvals |
| `po_double_validation_amount` | Monetary | — | Double validation amount |

## `ResConfigSettings` ← res.config.settings
Файл: `odoo/addons/purchase/models/res_config_settings.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `lock_confirmed_po` | Boolean | — |  |
| `po_lock` | Selection | company_id.po_lock | Purchase Order Modification * |
| `po_order_approval` | Boolean | — |  |
| `po_double_validation` | Selection | company_id.po_double_validation | Levels of Approvals * |
| `po_double_validation_amount` | Monetary | — | Minimum Amount |
| `company_currency_id` | Many2one | res.currency | Company Currency |
| `group_warning_purchase` | Boolean | — |  |
| `module_account_3way_match` | Boolean | — |  |
| `module_purchase_requisition` | Boolean | — |  |
| `module_purchase_product_matrix` | Boolean | — |  |
| `group_send_reminder` | Boolean | — |  |

## `ResPartner` ← res.partner
Файл: `odoo/addons/purchase/models/res_partner.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `property_purchase_currency_id` | Many2one | res.currency | Supplier Currency |
| `purchase_order_count` | Integer | — | Purchase Order Count |
| `purchase_warn_msg` | Text | — |  |
| `receipt_reminder_email` | Boolean | — |  |
| `reminder_date_before_receipt` | Integer | — |  |
| `buyer_id` | Many2one | res.users | Buyer |

## `account.analytic.account` ← mail.thread
*Analytic Account*  
Файл: `odoo/addons/analytic/models/analytic_account.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `plan_id` | Many2one | account.analytic.plan |  |
| `root_plan_id` | Many2one | account.analytic.plan |  |
| `line_ids` | One2many | account.analytic.line |  |

## `account.analytic.distribution.model` ← analytic.mixin
Файл: `odoo/addons/analytic/models/analytic_distribution_model.py`  

*Полей нет (абстрактная модель или наследование)*  

## `analytic.mixin`
*Analytic Mixin*  
Файл: `odoo/addons/analytic/models/analytic_mixin.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `distribution_analytic_account_ids` | Many2many | account.analytic.account |  |

## `html.field.history.mixin`
Файл: `odoo/addons/html_editor/models/html_field_history_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.onboarding`
Файл: `odoo/addons/onboarding/models/onboarding_onboarding.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.onboarding.step`
Файл: `odoo/addons/onboarding/models/onboarding_onboarding_step.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.progress`
Файл: `odoo/addons/onboarding/models/onboarding_progress.py`  

*Полей нет (абстрактная модель или наследование)*  

## `onboarding.progress.step`
Файл: `odoo/addons/onboarding/models/onboarding_progress_step.py`  

*Полей нет (абстрактная модель или наследование)*  

## `purchase.bill.line.match`
*Purchase Line and Vendor Bill line matching view*  
Файл: `odoo/addons/purchase/models/purchase_bill_line_match.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `pol_id` | Many2one | purchase.order.line |  |
| `aml_id` | Many2one | account.move.line |  |
| `company_id` | Many2one | res.company |  |
| `partner_id` | Many2one | res.partner |  |
| `product_id` | Many2one | product.product |  |
| `line_qty` | Float | — |  |
| `line_uom_id` | Many2one | uom.uom |  |
| `qty_invoiced` | Float | — |  |
| `qty_to_invoice` | Float | — |  |
| `purchase_order_id` | Many2one | purchase.order |  |
| `account_move_id` | Many2one | account.move |  |
| `line_amount_untaxed` | Monetary | — |  |
| `currency_id` | Many2one | res.currency |  |
| `state` | Char | — |  |
| `product_uom_id` | Many2one | uom.uom |  |
| `product_uom_qty` | Float | — |  |
| `product_uom_price` | Float | — |  |
| `billed_amount_untaxed` | Monetary | — |  |
| `purchase_amount_untaxed` | Monetary | — |  |
| `reference` | Char | — |  |

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
Файл: `odoo/addons/resource/models/resource_calendar.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.attendance`
Файл: `odoo/addons/resource/models/resource_calendar_attendance.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.calendar.leaves`
Файл: `odoo/addons/resource/models/resource_calendar_leaves.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.mixin`
Файл: `odoo/addons/resource/models/resource_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `resource.resource`
Файл: `odoo/addons/resource/models/resource_resource.py`  

*Полей нет (абстрактная модель или наследование)*  
