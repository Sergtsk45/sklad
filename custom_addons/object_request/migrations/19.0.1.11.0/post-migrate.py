import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """TD-017: «Зарезервировано» = фактический резерв открытых выдач."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env["object.request.line"].search(
        [("stock_ids.move_id", "!=", False)]
    )
    lines._sync_issue_reserve_from_moves()
    _logger.info(
        "object_request 1.11.0: issue reserve synced for %s lines",
        len(lines),
    )
