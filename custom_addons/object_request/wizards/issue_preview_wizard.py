from odoo import api, fields, models
from odoo.exceptions import UserError


class ObjectRequestIssuePreviewWizard(models.TransientModel):
    _name = "object.request.issue.preview.wizard"
    _description = "Предпросмотр выдач по складам"

    request_id = fields.Many2one(
        "object.request",
        string="Требование",
        required=True,
        readonly=True,
        ondelete="cascade",
    )
    group_ids = fields.One2many(
        "object.request.issue.preview.group",
        "wizard_id",
        string="Выдачи по складам",
    )
    group_count = fields.Integer(compute="_compute_group_count")

    @api.depends("group_ids")
    def _compute_group_count(self):
        for wizard in self:
            wizard.group_count = len(wizard.group_ids)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        request_id = self.env.context.get("default_request_id")
        if not request_id:
            return res
        request = self.env["object.request"].browse(request_id)
        stock_ids = request.line_ids.mapped("stock_ids").filtered(
            lambda stock: stock.qty_to_issue > 0 and stock.line_id.product_id
        )
        groups_by_warehouse = {}
        for stock in stock_ids:
            groups_by_warehouse.setdefault(
                stock.warehouse_id, self.env["object.request.line.stock"]
            )
            groups_by_warehouse[stock.warehouse_id] |= stock

        customer_loc = self.env.ref(
            "stock.stock_location_customers",
            raise_if_not_found=False,
        )
        group_vals = []
        for warehouse, warehouse_stock_ids in groups_by_warehouse.items():
            if not warehouse:
                raise UserError(
                    "В строках распределения требования не заполнено поле склада задания. "
                    "Проверьте распределение по складам перед созданием выдачи."
                )
            group_vals.append(
                (
                    0,
                    0,
                    {
                        "picking_type_id": warehouse.int_type_id.id,
                        "source_location_id": warehouse.lot_stock_id.id,
                        "destination_location_id": customer_loc.id
                        if customer_loc
                        else False,
                        "scheduled_date": fields.Datetime.now(),
                        "included": True,
                        "stock_line_ids": [(6, 0, warehouse_stock_ids.ids)],
                    },
                )
            )
        res.update(
            {
                "request_id": request.id,
                "group_ids": group_vals,
            }
        )
        return res

    def _relink_issue_preview_stock_lines(self):
        """Веб-клиент может обнулить M2m строк при переключении «Создать» — подставляем из требования."""
        request = self.request_id
        stock_ids = request.line_ids.mapped("stock_ids").filtered(
            lambda stock: stock.qty_to_issue > 0 and stock.line_id.product_id
        )
        by_wh = {}
        Stock = request.env["object.request.line.stock"]
        for stock in stock_ids:
            if not stock.warehouse_id:
                raise UserError(
                    "В строках распределения требования не заполнено поле склада задания. "
                    "Проверьте распределение по складам перед созданием выдачи."
                )
            by_wh.setdefault(stock.warehouse_id.id, Stock)
            by_wh[stock.warehouse_id.id] |= stock

        for group in self.group_ids.filtered("included"):
            wh = group.picking_type_id.warehouse_id
            if not wh:
                raise UserError(
                    "Не удалось определить склад по типу операции группы предпросмотра."
                )
            lines = by_wh.get(wh.id)
            if not lines:
                raise UserError(
                    f"Для склада «{wh.name}» не найдено строк распределения с количеством к выдаче."
                )
            group.write({"stock_line_ids": [(6, 0, lines.ids)]})

    def action_create_issues(self):
        self.ensure_one()
        self._relink_issue_preview_stock_lines()
        groups = self.group_ids.filtered("included")
        if not groups:
            raise UserError("Нет выбранных складов для создания выдач.")
        pickings = self.env["stock.picking"]
        for group in groups:
            pickings |= group._create_picking()
        self.request_id.write(
            {
                "issue_picking_ids": [(4, picking.id) for picking in pickings],
            }
        )
        return {
            "type": "ir.actions.act_window",
            "name": "Выдачи",
            "res_model": "stock.picking",
            "view_mode": "list,form",
            "domain": [("id", "in", pickings.ids)],
            "target": "current",
        }


