import logging
from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

TARGET_REQUESTS = ("OR/2026/06/0014", "OR/2026/06/0016")


def _normalize(value):
    return " ".join((value or "").split())


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    lines = env["object.request.line"].search(
        [
            ("request_id.name", "in", TARGET_REQUESTS),
            ("supplier_article", "!=", False),
        ]
    )
    migrated = 0
    for line in lines:
        article = _normalize(line.supplier_article)
        line.write(
            {
                "technical_designation": (
                    line.technical_designation or article
                ),
                "supplier_article": False,
            }
        )
        migrated += 1
    _logger.info(
        "object_request 1.4.0: migrated %s technical designations.",
        migrated,
    )
