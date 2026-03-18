import logging
import re

_logger = logging.getLogger(__name__)

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_SIZE = 12

CONTEXT_WHITELIST = frozenset([
    'module', 'action', 'model', 'view_type', 'lang', 'user_groups', 'url',
])

# Паттерны prompt injection
_INJECTION_PATTERNS = [
    r'ignore\s+(previous|all|above|prior)\s+instructions?',
    r'forget\s+(everything|all|your|previous)',
    r'you\s+are\s+now\s+',
    r'act\s+as\s+',
    r'pretend\s+(to\s+be|you\s+are)',
    r'disregard\s+(your|all)',
    r'new\s+persona',
    r'(?<!\w)system\s*:\s*(?!\w)',
    r'<\s*/?system\s*>',
    r'\[INST\]',
    r'<<SYS>>',
]

_COMPILED_INJECTION = [
    re.compile(p, re.IGNORECASE) for p in _INJECTION_PATTERNS
]

# Фразы, обещающие автоматические действия
_UNSAFE_RESPONSE_PATTERNS = [
    r'я\s+(выполн|сдела|созда|удал|измен|запус)\w*',
    r'сейчас\s+(выполн|сдела|созда|удал|измен)\w*',
    r'автоматически\s+(выполн|создам|удалю|изменю)\w*',
    r'\bI\s+will\s+(execute|delete|create|modify|run)\b',
    r'\bI\s+have\s+(executed|deleted|created|modified)\b',
]

_COMPILED_UNSAFE = [
    re.compile(p, re.IGNORECASE) for p in _UNSAFE_RESPONSE_PATTERNS
]

_DISCLAIMER = (
    '\n\n⚠️ Обратите внимание: ассистент даёт только рекомендации '
    'и не выполняет действия в системе автоматически.'
)


class ResponseGuard:
    """Validates requests and filters responses for safety."""

    def sanitize_context(self, context):
        """Remove fields not in whitelist from context dict."""
        if not isinstance(context, dict):
            return {}
        return {k: v for k, v in context.items() if k in CONTEXT_WHITELIST}

    def validate_request(self, message, history):
        """
        Validate incoming request.

        :returns: (is_valid: bool, error_message: str|None)
        """
        if not message or not str(message).strip():
            return False, 'Сообщение не может быть пустым'

        if len(str(message)) > MAX_MESSAGE_LENGTH:
            return False, 'Сообщение слишком длинное'

        if self._has_injection(message):
            _logger.warning(
                'Prompt injection detected (msg_len=%d)', len(message)
            )
            return False, 'Запрос содержит недопустимые конструкции'

        if isinstance(history, list) and len(history) > MAX_HISTORY_SIZE:
            return False, 'История сообщений превышает допустимый размер'

        return True, None

    def filter_response(self, answer):
        """
        Filter response for unsafe content.

        :returns: cleaned answer string
        """
        if not answer:
            return answer

        for pattern in _COMPILED_UNSAFE:
            if pattern.search(answer):
                _logger.warning(
                    'Unsafe response pattern detected, appending disclaimer'
                )
                return answer + _DISCLAIMER

        return answer

    def _has_injection(self, text):
        for pattern in _COMPILED_INJECTION:
            if pattern.search(text):
                return True
        return False
