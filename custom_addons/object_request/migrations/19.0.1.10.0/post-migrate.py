import logging

_logger = logging.getLogger(__name__)


def migrate(env, version):
    env.cr.execute(
        """
        UPDATE object_request_line_stock
           SET qty_planned_to_issue = COALESCE(qty_to_issue, 0.0)
         WHERE COALESCE(qty_planned_to_issue, 0.0) = 0.0
           AND COALESCE(qty_to_issue, 0.0) > 0.0
        """
    )
    _logger.info(
        "object_request 1.10.0: backfilled qty_planned_to_issue for %s rows.",
        env.cr.rowcount,
    )
