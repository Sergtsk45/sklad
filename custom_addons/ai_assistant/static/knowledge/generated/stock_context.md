# Odoo Schema: `stock_raw`

> Сгенерировано из `/tmp/akaidoo_raw/stock_raw.md` скриптом `extract_schema.py`.  
> Модели: 25, полей всего: 351.

## `BarcodeRule` ← barcode.rule
Файл: `odoo/addons/stock/models/barcode.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `type` | Selection | weight,location,lot,package |  |

## `ResCompany` ← res.company
Файл: `odoo/addons/stock/models/res_company.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `internal_transit_location_id` | Many2one | stock.location |  |
| `stock_move_email_validation` | Boolean | — |  |
| `stock_mail_confirmation_template_id` | Many2one | mail.template | Email Template confirmation picking |
| `annual_inventory_month` | Selection | 1,2,3,4,5,6,7,… | Annual Inventory Month |
| `annual_inventory_day` | Integer | — | Day of the month |
| `horizon_days` | Float | — | Replenishment Horizon |
| `stock_text_confirmation` | Boolean | — |  |
| `stock_confirmation_type` | Selection | sms |  |

## `ResConfigSettings` ← res.config.settings
Файл: `odoo/addons/stock/models/res_config_settings.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `module_product_expiry` | Boolean | — |  |
| `group_stock_production_lot` | Boolean | — |  |
| `group_stock_lot_print_gs1` | Boolean | — |  |
| `group_lot_on_delivery_slip` | Boolean | — |  |
| `group_stock_tracking_lot` | Boolean | — |  |
| `group_stock_tracking_owner` | Boolean | — |  |
| `group_stock_adv_location` | Boolean | — |  |
| `group_warning_stock` | Boolean | — |  |
| `group_stock_sign_delivery` | Boolean | — |  |
| `module_stock_picking_batch` | Boolean | — |  |
| `module_stock_barcode` | Boolean | — |  |
| `module_stock_barcode_barcodelookup` | Boolean | — |  |
| `stock_move_email_validation` | Boolean | — |  |
| `module_stock_sms` | Boolean | — |  |
| `module_delivery` | Boolean | — |  |
| `module_delivery_dhl` | Boolean | — |  |
| `module_delivery_fedex_rest` | Boolean | — |  |
| `module_delivery_ups_rest` | Boolean | — |  |
| `module_delivery_usps_rest` | Boolean | — |  |
| `module_delivery_bpost` | Boolean | — |  |
| `module_delivery_easypost` | Boolean | — |  |
| `module_delivery_sendcloud` | Boolean | — |  |
| `module_delivery_shiprocket` | Boolean | — |  |
| `module_delivery_starshipit` | Boolean | — |  |
| `module_delivery_envia` | Boolean | — |  |
| `module_quality_control` | Boolean | — |  |
| `module_quality_control_worksheet` | Boolean | — |  |
| `group_stock_multi_locations` | Boolean | — |  |
| `annual_inventory_month` | Selection | company_id.annual_inventory_month |  |
| `annual_inventory_day` | Integer | — |  |
| `group_stock_reception_report` | Boolean | — |  |
| `module_stock_dropshipping` | Boolean | — |  |
| `barcode_separator` | Char | — |  |
| `module_stock_fleet` | Boolean | — |  |
| `replenish_on_order` | Boolean | — |  |
| `stock_text_confirmation` | Boolean | — | Stock Text Validation with stock move |
| `stock_confirmation_type` | Selection | company_id.stock_confirmation_type | Stock Text Validation type |
| `horizon_days` | Float | — |  |

## `ResPartner` ← res.partner
Файл: `odoo/addons/stock/models/res_partner.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `property_stock_customer` | Many2one | stock.location | Customer Location |
| `property_stock_supplier` | Many2one | stock.location | Vendor Location |
| `picking_warn_msg` | Text | — |  |

## `barcode.nomenclature`
Файл: `odoo/addons/barcodes/models/barcode_nomenclature.py`  

*Полей нет (абстрактная модель или наследование)*  

## `barcode.rule`
Файл: `odoo/addons/barcodes/models/barcode_rule.py`  

*Полей нет (абстрактная модель или наследование)*  

