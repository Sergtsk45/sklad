from odoo import fields, models


class AiAssistantConfig(models.TransientModel):
    _inherit = 'res.config.settings'

    ai_assistant_api_key = fields.Char(
        string='OpenRouter API Key',
        config_parameter='ai_assistant.openrouter_api_key',
    )
    ai_assistant_base_url = fields.Char(
        string='Base URL OpenRouter',
        config_parameter='ai_assistant.openrouter_base_url',
    )
    ai_assistant_model = fields.Char(
        string='Модель',
        config_parameter='ai_assistant.openrouter_model',
    )
    ai_assistant_timeout = fields.Integer(
        string='Таймаут (сек)',
        config_parameter='ai_assistant.openrouter_timeout',
    )
    ai_assistant_max_history = fields.Integer(
        string='Макс. сообщений в истории',
        config_parameter='ai_assistant.max_history_size',
    )
    ai_assistant_enabled = fields.Boolean(
        string='Включить AI-ассистент',
        config_parameter='ai_assistant.enabled',
    )
    ai_assistant_system_prompt_override = fields.Text(
        string='Кастомный системный промпт (опционально)',
        config_parameter='ai_assistant.system_prompt_override',
    )
    ai_assistant_debug_logging = fields.Boolean(
        string='Debug-логирование',
        config_parameter='ai_assistant.debug_logging',
    )
