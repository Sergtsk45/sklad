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

    # --- OBR-012: синхронизация qty_issued после подтверждения выдачи ---

    def _action_done(self):
        """После подтверждения выдачи обновить qty_issued в строках."""
        result = super()._action_done()
        request_issues = self.filtered(lambda p: p.is_object_request_issue)
        if request_issues:
            request_issues._sync_qty_issued_to_request_lines()
        return result

    def _sync_qty_issued_to_request_lines(self):
        """Обновить qty_issued строк требования по done-количеству."""
        for picking in self:
            stock_lines = self.env["object.request.line.stock"].search(
                [
                    ("picking_id", "=", picking.id),
                ]
            )
            request_lines = stock_lines.mapped("line_id") or self.env[
                "object.request.line"
            ].search(
                [
                    ("issue_picking_id", "=", picking.id),
                ]
            )
            for line in request_lines:
                issue_moves = (
                    line.stock_ids.mapped("move_id").filtered(
                        lambda move: move.exists()
                    )
                    or line.issue_move_id
                )
                if not issue_moves:
                    continue
                qty_done = sum(issue_moves.mapped("quantity"))
                line.write({"qty_issued": qty_done})
            for request in picking.object_request_ids:
                request._notify_if_all_lines_supplied()
