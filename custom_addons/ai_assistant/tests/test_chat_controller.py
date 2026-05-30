import json
from unittest.mock import patch, MagicMock

from odoo.tests.common import HttpCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestChatController(HttpCase):

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')
        if not self.env['stock.warehouse'].search([('code', '=', 'ОбМ-4')], limit=1):
            self.env['stock.warehouse'].create({
                'name': 'Б. Хмельницкого, 112',
                'code': 'ОбМ-4',
            })

    def _post_chat(self, payload, authenticated=True):
        body = json.dumps(
            {'jsonrpc': '2.0', 'method': 'call', 'params': payload}
        )
        response = self.url_open(
            '/ai_assistant/chat',
            data=body.encode(),
            headers={'Content-Type': 'application/json'},
        )
        return response.json()

    def _post_chat_no_auth(self, payload):
        """Send chat request without authentication."""
        self.session = self.opener.cookies
        body = json.dumps(
            {'jsonrpc': '2.0', 'method': 'call', 'params': payload}
        )
        # Create a fresh opener without session cookies
        import urllib.request
        import urllib.error
        import http.cookiejar
        cj = http.cookiejar.CookieJar()
        opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(cj)
        )
        req = urllib.request.Request(
            self.base_url() + '/ai_assistant/chat',
            data=body.encode(),
            headers={'Content-Type': 'application/json'},
        )
        try:
            with opener.open(req) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return {}

    # --- validation tests ---

    def test_chat_returns_answer(self):
        with patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value={
                'type': 'message',
                'content': 'Привет.',
                'tool_calls': [],
                'model_used': 'test-model',
            },
        ):
            result = self._post_chat({'message': 'Привет'})
        data = result.get('result', {})
        self.assertIn('answer', data)
        self.assertFalse(data.get('error'))

    def test_chat_empty_message(self):
        result = self._post_chat({'message': ''})
        data = result.get('result', {})
        self.assertIn('error', data)

    def test_chat_message_too_long(self):
        result = self._post_chat({'message': 'x' * 2001})
        data = result.get('result', {})
        self.assertIn('error', data)

    def test_chat_history_too_large(self):
        history = [{'role': 'user', 'content': 'q'}] * 13
        result = self._post_chat({'message': 'Вопрос', 'history': history})
        data = result.get('result', {})
        self.assertIn('error', data)

    # --- mock OpenRouter: successful round-trip ---

    def test_chat_with_mock_openrouter_returns_answer(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.openrouter_api_key', 'test-key'
        )
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.module_enabled', 'True'
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'Нажмите Создать.'}}],
            'model': 'openai/gpt-4o-mini',
            'usage': {'total_tokens': 30},
        }
        with patch('requests.post', return_value=mock_resp):
            result = self._post_chat({'message': 'Как создать товар?'})
        data = result.get('result', {})
        self.assertIn('answer', data)
        self.assertFalse(data.get('error'))
        self.assertIn('Нажмите Создать', data.get('answer', ''))

    # --- mock OpenRouter: error → graceful fallback ---

    def test_chat_openrouter_unavailable_returns_fallback(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.openrouter_api_key', 'test-key'
        )
        import requests
        with patch('requests.post', side_effect=requests.exceptions.Timeout):
            result = self._post_chat({'message': 'Вопрос'})
        data = result.get('result', {})
        # Should return an error message, not a crash
        self.assertTrue(data.get('error') or data.get('answer'))

    def test_chat_openrouter_500_returns_fallback(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.openrouter_api_key', 'test-key'
        )
        mock_resp = MagicMock()
        mock_resp.status_code = 500
        mock_resp.json.return_value = {'error': 'Internal Server Error'}
        with patch('requests.post', return_value=mock_resp):
            result = self._post_chat({'message': 'Вопрос'})
        data = result.get('result', {})
        self.assertTrue(data.get('error') or data.get('answer'))

    # --- check_access endpoint ---

    def test_check_access_returns_dict(self):
        body = json.dumps(
            {'jsonrpc': '2.0', 'method': 'call', 'params': {}}
        )
        response = self.url_open(
            '/ai_assistant/check_access',
            data=body.encode(),
            headers={'Content-Type': 'application/json'},
        )
        result = response.json()
        data = result.get('result', {})
        self.assertIn('has_access', data)

    def test_actions_mode_read_tool_call_loop(self):
        partner = self.env['res.partner'].create({
            'name': 'ООО Tool Loop',
            'supplier_rank': 1,
        })
        responses = [
            {
                'type': 'tool_calls',
                'content': '',
                'tool_calls': [{
                    'id': 'call_1',
                    'name': 'find_partner',
                    'arguments': {
                        'query': partner.name,
                        'is_supplier': True,
                    },
                }],
                'model_used': 'test-model',
            },
            {
                'type': 'message',
                'content': 'Поставщик найден.',
                'tool_calls': [],
                'model_used': 'test-model',
            },
        ]
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            side_effect=responses,
        ):
            result = self._post_chat({
                'message': 'Найди поставщика',
                'context': {'module': 'purchase'},
            })

        data = result.get('result', {})
        self.assertEqual(data.get('answer'), 'Поставщик найден.')
        self.assertEqual(data.get('cards'), [])
        self.assertEqual(data.get('meta', {}).get('mode'), 'actions')

    def test_actions_mode_write_returns_confirmation_card(self):
        project = self.env['object.request.project'].create({
            'name': 'Chat Confirm Object',
        })
        response = {
            'type': 'tool_calls',
            'content': '',
            'tool_calls': [{
                'id': 'call_write',
                'name': 'create_object_request_draft',
                'arguments': {
                    'project_id': project.id,
                    'need_date': '2026-06-20',
                    'lines': [{
                        'name_raw': 'Труба',
                        'qty_requested': 2.0,
                        'preferred_vendor_id': None,
                    }],
                },
            }],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ):
            result = self._post_chat({'message': 'Создай требование'})

        data = result.get('result', {})
        self.assertEqual(data['cards'][0]['type'], 'confirmation')
        self.assertTrue(data['cards'][0]['pending_key'])
        self.assertEqual(
            data['cards'][0]['plan']['tool_name'],
            'create_object_request_draft',
        )

    def test_confirm_endpoint_executes_pending(self):
        project = self.env['object.request.project'].create({
            'name': 'Chat Execute Object',
        })
        pending_key = self._create_pending_or(project.id)

        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'ToolExecutor.execute',
            return_value={
                'success': True,
                'result': {
                    'request_id': 99,
                    'name': 'OR/TEST',
                    'url': '/odoo/object_request/99',
                },
            },
        ):
            result = self._post_confirm({
                'pending_key': pending_key,
                'decision': 'confirm',
            })

        data = result.get('result', {})
        self.assertEqual(data.get('meta', {}).get('status'), 'ok')
        self.assertEqual(data['cards'][0]['type'], 'result')
        self.assertEqual(data['cards'][0]['status'], 'success')
        self.assertTrue(data['cards'][0]['record']['id'])

    def test_confirm_with_wrong_key_returns_error(self):
        result = self._post_confirm({
            'pending_key': 'wrong',
            'decision': 'confirm',
        })

        data = result.get('result', {})
        self.assertIn('error', data)

    def test_idempotency_reuses_pending(self):
        project = self.env['object.request.project'].create({
            'name': 'Chat Idempotent Object',
        })

        first_key = self._create_pending_or(project.id)
        second_key = self._create_pending_or(project.id)

        self.assertEqual(first_key, second_key)

    def test_max_iterations_breaks_loop(self):
        response = {
            'type': 'tool_calls',
            'content': '',
            'tool_calls': [{
                'id': 'call_1',
                'name': 'find_partner',
                'arguments': {
                    'query': 'No Vendor',
                    'is_supplier': True,
                },
            }],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ):
            result = self._post_chat({'message': 'Loop tools'})

        data = result.get('result', {})
        self.assertEqual(
            data.get('meta', {}).get('status'),
            'max_iterations',
        )

    def test_actions_mode_with_screenshot_uses_tools(self):
        """Actions mode must keep tool loop when a screenshot is attached."""
        screenshot = 'data:image/jpeg;base64,' + ('A' * 1000)
        tools_response = {
            'type': 'message',
            'content': 'Вижу экран, поставщик найден.',
            'tool_calls': [],
            'model_used': 'vision-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=tools_response,
        ) as mock_tools, patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat',
        ) as mock_chat:
            result = self._post_chat({
                'message': 'Что на экране и найди поставщика',
                'context': {'module': 'purchase'},
                'screenshot': screenshot,
            })

        data = result.get('result', {})
        self.assertEqual(
            data.get('answer'),
            'Вижу экран, поставщик найден.',
        )
        self.assertEqual(data.get('meta', {}).get('mode'), 'actions')
        mock_tools.assert_called_once()
        mock_chat.assert_not_called()
        _, kwargs = mock_tools.call_args
        self.assertIn('model_override', kwargs)

    def test_consult_mode_uses_read_tools_not_send_chat(self):
        response = {
            'type': 'message',
            'content': (
                'Откройте [Заказы поставщикам](/odoo/purchase-orders).'
            ),
            'tool_calls': [],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='consult',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ) as mock_tools, patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat',
        ) as mock_chat:
            result = self._post_chat({
                'message': 'как посмотреть заказы поставщикам',
                'context': {'module': 'purchase'},
            })

        data = result.get('result', {})
        self.assertIn('purchase-orders', data.get('answer', ''))
        self.assertEqual(data.get('meta', {}).get('mode'), 'consult')
        mock_tools.assert_called_once()
        mock_chat.assert_not_called()
        tools_payload = mock_tools.call_args[0][1]
        tool_names = [item['function']['name'] for item in tools_payload]
        self.assertIn('get_navigation_link', tool_names)
        self.assertNotIn('create_object_request_draft', tool_names)

    def test_consult_mode_enriches_none_navigation_link(self):
        response = {
            'type': 'message',
            'content': (
                'Чтобы посмотреть заказы, перейдите в '
                '[Открыть «Заказы на закупку»](None). '
                'Путь: Покупка → Заказы → Заказы на закупку.'
            ),
            'tool_calls': [],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='consult',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ):
            result = self._post_chat({
                'message': 'как посмотреть заказы поставщикам',
                'context': {'module': 'purchase'},
            })

        data = result.get('result', {})
        answer = data.get('answer', '')
        self.assertNotIn('(None)', answer)
        self.assertIn('purchase-orders', answer)
        self.assertTrue(data.get('links'))
        self.assertIn('purchase-orders', data['links'][0]['url'])

    def test_consult_mode_enriches_warehouse_stock_link_from_history(self):
        response = {
            'type': 'message',
            'content': (
                'Я не могу предоставить ссылку на фильтр товаров по складу.'
            ),
            'tool_calls': [],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='consult',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ):
            result = self._post_chat({
                'message': 'дай ссылку на фильтр товаров по складу',
                'context': {'module': 'stock'},
                'history': [{
                    'role': 'assistant',
                    'content': (
                        'Найдено: Склад Б. Хмельницкого, 112 (ОбМ-4).'
                    ),
                }],
            })

        data = result.get('result', {})
        answer = data.get('answer', '')
        self.assertIn('ai-warehouse-stock', answer)
        self.assertTrue(any(
            'ai-warehouse-stock' in link.get('url', '')
            for link in data.get('links', [])
        ))

    def test_actions_mode_injects_invoice_context(self):
        from odoo.addons.ai_assistant.controllers import chat_controller

        supplier = self.env['res.partner'].create({
            'name': 'ИП Татаринов chat test',
            'vat': '280110406399',
            'supplier_rank': 1,
        })
        product = self.env['product.product'].create({
            'name': 'Труба chat invoice context',
            'is_storable': True,
            'purchase_ok': True,
        })
        invoice_data = {
            'invoice_number': 'НФ-CTX-1',
            'invoice_date': '2026-05-20',
            'supplier': {
                'name': supplier.name,
                'inn': supplier.vat,
            },
            'items': [{
                'line_no': 1,
                'name': product.name,
                'unit': 'м',
                'qty': 3.0,
                'price': 100.0,
                'amount_w_vat': 360.0,
                'article': '',
            }],
            'totals': {'total_w_vat': 360.0},
        }
        token = chat_controller._invoice_store.put(
            self.env.ref('base.user_admin').id,
            invoice_data,
        )
        captured_messages = []

        def _capture_send(messages, tools, model_override=None):
            captured_messages.extend(messages)
            return {
                'type': 'message',
                'content': 'План PO готов.',
                'tool_calls': [],
                'model_used': 'test-model',
            }

        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            side_effect=_capture_send,
        ):
            result = self._post_chat({
                'message': 'Создай PO по загруженному счёту',
                'extraction_token': token,
            })

        data = result.get('result', {})
        self.assertEqual(data.get('answer'), 'План PO готов.')
        system_contents = '\n'.join(
            msg.get('content', '')
            for msg in captured_messages
            if msg.get('role') == 'system'
        )
        self.assertIn('INVOICE_CONTEXT', system_contents)
        self.assertIn('"partner_id": %d' % supplier.id, system_contents)
        self.assertIn('"product_id": %d' % product.id, system_contents)

    def _post_confirm(self, payload):
        body = json.dumps(
            {'jsonrpc': '2.0', 'method': 'call', 'params': payload}
        )
        response = self.url_open(
            '/ai_assistant/confirm',
            data=body.encode(),
            headers={'Content-Type': 'application/json'},
        )
        return response.json()

    def _create_pending_or(self, project_id):
        response = {
            'type': 'tool_calls',
            'content': '',
            'tool_calls': [{
                'id': 'call_write',
                'name': 'create_object_request_draft',
                'arguments': {
                    'project_id': project_id,
                    'need_date': '2026-06-21',
                    'lines': [{
                        'name_raw': 'Кран',
                        'qty_requested': 1.0,
                        'preferred_vendor_id': None,
                    }],
                },
            }],
            'model_used': 'test-model',
        }
        with patch(
            'odoo.addons.ai_assistant.controllers.chat_controller.'
            'AiAssistantController._resolve_mode',
            return_value='actions',
        ), patch(
            'odoo.addons.ai_assistant.services.openrouter_client.'
            'OpenRouterClient.send_chat_with_tools',
            return_value=response,
        ):
            result = self._post_chat({'message': 'Создай OR'})
        return result['result']['cards'][0]['pending_key']
