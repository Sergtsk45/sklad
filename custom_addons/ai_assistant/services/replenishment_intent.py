import re

from .openrouter_client import OpenRouterClient


REPLENISHMENT_SCHEMA = {
    'type': 'object',
    'properties': {
        'intent': {'type': 'boolean'},
        'product_query': {'type': ['string', 'null']},
        'quantity': {'type': ['number', 'null']},
        'uom_text': {'type': ['string', 'null']},
        'vendor_query': {'type': ['string', 'null']},
        'vendor_preference': {
            'type': ['string', 'null'], 'enum': ['cheapest', None],
        },
        'warehouse_query': {'type': ['string', 'null']},
        'correction': {'type': 'boolean'},
        'selection_ordinal': {'type': ['integer', 'null'], 'minimum': 1},
        'confidence': {'type': 'number', 'minimum': 0, 'maximum': 1},
    },
    'required': [
        'intent', 'product_query', 'quantity', 'uom_text', 'vendor_query',
        'vendor_preference', 'warehouse_query', 'correction',
        'selection_ordinal', 'confidence',
    ],
    'additionalProperties': False,
}


class ReplenishmentIntentExtractor:
    CONFIDENCE_THRESHOLD = 0.65

    def __init__(self, env, client=None):
        self.client = client or OpenRouterClient(env)

    def extract(self, message):
        result = self.client.send_structured_chat(
            [{
                'role': 'system',
                'content': (
                    'Извлеки намерение пополнить склад. Возвращай только JSON. '
                    'Не выдумывай ID, цены или отсутствующие значения. '
                    'product_query копируй дословно из сообщения пользователя: '
                    'не склоняй, не исправляй и не перефразируй название товара.'
                ),
            }, {'role': 'user', 'content': message or ''}],
            {'name': 'replenishment_intent', 'strict': True,
             'schema': REPLENISHMENT_SCHEMA},
            max_tokens=400,
            timeout=8,
        )
        product_query = (result.get('product_query') or '').strip()
        source = re.sub(r'\s+', ' ', message or '').casefold()
        verbatim = re.sub(r'\s+', ' ', product_query).casefold()
        if not product_query or verbatim not in source:
            fallback = keyword_replenishment_fallback(message)
            result['product_query'] = (
                fallback.get('product_query') if fallback else None
            )
        return result


_INTENT_RE = re.compile(
    r'\b(?:пополни(?:ть|те)?|пополнени(?:е|я|ю|ем)|'
    r'дозакажи(?:те)?|закупи(?:ть|те)?)\b',
    re.IGNORECASE,
)
_INTRO_RE = re.compile(
    r'\b(?:сделай(?:те)?|создай(?:те)?|пожалуйста|нужно|надо)\b',
    re.I,
)
_QTY_TAIL_RE = re.compile(
    r'\b\d+(?:[.,]\d+)?\s*'
    r'(?:шт(?:ук(?:и|а|ов)?)?|м(?:етр(?:а|ов)?)?|кг|килограмм(?:а|ов)?)\b',
    re.I,
)
_VENDOR_TAIL_RE = re.compile(r'\s+\bот\b\s+.+?(?=\s+\bна\b|$)', re.I)
_WAREHOUSE_TAIL_RE = re.compile(
    r'\s+\bна\b\s+[^,.;]*(?:склад[^,.;]*)?$', re.I
)


def keyword_replenishment_fallback(message):
    text = (message or '').strip()
    if not _INTENT_RE.search(text):
        return None
    product_query = _INTRO_RE.sub(' ', _INTENT_RE.sub(' ', text))
    product_query = re.sub(r'^\s*для\b', ' ', product_query, flags=re.I)
    product_query = _QTY_TAIL_RE.sub(' ', product_query)
    product_query = _VENDOR_TAIL_RE.sub(' ', product_query)
    product_query = _WAREHOUSE_TAIL_RE.sub(' ', product_query)
    # Conservative fallback: do not contaminate catalog search with values
    # belonging to later workflow steps. Those steps will ask explicitly.
    product_query = re.split(
        r'\s+\d+(?:[.,]\d+)?\s*(?:шт\.?|кг|м|л)?\b',
        product_query,
        maxsplit=1,
        flags=re.I,
    )[0]
    product_query = re.split(r'\s+от\s+', product_query, maxsplit=1,
                             flags=re.I)[0]
    product_query = re.sub(r'\s+', ' ', product_query).strip(' ,.;:-')
    return {
        'intent': True,
        'product_query': product_query if len(product_query) >= 2 else None,
        'quantity': None,
        'uom_text': None,
        'vendor_query': None,
        'vendor_preference': None,
        'warehouse_query': None,
        'correction': False,
        'selection_ordinal': None,
        'confidence': 0.7,
        'fallback': True,
    }
