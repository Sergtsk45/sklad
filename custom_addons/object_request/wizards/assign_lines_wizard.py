from odoo import models, fields, api
from odoo.exceptions import UserError


class ObjectRequestLineAssignWizard(models.TransientModel):
    _name = "object.request.line.assign.wizard"
    _description = "Массовое назначение поставщика / товара для строк"

    assign_type = fields.Selection(
        [
            ("vendor", "Назначить поставщика"),
            ("product", "Назначить товар"),
        ],
        string="Тип назначения",
        required=True,
        default="vendor",
    )
    vendor_id = fields.Many2one(
        "res.partner",
        string="Поставщик",
        domain="[('supplier_rank', '>', 0)]",
    )
    product_id = fields.Many2one("product.product", string="Товар")
    line_count = fields.Integer(
        string="Строк выбрано", compute="_compute_line_count"
    )

    @api.depends()
    def _compute_line_count(self):
        for rec in self:
            rec.line_count = len(self.env.context.get("active_ids", []))

    def action_assign(self):
        active_ids = self.env.context.get("active_ids", [])
        lines = self.env["object.request.line"].browse(active_ids)
        if not lines:
            raise UserError("Не выбраны строки для обработки.")
        if self.assign_type == "vendor":
            if not self.vendor_id:
                raise UserError("Выберите поставщика.")
            lines.write(
                {
                    "preferred_vendor_id": self.vendor_id.id,
                    "manual_vendor_required": False,
                }
            )
        else:
            if not self.product_id:
                raise UserError("Выберите товар.")
            lines.write(
                {
                    "product_id": self.product_id.id,
                    "uom_id": self.product_id.uom_id.id,
                    "matching_required": False,
                }
            )
        return {"type": "ir.actions.act_window_close"}
