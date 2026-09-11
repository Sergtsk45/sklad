# @file: address_utils.py
# @description: Простые эвристики адреса поставщика из счёта.
# @created: 2026-06-12

import re


_ZIP_RE = re.compile(r'^\s*(?P<zip>\d{6})(?:\s*,\s*|\s+)')
_CITY_RE = re.compile(
    r'(?:^|[,;\s])(?:г\.?|город)\s*'
    r'(?P<city>[А-ЯЁA-Z][А-ЯЁA-Zа-яёa-z.\-\s]+?)'
    r'(?=,|;|\s+(?:ул\.?|улица|пр-кт|проспект|пер\.?|'
    r'ш\.?|шоссе|д\.?|дом)\b|$)'
)


def parse_supplier_address(address):
    """
    Return res.partner address vals from a raw invoice address.

    v1 keeps the original address in ``street`` to avoid data loss and only
    adds safe structured hints for ``zip`` and ``city`` when obvious.
    """
    raw = (address or '').strip()
    if not raw:
        return {}

    vals = {'street': raw}
    zip_match = _ZIP_RE.search(raw)
    if zip_match:
        vals['zip'] = zip_match.group('zip')

    city_match = _CITY_RE.search(raw)
    if city_match:
        city = re.sub(r'\s+', ' ', city_match.group('city')).strip(' .')
        if city:
            vals['city'] = city
    return vals
