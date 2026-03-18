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
