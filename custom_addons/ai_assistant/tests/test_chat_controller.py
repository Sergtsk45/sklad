import json
from unittest.mock import patch, MagicMock

from odoo.tests.common import HttpCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestChatController(HttpCase):

    def setUp(self):
        super().setUp()
        self.authenticate('admin', 'admin')

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
            'OpenRouterClient.send_chat',
            return_value={
                'answer': 'Привет.',
                'model_used': 'test-model',
                'mode': 'text',
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
