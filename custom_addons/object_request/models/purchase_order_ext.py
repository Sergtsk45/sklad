from odoo import models, fields


class PurchaseOrderExt(models.Model):
    _inherit = "purchase.order"

    is_object_request_purchase = fields.Boolean(
        string="Закупка по требованию",
        default=False,
        index=True,
    )
    object_request_project_id = fields.Many2one(
        "object.request.project",
        string="Объект требования",
        index=True,
    )
    dest_warehouse_id = fields.Many2one(
        related="picking_type_id.warehouse_id",
        string="Склад",
        readonly=True,
    )
    # Reverse side of object.request.purchase_order_ids many2many
    object_request_ids = fields.Many2many(
        "object.request",
        "object_request_purchase_order_rel",
        "purchase_id",
        "request_id",
        string="Требования на комплектацию",
    )
    object_request_count = fields.Integer(
        compute="_compute_object_request_count",
        string="Требований",
    )

    def _compute_object_request_count(self):
        for rec in self:
            rec.object_request_count = len(rec.object_request_ids)

    def _get_transfer_report_filename(self):
        self.ensure_one()
        warehouse = (
            self.object_request_project_id.warehouse_id
            or self.picking_type_id.warehouse_id
        )
        suffix = (
            warehouse.display_name
            or self.object_request_project_id.display_name
        )
        invoice_ref = self.partner_ref or self.name
        return "Передаточная ведомость №%s%s" % (
            invoice_ref or "",
            " %s" % suffix if suffix else "",
        )

    def get_transfer_delivery_address_display(self):
        """Текст адреса доставки для передаточной ведомости."""
        self.ensure_one()
        if self.dest_address_id:
            partner = self.dest_address_id
            return partner.contact_address or partner.display_name
        project = self.object_request_project_id
        if not project and self.object_request_ids:
            project = self.object_request_ids[:1].project_id
        if not project:
            return False
        return (project.address or project.name or "").strip() or False

    def action_open_object_requests(self):
        self.ensure_one()
        if len(self.object_request_ids) == 1:
            return {
                "type": "ir.actions.act_window",
                "name": "Требование на комплектацию",
                "res_model": "object.request",
                "res_id": self.object_request_ids[0].id,
                "view_mode": "form",
                "target": "current",
            }
        return {
            "type": "ir.actions.act_window",
            "name": "Требования на комплектацию",
            "res_model": "object.request",
            "view_mode": "list,form",
            "domain": [("id", "in", self.object_request_ids.ids)],
            "target": "current",
        }
