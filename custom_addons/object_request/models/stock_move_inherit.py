from odoo import fields, models


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

    object_request_stock_id = fields.Many2one(
        "object.request.line.stock",
        string="Распределение требования",
        index=True,
        copy=False,
        ondelete="set null",
    )

    def _prepare_move_split_vals(self, qty):
        """Остаток в backorder остаётся привязан к распределению заявки."""
        vals = super()._prepare_move_split_vals(qty)
        if self.object_request_stock_id:
            vals["object_request_stock_id"] = self.object_request_stock_id.id
        return vals

    # --- TD-017: резерв выдачи по требованию входит в «Обеспечено» ---

    def _recompute_state(self):
        """После смены резерва обновить «Зарезервировано» в требовании."""
        result = super()._recompute_state()
        self._sync_object_request_issue_reserve()
        return result

    def _action_cancel(self):
        """Отменённое движение выдачи больше не обеспечивает строку."""
        result = super()._action_cancel()
        self._sync_object_request_issue_reserve()
        return result

    def _sync_object_request_issue_reserve(self):
        issue_moves = self.filtered(
            lambda move: move.picking_id.is_object_request_issue
        )
        if not issue_moves:
            return
        # Служебная синхронизация: кладовщик и складской пользователь
        # не имеют права записи в распределения требования.
        stocks = issue_moves.sudo().object_request_stock_id
        stocks |= self.env["object.request.line.stock"].sudo().search(
            [("move_id", "in", issue_moves.ids)]
        )
        stocks.mapped("line_id")._sync_issue_reserve_from_moves()
