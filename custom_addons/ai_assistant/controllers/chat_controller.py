import json
import logging
import time

from odoo import http
from odoo.exceptions import ValidationError
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
from odoo.addons.ai_assistant.services.navigation_helper import (
    NavigationHelper,
)
from odoo.addons.ai_assistant.services.warehouse_stock_link_helper import (
    WarehouseStockLinkHelper,
)
from odoo.addons.ai_assistant.services.invoice_extraction_store import (
    InvoiceExtractionStore,
)
from odoo.addons.ai_assistant.services.invoice_context_helper import (
    InvoiceContextHelper,
)
from odoo.addons.ai_assistant.services.invoice_parsing import (
    extract_invoice,
    validate_invoice_data,
)
from odoo.addons.ai_assistant.services.invoice_workflow import (
    InvoiceWorkflow,
)

_logger = logging.getLogger(__name__)

MAX_HISTORY_SIZE = 12
MAX_SCREENSHOT_B64 = 500_000   # ~500 KB base64 — AIA-024
MAX_INVOICE_BYTES = 5 * 1024 * 1024  # 5 MB — AIA-056
ALLOWED_INVOICE_EXTENSIONS = frozenset({'pdf', 'xlsx'})

# AIA-026: Rate limit для vision-запросов
_VISION_RATE = {}              # {uid: [timestamp, ...]}
VISION_RATE_WINDOW = 60        # секунд
VISION_RATE_MAX = 5            # запросов в окне

_knowledge_provider = KnowledgeProviderV2()
_prompt_builder = PromptBuilder()