class ObjectRequestIssuePreviewGroup(models.TransientModel):
    _name = "object.request.issue.preview.group"
    _description = "Группа выдачи по складу"
    _order = "warehouse_id"

    wizard_id = fields.Many2one(
        "object.request.issue.preview.wizard",
        required=True,
        ondelete="cascade",
    )
    picking_type_id = fields.Many2one(
        "stock.picking.type",
        string="Тип операции",
        required=True,
    )
    source_location_id = fields.Many2one(
        "stock.location",
        string="Откуда",
        required=True,
    )
    destination_location_id = fields.Many2one(
        "stock.location",
        string="Куда",
        required=True,
    )
    scheduled_date = fields.Datetime(
        string="Дата выдачи",
        required=True,
        default=fields.Datetime.now,
    )
    comment = fields.Text(string="Комментарий")
    included = fields.Boolean(string="Создать", default=True)
    stock_line_ids = fields.Many2many(
        "object.request.line.stock",
        "object_request_issue_preview_group_stock_rel",
        "group_id",
        "stock_line_id",
        string="Строки распределения",
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Склад",
        compute="_compute_warehouse_id",
        store=True,
        readonly=True,
    )
    line_count = fields.Integer(compute="_compute_totals", string="Строк")
    qty_total = fields.Float(
        compute="_compute_totals",
        string="Количество",
        digits="Product Unit of Measure",
    )

    @api.depends("stock_line_ids", "stock_line_ids.warehouse_id")
    def _compute_warehouse_id(self):
        """Склад берётся из строк распределения (не допускает потери склада через UI)."""
        for group in self:
            stocks = group.stock_line_ids.filtered(lambda stock: stock.warehouse_id)
            group.warehouse_id = stocks[:1].warehouse_id

    @api.depends("stock_line_ids", "stock_line_ids.qty_to_issue")
    def _compute_totals(self):
        for group in self:
            group.line_count = len(group.stock_line_ids)
            group.qty_total = sum(group.stock_line_ids.mapped("qty_to_issue"))

    @api.onchange("picking_type_id")
    def _onchange_picking_type_id(self):
        for group in self:
            if group.picking_type_id.default_location_src_id:
                group.source_location_id = (
                    group.picking_type_id.default_location_src_id
                )
            if group.picking_type_id.default_location_dest_id:
                group.destination_location_id = (
                    group.picking_type_id.default_location_dest_id
                )

    def _create_picking(self):
        self.ensure_one()
        stock_lines = self.stock_line_ids.filtered(
            lambda stock: stock.qty_to_issue > 0
        )
        if not stock_lines:
            wh_label = self.warehouse_id.name if self.warehouse_id else "неизвестен"
            raise UserError(f"Нет строк к выдаче по складу {wh_label}.")
        picking = self.env["stock.picking"].create(
            {
                "picking_type_id": self.picking_type_id.id,
                "location_id": self.source_location_id.id,
                "location_dest_id": self.destination_location_id.id,
                "origin": self.wizard_id.request_id.name,
                "scheduled_date": self.scheduled_date,
                "is_object_request_issue": True,
                "object_request_project_id": (
                    self.wizard_id.request_id.project_id.id
                ),
            }
        )
        move_vals = []
        for stock_line in stock_lines:
            line = stock_line.line_id
            uom = line.uom_id or line.product_id.uom_id
            move_vals.append(
                {
                    "picking_id": picking.id,
                    "product_id": line.product_id.id,
                    "product_uom_qty": stock_line.qty_to_issue,
                    "product_uom": uom.id,
                    "location_id": self.source_location_id.id,
                    "location_dest_id": self.destination_location_id.id,
                }
            )
        moves = self.env["stock.move"].create(move_vals)
        for stock_line, move in zip(stock_lines, moves):
            stock_line.write(
                {
                    "picking_id": picking.id,
                    "move_id": move.id,
                }
            )
            stock_line.line_id.write(
                {
                    "issue_picking_id": picking.id,
                    "issue_move_id": move.id,
                }
            )
        picking.action_assign()
        for stock_line, move in zip(stock_lines, moves):
            qty_reserved = sum(ml.quantity for ml in move.move_line_ids)
            stock_line.write({"qty_reserved": qty_reserved})
            stock_line.line_id.write(
                {
                    "qty_reserved": qty_reserved,
                    "issue_reserved": qty_reserved > 0,
                }
            )
        return picking
