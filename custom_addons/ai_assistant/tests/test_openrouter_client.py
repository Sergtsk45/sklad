from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.addons.ai_assistant.services.openrouter_client import (
    OpenRouterClient,
)


@tagged('post_install', '-at_install')
class TestOpenRouterClient(TransactionCase):

    def _make_client(self, api_key=''):
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.openrouter_api_key', api_key
        )
        return OpenRouterClient(self.env)

    def test_no_api_key_raises(self):
        client = self._make_client(api_key='')
        with self.assertRaises(ValueError):
            client.send_chat([{'role': 'user', 'content': 'test'}])

    def test_send_chat_mocked(self):
        client = self._make_client(api_key='test-key-123')

        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'Привет!'}}],
            'model': 'openai/gpt-4o-mini',
            'usage': {'total_tokens': 42},
        }

        with patch('requests.post', return_value=mock_resp) as mock_post:
            result = client.send_chat([{'role': 'user', 'content': 'Привет'}])

        self.assertEqual(result['answer'], 'Привет!')
        self.assertEqual(result['tokens_used'], 42)

        call_kwargs = mock_post.call_args
        payload = call_kwargs[1]['json']
        self.assertEqual(payload['messages'][0]['role'], 'user')
        self.assertIn('model', payload)
        headers = call_kwargs[1]['headers']
        self.assertIn('HTTP-Referer', headers)
        self.assertEqual(headers.get('X-Title'), 'Odoo AI Assistant')

    def test_is_security_policy_error(self):
        self.assertTrue(
            OpenRouterClient.is_security_policy_error(
                ValueError(
                    'OpenRouter: ошибка 403: Access denied by security policy.'
                )
            )
        )
        self.assertFalse(
            OpenRouterClient.is_security_policy_error(
                ValueError('OpenRouter: неверный API ключ')
            )
        )

    def test_http_referer_uses_web_base_url(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'web.base.url', 'https://skladtsk.duckdns.org'
        )
        client = self._make_client(api_key='test-key-123')
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            'choices': [{'message': {'content': 'ok'}}],
            'model': 'google/gemini-2.5-flash',
            'usage': {'total_tokens': 1},
        }
        with patch('requests.post', return_value=mock_resp) as mock_post:
            client.send_chat([{'role': 'user', 'content': 'hi'}])
        headers = mock_post.call_args[1]['headers']
        self.assertEqual(
            headers['HTTP-Referer'],
            'https://skladtsk.duckdns.org',
        )
