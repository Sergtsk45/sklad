from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class ObjectRequest(models.Model):
    _name = "object.request"
    _description = "Object Supply Request"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "create_date desc, id desc"

    # --- Основные поля ---
    name = fields.Char(
        string="Номер документа",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        tracking=True,
    )
    project_id = fields.Many2one(
        "object.request.project",
        string="Объект",
        required=True,
        tracking=True,
        index=True,
    )
    foreman_user_id = fields.Many2one(
        "res.users",
        string="Прораб",
        required=True,
        tracking=True,
        index=True,
    )
    need_date = fields.Date(
        string="Дата потребности",
        required=True,
        tracking=True,
        index=True,
    )
    priority = fields.Selection(
        [
            ("0", "Низкий"),
            ("1", "Обычный"),
            ("2", "Высокий"),
            ("3", "Критический"),
        ],
        string="Приоритет",
        default="1",
        required=True,
        tracking=True,
        index=True,
    )
    comment = fields.Text(string="Комментарий")
    state = fields.Selection(
        [
            ("draft", "Черновик"),
            ("in_progress", "В работе"),
            ("closed", "Закрыто"),
            ("cancelled", "Отменено"),
        ],
        string="Статус",
        default="draft",
        required=True,
        tracking=True,
        index=True,
    )
    active = fields.Boolean(default=True)

    # --- Строки ---
    line_ids = fields.One2many(
        "object.request.line",
        "request_id",
        string="Строки",
        copy=True,
    )
    line_stock_ids = fields.Many2many(
        "object.request.line.stock",
        compute="_compute_line_stock_ids",
        string="Распределение по складам",
    )

    # --- Поля импорта ---
    source_file_name = fields.Char(string="Имя файла")
    source_file_checksum = fields.Char(string="Контрольная сумма", index=True)
    imported_at = fields.Datetime(string="Дата импорта", readonly=True)
    imported_by_user_id = fields.Many2one(
        "res.users",
        string="Импортировал",
        readonly=True,
    )

    # --- Поля процесса ---
    matching_state = fields.Selection(
        [
            ("all_matched", "Все сопоставлено"),
            ("partial", "Есть проблемы"),
            ("requires_mapping", "Требует сопоставления"),
        ],
        string="Статус сопоставления",
        compute="_compute_matching_state",
        store=True,
        index=True,
    )
    approval_state = fields.Selection(
        [
            ("not_required", "Не требуется"),
            ("pending", "Ожидает согласования"),
            ("approved", "Согласовано"),
            ("rejected", "Отклонено"),
        ],
        string="Согласование",
        default="not_required",
        tracking=True,
    )

    # --- Ролевые поля ---
    buyer_user_id = fields.Many2one(
        "res.users", string="Снабженец", tracking=True
    )
    warehouse_user_id = fields.Many2one(
        "res.users", string="Кладовщик", tracking=True
    )
    approver_user_id = fields.Many2one(
        "res.users",
        string="Согласующий",
        tracking=True,
    )

    # --- Связи с документами Odoo ---
    issue_picking_ids = fields.Many2many(
        "stock.picking",
        "object_request_stock_picking_rel",
        "request_id",
        "picking_id",
        string="Выдачи",
    )
    issue_picking_count = fields.Integer(
        compute="_compute_issue_picking_count"
    )

    purchase_order_ids = fields.Many2many(
        "purchase.order",
        "object_request_purchase_order_rel",
        "request_id",
        "purchase_id",
        string="Закупки",
    )
    purchase_order_count = fields.Integer(
        compute="_compute_purchase_order_count"
    )

    # --- Агрегатные счётчики ---
    line_count = fields.Integer(compute="_compute_line_count", string="Строк")
    line_problem_count = fields.Integer(
        compute="_compute_line_counters", store=True
    )
    line_matched_count = fields.Integer(
        compute="_compute_line_counters", store=True
    )
    line_to_issue_count = fields.Integer(
        compute="_compute_line_counters", store=True
    )
    line_to_buy_count = fields.Integer(
        compute="_compute_line_counters", store=True
    )
    line_fully_supplied_count = fields.Integer(
        compute="_compute_line_counters",
        store=True,
    )

    # --- Количественные агрегаты ---
    qty_total_requested = fields.Float(
        compute="_compute_qty_totals", store=True
    )
    qty_total_to_issue = fields.Float(
        compute="_compute_qty_totals", store=True
    )
    qty_total_to_buy = fields.Float(compute="_compute_qty_totals", store=True)
    qty_total_issued = fields.Float(compute="_compute_qty_totals", store=True)
    qty_total_reserved = fields.Float(
        compute="_compute_qty_totals", store=True
    )

    # --- Служебные поля ---
    company_id = fields.Many2one(
        "res.company",
        string="Компания",
        required=True,
        default=lambda self: self.env.company,
        index=True,
    )
    currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        store=True,
    )

    _name_uniq = models.Constraint(
        "UNIQUE(name)",
        "Номер документа должен быть уникальным.",
    )

    # --- Создание с автонумерацией ---
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = (
                    self.env["ir.sequence"]
                    .sudo()
                    .next_by_code("object.request.sequence")
                    or "New"
                )
        return super().create(vals_list)

    # --- Computed methods ---
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(rec.line_ids)

    @api.depends("line_ids.stock_ids")
    def _compute_line_stock_ids(self):
        for rec in self:
            rec.line_stock_ids = rec.line_ids.mapped("stock_ids")

    @api.depends("line_ids.matching_required", "line_ids.product_id")
    def _compute_matching_state(self):
        for rec in self:
            if not rec.line_ids:
                rec.matching_state = "all_matched"
                continue
            problem = sum(
                1
                for ln in rec.line_ids
                if ln.matching_required or not ln.product_id
            )
            if problem == 0:
                rec.matching_state = "all_matched"
            elif problem == len(rec.line_ids):
                rec.matching_state = "requires_mapping"
            else:
                rec.matching_state = "partial"

    @api.depends(
        "line_ids.line_state",
        "line_ids.matching_required",
        "line_ids.manual_vendor_required",
        "line_ids.qty_to_issue",
        "line_ids.qty_to_buy",
    )
    def _compute_line_counters(self):
        for rec in self:
            lns = rec.line_ids
            rec.line_problem_count = sum(
                1
                for ln in lns
                if ln.matching_required or ln.manual_vendor_required
            )
            rec.line_matched_count = sum(
                1 for ln in lns if not ln.matching_required and ln.product_id
            )
            rec.line_to_issue_count = sum(
                1 for ln in lns if ln.qty_to_issue > 0
            )
            rec.line_to_buy_count = sum(1 for ln in lns if ln.qty_to_buy > 0)
            rec.line_fully_supplied_count = sum(
                1 for ln in lns if ln.line_state == "fully_supplied"
            )

    @api.depends(
        "line_ids.qty_requested",
        "line_ids.qty_to_issue",
        "line_ids.qty_to_buy",
        "line_ids.qty_issued",
        "line_ids.qty_reserved",
    )
    def _compute_qty_totals(self):
        for rec in self:
            lns = rec.line_ids
            rec.qty_total_requested = sum(ln.qty_requested for ln in lns)
            rec.qty_total_to_issue = sum(ln.qty_to_issue for ln in lns)
            rec.qty_total_to_buy = sum(ln.qty_to_buy for ln in lns)
            rec.qty_total_issued = sum(ln.qty_issued for ln in lns)
            rec.qty_total_reserved = sum(ln.qty_reserved for ln in lns)

    def _compute_issue_picking_count(self):
        for rec in self:
            rec.issue_picking_count = len(rec.issue_picking_ids)

    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.purchase_order_ids)

    # --- Методы согласования ---
    def action_submit_for_approval(self):
        """Отправить документ на согласование."""
        self.ensure_one()
        if not self.approver_user_id:
            raise UserError(
                "Укажите согласующего перед отправкой на согласование."
            )
        if self.approval_state == "pending":
            raise UserError("Документ уже отправлен на согласование.")
        self.write({"approval_state": "pending"})
        self.message_post(
            body=(
                f"Требование отправлено на согласование. "
                f"Согласующий: {self.approver_user_id.name}."
            ),
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=[self.approver_user_id.partner_id.id],
        )

    def action_approve(self):
        """Согласовать документ."""
        self.ensure_one()
        self.write({"approval_state": "approved"})
        partner_ids = [
            p.id
            for p in (
                self.foreman_user_id.partner_id | self.buyer_user_id.partner_id
            )
            if p
        ]
        self.message_post(
            body=(
                f"Требование согласовано ({self.env.user.name}). "
                "Документ можно перевести в работу."
            ),
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=partner_ids,
        )

    def action_reject(self):
        """Отклонить документ."""
        self.ensure_one()
        self.write({"approval_state": "rejected"})
        partner_ids = [
            p.id
            for p in (
                self.foreman_user_id.partner_id | self.buyer_user_id.partner_id
            )
            if p
        ]
        self.message_post(
            body=(
                f"Требование отклонено ({self.env.user.name}). "
                "Исправьте замечания и повторно отправьте на согласование."
            ),
            message_type="notification",
            subtype_xmlid="mail.mt_note",
            partner_ids=partner_ids,
        )

    # --- Методы смены статуса ---
    def action_in_progress(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError("Нельзя перевести документ в работу без строк.")
        if self.approval_state == "pending":
            raise UserError(
                "Документ ожидает согласования. "
                "Дождитесь решения согласующего."
            )
        if self.approval_state == "rejected":
            raise UserError(
                "Документ отклонён согласующим. "
                "Исправьте замечания и повторно отправьте на согласование."
            )
        unmatched = self.line_ids.filtered(
            lambda ln: ln.matching_required or not ln.product_id
        )
        if unmatched:
            return {
                "type": "ir.actions.act_window",
                "name": "Предупреждение",
                "res_model": "object.request.confirm.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_request_id": self.id,
                    "default_action_type": "in_progress",
                    "default_message": (
                        f"Несопоставленных строк: {len(unmatched)}. "
                        "Они потребуют ручного сопоставления снабженцем. "
                        "Перевести документ в работу?"
                    ),
                },
            }
        self.write({"state": "in_progress"})

    def action_close(self):
        self.ensure_one()
        unprocessed = self.line_ids.filtered(
            lambda ln: ln.line_state not in ("fully_supplied", "cancelled")
        )
        if unprocessed:
            return {
                "type": "ir.actions.act_window",
                "name": "Подтверждение закрытия",
                "res_model": "object.request.confirm.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_request_id": self.id,
                    "default_action_type": "close",
                    "default_message": (
                        f"{len(unprocessed)} строк не полностью обработаны "
                        "(не полностью обеспечены и не отменены). "
                        "Закрыть документ несмотря на это?"
                    ),
                },
            }
        self.write({"state": "closed"})

    def action_cancel(self):
        for rec in self:
            for picking in rec.issue_picking_ids.filtered(
                lambda p: p.state in ("confirmed", "assigned", "waiting")
            ):
                picking.do_unreserve()
            rec.line_ids.write({"qty_reserved": 0.0, "issue_reserved": False})
        self.write({"state": "cancelled"})

    # --- Smart button actions ---
    def action_open_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Строки требования",
            "res_model": "object.request.line",
            "view_mode": "list",
            "domain": [("request_id", "=", self.id)],
            "context": {"default_request_id": self.id},
        }

    def action_open_problem_lines(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Проблемные строки",
            "res_model": "object.request.line",
            "view_mode": "list",
            "domain": [
                ("request_id", "=", self.id),
                "|",
                ("matching_required", "=", True),
                ("manual_vendor_required", "=", True),
            ],
            "context": {"default_request_id": self.id},
        }

    def action_open_issue_pickings(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Выдачи",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "domain": [("id", "in", self.issue_picking_ids.ids)],
        }

    def action_open_purchase_orders(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Закупки",
            "res_model": "purchase.order",
            "view_mode": "list,form",
            "domain": [("id", "in", self.purchase_order_ids.ids)],
        }

    def action_lines_buy_all(self):
        self.ensure_one()
        self.line_ids.action_buy_all()
        return self._line_mass_action_notification("Закупить всё")

    def action_lines_issue_max(self):
        self.ensure_one()
        self.line_ids.action_issue_max()
        return self._line_mass_action_notification("Выдать максимум")

    def action_lines_reset_split(self):
        self.ensure_one()
        self.line_ids.action_reset_split()
        return self._line_mass_action_notification("Сбросить разбивку")

    def _line_mass_action_notification(self, title):
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": f"Обработано строк: {len(self.line_ids)}.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_rematch_lines(self):
        """Повторно запустить автосопоставление по несопоставленным строкам."""
        self.ensure_one()
        parser = self.env["object.request.excel.parser"]
        unmatched = self.line_ids.filtered(
            lambda ln: ln.matching_required or not ln.product_id
        )
        if not unmatched:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": "Пересопоставление",
                    "message": "Нет строк, требующих сопоставления.",
                    "type": "info",
                    "sticky": False,
                },
            }
        newly_matched = 0
        for line in unmatched:
            result = parser.match_row(
                line.supplier_article, line.name_raw, line.supplier_raw
            )
            vals = {
                "matching_required": result["matching_required"],
                "manual_vendor_required": result["manual_vendor_required"],
            }
            if result["product"]:
                vals["product_id"] = result["product"].id
                vals["uom_id"] = result["product"].uom_id.id
                if not line.preferred_vendor_id:
                    if result["vendor"]:
                        vals["preferred_vendor_id"] = result["vendor"].id
                    elif result["product"].seller_ids:
                        vals["preferred_vendor_id"] = (
                            result["product"].seller_ids[0].partner_id.id
                        )
                newly_matched += 1
            elif result["vendor"] and not line.preferred_vendor_id:
                vals["preferred_vendor_id"] = result["vendor"].id
            line.write(vals)
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Пересопоставление завершено",
                "message": (
                    f"Обработано {len(unmatched)} строк. "
                    f"Сопоставлено новых: {newly_matched}."
                ),
                "type": "success" if newly_matched else "warning",
                "sticky": False,
            },
        }

    def _notify_if_all_lines_supplied(self):
        """Уведомить, если все активные строки полностью обеспечены."""
        self.ensure_one()
        active_lines = self.line_ids.filtered(lambda ln: not ln.is_cancelled)
        if not active_lines:
            return
        if all(ln.line_state == "fully_supplied" for ln in active_lines):
            self.message_post(
                body=(
                    "Все строки требования полностью обеспечены. "
                    "Документ можно закрыть."
                ),
                message_type="notification",
                subtype_xmlid="mail.mt_note",
            )

    def action_check_stock(self):
        """Проверить остатки по всем активным складам компании."""
        self.ensure_one()
        warehouses = self.env["stock.warehouse"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("active", "=", True),
            ]
        )
        lines = self.line_ids.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled
        )
        if not lines:
            raise UserError(
                "Нет строк с сопоставленным товаром для проверки наличия."
            )
        qty_by_product_warehouse = self._get_stock_qty_by_product_warehouse(
            lines.mapped("product_id"),
            warehouses,
        )
        now = fields.Datetime.now()
        stock_model = self.env["object.request.line.stock"].with_context(
            auto_stock_distribution=True,
            stock_check_only=True,
        )
        for line in lines:
            existing_by_warehouse = {
                stock.warehouse_id.id: stock for stock in line.stock_ids
            }
            for warehouse in warehouses:
                qty = qty_by_product_warehouse.get(
                    (line.product_id.id, warehouse.id),
                    0.0,
                )
                stock = existing_by_warehouse.get(warehouse.id)
                vals = {"qty_on_hand": qty, "last_check_date": now}
                if stock:
                    stock.with_context(
                        auto_stock_distribution=True,
                        stock_check_only=True,
                    ).write(vals)
                else:
                    stock_model.create(
                        {
                            "line_id": line.id,
                            "warehouse_id": warehouse.id,
                            **vals,
                        }
                    )
            stale_stock_ids = line.stock_ids.filtered(
                lambda stock: stock.warehouse_id not in warehouses
            )
            if stale_stock_ids:
                stale_stock_ids.with_context(
                    auto_stock_distribution=True
                ).unlink()
        lines_with_stock = lines.filtered(lambda ln: ln.stock_qty_on_hand > 0)
        if lines_with_stock:
            return {
                "type": "ir.actions.act_window",
                "name": "Проверка актуальности требования",
                "res_model": "object.request.stock.check.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {"default_request_id": self.id},
            }
        found = len(lines_with_stock)
        total = len(lines)
        if found:
            msg = f"Найдено {found} из {total} позиций."
            ntype = "success"
        else:
            msg = (
                f"Ни одна из {total} позиций не найдена на выбранных складах."
            )
            ntype = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Расчёт наличия выполнен",
                "message": msg,
                "type": ntype,
                "sticky": False,
            },
        }

    def _get_stock_qty_by_product_warehouse(self, products, warehouses):
        locations_by_warehouse = self._get_stock_locations_by_warehouse(
            warehouses
        )
        all_locations = self.env["stock.location"].browse()
        for locations in locations_by_warehouse.values():
            all_locations |= locations
        if not products or not all_locations:
            return {}

        result = {}
        location_to_warehouse = {}
        for warehouse_id, locations in locations_by_warehouse.items():
            for location in locations:
                location_to_warehouse[location.id] = warehouse_id

        groups = self.env["stock.quant"].read_group(
            [
                ("product_id", "in", products.ids),
                ("location_id", "in", all_locations.ids),
            ],
            [
                "product_id",
                "location_id",
                "quantity:sum",
                "reserved_quantity:sum",
            ],
            ["product_id", "location_id"],
            lazy=False,
        )
        for group in groups:
            product_id = group["product_id"][0]
            location_id = group["location_id"][0]
            warehouse_id = location_to_warehouse.get(location_id)
            if not warehouse_id:
                continue
            qty = group.get("quantity", 0.0) - group.get(
                "reserved_quantity", 0.0
            )
            key = (product_id, warehouse_id)
            result[key] = result.get(key, 0.0) + max(qty, 0.0)
        return result

    def _get_stock_locations_by_warehouse(self, warehouses):
        locations_by_warehouse = {}
        location_model = self.env["stock.location"].with_context(
            active_test=False
        )
        for warehouse in warehouses:
            root = warehouse.view_location_id or warehouse.lot_stock_id
            if not root:
                locations_by_warehouse[warehouse.id] = location_model.browse()
                continue
            locations_by_warehouse[warehouse.id] = location_model.search(
                [
                    ("id", "child_of", root.id),
                    ("usage", "=", "internal"),
                ]
            )
        return locations_by_warehouse

    def action_auto_split(self):
        """Авто-разбивка по складам с минимизацией числа складов."""
        self.ensure_one()
        lines = self.line_ids.filtered(
            lambda ln: ln.product_id and not ln.is_cancelled
        )
        if not lines:
            raise UserError(
                "Нет строк с сопоставленным товаром для авто-разбивки."
            )
        not_checked = lines.filtered(lambda ln: not ln.stock_check_date)
        if not_checked:
            raise UserError(
                "Сначала выполните расчёт наличия "
                "(кнопка «Рассчитать наличие»)."
            )
        manual_lines = lines.filtered("manual_plan_override")
        if manual_lines and not self.env.context.get("force_auto_split"):
            return {
                "type": "ir.actions.act_window",
                "name": "Перезаписать распределение?",
                "res_model": "object.request.auto.split.confirm.wizard",
                "view_mode": "form",
                "target": "new",
                "context": {
                    "default_request_id": self.id,
                    "default_manual_line_count": len(manual_lines),
                },
            }
        stock_context = {"auto_stock_distribution": True}
        for line in lines:
            requested = max(line.qty_requested - line.qty_issued, 0.0)
            project_warehouse = line.request_id.project_id.warehouse_id
            project_stock = line.stock_ids.filtered(
                lambda stock: (
                    stock.warehouse_id == project_warehouse
                    and stock.qty_on_hand > 0
                )
            )[:1]
            other_stock_ids = (line.stock_ids - project_stock).sorted(
                key=lambda stock: stock.qty_on_hand,
                reverse=True,
            )
            stock_ids = project_stock | other_stock_ids
            stock_ids.with_context(**stock_context).write(
                {
                    "qty_to_issue": 0.0,
                }
            )
            remaining = requested
            single_stock = next(
                (
                    stock
                    for stock in stock_ids
                    if (
                        stock.qty_on_hand >= requested
                        and stock.id not in project_stock.ids
                    )
                ),
                False,
            )
            if single_stock and not project_stock:
                single_stock.with_context(**stock_context).write(
                    {
                        "qty_to_issue": requested,
                    }
                )
                remaining = 0.0
            else:
                for stock in stock_ids:
                    if remaining <= 0:
                        break
                    qty = min(max(stock.qty_on_hand, 0.0), remaining)
                    if qty <= 0:
                        continue
                    stock.with_context(**stock_context).write(
                        {
                            "qty_to_issue": qty,
                        }
                    )
                    remaining -= qty
            qty_to_issue = sum(line.stock_ids.mapped("qty_to_issue"))
            qty_to_buy = requested - qty_to_issue
            if qty_to_issue > 0 and qty_to_buy > 0:
                mode = "mixed"
            elif qty_to_issue > 0:
                mode = "issue"
            elif qty_to_buy > 0:
                mode = "buy"
            else:
                mode = "manual"
            line.write(
                {
                    "qty_to_issue": qty_to_issue,
                    "qty_to_buy": qty_to_buy,
                    "procurement_mode": mode,
                    "manual_plan_override": False,
                }
            )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Авто-разбивка выполнена",
                "message": f"Обработано строк: {len(lines)}.",
                "type": "success",
                "sticky": False,
            },
        }

    def action_open_issue_wizard(self):
        """Открыть wizard создания выдачи со склада."""
        self.ensure_one()
        stock_to_issue = self.line_ids.mapped("stock_ids").filtered(
            lambda stock: stock.qty_to_issue > 0 and stock.line_id.product_id
        )
        if not stock_to_issue:
            raise UserError(
                "Нет строк с заполненным количеством к выдаче. "
                "Заполните распределение по складам."
            )
        return {
            "type": "ir.actions.act_window",
            "name": "Создать выдачи",
            "res_model": "object.request.issue.preview.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
            },
        }

    def action_open_purchase_wizard(self):
        """Открыть wizard создания черновиков закупки."""
        self.ensure_one()
        lines_to_buy = self.line_ids.filtered(
            lambda ln: ln.qty_to_buy > 0 and ln.product_id
        )
        if not lines_to_buy:
            raise UserError(
                "Нет строк с товаром и количеством к закупке. "
                "Заполните поле «К закупке» в строках документа."
            )
        return {
            "type": "ir.actions.act_window",
            "name": "Создать закупки",
            "res_model": "object.request.purchase.wizard",
            "view_mode": "form",
            "target": "new",
            "context": {
                "default_request_id": self.id,
            },
        }

    # --- Constraints ---
    @api.constrains("state", "line_ids")
    def _check_state_has_lines(self):
        for rec in self:
            if rec.state == "in_progress" and not rec.line_ids:
                raise ValidationError(
                    "Документ в работе должен содержать хотя бы одну строку."
                )
