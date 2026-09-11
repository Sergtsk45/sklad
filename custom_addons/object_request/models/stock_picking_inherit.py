from odoo import models, fields


class StockPickingInherit(models.Model):
    _inherit = "stock.picking"

    is_object_request_issue = fields.Boolean(
        string="Выдача по требованию",
        default=False,
        index=True,
    )
    object_request_project_id = fields.Many2one(
        "object.request.project",
        string="Объект требования",
        index=True,
    )
    # Reverse side of object.request.issue_picking_ids many2many
    object_request_ids = fields.Many2many(
        "object.request",
        "object_request_stock_picking_rel",
        "picking_id",
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

    def _get_issue_report_filename(self):
        """Имя PDF расходной накладной: номер, склад, объект назначения."""
        self.ensure_one()
        warehouse = self.picking_type_id.warehouse_id
        warehouse_name = (
            warehouse.display_name
            if warehouse
            else (self.location_id.display_name if self.location_id else "")
        )
        project = self.object_request_project_id
        if not project and self.object_request_ids:
            project = self.object_request_ids[:1].project_id
        project_name = project.display_name if project else ""
        return "Расходная накладная №%s%s%s" % (
            self.name or "",
            " %s" % warehouse_name if warehouse_name else "",
            " %s" % project_name if project_name else "",
        )

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

    # --- OBR-012: синхронизация обеспечения после подтверждения движения ---

    def _action_done(self):
        """После подтверждения выдачи/прихода обновить qty_issued."""
        result = super()._action_done()
        request_issues = self.filtered(lambda p: p.is_object_request_issue)
        if request_issues:
            request_issues._sync_qty_issued_to_request_lines()
        purchase_receipts = self.filtered(
            lambda p: p.picking_type_id.code == "incoming"
            and p.move_ids.purchase_line_id
        )
        if purchase_receipts:
            purchase_receipts._sync_qty_issued_to_request_lines()
        return result

    def _sync_qty_issued_to_request_lines(self):
        """Обновить qty_issued строк требования по done-количеству."""
        request_lines = self.env["object.request.line"]
        request_lines |= self._request_lines_from_issue_pickings()
        request_lines |= self._request_lines_from_purchase_receipts()
        request_lines.recompute_supply_state_from_done_moves()
        for request in request_lines.mapped("request_id"):
            request._notify_if_all_lines_supplied()

    def _request_lines_from_issue_pickings(self):
        lines = self.env["object.request.line"]
        for picking in self:
            stock_lines = self.env["object.request.line.stock"].search(
                [
                    ("picking_id", "=", picking.id),
                ]
            )
            lines |= stock_lines.mapped("line_id")
            lines |= self.env["object.request.line"].search(
                [
                    ("issue_picking_id", "=", picking.id),
                ]
            )
        return lines

    def _request_lines_from_purchase_receipts(self):
        purchase_lines = self.move_ids.purchase_line_id
        if not purchase_lines:
            return self.env["object.request.line"]
        return self.env["object.request.line"].search(
            [
                ("purchase_order_line_id", "in", purchase_lines.ids),
            ]
        )
