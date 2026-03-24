import logging
import time

from odoo import http
from odoo.http import request
from odoo.addons.ai_assistant.services.openrouter_client import (
    OpenRouterClient,
)
from odoo.addons.ai_assistant.services.context_resolver import (
    ContextResolver,
)
from odoo.addons.ai_assistant.services.knowledge_provider_v2 import (
    KnowledgeProviderV2,
)
from odoo.addons.ai_assistant.services.prompt_builder import PromptBuilder
from odoo.addons.ai_assistant.services.response_guard import ResponseGuard

_logger = logging.getLogger(__name__)

MAX_HISTORY_SIZE = 12
MAX_SCREENSHOT_B64 = 500_000   # ~500 KB base64 — AIA-024

# AIA-026: Rate limit для vision-запросов
_VISION_RATE = {}              # {uid: [timestamp, ...]}
VISION_RATE_WINDOW = 60        # секунд
VISION_RATE_MAX = 5            # запросов в окне

_knowledge_provider = KnowledgeProviderV2()
_prompt_builder = PromptBuilder()

_GROUP_USER = 'ai_assistant.group_ai_assistant_user'

_MODULE_FROM_MODEL = {
    'stock': 'stock', 'purchase': 'purchase', 'sale': 'sale',
    'account': 'account', 'crm': 'crm', 'res': 'contacts',
    'project': 'project', 'hr': 'hr',
}

_MODULE_FROM_ACTION = {
    'склад': 'stock', 'warehouse': 'stock',
    'закупки': 'purchase', 'purchase': 'purchase',
    'продажи': 'sale', 'sales': 'sale',
    'crm': 'crm',
    'контакты': 'contacts', 'contacts': 'contacts',
    'бухгалтерия': 'account', 'accounting': 'account', 'invoicing': 'account',
    'настройки': 'settings', 'settings': 'settings',
    'проект': 'project', 'project': 'project',
    'персонал': 'hr', 'employees': 'hr',
}


