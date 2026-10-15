from odoo import models


class StockMoveInherit(models.Model):
    _inherit = "stock.move"

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
        stocks = self.env["object.request.line.stock"].sudo().search(
            [("move_id", "in", issue_moves.ids)]
        )
        stocks.mapped("line_id")._sync_issue_reserve_from_moves()
