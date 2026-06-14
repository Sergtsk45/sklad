import logging

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    """Установить дефолтные параметры AI-сопоставления."""
    defaults = {
        'object_request.ai_matching_enabled': 'True',
        'object_request.ai_matching_auto_threshold': '0.90',
        'object_request.ai_matching_suggest_threshold': '0.70',
        'object_request.ai_matching_batch_size': '50',
    }
    for key, value in defaults.items():
        cr.execute(
            """
            INSERT INTO ir_config_parameter (
                key, value, create_uid, write_uid,
                create_date, write_date
            )
            VALUES (%s, %s, 1, 1, NOW(), NOW())
            ON CONFLICT (key) DO NOTHING
            """,
            (key, value),
        )
    _logger.info('object_request 1.3.0: AI config parameters set.')
