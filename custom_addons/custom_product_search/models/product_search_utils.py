"""Shared helpers for normalized product search."""

import re


_SPACES_RE = re.compile(r'\s+')
_TECH_SIZE_RE = re.compile(r'\b(ду|dn)\s+(\d+)\b', flags=re.IGNORECASE)


def normalize_product_search_text(value):
    """Return a normalized product search string."""
    if not value:
        return ''

    normalized = str(value).replace('\u00A0', ' ')
    normalized = normalized.replace('ё', 'е').replace('Ё', 'Е').lower()
    normalized = _SPACES_RE.sub(' ', normalized).strip()
    return _TECH_SIZE_RE.sub(r'\1\2', normalized)
