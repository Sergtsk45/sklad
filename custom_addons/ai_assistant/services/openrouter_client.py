import logging

import requests

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_MODEL = 'openai/gpt-4o-mini'
DEFAULT_TIMEOUT = 30


class OpenRouterClient:

    def __init__(self, env):
        params = env['ir.config_parameter'].sudo()
        self._api_key = params.get_param('ai_assistant.openrouter_api_key', '')
        self._base_url = params.get_param(
            'ai_assistant.openrouter_base_url', DEFAULT_BASE_URL
        )
        self._model = params.get_param(
            'ai_assistant.openrouter_model', DEFAULT_MODEL
        )
        self._timeout = int(params.get_param(
            'ai_assistant.openrouter_timeout', DEFAULT_TIMEOUT
        ))

    def send_chat(self, messages, max_tokens=1000):
        if not self._api_key:
            raise ValueError('OpenRouter API key не настроен')

        url = self._base_url.rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self._api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8069',
        }
        payload = {
            'model': self._model,
            'messages': messages,
            'max_tokens': max_tokens,
        }

        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=self._timeout
            )
        except requests.Timeout:
            raise ConnectionError('OpenRouter: таймаут запроса')

        _logger.info(
            'OpenRouter response: status=%s model=%s',
            resp.status_code, self._model
        )

        if resp.status_code == 429:
            raise ConnectionError('OpenRouter: превышен лимит запросов')
        if resp.status_code >= 500:
            raise ConnectionError('OpenRouter: ошибка сервера')

        try:
            data = resp.json()
        except Exception:
            raise ValueError('OpenRouter: некорректный ответ')

        return self._parse_response(data)

    def _parse_response(self, data):
        try:
            choice = data['choices'][0]
            answer = choice['message']['content']
            model_used = data.get('model', self._model)
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            return {
                'answer': answer,
                'model_used': model_used,
                'tokens_used': tokens_used,
            }
        except (KeyError, IndexError):
            raise ValueError('OpenRouter: некорректный ответ')
