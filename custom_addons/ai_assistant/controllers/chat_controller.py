import logging

from odoo import http
from odoo.http import request
from odoo.addons.ai_assistant.services.openrouter_client import (
    OpenRouterClient,
)
from odoo.addons.ai_assistant.services.context_resolver import (
    ContextResolver,
)
from odoo.addons.ai_assistant.services.knowledge_provider import (
    KnowledgeProvider,
)
from odoo.addons.ai_assistant.services.prompt_builder import PromptBuilder
from odoo.addons.ai_assistant.services.response_guard import ResponseGuard

_logger = logging.getLogger(__name__)

MAX_HISTORY_SIZE = 12

_knowledge_provider = KnowledgeProvider()
_prompt_builder = PromptBuilder()

_GROUP_USER = 'ai_assistant.group_ai_assistant_user'


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

    def _get_ai_response(self, message, history, context=None, override=None):
        try:
            messages = self._build_messages(
                message, history, context, override=override
            )
            result = OpenRouterClient(request.env).send_chat(messages)
            _logger.debug(
                '[AI Assistant] Response: model=%s, len=%d',
                result.get('model_used'),
                len(result.get('answer', '')),
            )
            return {
                'answer': result['answer'],
                'suggestions': [],
                'meta': {'model_used': result.get('model_used')},
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
        module = (context or {}).get('module', '')
        if not module:
            model = (context or {}).get('model', '')
            if model:
                prefix = model.split('.')[0]
                _MODULE_FROM_MODEL = {
                    'stock': 'stock', 'purchase': 'purchase', 'sale': 'sale',
                    'account': 'account', 'crm': 'crm', 'res': 'contacts',
                    'project': 'project', 'hr': 'hr',
                }
                module = _MODULE_FROM_MODEL.get(prefix, '')
                if module:
                    _logger.info('[AI Assistant] module resolved from model %r -> %r', model, module)
        if not module:
            action = (context or {}).get('action', '')
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
            module = _MODULE_FROM_ACTION.get(action.lower().strip(), '')
            if module:
                _logger.info('[AI Assistant] module resolved from action %r -> %r', action, module)
        snippets = _knowledge_provider.get_snippets(module, message)

        system_parts = [_prompt_builder.build_system_prompt(override=override)]

        safety = _prompt_builder.build_safety_rules()
        if safety:
            system_parts.append(safety)

        context_block = _prompt_builder.build_context_block(context)
        if context_block:
            system_parts.append(context_block)

        knowledge_block = _prompt_builder.build_knowledge_block(snippets)
        if knowledge_block:
            system_parts.append(knowledge_block)

        technical_context = _knowledge_provider.get_technical_context(module)
        tech_block = _prompt_builder.build_technical_context_block(technical_context)
        if tech_block:
            system_parts.append(tech_block)

        system_prompt = '\n\n'.join(system_parts)
        _logger.info(
            '[AI Assistant] build_messages: module=%r snippets=%d tech_context=%s system_prompt_len=%d',
            module, len(snippets),
            ('yes(%d)' % len(technical_context)) if technical_context else 'no',
            len(system_prompt),
        )

        debug = request.env['ir.config_parameter'].sudo().get_param(
            'ai_assistant.debug_logging', False
        )
        if debug in (True, '1', 'True', 'true'):
            _logger.debug(
                '[AI Assistant] Prompt debug:\n'
                '  module=%s, history_len=%d\n'
                '  tech_context=%s (%d chars)\n'
                '  snippets=%d\n'
                '  system_prompt_len=%d chars\n'
                '--- SYSTEM PROMPT START ---\n%s\n--- SYSTEM PROMPT END ---',
                module,
                len(history),
                'yes' if technical_context else 'no',
                len(technical_context or ''),
                len(snippets),
                len(system_prompt),
                system_prompt,
            )

        return _prompt_builder.build_messages(system_prompt, history, message)

    def _mock_response(self):
        return {
            'answer': 'Я пока не подключён к AI, но скоро буду помогать!',
            'suggestions': [],
            'meta': {'mock': True},
        }
