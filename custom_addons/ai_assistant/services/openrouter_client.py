import json
import logging

import requests

_logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = 'https://openrouter.ai/api/v1'
DEFAULT_TEXT_MODEL = 'google/gemini-2.5-flash'
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

        self._raise_for_http_error(resp, model)
        return self._parse_response(self._json_or_error(resp), mode=mode)

    def send_chat_with_tools(
        self,
        messages,
        tools,
        tool_choice='auto',
        max_tokens=1500,
        model_override=None,
    ):
        """Отправить сообщения в OpenRouter с OpenAI-compatible tools."""
        if not self._api_key:
            raise ValueError('OpenRouter API key не настроен')

        model = model_override or self._text_model
        url = self._base_url.rstrip('/') + '/chat/completions'
        headers = {
            'Authorization': f'Bearer {self._api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'http://localhost:8069',
        }
        payload = {
            'model': model,
            'messages': messages,
            'tools': tools,
            'tool_choice': tool_choice,
            'max_tokens': max_tokens,
        }

        _logger.info(
            'OpenRouter tools request: model=%s tools=%s',
            model, len(tools or [])
        )

        try:
            resp = requests.post(
                url, json=payload, headers=headers, timeout=self._timeout
            )
        except requests.Timeout:
            raise ConnectionError('OpenRouter: таймаут запроса')

        _logger.info(
            'OpenRouter tools response: status=%s model=%s',
            resp.status_code, model
        )

        self._raise_for_http_error(resp, model)
        return self._parse_tools_response(self._json_or_error(resp))

    def _json_or_error(self, resp):
        try:
            return resp.json()
        except Exception:
            raise ValueError('OpenRouter: некорректный ответ')

    def _raise_for_http_error(self, resp, model):
        if resp.status_code == 401:
            raise ValueError('OpenRouter: неверный API ключ')
        if resp.status_code == 404:
            raise ValueError(
                'OpenRouter: модель %s не найдена '
                '(возможно снята с публикации)' % model
            )
        if resp.status_code == 429:
            raise ConnectionError('OpenRouter: превышен лимит запросов')
        if resp.status_code >= 500:
            raise ConnectionError('OpenRouter: ошибка сервера')
        if resp.status_code >= 400:
            data = {}
            try:
                data = resp.json()
            except Exception:
                pass
            detail = (
                data.get('error', {}).get('message')
                if isinstance(data.get('error'), dict)
                else data.get('error')
            )
            raise ValueError(
                'OpenRouter: ошибка %s%s' % (
                    resp.status_code,
                    ': %s' % detail if detail else '',
                )
            )

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

    def _parse_tools_response(self, data):
        try:
            choice = data['choices'][0]
            message = choice['message']
        except (KeyError, IndexError):
            raise ValueError('OpenRouter: некорректный ответ')

        finish_reason = choice.get('finish_reason')
        model_used = data.get('model', self._text_model)
        tokens_used = data.get('usage', {}).get('total_tokens', 0)
        tool_calls = message.get('tool_calls') or []

        if tool_calls:
            parsed_tool_calls = [
                self._parse_tool_call(tool_call)
                for tool_call in tool_calls
            ]
            _logger.info(
                'OpenRouter tool_calls: count=%s names=%s',
                len(parsed_tool_calls),
                [item['name'] for item in parsed_tool_calls],
            )
            return {
                'type': 'tool_calls',
                'content': message.get('content') or '',
                'tool_calls': parsed_tool_calls,
                'finish_reason': finish_reason,
                'model_used': model_used,
                'tokens_used': tokens_used,
            }

        return {
            'type': 'message',
            'content': message.get('content') or '',
            'tool_calls': [],
            'finish_reason': finish_reason,
            'model_used': model_used,
            'tokens_used': tokens_used,
        }

    def _parse_tool_call(self, tool_call):
        function = tool_call.get('function') or {}
        arguments, parse_error = self._parse_tool_arguments(
            function.get('arguments')
        )
        result = {
            'id': tool_call.get('id'),
            'name': function.get('name'),
            'arguments': arguments,
        }
        if parse_error:
            result['arguments_error'] = parse_error
        return result

    def _parse_tool_arguments(self, raw_arguments):
        if raw_arguments in (None, ''):
            return {}, None
        if isinstance(raw_arguments, dict):
            return raw_arguments, None
        try:
            return json.loads(raw_arguments), None
        except (TypeError, ValueError):
            return {}, 'invalid_json'
