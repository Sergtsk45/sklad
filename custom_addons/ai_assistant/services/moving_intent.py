import re

from .openrouter_client import OpenRouterClient


MOVING_SCHEMA = {
    'type': 'object',
    'properties': {
        'intent': {'type': 'boolean'},
        'product_query': {'type': ['string', 'null']},
        'quantity': {'type': ['number', 'null']},
        'uom_text': {'type': ['string', 'null']},
        'source_warehouse_query': {'type': ['string', 'null']},
        'destination_warehouse_query': {'type': ['string', 'null']},
        'scheduled_date_text': {'type': ['string', 'null']},
        'correction': {'type': 'boolean'},
        'selection_ordinal': {'type': ['integer', 'null'], 'minimum': 1},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
    },
    'required': [
        'intent', 'product_query', 'quantity', 'uom_text',
        'source_warehouse_query', 'destination_warehouse_query',
        'scheduled_date_text', 'correction', 'selection_ordinal', 'confidence',
    ],
    'additionalProperties': False,
}

_MOVE_RE = re.compile(
    r'\b(?:перемест(?:и|ить|ите)|перенес(?:и|ти|ите)|перевед(?:и|ите)|'
    r'перемещени(?:е|я|ю|ем|и|й))\b', re.I,
)
_WAREHOUSE_CONTEXT_RE = re.compile(
    r'\bсклад\w*\b|\bс(?:о)?\s+.+?\s+на\s+|\b(?:O\d+|ОбМ-\d+)\b', re.I,
)
_QTY_RE = re.compile(
    r'(?<!\w)(\d+(?:[.,]\d+)?)\s*'
    r'(шт(?:\.|ук\w*)?|кг|килограмм\w*|г|л|м(?:етр\w*)?)?\b', re.I,
)
_ROUTE_RE = re.compile(
    r'\bс(?:о)?\s+(?P<src>.+?)\s+на\s+(?P<dst>.+?)'
    r'(?=\s+(?:сегодня|завтра|\d{2}\.\d{2}\.\d{4}|\d{4}-\d{2}-\d{2})\b|$)',
    re.I,
)
_DATE_RE = re.compile(
    r'\b(?:сегодня|завтра|\d{2}\.\d{2}\.\d{4}(?:\s+\d{1,2}:\d{2})?'
    r'|\d{4}-\d{2}-\d{2}(?:\s+\d{1,2}:\d{2})?)\b', re.I,
)


def is_moving_candidate(message):
    text = message or ''
    return bool(_MOVE_RE.search(text) and _WAREHOUSE_CONTEXT_RE.search(text))


def keyword_moving_fallback(message):
    text = (message or '').strip()
    if not is_moving_candidate(text):
        return None
    qty_match = _QTY_RE.search(text)
    route_match = _ROUTE_RE.search(text)
    date_match = _DATE_RE.search(text)
    product = _MOVE_RE.sub(' ', text, count=1)
    if qty_match:
        product = product.replace(qty_match.group(0), ' ', 1)
    if route_match:
        product = product.replace(route_match.group(0), ' ', 1)
    if date_match:
        product = product.replace(date_match.group(0), ' ', 1)
    product = re.sub(r'\b(?:товар|товара|пожалуйста)\b', ' ', product, flags=re.I)
    product = re.sub(r'\s+', ' ', product).strip(' ,.;:-')
    return {
        'intent': True,
        'product_query': product if len(product) >= 2 else None,
        'quantity': (
            float(qty_match.group(1).replace(',', '.')) if qty_match else None
        ),
        'uom_text': qty_match.group(2) if qty_match and qty_match.group(2) else None,
        'source_warehouse_query': (
            _clean_warehouse_phrase(route_match.group('src'))
            if route_match else None
        ),
        'destination_warehouse_query': (
            _clean_warehouse_phrase(route_match.group('dst'))
            if route_match else None
        ),
        'scheduled_date_text': date_match.group(0) if date_match else None,
        'correction': False,
        'selection_ordinal': None,
        'confidence': 0.7,
        'fallback': True,
    }


class MovingIntentExtractor:
    def __init__(self, env, client=None):
        self.client = client or OpenRouterClient(env)

    def extract(self, message):
        fallback = keyword_moving_fallback(message)
        try:
            result = self.client.send_structured_chat(
                [{
                    'role': 'system',
                    'content': (
                        'Извлеки намерение межскладского перемещения. '
                        'Возвращай только JSON без tools и ID. Все query и date '
                        'поля копируй дословно; не исправляй и не выдумывай.'
                    ),
                }, {'role': 'user', 'content': message or ''}],
                {'name': 'moving_intent', 'strict': True, 'schema': MOVING_SCHEMA},
                max_tokens=450,
                timeout=8,
            )
        except Exception:
            return fallback or _empty_intent()
        source = _normalize(message)
        for field in (
            'product_query', 'uom_text', 'source_warehouse_query',
            'destination_warehouse_query', 'scheduled_date_text',
        ):
            value = result.get(field)
            if value and _normalize(value) not in source:
                result[field] = (fallback or {}).get(field)
        if not _quantity_has_evidence(result.get('quantity'), message):
            result['quantity'] = (fallback or {}).get('quantity')
        return result


def _normalize(value):
    return re.sub(r'\s+', ' ', value or '').strip().casefold()


def _clean_warehouse_phrase(value):
    value = (value or '').strip(' ,.;')
    return re.sub(r'^(?:склад(?:а|у|ом|е)?\s+)', '', value, flags=re.I)


def _quantity_has_evidence(quantity, message):
    if quantity is None:
        return True
    try:
        expected = float(quantity)
    except (TypeError, ValueError):
        return False
    for value in re.findall(r'(?<!\w)\d+(?:[.,]\d+)?(?!\w)', message or ''):
        if abs(float(value.replace(',', '.')) - expected) <= 1e-12:
            return True
    return False


def _empty_intent():
    return {key: None for key in MOVING_SCHEMA['properties']} | {
        'intent': False, 'correction': False, 'confidence': 0,
    }
