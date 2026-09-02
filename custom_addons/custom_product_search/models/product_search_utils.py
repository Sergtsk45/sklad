"""Shared helpers for normalized product search."""

import re


_SPACES_RE = re.compile(r'\s+')
_TECH_SIZE_RE = re.compile(
    r'\b(ду|ру|dn|pn)\s*-?\s*(\d+)\b',
    flags=re.IGNORECASE,
)
_DIMENSION_RE = re.compile(r'(?<=\d)\s*[xх×]\s*(?=\d)', flags=re.IGNORECASE)
_DECIMAL_COMMA_RE = re.compile(r'(?<=\d),(?=\d)')
_CYRILLIC_WORD_RE = re.compile(r'^[а-я]+$')
_RU_SEARCH_SUFFIXES = tuple(sorted({
    'иями', 'ями', 'ами', 'ого', 'ему', 'ому', 'ыми', 'ими',
    'ией', 'иям', 'ием', 'иях', 'ую', 'юю', 'ая', 'яя', 'ые', 'ие',
    'ой', 'ей', 'ым', 'им', 'ых', 'их', 'ов', 'ев', 'ам', 'ям',
    'ах', 'ях', 'ом', 'ем', 'ою', 'ею', 'ию', 'ия', 'ья', 'ью',
    'ый', 'ий', 'а', 'я', 'у', 'ю', 'ы', 'и', 'е', 'о',
}, key=len, reverse=True))


def normalize_product_search_text(value):
    """Return a normalized product search string."""
    if not value:
        return ''

    normalized = str(value).replace('\u00A0', ' ')
    normalized = normalized.replace('ё', 'е').replace('Ё', 'Е').lower()
    normalized = _TECH_SIZE_RE.sub(r'\1\2', normalized)
    normalized = _DIMENSION_RE.sub('x', normalized)
    normalized = _DECIMAL_COMMA_RE.sub('.', normalized)
    normalized = _SPACES_RE.sub(' ', normalized).strip()
    return normalized


def russian_morphology_search_tokens(value):
    """Return conservative stems used only after exact search found nothing."""
    normalized = normalize_product_search_text(value)
    result = []
    for token in normalized.split():
        stem = token
        if len(token) >= 4 and _CYRILLIC_WORD_RE.fullmatch(token):
            for suffix in _RU_SEARCH_SUFFIXES:
                candidate = token[:-len(suffix)]
                if token.endswith(suffix) and len(candidate) >= 3:
                    stem = candidate
                    break
        result.append(stem)
    return result
