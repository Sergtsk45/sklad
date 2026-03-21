import logging

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

_knowledge_provider = KnowledgeProviderV2()
_prompt_builder = PromptBuilder()

_GROUP_USER = 'ai_assistant.group_ai_assistant_user'

# Маппинг model prefix → module
_MODULE_FROM_MODEL = {
    'stock': 'stock', 'purchase': 'purchase', 'sale': 'sale',
    'account': 'account', 'crm': 'crm', 'res': 'contacts',
    'project': 'project', 'hr': 'hr',
}

# Маппинг action name → module
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
        """Return whether the current user has AI Assistant access."""
        has_access = request.env.user.has_group(_GROUP_USER)
        return {'has_access': has_access}

    @http.route('/ai_assistant/chat', type='jsonrpc', auth='user',
                methods=['POST'])
    def chat(self, message=None, context=None, history=None, **kwargs):
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
            override = params.get_param(
                'ai_assistant.system_prompt_override', ''
            )
            result = self._get_ai_response(
                message, history, resolved_ctx, override=override or None
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
                         override=None, model_override=None):
        try:
            messages = self._build_messages(
                message, history, context, override=override
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

    def _build_messages(self, message, history, context, override=None):
        module = self._resolve_module(context)

        knowledge = _knowledge_provider.get_knowledge(
            module, message, include_technical=True
        )

        debug = request.env['ir.config_parameter'].sudo().get_param(
            'ai_assistant.debug_logging', False
        )
        if debug in (True, '1', 'True', 'true'):
            _logger.debug(
                '[AI Assistant] Prompt debug:\n'
                '  module=%s, history_len=%d\n'
                '  docs_chars=%d, tech_context=%s\n'
                '  term_mapping keys=%s',
                module,
                len(history),
                len(knowledge.get('docs_snippets', '') or ''),
                ('yes(%d)' % len(knowledge['tech_context']))
                if knowledge.get('tech_context') else 'no',
                list(knowledge.get('term_mapping', {}).keys()),
            )

        _logger.info(
            '[AI Assistant] build_messages: module=%r docs_chars=%d tech=%s',
            module,
            len(knowledge.get('docs_snippets', '') or ''),
            'yes' if knowledge.get('tech_context') else 'no',
        )

        return _prompt_builder.build_messages(
            message, history, context,
            knowledge=knowledge,
            override=override,
        )

    def _resolve_module(self, context):
        """Определить модуль из контекста экрана."""
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

    def _mock_response(self):
        return {
            'answer': 'Я пока не подключён к AI, но скоро буду помогать!',
            'suggestions': [],
            'meta': {'mock': True},
        }