class AiAssistantController(http.Controller):

    @http.route('/ai_assistant/check_access', type='jsonrpc', auth='user',
                methods=['POST'])
    def check_access(self, **kwargs):
        has_access = request.env.user.has_group(_GROUP_USER)
        return {'has_access': has_access}

    @http.route('/ai_assistant/chat', type='jsonrpc', auth='user',
                methods=['POST'])
    def chat(self, message=None, context=None, history=None,
             screenshot=None, **kwargs):
        try:
            if not request.env.user.has_group(_GROUP_USER):
                return {'error': 'Доступ запрещён'}

            params = request.env['ir.config_parameter'].sudo()
            enabled = params.get_param('ai_assistant.enabled', '1')
            if enabled not in ('1', 'True', 'true', ''):
                return {
                    'answer': 'AI-ассистент отключён администратором.',
                    'suggestions': [],
                    'meta': {},
                }

            guard = ResponseGuard()
            is_valid, error = guard.validate_request(message, history)
            if not is_valid:
                return {'error': error}

            history = self._trim_history(history)
            _logger.info('[AI Assistant] RAW context from frontend: %r', context)
            resolved_ctx = ContextResolver().resolve(context, request.env)
            override = params.get_param('ai_assistant.system_prompt_override', '')

            # AIA-024: парсинг и валидация скриншота
            image_data = self._parse_screenshot(screenshot)

            # AIA-026: rate limit для vision-запросов
            if image_data:
                uid = request.env.uid
                if not self._vision_rate_ok(uid):
                    _logger.warning(
                        '[AI Assistant] Vision rate limit exceeded for uid=%s', uid
                    )
                    image_data = None  # деградируем до текстового

            # Выбор модели: vision если есть скриншот
            model_override = None
            if image_data:
                model_override = params.get_param(
                    'ai_assistant.vision_model', ''
                ) or None

            result = self._get_ai_response(
                message, history, resolved_ctx,
                override=override or None,
                image_data=image_data,
                model_override=model_override,
            )

            if 'answer' in result:
                result['answer'] = guard.filter_response(result['answer'])

            return result
        except Exception:
            _logger.exception('Error in /ai_assistant/chat')
            return {'error': 'Сервис временно недоступен. Попробуйте позже.'}

    def _trim_history(self, history):
        if not isinstance(history, list):
            return []
        return history[-MAX_HISTORY_SIZE:]

    def _get_ai_response(self, message, history, context=None,
                         override=None, image_data=None, model_override=None):
        try:
            messages = self._build_messages(
                message, history, context,
                override=override, image_data=image_data,
            )
            client = OpenRouterClient(request.env)
            result = client.send_chat(messages, model_override=model_override)
            _logger.debug(
                '[AI Assistant] Response: model=%s mode=%s len=%d',
                result.get('model_used'),
                result.get('mode', 'text'),
                len(result.get('answer', '')),
            )
            return {
                'answer': result['answer'],
                'suggestions': [],
                'meta': {
                    'model_used': result.get('model_used'),
                    'mode': result.get('mode', 'text'),
                },
            }
        except ValueError:
            return self._mock_response()
        except ConnectionError as e:
            return {
                'answer': str(e),
                'suggestions': [],
                'meta': {'status': 'error'},
            }

    def _build_messages(self, message, history, context,
                        override=None, image_data=None):
        module = self._resolve_module(context)

        knowledge = _knowledge_provider.get_knowledge(module, message)

        debug = request.env['ir.config_parameter'].sudo().get_param(
            'ai_assistant.debug_logging', False
        )
        if debug in (True, '1', 'True', 'true'):
            _logger.debug(
                '[AI Assistant] Prompt debug:\n'
                '  module=%s, history_len=%d, has_screenshot=%s\n'
                '  docs_chars=%d, tech_context=%s',
                module, len(history), bool(image_data),
                len(knowledge.get('docs_snippets', '') or ''),
                'yes' if knowledge.get('tech_context') else 'no',
            )

        _logger.info(
            '[AI Assistant] build_messages: module=%r docs_chars=%d '
            'tech=%s vision=%s',
            module,
            len(knowledge.get('docs_snippets', '') or ''),
            'yes' if knowledge.get('tech_context') else 'no',
            'yes' if image_data else 'no',
        )

        return _prompt_builder.build_messages(
            message, history, context,
            knowledge=knowledge,
            override=override,
            image_data=image_data,
        )

    def _resolve_module(self, context):
        if not context:
            return ''
        module = context.get('module', '')
        if module:
            return module
        model = context.get('model', '')
        if model:
            prefix = model.split('.')[0]
            module = _MODULE_FROM_MODEL.get(prefix, '')
            if module:
                _logger.info(
                    '[AI Assistant] module resolved from model %r -> %r',
                    model, module
                )
                return module
        action = context.get('action', '')
        if action:
            module = _MODULE_FROM_ACTION.get(action.lower().strip(), '')
            if module:
                _logger.info(
                    '[AI Assistant] module resolved from action %r -> %r',
                    action, module
                )
        return module

    # AIA-024 ──────────────────────────────────────────────────────────

    def _parse_screenshot(self, data_url):
        """
        Валидировать и распарсить скриншот из data URL.
        Не логируем содержимое (персональные данные на экране).

        :returns dict|None: {'media_type': str, 'data': str} или None
        """
        if not data_url or not isinstance(data_url, str):
            return None
        if not data_url.startswith('data:image/'):
            _logger.warning('[AI Assistant] Invalid screenshot format')
            return None
        try:
            header, b64data = data_url.split(',', 1)
        except ValueError:
            return None
        if len(b64data) > MAX_SCREENSHOT_B64:
            _logger.warning('[AI Assistant] Screenshot too large: %d bytes', len(b64data))
            return None
        try:
            media_type = header.split(':')[1].split(';')[0]
        except (IndexError, AttributeError):
            return None
        if media_type not in ('image/jpeg', 'image/png', 'image/webp'):
            return None
        return {'media_type': media_type, 'data': b64data}

    # AIA-026 ──────────────────────────────────────────────────────────

    def _vision_rate_ok(self, uid):
        """Проверить rate limit для vision-запросов (5/мин на пользователя)."""
        now = time.time()
        timestamps = _VISION_RATE.get(uid, [])
        # Удаляем устаревшие
        timestamps = [t for t in timestamps if now - t < VISION_RATE_WINDOW]
        if len(timestamps) >= VISION_RATE_MAX:
            return False
        timestamps.append(now)
        _VISION_RATE[uid] = timestamps
        return True

    def _mock_response(self):
        return {
            'answer': 'Я пока не подключён к AI, но скоро буду помогать!',
            'suggestions': [],
            'meta': {'mock': True},
        }
