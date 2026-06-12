from odoo import fields, models


class ObjectRequestRememberMatchingWizard(models.TransientModel):
    _name = "object.request.remember.matching.wizard"
    _description = "Подтверждение конфликтного сопоставления артикула"

    line_ids = fields.Many2many(
        "object.request.line",
        string="Строки требования",
        required=True,
    )
    message = fields.Text(string="Предупреждение", readonly=True)

    def action_confirm(self):
        self.ensure_one()
        return self.line_ids.with_context(
            confirm_supplierinfo_conflict=True
        ).action_remember_matching()
