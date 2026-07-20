from odoo import api, models, fields
from odoo.exceptions import ValidationError


class ObjectRequestLineStock(models.Model):
    _name = "object.request.line.stock"
    _description = "Object Request Line Stock"
    _order = "line_id, id"
    _check_company_auto = True

    line_id = fields.Many2one(
        "object.request.line",
        string="Строка требования",
        required=True,
        ondelete="cascade",
        index=True,
    )
    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Склад",
        required=True,
        index=True,
    )
    company_id = fields.Many2one(
        "res.company",
        string="Компания",
        related="line_id.company_id",
        store=True,
    )
    qty_on_hand = fields.Float(
        string="Доступно на складе",
        digits="Product Unit of Measure",
    )
    qty_to_issue = fields.Float(
        string="К выдаче со склада",
        digits="Product Unit of Measure",
    )
    qty_planned_to_issue = fields.Float(
        string="Исходный план выдачи",
        digits="Product Unit of Measure",
        readonly=True,
    )
    qty_reserved = fields.Float(
        string="Зарезервировано",
        digits="Product Unit of Measure",
    )
    last_check_date = fields.Datetime(string="Дата проверки")
    picking_id = fields.Many2one("stock.picking", string="Выдача", index=True)
    move_id = fields.Many2one(
        "stock.move", string="Движение выдачи", index=True
    )

    _object_request_line_stock_unique = models.Constraint(
        "UNIQUE(line_id, warehouse_id)",
        "Для строки требования склад должен быть уникальным.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if "qty_planned_to_issue" not in vals:
                vals["qty_planned_to_issue"] = vals.get("qty_to_issue", 0.0)
        records = super().create(vals_list)
        records._check_qty_to_issue_limit()
        records.mapped("line_id")._sync_stock_totals_from_stock_ids()
        return records

    def write(self, vals):
        manual_qty_change = (
            "qty_to_issue" in vals
            and not self.env.context.get("auto_stock_distribution")
        )
        if (
            "qty_to_issue" in vals
            and "qty_planned_to_issue" not in vals
            and not self.env.context.get("supply_state_recompute")
        ):
            vals = dict(vals, qty_planned_to_issue=vals["qty_to_issue"])
        result = super().write(vals)
        if manual_qty_change:
            self.mapped("line_id").write({"manual_plan_override": True})
        if not self.env.context.get("skip_qty_to_issue_limit"):
            self._check_qty_to_issue_limit()
        if not self.env.context.get("skip_stock_total_sync"):
            self.mapped("line_id")._sync_stock_totals_from_stock_ids()
        return result

    def unlink(self):
        lines = self.mapped("line_id")
        result = super().unlink()
        lines._sync_stock_totals_from_stock_ids()
        return result

    def _check_qty_to_issue_limit(self):
        for line in self.mapped("line_id"):
            planned = sum(line.stock_ids.mapped("qty_to_issue"))
            allowed = max(line.qty_requested - line.qty_issued, 0.0)
            if planned > allowed + 0.00001:
                raise ValidationError(
                    "Сумма к выдаче по складам не может превышать "
                    "остаток к обеспечению."
                )
