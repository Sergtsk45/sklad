import logging

import requests

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_TEXT_MODEL = 'google/gemini-2.0-flash-001'
DEFAULT_VISION_MODEL = 'openai/gpt-4o'
DEFAULT_TIMEOUT = 30

# Ключ оставлен для обратной совместимости (старые инсталляции)
_LEGACY_MODEL_PARAM = 'ai_assistant.openrouter_model'


class OpenRouterClient:

    def __init__(self, env):
        params = env['ir.config_parameter'].sudo()
        self._api_key = params.get_param('ai_assistant.openrouter_api_key', '')
        self._base_url = params.get_param(
            'ai_assistant.openrouter_base_url', DEFAULT_BASE_URL
        )
        # Основная модель для текстовых запросов; fallback → legacy → default
        text_model = params.get_param('ai_assistant.text_model', '')
        if not text_model:
            text_model = params.get_param(_LEGACY_MODEL_PARAM, DEFAULT_TEXT_MODEL)
        self._text_model = text_model or DEFAULT_TEXT_MODEL

        # Модель для vision-запросов (со скриншотом)
        self._vision_model = params.get_param(
            'ai_assistant.vision_model', DEFAULT_VISION_MODEL
        ) or DEFAULT_VISION_MODEL

        self._timeout = int(params.get_param(
            'ai_assistant.openrouter_timeout', DEFAULT_TIMEOUT
        ))

        # Для обратной совместимости: _model указывает на текстовую
        self._model = self._text_model

    def send_chat(self, messages, max_tokens=1500, model_override=None):
        """
        Отправить сообщения в OpenRouter.

        :param model_override: str|None — если передан, используется вместо
                               дефолтной модели (позволяет выбрать vision-модель).
        """
        if not self._api_key:
            raise ValueError('OpenRouter API key не настроен')

        model = model_override or self._text_model
        mode = 'vision' if model_override and model_override != self._text_model else 'text'

        url = self._base_url.rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self._api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8069',
        }
        payload = {
            'model': model,
            'messages': messages,
            'max_tokens': max_tokens,
        }

        _logger.info(
            'OpenRouter request: model=%s mode=%s', model, mode
        )

        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=self._timeout
            )
        except requests.Timeout:
            raise ConnectionError('OpenRouter: таймаут запроса')

        _logger.info(
            'OpenRouter response: status=%s model=%s',
            resp.status_code, model
        )

        if resp.status_code == 429:
            raise ConnectionError('OpenRouter: превышен лимит запросов')
        if resp.status_code >= 500:
            raise ConnectionError('OpenRouter: ошибка сервера')

        try:
            data = resp.json()
        except Exception:
            raise ValueError('OpenRouter: некорректный ответ')

        return self._parse_response(data, mode=mode)

    def _parse_response(self, data, mode='text'):
        try:
            choice = data['choices'][0]
            answer = choice['message']['content']
            model_used = data.get('model', self._text_model)
            tokens_used = data.get('usage', {}).get('total_tokens', 0)
            return {
                'answer': answer,
                'model_used': model_used,
                'tokens_used': tokens_used,
                'mode': mode,
            }
        except (KeyError, IndexError):
            raise ValueError('OpenRouter: некорректный ответ')
