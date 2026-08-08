from odoo import fields, models


class CalendarEvent(models.Model):
    _inherit = "calendar.event"

    object_request_id = fields.Many2one(
        "object.request",
        string="Требование",
        index=True,
        ondelete="set null",
        copy=False,
    )
    source_bill_id = fields.Many2one(
        "account.move",
        string="Исходный счёт поставщика",
        index=True,
        ondelete="set null",
        copy=False,
        domain="[('move_type', '=', 'in_invoice')]",
    )

    _object_request_bill_unique = models.Constraint(
        "UNIQUE(object_request_id, source_bill_id)",
        "Для одного требования и счёта поставщика может быть только одна "
        "встреча.",
    )
