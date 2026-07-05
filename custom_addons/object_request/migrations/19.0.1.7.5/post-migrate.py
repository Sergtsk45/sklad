import logging

from odoo import SUPERUSER_ID, api


_logger = logging.getLogger(__name__)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    stats = env[
        'object.request.matching.memory'
    ].sudo().backfill_flange_pn16_memory()
    _logger.info(
        'object_request 1.7.5: flange PN16 memory backfill completed: %s',
        stats,
    )
