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
from odoo.addons.ai_assistant.services.action_tools.executor import (
    ToolExecutor,
)
from odoo.addons.ai_assistant.services.action_tools.registry import (
    default_registry,
)
from odoo.addons.ai_assistant.services.action_tools.base import (
    AbstractWriteTool,
)
from odoo.addons.ai_assistant.services.pending_action import (
    PendingActionStore,
)

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
_GROUP_SUPPLY = 'ai_assistant.group_ai_assistant_supply'
_pending_actions = PendingActionStore()

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
            _logger.info(
                '[AI Assistant] RAW context from frontend: %r',
                context,
            )
            resolved_ctx = ContextResolver().resolve(context, request.env)
            override = params.get_param(
                'ai_assistant.system_prompt_override',
                '',
            )

            # AIA-024: парсинг и валидация скриншота
            image_data = self._parse_screenshot(screenshot)

            # AIA-026: rate limit для vision-запросов
            if image_data:
                uid = request.env.uid
                if not self._vision_rate_ok(uid):
                    _logger.warning(
                        '[AI Assistant] Vision rate limit exceeded for uid=%s',
                        uid,
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
                params=params,
            )

            if 'answer' in result:
                result['answer'] = guard.filter_response(result['answer'])

            return result
        except Exception:
            _logger.exception('Error in /ai_assistant/chat')
            return {'error': 'Сервис временно недоступен. Попробуйте позже.'}

    @http.route('/ai_assistant/confirm', type='jsonrpc', auth='user',
                methods=['POST'])
    def confirm(self, pending_key=None, decision=None, **kwargs):
        try:
            if not request.env.user.has_group(_GROUP_USER):
                return {'error': 'Доступ запрещён'}
            if decision not in ('confirm', 'cancel'):
                return {'error': 'Некорректное решение'}
            item = _pending_actions.pop(request.env.uid, pending_key)
            if not item:
                return {'error': 'Действие не найдено или устарело'}
            if decision == 'cancel':
                return {
                    'answer': 'Действие отменено.',
                    'suggestions': [],
                    'cards': [],
                    'meta': {'status': 'cancelled'},
                }

            result = ToolExecutor(request.env).execute(
                item['tool_name'],
                item['args'],
            )
            if not result.get('success'):
                return {
                    'answer': result['error']['message'],
                    'suggestions': [],
                    'cards': [self._result_card_error(result['error'])],
                    'meta': {'status': 'error'},
                }
            return {
                'answer': 'Готово. Черновик создан.',
                'suggestions': [],
                'cards': [
                    self._result_card_success(
                        item['tool_name'],
                        result['result'],
                    )
                ],
                'meta': {'status': 'ok'},
            }
        except Exception:
            _logger.exception('Error in /ai_assistant/confirm')
            return {'error': 'Сервис временно недоступен. Попробуйте позже.'}

    def _trim_history(self, history):
        if not isinstance(history, list):
            return []
        return history[-MAX_HISTORY_SIZE:]

    def _get_ai_response(self, message, history, context=None,
                         override=None, image_data=None, model_override=None,
                         params=None):
        try:
            mode = self._resolve_mode(params)
            messages = self._build_messages(
                message, history, context,
                override=override, image_data=image_data,
                mode=mode,
            )
            client = OpenRouterClient(request.env)
            if mode == 'actions':
                vision_model = model_override if image_data else None
                return self._get_actions_response(
                    client,
                    messages,
                    model_override=vision_model,
                )
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
                        override=None, image_data=None, mode='consult'):
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
            mode=mode,
        )

    def _resolve_mode(self, params):
        if not params:
            params = request.env['ir.config_parameter'].sudo()
        actions_enabled = params.get_param(
            'ai_assistant.actions_enabled',
            '0',
        )
        if actions_enabled not in ('1', 'True', 'true', True):
            return 'consult'
        if not request.env.user.has_group(_GROUP_SUPPLY):
            return 'consult'
        return 'actions'

    def _get_actions_response(self, client, messages, model_override=None):
        executor = ToolExecutor(request.env)
        tools = default_registry.to_openrouter_tools(request.env)
        for _iteration in range(5):
            response = client.send_chat_with_tools(
                messages,
                tools,
                model_override=model_override,
            )
            if response.get('type') == 'message':
                return {
                    'answer': response.get('content', ''),
                    'suggestions': [],
                    'cards': [],
                    'meta': {
                        'model_used': response.get('model_used'),
                        'mode': 'actions',
                    },
                }
            tool_calls = response.get('tool_calls') or []
            if not tool_calls:
                break
            write_call = self._first_write_tool_call(tool_calls)
            read_calls = self._read_tool_calls(tool_calls)
            if write_call and read_calls:
                # Mixed batch: execute reads first so LLM has full context
                # before we show a write confirmation. Assistant message only
                # includes read calls so every tool_call_id gets a result.
                messages.append(
                    self._assistant_tool_calls_message(response, read_calls)
                )
                for tool_call in read_calls:
                    result = executor.execute(
                        tool_call['name'],
                        tool_call.get('arguments') or {},
                    )
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.get('id'),
                        'name': tool_call['name'],
                        'content': self._json_dumps(result),
                    })
                continue
            if write_call:
                args = write_call.get('arguments') or {}
                pending_key = _pending_actions.put(
                    request.env.uid,
                    write_call['name'],
                    args,
                    idempotency_key=self._idempotency_key(
                        write_call['name'],
                        args,
                    ),
                )
                return {
                    'answer': 'Проверьте план и подтвердите действие.',
                    'suggestions': [],
                    'cards': [
                        self._confirmation_card(write_call, pending_key)
                    ],
                    'meta': {'mode': 'actions', 'status': 'pending'},
                }

            messages.append(self._assistant_tool_calls_message(response))
            for tool_call in tool_calls:
                result = executor.execute(
                    tool_call['name'],
                    tool_call.get('arguments') or {},
                )
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.get('id'),
                    'name': tool_call['name'],
                    'content': self._json_dumps(result),
                })

        return {
            'answer': 'Не удалось завершить обработку tools за 5 итераций.',
            'suggestions': [],
            'cards': [],
            'meta': {'mode': 'actions', 'status': 'max_iterations'},
        }

    def _first_write_tool_call(self, tool_calls):
        for tool_call in tool_calls:
            try:
                tool = default_registry.get(tool_call['name'])
            except KeyError:
                continue
            if tool.is_write:
                return tool_call
        return None

    def _read_tool_calls(self, tool_calls):
        reads = []
        for tool_call in tool_calls:
            try:
                tool = default_registry.get(tool_call['name'])
            except KeyError:
                continue
            if not tool.is_write:
                reads.append(tool_call)
        return reads

    def _idempotency_key(self, tool_name, args):
        try:
            tool = default_registry.get(tool_name)
            if not isinstance(tool, AbstractWriteTool):
                return None
            tool.validate_args(args or {})
            return tool.idempotency_key(args or {})
        except Exception:
            _logger.debug(
                'Failed to build idempotency key for tool=%s',
                tool_name,
                exc_info=True,
            )
            return None

    def _assistant_tool_calls_message(self, response, tool_calls=None):
        if tool_calls is None:
            tool_calls = response.get('tool_calls') or []
        return {
            'role': 'assistant',
            'content': response.get('content') or '',
            'tool_calls': [
                {
                    'id': item.get('id'),
                    'type': 'function',
                    'function': {
                        'name': item['name'],
                        'arguments': self._json_dumps(
                            item.get('arguments') or {}
                        ),
                    },
                }
                for item in tool_calls
            ],
        }

    def _confirmation_card(self, tool_call, pending_key):
        args = tool_call.get('arguments') or {}
        return {
            'type': 'confirmation',
            'pending_key': pending_key,
            'plan': {
                'title': 'Подтвердите действие',
                'tool_name': tool_call['name'],
                'fields': self._summarize_args(args),
            },
        }

    def _summarize_args(self, args):
        fields = []
        for key, value in sorted((args or {}).items()):
            if isinstance(value, list):
                value = '%s строк' % len(value)
            elif isinstance(value, dict):
                value = 'объект'
            elif value is None:
                value = ''
            else:
                value = str(value)
            fields.append({'label': key, 'value': value})
        return fields

    def _result_card_success(self, tool_name, result):
        model, record_id = self._result_record(tool_name, result)
        return {
            'type': 'result',
            'status': 'success',
            'record': {
                'model': model,
                'id': record_id,
                'name': result.get('name') or '',
                'url': result.get('url') or '',
            },
            'next_hint': 'Откройте черновик и проверьте данные.',
        }

    def _result_card_error(self, error):
        return {
            'type': 'result',
            'status': 'error',
            'error': {'message': error.get('message')},
            'next_hint': '',
        }

    def _result_record(self, tool_name, result):
        if tool_name == 'create_object_request_draft':
            return 'object.request', result.get('request_id')
        if tool_name == 'create_purchase_order_draft':
            return 'purchase.order', result.get('po_id')
        if tool_name == 'create_internal_picking_draft':
            return 'stock.picking', result.get('picking_id')
        return '', result.get('record_id')

    def _json_dumps(self, value):
        import json
        return json.dumps(value, ensure_ascii=False)

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
            _logger.warning(
                '[AI Assistant] Screenshot too large: %d bytes',
                len(b64data),
            )
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