## `barcodes.barcode_events_mixin`
Файл: `odoo/addons/barcodes/models/barcode_events_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

## `html.field.history.mixin`
Файл: `odoo/addons/html_editor/models/html_field_history_mixin.py`  

*Полей нет (абстрактная модель или наследование)*  

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
| `name` | Char | — |  |
| `complete_name` | Char | — |  |
| `dest_complete_name` | Char | — |  |
| `quant_ids` | One2many | stock.quant |  |
| `contained_quant_ids` | One2many | stock.quant |  |
| `content_description` | Char | — |  |
| `package_type_id` | Many2one | stock.package.type |  |
| `location_id` | Many2one | stock.location |  |
| `location_dest_id` | Many2one | stock.location |  |
| `company_id` | Many2one | res.company |  |
| `owner_id` | Many2one | res.partner |  |
| `parent_package_id` | Many2one | stock.package |  |
| `child_package_ids` | One2many | stock.package | Contained Packages |
| `all_children_package_ids` | One2many | stock.package |  |
| `package_dest_id` | Many2one | stock.package |  |
| `outermost_package_id` | Many2one | stock.package |  |
| `child_package_dest_ids` | One2many | stock.package |  |
| `move_line_ids` | One2many | stock.move.line |  |
| `picking_ids` | Many2many | stock.picking | Transfers |
| `shipping_weight` | Float | — | Shipping Weight |
| `valid_sscc` | Boolean | — |  |
| `pack_date` | Date | — |  |
| `parent_path` | Char | — |  |
| `json_popover` | Char | — |  |

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

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `sequence` | Integer | — |  |
| `sequence_id` | Many2one | ir.sequence |  |
| `sequence_code` | Char | — |  |
| `height` | Float | — |  |
| `width` | Float | — |  |
| `packaging_length` | Float | — |  |
| `base_weight` | Float | — | Weight |
| `max_weight` | Float | — |  |
| `barcode` | Char | — |  |
| `weight_uom_name` | Char | — | Weight unit of measure label |
| `length_uom_name` | Char | — | Length unit of measure label |
| `company_id` | Many2one | res.company |  |
| `package_use` | Selection | disposable,reusable | Package Use |
| `has_quants` | Boolean | — |  |
| `storage_category_capacity_ids` | One2many | stock.storage.category.capacity |  |
| `route_ids` | Many2many | stock.route | Routes |

## `stock.quant`
*Quants*  
Файл: `odoo/addons/stock/models/stock_quant.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `product_id` | Many2one | product.product |  |
| `product_tmpl_id` | Many2one | product.template | Product Template |
| `product_uom_id` | Many2one | uom.uom |  |
| `is_favorite` | Boolean | — |  |
| `company_id` | Many2one | ? | Company |
| `location_id` | Many2one | stock.location |  |
| `warehouse_id` | Many2one | stock.warehouse |  |
| `storage_category_id` | Many2one | ? |  |
| `cyclic_inventory_frequency` | Integer | — |  |
| `lot_id` | Many2one | stock.lot |  |
| `sn_duplicated` | Boolean | — | Duplicated Serial Number |
| `package_id` | Many2one | stock.package |  |
| `owner_id` | Many2one | res.partner |  |
| `quantity` | Float | — |  |
| `reserved_quantity` | Float | — |  |
| `available_quantity` | Float | — |  |
| `in_date` | Datetime | — |  |
| `tracking` | Selection | product_id.tracking |  |
| `on_hand` | Boolean | — |  |
| `product_categ_id` | Many2one | ? |  |
| `inventory_quantity` | Float | — |  |
| `inventory_quantity_auto_apply` | Float | — |  |
| `inventory_diff_quantity` | Float | — |  |
| `inventory_date` | Date | — |  |
| `last_count_date` | Date | — |  |
| `inventory_quantity_set` | Boolean | — |  |
| `is_outdated` | Boolean | — |  |
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

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `route_id` | Many2one | stock.route | Preferred Route |
| `allowed_route_ids` | Many2many | stock.route |  |

## `stock.rule`
*Stock Rule*  
Файл: `odoo/addons/stock/models/stock_rule.py`  

| Поле | Тип | Связь / Выбор | Описание |
|------|-----|---------------|----------|
| `name` | Char | — |  |
| `active` | Boolean | — |  |
| `action` | Selection | pull,push,pull_push | Action |
| `sequence` | Integer | — |  |
| `company_id` | Many2one | res.company |  |
| `location_dest_id` | Many2one | stock.location |  |
| `location_src_id` | Many2one | stock.location |  |
| `location_dest_from_rule` | Boolean | — |  |
| `route_id` | Many2one | stock.route |  |
| `route_company_id` | Many2one | ? | Route Company |
| `procure_method` | Selection | make_to_stock,make_to_order,mts_else_mto | Supply Method |
| `route_sequence` | Integer | — |  |
| `picking_type_id` | Many2one | stock.picking.type |  |
| `picking_type_code_domain` | Json | — |  |
| `delay` | Integer | — |  |
| `partner_address_id` | Many2one | res.partner |  |
| `propagate_cancel` | Boolean | — |  |
| `propagate_carrier` | Boolean | — |  |
| `warehouse_id` | Many2one | stock.warehouse |  |
| `auto` | Selection | manual,transparent | Automatic Move |
| `rule_message` | Html | — |  |
| `push_domain` | Char | — |  |

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
| `name` | Char | — |  |
| `trigger` | Selection | auto,manual | Trigger |
| `active` | Boolean | — |  |
| `snoozed_until` | Date | — |  |
| `warehouse_id` | Many2one | stock.warehouse |  |
| `location_id` | Many2one | stock.location |  |
| `product_tmpl_id` | Many2one | product.template |  |
| `product_id` | Many2one | product.product |  |
| `product_category_id` | Many2one | product.category |  |
| `product_uom` | Many2one | uom.uom |  |
| `product_uom_name` | Char | — | Product unit of measure label |
| `product_min_qty` | Float | — |  |
| `product_max_qty` | Float | — |  |
| `allowed_replenishment_uom_ids` | Many2many | uom.uom |  |
| `replenishment_uom_id` | Many2one | uom.uom |  |
| `replenishment_uom_id_placeholder` | Char | — |  |
| `company_id` | Many2one | res.company |  |
| `allowed_location_ids` | One2many | stock.location |  |
| `rule_ids` | Many2many | stock.rule | Rules used |
| `lead_horizon_date` | Date | — |  |
| `lead_days` | Float | — |  |
| `route_id` | Many2one | stock.route | Route |
| `route_id_placeholder` | Char | — |  |
| `effective_route_id` | Many2one | stock.route |  |
| `qty_on_hand` | Float | — |  |
| `qty_forecast` | Float | — |  |
| `qty_to_order` | Float | — |  |
| `qty_to_order_computed` | Float | — |  |
| `qty_to_order_manual` | Float | — |  |
| `days_to_order` | Float | — |  |
| `unwanted_replenish` | Boolean | — |  |
| `show_supply_warning` | Boolean | — |  |
| `deadline_date` | Date | — |  |
