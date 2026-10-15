import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)


def _backorder_pickings(env, picking):
    result = env["stock.picking"]
    current = picking
    while current:
        current = env["stock.picking"].search(
            [("backorder_id", "in", current.ids)]
        )
        result |= current
    return result


def _link_backorder_moves(env, stock):
    """Привязать к распределению движения backorder его выдачи."""
    move = stock.move_id
    same_product = env["object.request.line.stock"].search(
        [
            ("picking_id", "=", stock.picking_id.id),
            ("line_id.product_id", "=", move.product_id.id),
        ]
    )
    if len(same_product) != 1:
        return False
    candidates = _backorder_pickings(env, move.picking_id).move_ids.filtered(
        lambda item: item.product_id == move.product_id
        and not item.object_request_stock_id
    )
    if not candidates:
        return False
    candidates.write({"object_request_stock_id": stock.id})
    return True


def migrate(cr, version):
    """Связь движений выдачи с распределением, включая backorder."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    stocks = env["object.request.line.stock"].search(
        [("move_id", "!=", False)]
    )
    for stock in stocks:
        if not stock.move_id.object_request_stock_id:
            stock.move_id.object_request_stock_id = stock
    with_backorder = stocks.filtered(
        lambda stock: _link_backorder_moves(env, stock)
    )
    for line in with_backorder.mapped("line_id"):
        try:
            with cr.savepoint():
                line.recompute_supply_state_from_done_moves()
        except Exception:
            _logger.exception(
                "object_request 1.11.1: recompute failed for line %s", line.id
            )
    stocks.mapped("line_id")._sync_issue_reserve_from_moves()
    _logger.info(
        "object_request 1.11.1: linked %s issue moves, backorders for %s "
        "stock lines",
        len(stocks),
        len(with_backorder),
    )
