"""Shared helpers for normalized product search."""

import re


_SPACES_RE = re.compile(r'\s+')
_TECH_SIZE_RE = re.compile(
    r'\b(ду|ру|dn|pn)\s*-?\s*(\d+)\b',
    flags=re.IGNORECASE,
)
_DIMENSION_RE = re.compile(r'(?<=\d)\s*[xх×]\s*(?=\d)', flags=re.IGNORECASE)
_DECIMAL_COMMA_RE = re.compile(r'(?<=\d),(?=\d)')


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