_GROUP_USER = 'ai_assistant.group_ai_assistant_user'
_GROUP_SUPPLY = 'ai_assistant.group_ai_assistant_supply'
_pending_actions = PendingActionStore()
_invoice_store = InvoiceExtractionStore()

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
        has_supply = (
            has_access and request.env.user.has_group(_GROUP_SUPPLY)
        )
        return {'has_access': has_access, 'has_supply': has_supply}

    @http.route('/ai_assistant/upload_invoice', type='http', auth='user',
                methods=['POST'], csrf=False)
    def upload_invoice(self, **kwargs):
        """
        AIA-056: Принять PDF/XLSX счёт, распарсить, вернуть сводку.
        Доступно только группе group_ai_assistant_supply.
        Не логируем содержимое файла (PII).
        """
        def _json_error(msg, status=400):
            return request.make_json_response(
                {'success': False, 'error': msg}, status=status
            )

        if not request.env.user.has_group(_GROUP_SUPPLY):
            return _json_error(
                'Доступ запрещён: требуется группа «Снабжение»',
                403,
            )

        uploaded_file = request.httprequest.files.get('file')
        if not uploaded_file:
            return _json_error('Файл не передан')

        filename = (uploaded_file.filename or '').strip()
        ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_INVOICE_EXTENSIONS:
            return _json_error(
                f'Недопустимый тип файла «{ext}». '
                f'Разрешены: {", ".join(sorted(ALLOWED_INVOICE_EXTENSIONS))}'
            )

        file_bytes = uploaded_file.read()
        if len(file_bytes) > MAX_INVOICE_BYTES:
            return _json_error(
                f'Файл слишком большой: {len(file_bytes) // 1024} КБ. '
                f'Максимум: {MAX_INVOICE_BYTES // 1024 // 1024} МБ'
            )

        if ext == 'pdf' and not file_bytes.startswith(b'%PDF'):
            return _json_error('Файл не является PDF (неверный заголовок)')
        if (
            ext == 'xlsx'
            and file_bytes[:4] not in (b'PK\x03\x04', b'PK\x05\x06')
        ):
            return _json_error('Файл не является XLSX (неверный заголовок)')
        if ext == 'xlsx':
            return _json_error(
                'XLSX-формат будет поддержан в следующей версии. '
                'Пожалуйста, используйте PDF.'
            )

        try:
            invoice_data = extract_invoice(file_bytes, env=request.env)
        except ValueError as exc:
            _logger.warning(
                '[AI Assistant] upload_invoice: parse error for file=%s: %s',
                filename, exc,
            )
            return _json_error(f'Не удалось распознать счёт: {exc}')
        except Exception:
            _logger.exception(
                '[AI Assistant] upload_invoice: unexpected error for file=%s',
                filename,
            )
            return _json_error('Ошибка при обработке файла')

        warnings = validate_invoice_data(invoice_data)
        uid = request.env.uid
        extraction_token = _invoice_store.put(
            uid,
            invoice_data,
            filename=filename,
            file_bytes=file_bytes,
            mimetype='application/pdf' if ext == 'pdf' else '',
        )
        invoice_context = InvoiceContextHelper(
            request.env,
            _invoice_store,
        ).fetch_context(uid, extraction_token)
        workflow = InvoiceWorkflow(request.env, _invoice_store)
        suggestions = self._invoice_upload_suggestions(
            workflow,
            uid,
            extraction_token,
            invoice_context,
        )

        totals = invoice_data.get('totals', {})
        total_w_vat = totals.get('total_w_vat', '')
        supplier_name = (
            invoice_data.get('supplier', {}).get('name', '') or
            invoice_data.get('invoice_number', '') or
            'неизвестен'
        )
        item_count = len(invoice_data.get('items', []))

        _logger.info(
            '[AI Assistant] upload_invoice: uid=%s file=%s items=%d '
            'total=%s warnings=%d',
            uid, filename, item_count, total_w_vat, len(warnings),
        )

        summary_parts = [f'Счёт распознан: {item_count} позиций']
        if total_w_vat:
            try:
                summary_parts.append(
                    f'сумма {float(total_w_vat):,.2f} ₽'.replace(
                        ',',
                        '\u00a0',
                    )
                )
            except (ValueError, TypeError):
                summary_parts.append(f'сумма {total_w_vat}')
        if supplier_name:
            summary_parts.append(f'поставщик: {supplier_name}')
        summary = '. '.join(summary_parts) + '.'

        partner_ctx = (invoice_context or {}).get('partner') or {}
        partner_status = partner_ctx.get('status')
        if partner_status == 'matched':
            matched_name = partner_ctx.get('name') or supplier_name
            matched_id = partner_ctx.get('partner_id')
            summary += (
                f'\n✅ Поставщик найден в Odoo: {matched_name}'
                + (f' (id {matched_id})' if matched_id else '')
            )
        elif partner_status == 'ambiguous':
            summary += '\n⚠ Найдено несколько контрагентов — уточните запрос.'
        elif partner_ctx.get('partner_error') == 'inn_required':
            summary += (
                '\n⚠ Поставщик не найден, ИНН в счёте отсутствует — '
                'создайте контрагента вручную.'
            )
        if warnings:
            warning_lines = warnings[:5]
            if len(warnings) > 5:
                warning_lines.append('… и ещё %s' % (len(warnings) - 5))
            summary += '\n\nПредупреждения (%s):\n' % len(warnings)
            summary += '\n'.join('• %s' % line for line in warning_lines)

        return request.make_json_response({
            'success': True,
            'extraction_token': extraction_token,
            'summary': summary,
            'warnings': warnings,
            'suggestions': suggestions,
            'meta': {
                'item_count': item_count,
                'total_w_vat': total_w_vat,
                'supplier_name': supplier_name,
                'invoice_number': invoice_data.get('invoice_number', ''),
                'invoice_date': invoice_data.get('invoice_date', ''),
                'warnings_count': len(warnings),
            },
        })

    def _invoice_upload_suggestions(
        self, workflow, uid, extraction_token, invoice_context
    ):
        partner = (invoice_context or {}).get('partner') or {}
        if partner.get('needs_create_partner_draft'):
            name = (
                partner.get('extracted_name')
                or (partner.get('partner_draft_args') or {}).get('name')
                or 'поставщика'
            )
            return [{
                'label': 'Создать поставщика: %s' % self._short_label(name),
                'action': InvoiceWorkflow.ACTION_CREATE_PARTNER,
            }]
        draft = workflow.next_product_draft(uid, extraction_token)
        if draft:
            return [{
                'label': 'Создать товар: %s'
                % self._short_label(draft.get('line_name') or ''),
                'action': InvoiceWorkflow.ACTION_NEXT_PRODUCT,
            }]
        partner_ready = workflow.partner_ready(uid, extraction_token)
        products_ready = workflow.all_products_ready(uid, extraction_token)
        if partner_ready and products_ready:
            return workflow.purchase_start_suggestions(uid, extraction_token)
        return []

    @http.route('/ai_assistant/chat', type='jsonrpc', auth='user',
                methods=['POST'])
    def chat(self, message=None, context=None, history=None,
             screenshot=None, extraction_token=None,
             invoice_workflow_action=None, invoice_po_warehouse=None,
             awaiting_po_warehouse=None, invoice_workflow_payload=None,
             **kwargs):
        try:
            if not request.env.user.has_group(_GROUP_USER):
                return {'error': 'Доступ запрещён'}

            workflow_result = self._dispatch_invoice_workflow(
                extraction_token=extraction_token,
                invoice_workflow_action=invoice_workflow_action,
                invoice_po_warehouse=invoice_po_warehouse,
                awaiting_po_warehouse=awaiting_po_warehouse,
                invoice_workflow_payload=invoice_workflow_payload,
                message=message,
            )
            if workflow_result is not None:
                if 'answer' in workflow_result:
                    workflow_result['answer'] = (
                        ResponseGuard().filter_response(
                            workflow_result['answer']
                        )
                    )
                return workflow_result

            guard = ResponseGuard()
            is_valid, error = guard.validate_request(message, history)
            if not is_valid:
                return {'error': error}

            params = request.env['ir.config_parameter'].sudo()
            enabled = params.get_param('ai_assistant.enabled', '1')
            if enabled not in ('1', 'True', 'true', ''):
                return {
                    'answer': 'AI-ассистент отключён администратором.',
                    'suggestions': [],
                    'meta': {},
                }

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
                extraction_token=extraction_token,
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
            metadata = item.get('metadata') or {}
            suggestions = []
            extraction_token = metadata.get('extraction_token')
            if (
                extraction_token and
                item['tool_name'] == 'create_product_draft' and
                metadata.get('invoice_line_key') is not None
            ):
                workflow = InvoiceWorkflow(request.env, _invoice_store)
                workflow.record_product_created(
                    request.env.uid,
                    extraction_token,
                    metadata['invoice_line_key'],
                    result['result']['product_id'],
                )
                suggestions = workflow.suggestions_after_product_created(
                    request.env.uid,
                    extraction_token,
                )
            elif (
                extraction_token and
                item['tool_name'] == 'create_partner_draft'
            ):
                workflow = InvoiceWorkflow(request.env, _invoice_store)
                workflow.record_partner_created(
                    request.env.uid,
                    extraction_token,
                    result['result']['partner_id'],
                )
                suggestions = workflow.suggestions_after_partner_created(
                    request.env.uid,
                    extraction_token,
                )
            elif (
                extraction_token and
                item['tool_name'] == 'create_purchase_order_draft'
            ):
                suggestions = []
            return {
                'answer': 'Готово. Черновик создан.',
                'suggestions': suggestions,
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
                         params=None, extraction_token=None):
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
                nav_helper = NavigationHelper(request.env)
                stock_helper = WarehouseStockLinkHelper(request.env)
                invoice_helper = InvoiceContextHelper(
                    request.env,
                    _invoice_store,
                )
                nav_result = nav_helper.fetch_link(message)
                stock_result = stock_helper.fetch_link(message, history)
                invoice_context = invoice_helper.fetch_context(
                    request.env.uid,
                    extraction_token,
                )
                return self._get_tools_response(
                    client,
                    messages,
                    model_override=vision_model,
                    allow_write=True,
                    mode_label='actions',
                    nav_helper=nav_helper,
                    nav_result=nav_result,
                    stock_helper=stock_helper,
                    stock_result=stock_result,
                    invoice_helper=invoice_helper,
                    invoice_context=invoice_context,
                    extraction_token=extraction_token,
                )
            vision_model = model_override if image_data else None
            nav_helper = NavigationHelper(request.env)
            stock_helper = WarehouseStockLinkHelper(request.env)
            nav_result = nav_helper.fetch_link(message)
            stock_result = stock_helper.fetch_link(message, history)
            return self._get_tools_response(
                client,
                messages,
                model_override=vision_model,
                allow_write=False,
                mode_label='consult',
                nav_helper=nav_helper,
                nav_result=nav_result,
                stock_helper=stock_helper,
                stock_result=stock_result,
            )
        except ValueError as e:
            _logger.warning('[AI Assistant] OpenRouter unavailable: %s', e)
            return self._ai_unavailable_response(str(e))
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

    def _get_tools_response(
        self,
        client,
        messages,
        model_override=None,
        allow_write=True,
        mode_label='actions',
        nav_helper=None,
        nav_result=None,
        stock_helper=None,
        stock_result=None,
        invoice_helper=None,
        invoice_context=None,
        extraction_token=None,
    ):
        executor = ToolExecutor(request.env)
        context_messages = []
        if nav_result and nav_helper:
            ctx_msg = nav_helper.build_context_message(nav_result)
            if ctx_msg:
                context_messages.append(ctx_msg)
        if stock_result and stock_helper:
            ctx_msg = stock_helper.build_context_message(stock_result)
            if ctx_msg:
                context_messages.append(ctx_msg)
        if invoice_context and invoice_helper:
            ctx_msg = invoice_helper.build_context_message(invoice_context)
            if ctx_msg:
                context_messages.append(ctx_msg)
        if context_messages:
            messages = list(messages) + [{
                'role': 'system',
                'content': '\n'.join(context_messages),
            }]
        tools = default_registry.to_openrouter_tools(
            request.env,
            read_only=not allow_write,
        )
        for _iteration in range(5):
            response = client.send_chat_with_tools(
                messages,
                tools,
                model_override=model_override,
            )
            if response.get('type') == 'message':
                answer = response.get('content', '')
                if nav_helper and nav_result:
                    answer = nav_helper.enrich_answer(answer, nav_result)
                if stock_helper and stock_result:
                    answer = stock_helper.enrich_answer(answer, stock_result)
                suggestions = self._partner_category_suggestions(answer)
                answer = self._strip_partner_category_marker(answer)
                return {
                    'answer': answer,
                    'suggestions': suggestions,
                    'cards': [],
                    'links': self._response_links(nav_result, stock_result),
                    'meta': {
                        'model_used': response.get('model_used'),
                        'mode': mode_label,
                    },
                }
            tool_calls = response.get('tool_calls') or []
            if not tool_calls:
                break
            write_call = (
                self._first_write_tool_call(tool_calls)
                if allow_write else None
            )
            read_calls = self._read_tool_calls(tool_calls)
            if write_call and read_calls:
                # Mixed batch: execute reads first so LLM has full context
                # before we show a write confirmation. Assistant message only
                # includes read calls so every tool_call_id gets a result.
                messages.append(
                    self._assistant_tool_calls_message(response, read_calls)
                )
                for tool_call in read_calls:
                    result = self._execute_tool_call(
                        executor,
                        tool_call,
                        allow_write=allow_write,
                        extraction_token=extraction_token,
                    )
                    messages.append({
                        'role': 'tool',
                        'tool_call_id': tool_call.get('id'),
                        'name': tool_call['name'],
                        'content': self._tool_result_content(
                            tool_call['name'],
                            result,
                        ),
                    })
                continue
            if write_call:
                args = write_call.get('arguments') or {}
                metadata = {}
                if (
                    extraction_token and
                    write_call['name'] == 'create_partner_draft'
                ):
                    workflow = InvoiceWorkflow(request.env, _invoice_store)
                    draft = workflow.next_partner_draft(
                        request.env.uid,
                        extraction_token,
                    )
                    if draft:
                        args = draft['args']
                        metadata = {'extraction_token': extraction_token}
                        write_call['arguments'] = args
                elif (
                    extraction_token and
                    write_call['name'] == 'create_product_draft'
                ):
                    workflow = InvoiceWorkflow(request.env, _invoice_store)
                    args, metadata = workflow.attach_to_product_draft(
                        request.env.uid,
                        extraction_token,
                        args,
                    )
                    write_call['arguments'] = args
                pending_key = _pending_actions.put(
                    request.env.uid,
                    write_call['name'],
                    args,
                    idempotency_key=self._idempotency_key(
                        write_call['name'],
                        args,
                    ),
                    metadata=metadata,
                )
                return {
                    'answer': 'Проверьте план и подтвердите действие.',
                    'suggestions': [],
                    'cards': [
                        self._confirmation_card(write_call, pending_key)
                    ],
                    'meta': {'mode': mode_label, 'status': 'pending'},
                }

            messages.append(self._assistant_tool_calls_message(response))
            for tool_call in tool_calls:
                result = self._execute_tool_call(
                    executor,
                    tool_call,
                    allow_write=allow_write,
                    extraction_token=extraction_token,
                )
                messages.append({
                    'role': 'tool',
                    'tool_call_id': tool_call.get('id'),
                    'name': tool_call['name'],
                    'content': self._tool_result_content(
                        tool_call['name'],
                        result,
                    ),
                })

        return {
            'answer': 'Не удалось завершить обработку tools за 5 итераций.',
            'suggestions': [],
            'cards': [],
            'meta': {'mode': mode_label, 'status': 'max_iterations'},
        }

    def _execute_tool_call(
        self, executor, tool_call, allow_write=True, extraction_token=None
    ):
        name = tool_call['name']
        args = tool_call.get('arguments') or {}
        if not allow_write:
            try:
                tool = default_registry.get(name)
            except KeyError:
                pass
            else:
                if tool.is_write:
                    return {
                        'success': False,
                        'error': {
                            'code': 'write_not_allowed',
                            'message': (
                                'Создание документов доступно только '
                                'пользователями группы «Снабжение».'
                            ),
                        },
                    }
        if name == 'find_partner' and extraction_token:
            args = self._augment_find_partner_args(args, extraction_token)
        return executor.execute(name, args)

    def _augment_find_partner_args(self, args, extraction_token):
        """
        Если LLM ищет поставщика при активном счёте — сначала пробуем ИНН.

        Возвращает args без изменений, если ИНН из счёта не совпадает с query
        или ИНН не извлечён, но в таком случае вся оригинальная логика
        find_partner остаётся в силе.
        """
        uid = request.env.uid
        invoice_data = _invoice_store.get(uid, extraction_token)
        if not invoice_data:
            return args
        inn = (
            (invoice_data.get('supplier') or {}).get('inn') or ''
        ).strip()
        if not inn:
            return args
        query = (args.get('query') or '').strip()
        if query == inn:
            return args
        return dict(args, query=inn)

    def _tool_result_content(self, tool_name, result):
        if result.get('success') and isinstance(result.get('result'), dict):
            try:
                tool = default_registry.get(tool_name)
            except KeyError:
                tool = None
            if tool and not tool.is_write:
                return self._json_dumps(result['result'])
        return self._json_dumps(result)

    def _response_links(self, nav_result, stock_result):
        links = []
        if nav_result and nav_result.get('url'):
            links.append({
                'label': nav_result['label'],
                'url': nav_result['url'],
                'menu_breadcrumb': nav_result.get('menu_breadcrumb') or '',
            })
        if stock_result and stock_result.get('url'):
            links.append({
                'label': stock_result['label'],
                'url': stock_result['url'],
                'menu_breadcrumb': stock_result.get('menu_breadcrumb') or '',
            })
        return links

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
                'title': self._confirmation_title(tool_call['name'], args),
                'tool_name': tool_call['name'],
                'fields': self._summarize_args(args),
            },
        }

    def _confirmation_title(self, tool_name, args=None):
        args = args or {}
        if tool_name == 'create_partner_draft':
            category = args.get('category')
            if isinstance(category, list):
                category = category[0] if category else ''
            return {
                'Поставщик': 'Создать поставщика',
                'Заказчик': 'Создать заказчика',
                'Покупатель': 'Создать покупателя',
                'Подрядчик': 'Создать подрядчика',
            }.get(category, 'Создать контрагента')
        if tool_name == 'update_partner_draft':
            return 'Обновить контрагента'
        if tool_name == 'add_partner_bank_draft':
            return 'Добавить банковские реквизиты'
        if tool_name == 'add_partner_contact_draft':
            return 'Добавить контактное лицо'
        return 'Подтвердите действие'

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

    def _short_label(self, text, limit=48):
        value = (text or '').strip()
        if len(value) <= limit:
            return value
        return value[: limit - 1] + '…'

    def _result_card_success(self, tool_name, result):
        model, record_id = self._result_record(tool_name, result)
        steps = self._next_steps(tool_name)
        return {
            'type': 'result',
            'status': 'success',
            'record': {
                'model': model,
                'id': record_id,
                'name': result.get('name') or '',
                'url': result.get('url') or '',
            },
            'details': self._result_details(tool_name, result),
            'next_hint': steps[0] if steps else 'Откройте черновик.',
            'steps': steps,
        }

    def _result_details(self, tool_name, result):
        if tool_name != 'update_partner_draft':
            return []
        return [
            {
                'label': 'Обновлено',
                'value': (
                    ', '.join(result.get('updated_fields') or []) or 'нет'
                ),
            },
            {
                'label': 'Пропущено',
                'value': (
                    ', '.join(result.get('skipped_fields') or []) or 'нет'
                ),
            },
        ]

    def _next_steps(self, tool_name):
        if tool_name == 'create_purchase_order_draft':
            return [
                'Откройте черновик и проверьте строки и склад.',
                (
                    'Нажмите «Подтвердить» (Confirm) — PO перейдёт '
                    'в статус «В процессе».'
                ),
                (
                    'Откройте вкладку «Приход» (Receipt) — появится '
                    'входящее поступление.'
                ),
                'В поступлении: «Проверить наличие» → «Провести» (Validate).',
                '⚠ Оплата счёта — в 1С, не в Odoo.',
            ]
        if tool_name == 'create_internal_picking_draft':
            return [
                'Откройте черновик перемещения и проверьте строки.',
                '«Проверить наличие» → «Провести» (Validate).',
            ]
        if tool_name == 'create_object_request_draft':
            return [
                'Откройте черновик требования и проверьте позиции.',
                'Переведите в статус «В работе» для снабженца.',
            ]
        if tool_name == 'create_product_draft':
            return [
                (
                    'Откройте карточку товара и дозаполните поля '
                    '(цена, категория).'
                ),
            ]
        if tool_name == 'create_partner_draft':
            return [
                (
                    'Откройте карточку поставщика/контрагента и проверьте '
                    'реквизиты.'
                ),
            ]
        if tool_name == 'update_partner_draft':
            return ['Откройте карточку контрагента и проверьте изменения.']
        if tool_name == 'add_partner_bank_draft':
            return ['Откройте карточку контрагента и проверьте банк и счёт.']
        if tool_name == 'add_partner_contact_draft':
            return ['Откройте карточку контрагента и проверьте контакт.']
        return ['Откройте черновик и проверьте данные.']

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
        if tool_name == 'create_product_draft':
            return 'product.product', result.get('product_id')
        if tool_name == 'create_partner_draft':
            return 'res.partner', result.get('partner_id')
        if tool_name == 'update_partner_draft':
            return 'res.partner', result.get('partner_id')
        if tool_name == 'add_partner_bank_draft':
            return 'res.partner', result.get('partner_id')
        if tool_name == 'add_partner_contact_draft':
            return 'res.partner', result.get('partner_id')
        if tool_name == 'create_internal_picking_draft':
            return 'stock.picking', result.get('picking_id')
        return '', result.get('record_id')

    def _partner_category_suggestions(self, answer):
        text = answer or ''
        if (
            '[PARTNER_CATEGORY_REQUIRED]' not in text and
            'К какой категории отнести' not in text
        ):
            return []
        return [
            {'label': category, 'action': category}
            for category in (
                'Поставщик',
                'Заказчик',
                'Покупатель',
                'Подрядчик',
            )
        ]

    def _strip_partner_category_marker(self, answer):
        return (
            (answer or '')
            .replace('[PARTNER_CATEGORY_REQUIRED]', '')
            .strip()
        )

    def _json_dumps(self, value):
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

    def _dispatch_invoice_workflow(
        self,
        extraction_token=None,
        invoice_workflow_action=None,
        invoice_po_warehouse=None,
        awaiting_po_warehouse=None,
        invoice_workflow_payload=None,
        message=None,
    ):
        if not request.env.user.has_group(_GROUP_SUPPLY):
            return None
        token = extraction_token
        if not token:
            return None
        workflow = InvoiceWorkflow(request.env, _invoice_store)
        uid = request.env.uid
        payload = invoice_workflow_payload or {}
        if not isinstance(payload, dict):
            payload = {}

        if invoice_workflow_action == InvoiceWorkflow.ACTION_CREATE_PARTNER:
            return self._partner_pending_response(workflow, uid, token)

        if invoice_workflow_action == InvoiceWorkflow.ACTION_PO_START:
            return workflow.set_create_po_decision(
                uid,
                token,
                payload.get('create_po') is True,
            )

        if (
            invoice_workflow_action
            == InvoiceWorkflow.ACTION_PO_SELECT_WAREHOUSE
        ):
            return workflow.select_warehouse(
                uid,
                token,
                payload=payload,
                warehouse_query=invoice_po_warehouse,
            )

        if (
            invoice_workflow_action
            == InvoiceWorkflow.ACTION_PO_SET_ATTACH_INVOICE
        ):
            return workflow.set_attach_invoice_decision(
                uid,
                token,
                payload.get('attach_invoice') is True,
            )

        if (
            invoice_workflow_action
            == InvoiceWorkflow.ACTION_PO_SET_RECEIVE_PICKING
        ):
            return workflow.set_receive_picking_decision(
                uid,
                token,
                payload.get('receive_picking') is True,
            )

        if invoice_workflow_action == InvoiceWorkflow.ACTION_PO_CANCEL:
            return workflow.cancel_purchase_flow(uid, token)

        if invoice_workflow_action == InvoiceWorkflow.ACTION_PO_EXECUTE_PLAN:
            try:
                return workflow.execute_purchase_plan(uid, token)
            except ValidationError as err:
                return {
                    'answer': str(err),
                    'suggestions': [],
                    'cards': [],
                    'meta': {'status': 'error'},
                }

        if message and self._message_intends_partner(message):
            partner_response = self._partner_pending_response(
                workflow, uid, token
            )
            if partner_response:
                return partner_response
            if not workflow.partner_ready(uid, token):
                return {
                    'answer': (
                        'Поставщика нельзя создать из счёта: '
                        'ИНН не распознан. '
                        'Уточните ИНН или создайте контрагента вручную.'
                    ),
                    'suggestions': [],
                    'cards': [],
                    'meta': {'status': 'partner_incomplete'},
                }

        if not workflow.partner_ready(uid, token):
            if (
                invoice_workflow_action in (
                    InvoiceWorkflow.ACTION_NEXT_PRODUCT,
                    InvoiceWorkflow.ACTION_PREPARE_PO,
                )
                or (message and self._message_intends_po(message))
                or awaiting_po_warehouse
            ):
                partner_response = self._partner_pending_response(
                    workflow,
                    uid,
                    token,
                    answer=(
                        'Сначала нужно создать поставщика из счёта. '
                        'Проверьте карточку и подтвердите.'
                    ),
                )
                if partner_response:
                    return partner_response
                return {
                    'answer': (
                        'Поставщик счёта не найден, а ИНН не распознан. '
                        'Уточните ИНН или создайте контрагента вручную.'
                    ),
                    'suggestions': [],
                    'cards': [],
                    'meta': {'status': 'partner_incomplete'},
                }

        if invoice_workflow_action == InvoiceWorkflow.ACTION_NEXT_PRODUCT:
            draft = workflow.next_product_draft(uid, token)
            if not draft:
                return workflow.all_products_done_payload()
            return self._pending_write_response(
                'create_product_draft',
                draft['args'],
                metadata={
                    'extraction_token': token,
                    'invoice_line_key': draft['line_key'],
                },
                answer=(
                    'Следующая позиция счёта. Проверьте карточку '
                    'и подтвердите.'
                ),
            )

        # Перехватываем намерение «добавь на склад» / «создай закупку»
        # раньше, чем LLM сделает это минуя workflow.
        if message and self._message_intends_po(message):
            if not workflow.all_products_ready(uid, token):
                draft = workflow.next_product_draft(uid, token)
                if draft:
                    return self._pending_write_response(
                        'create_product_draft',
                        draft['args'],
                        metadata={
                            'extraction_token': token,
                            'invoice_line_key': draft['line_key'],
                        },
                        answer=(
                            'Сначала нужно создать карточки для новых '
                            'товаров из счёта. '
                            'Начнём с первого:'
                        ),
                    )
            else:
                return workflow.begin_purchase_flow_prompt(uid, token)

        warehouse_query = (invoice_po_warehouse or '').strip()
        if awaiting_po_warehouse and not warehouse_query and message:
            warehouse_query = (message or '').strip()
        if invoice_workflow_action == InvoiceWorkflow.ACTION_PREPARE_PO:
            return workflow.begin_purchase_flow_prompt(uid, token)
        if awaiting_po_warehouse and warehouse_query:
            return workflow.select_warehouse(
                uid,
                token,
                payload={},
                warehouse_query=warehouse_query,
            )

        return None

    def _partner_pending_response(
        self,
        workflow,
        uid,
        token,
        answer=(
            'Поставщик из счёта не найден. '
            'Проверьте карточку и подтвердите.'
        ),
    ):
        draft = workflow.next_partner_draft(uid, token)
        if not draft:
            return None
        return self._pending_write_response(
            'create_partner_draft',
            draft['args'],
            metadata={'extraction_token': token},
            answer=answer,
        )

    def _pending_write_response(
        self,
        tool_name,
        args,
        metadata=None,
        answer='Проверьте план и подтвердите действие.',
        meta=None,
    ):
        pending_key = _pending_actions.put(
            request.env.uid,
            tool_name,
            args,
            idempotency_key=self._idempotency_key(tool_name, args),
            metadata=metadata or {},
        )
        write_call = {'name': tool_name, 'arguments': args}
        return {
            'answer': answer,
            'suggestions': [],
            'cards': [self._confirmation_card(write_call, pending_key)],
            'meta': dict({'status': 'pending'}, **(meta or {})),
        }

    _PO_INTENT_KEYWORDS = (
        'добавь на склад', 'добавить на склад',
        'внеси на склад', 'внести на склад',
        'создай закупку', 'создать закупку',
        'оформи закупку', 'оформить закупку',
        'сделай po', 'создай po', 'create po',
        'занеси на склад', 'занести на склад',
        'закупку на склад', 'приёмку', 'приемку',
        'добавь товары', 'добавить товары',
    )

    def _message_intends_po(self, message):
        text = (message or '').lower().strip()
        return any(kw in text for kw in self._PO_INTENT_KEYWORDS)

    _PARTNER_INTENT_KEYWORDS = (
        'добавь поставщика',
        'добавить поставщика',
        'создай поставщика',
        'создать поставщика',
        'добавь контрагента',
        'добавить контрагента',
        'создай контрагента',
        'создать контрагента',
        'занеси в базу',
        'занести в базу',
    )

    def _message_intends_partner(self, message):
        text = (message or '').lower().strip()
        return any(kw in text for kw in self._PARTNER_INTENT_KEYWORDS)

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

    def _ai_unavailable_response(self, reason=''):
        if 'API key' in reason or 'API ключ' in reason:
            answer = (
                'AI не настроен: укажите OpenRouter API Key '
                'в Настройках → AI-консультант.'
            )
        elif 'не найдена' in reason or '404' in reason:
            answer = (
                'Модель OpenRouter недоступна (снята или неверный slug). '
                'Обновите поле «Модель (текст)» в настройках AI-консультанта '
                '(рекомендуется google/gemini-2.5-flash).'
            )
        else:
            answer = (
                'AI временно недоступен. Обратитесь к администратору Odoo.'
            )
            if reason:
                answer += ' (%s)' % reason
        return {
            'answer': answer,
            'suggestions': [],
            'meta': {'status': 'ai_unavailable'},
        }
