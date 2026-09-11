from unittest.mock import MagicMock, patch

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.openrouter_client import (
    OpenRouterClient,
)


@tagged('post_install', '-at_install')
class TestOpenRouterTools(TransactionCase):

    def _make_client(self):
        self.env['ir.config_parameter'].sudo().set_param(
            'ai_assistant.openrouter_api_key', 'test-key'
        )
        return OpenRouterClient(self.env)

    def _mock_response(self, payload):
        response = MagicMock()
        response.status_code = 200
        response.json.return_value = payload
        return response

    def test_send_with_tools_passes_tools_in_payload(self):
        client = self._make_client()
        tools = [{'type': 'function', 'function': {'name': 'search_products'}}]
        response = self._mock_response({
            'choices': [{
                'finish_reason': 'stop',
                'message': {'content': 'Готово'},
            }],
            'model': 'test-model',
            'usage': {'total_tokens': 10},
        })

        with patch('requests.post', return_value=response) as mock_post:
            client.send_chat_with_tools(
                [{'role': 'user', 'content': 'Найди трубу'}],
                tools,
                tool_choice='auto',
            )

        payload = mock_post.call_args[1]['json']
        self.assertEqual(payload['tools'], tools)
        self.assertEqual(payload['tool_choice'], 'auto')

    def test_parses_tool_calls_response(self):
        client = self._make_client()
        response = self._mock_response({
            'choices': [{
                'finish_reason': 'tool_calls',
                'message': {
                    'content': None,
                    'tool_calls': [{
                        'id': 'call_1',
                        'type': 'function',
                        'function': {
                            'name': 'search_products',
                            'arguments': '{"query": "труба", "limit": 5}',
                        },
                    }],
                },
            }],
            'model': 'test-model',
            'usage': {'total_tokens': 20},
        })

        with patch('requests.post', return_value=response):
            result = client.send_chat_with_tools([], [])

        self.assertEqual(result['type'], 'tool_calls')
        self.assertEqual(result['finish_reason'], 'tool_calls')
        self.assertEqual(result['tool_calls'][0]['id'], 'call_1')
        self.assertEqual(result['tool_calls'][0]['name'], 'search_products')
        self.assertEqual(
            result['tool_calls'][0]['arguments'],
            {'query': 'труба', 'limit': 5},
        )

    def test_handles_invalid_json_in_arguments(self):
        client = self._make_client()
        response = self._mock_response({
            'choices': [{
                'finish_reason': 'tool_calls',
                'message': {
                    'tool_calls': [{
                        'id': 'call_bad',
                        'function': {
                            'name': 'find_partner',
                            'arguments': '{"query": ',
                        },
                    }],
                },
            }],
            'model': 'test-model',
            'usage': {'total_tokens': 3},
        })

        with patch('requests.post', return_value=response):
            result = client.send_chat_with_tools([], [])

        tool_call = result['tool_calls'][0]
        self.assertEqual(tool_call['arguments'], {})
        self.assertEqual(tool_call['arguments_error'], 'invalid_json')

    def test_finish_reason_stop_returns_message(self):
        client = self._make_client()
        response = self._mock_response({
            'choices': [{
                'finish_reason': 'stop',
                'message': {'content': 'Ответ без tools'},
            }],
            'model': 'test-model',
            'usage': {'total_tokens': 7},
        })

        with patch('requests.post', return_value=response):
            result = client.send_chat_with_tools([], [])

        self.assertEqual(result['type'], 'message')
        self.assertEqual(result['content'], 'Ответ без tools')
        self.assertEqual(result['tool_calls'], [])
        self.assertEqual(result['tokens_used'], 7)
