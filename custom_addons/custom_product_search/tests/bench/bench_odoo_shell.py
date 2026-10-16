"""Online benchmark through the real ORM methods (read-only).

    docker exec -i odoo19-local odoo shell -d <db> --no-http \\
        < custom_addons/custom_product_search/tests/bench/bench_odoo_shell.py

Uses ``data/pairs.csv`` copied into the container next to the addon; the
expected product is matched by name. Prints found@8 / top1 for
``name_search`` (autocomplete), the list filter and ``ai_search_products``,
plus the slowest autocomplete queries.
"""

import csv
import time

LIMIT = 8
PAIRS = '/mnt/extra-addons/custom_product_search/tests/bench/data/pairs.csv'


def run(env):
    product_model = env['product.product']
    with open(PAIRS, encoding='utf-8') as handle:
        pairs = list(csv.DictReader(handle))
    names = {
        product.name: product.id
        for product in product_model.search([])
    }
    pairs = [pair for pair in pairs if pair['expected'] in names]
    stats = {'autocomplete': [0, 0], 'list filter': [0, 0], 'ai': [0, 0]}
    timings = []
    for pair in pairs:
        expected = names[pair['expected']]
        started = time.perf_counter()
        ids = [row[0] for row in product_model.name_search(
            pair['query'], limit=LIMIT,
        )]
        timings.append((time.perf_counter() - started, pair['query']))
        listed = product_model.search(
            [('x_smart_search', 'ilike', pair['query'])],
        ).ids
        ai_ids = [row['id'] for row in product_model.ai_search_products(
            pair['query'], limit=LIMIT,
        )]
        for key, result in (
            ('autocomplete', ids), ('list filter', listed), ('ai', ai_ids),
        ):
            if expected in result[:LIMIT] or (
                key == 'list filter' and expected in result
            ):
                stats[key][0] += 1
                stats[key][1] += bool(result) and result[0] == expected
    total = len(pairs)
    print(f'pairs: {total}')
    for key, (found, top1) in stats.items():
        print(
            f'{key:12} found {found:3} ({100 * found / total:.0f}%)'
            f'  top1 {top1:3} ({100 * top1 / total:.0f}%)'
        )
    timings.sort(reverse=True)
    average = sum(seconds for seconds, _query in timings) / len(timings)
    print(f'autocomplete avg {1000 * average:.1f} ms, slowest:')
    for seconds, query in timings[:5]:
        print(f'  {1000 * seconds:.1f} ms  {query}')


run(env)  # noqa: F821 - provided by odoo shell
env.cr.rollback()  # noqa: F821
