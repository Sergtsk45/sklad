"""Starter synonyms for product search; loaded into product.search.synonym."""

from .product_search_utils import normalize_product_search_text


# (terms, canonical): every term is replaced by the canonical form both in
# product names and in queries.
DEFAULT_SYNONYMS = [
    ('оц оцинк оцинкованный оцинкованная цинк', 'оцинкованный'),
    ('dn d д', 'ду'),
    ('pn', 'ру'),
    ('ст стал', 'стальной'),
    ('шар', 'шаровый'),
    ('ппр', 'ppr'),
    ('уголок', 'угольник'),
    ('гофра гофр', 'гофрированный'),
    ('нерж', 'нержавеющий'),
    ('вн', 'вр'),
    ('нар', 'нр'),
    ('бп', 'блок питания'),
    ('автомат', 'выключатель автоматический'),
    ('динрейка динрейку динрейке', 'din рейка'),
    ('земля', 'заземление'),
]


def default_synonym_map():
    """Return {normalized term: normalized canonical} for DEFAULT_SYNONYMS."""
    result = {}
    for terms, canonical in DEFAULT_SYNONYMS:
        for term in terms.split():
            result[normalize_product_search_text(term)] = (
                normalize_product_search_text(canonical)
            )
    return result
