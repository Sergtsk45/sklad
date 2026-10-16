"""Offline benchmark of product search (plan 2026-10-17-product-search-v2).

Data (``data/``): ``catalog.csv`` — active product names, ``pairs.csv`` —
foreman text from request lines and the product chosen by purchasing.
No suppliers, prices or ids.

Run from the repository root:

    python3 custom_addons/custom_product_search/tests/bench/bench_search.py

Modes: C — current autocomplete (ilike, all words required),
V2 — tokens + synonyms + ranking (``product_search_tokens``).
"""

import csv
import importlib.util
import os
import sys
import types

LIMIT = 8
HERE = os.path.dirname(os.path.abspath(__file__))
MODELS = os.path.join(HERE, '..', '..', 'models')
DATA = os.path.join(HERE, 'data')


def _load_models():
    package = types.ModuleType('cps_models')
    package.__path__ = [MODELS]
    sys.modules['cps_models'] = package
    modules = {}
    for name in ('product_search_utils', 'product_search_tokens',
                 'product_search_synonyms_data'):
        spec = importlib.util.spec_from_file_location(
            f'cps_models.{name}', os.path.join(MODELS, f'{name}.py'),
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        modules[name] = module
    return modules


def _read_csv(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def current_search(catalog, norm, query):
    """Emulate the current autocomplete: ilike, then normalized AND."""
    low = query.lower()
    result = [name for name in catalog if low in name.lower()][:LIMIT]
    if len(result) >= LIMIT:
        return result
    normalized = norm(query)
    words = normalized.split()
    for name in catalog:
        if name in result:
            continue
        text = norm(name)
        if normalized in text or (
            len(words) > 1 and all(word in text for word in words)
        ):
            result.append(name)
            if len(result) >= LIMIT:
                break
    return result


def make_v2(catalog, tokens_module, synonyms):
    """Return a search function equivalent to the SQL implementation."""
    tokenize = tokens_module.tokenize_product_text
    docs = [(name, tokenize(name, synonyms), name) for name in catalog]
    vocabulary = tokens_module.build_vocabulary(doc[1] for doc in docs)

    def search(query):
        plan = tokens_module.build_search_plan(query, vocabulary, synonyms)
        lexemes = set(tokens_module.plan_lexemes(plan))
        candidates = [doc for doc in docs if lexemes & set(doc[1])]
        return tokens_module.rank_candidates(plan, candidates, LIMIT)
    return search


def evaluate(search, pairs, transform=None):
    found = top1 = 0
    misses = []
    for pair in pairs:
        query = transform(pair['query']) if transform else pair['query']
        result = search(query)[:LIMIT]
        if pair['expected'] in result:
            found += 1
            top1 += result[0] == pair['expected']
        else:
            misses.append((query, pair['expected'], result[:3]))
    return found, top1, misses


def main():
    modules = _load_models()
    norm = modules['product_search_utils'].normalize_product_search_text
    synonyms = modules['product_search_synonyms_data'].default_synonym_map()
    catalog = [row['name'] for row in _read_csv('catalog.csv')]
    pairs = [
        row for row in _read_csv('pairs.csv') if row['expected'] in catalog
    ]
    tokens_module = modules['product_search_tokens']
    modes = {
        'C current': lambda q: current_search(catalog, norm, q),
        'V2 no synonyms': make_v2(catalog, tokens_module, {}),
        'V2': make_v2(catalog, tokens_module, synonyms),
    }
    total = len(pairs)
    print(f'pairs: {total}, catalog: {len(catalog)}')
    for name, search in modes.items():
        found, top1, misses = evaluate(search, pairs)
        short, _t, _m = evaluate(
            search, pairs, lambda q: ' '.join(q.split()[:2]),
        )
        print(
            f'{name:16} found@8 {found:3} ({100 * found / total:.0f}%)'
            f'  top1 {top1:3} ({100 * top1 / total:.0f}%)'
            f'  2 words found@8 {short:3} ({100 * short / total:.0f}%)'
        )
        if '-v' in sys.argv and name == 'V2':
            for query, expected, got in misses:
                print(f'  MISS {query!r} -> {expected!r}\n       got {got}')


if __name__ == '__main__':
    main()
