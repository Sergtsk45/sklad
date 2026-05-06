"""Regression tests for normalized product search."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.product_search_utils import normalize_product_search_text


@tagged('post_install', '-at_install')
class TestCustomProductSearch(TransactionCase):

    def setUp(self):
        super().setUp()
        self.product = self.env['product.product'].create({
            'name': 'кран  шаровый\u00A0 Ду50',
            'default_code': 'KS-DU50',
            'barcode': '4600000000500',
            'type': 'consu',
        })

    def test_normalize_product_search_text(self):
        self.assertEqual(
            normalize_product_search_text('  Кран\u00A0 шаровый  ДУ 50  '),
            'кран шаровый ду50',
        )
        self.assertEqual(
            normalize_product_search_text('DN 50 Ёлка'),
            'dn50 елка',
        )

    def test_computed_search_fields(self):
        self.assertEqual(self.product.x_search_name, 'кран шаровый ду50')
        self.assertEqual(
            self.product.product_tmpl_id.x_search_name,
            'кран шаровый ду50',
        )

    def test_product_name_search_normalized_queries(self):
        queries = [
            'кран шаровый Ду50',
            'кран ду50',
            'шаровый ду 50',
            'ДУ50',
        ]
        for query in queries:
            with self.subTest(query=query):
                product_model = self.env['product.product']
                result_ids = [
                    product_id
                    for product_id, _display_name
                    in product_model.name_search(query, limit=20)
                ]
                self.assertIn(self.product.id, result_ids)

    def test_product_name_search_by_reference_and_barcode(self):
        product_model = self.env['product.product']
        self.assertIn(
            self.product.id,
            [
                product_id
                for product_id, _display_name
                in product_model.name_search('KS-DU50', limit=20)
            ],
        )
        self.assertIn(
            self.product.id,
            [
                product_id
                for product_id, _display_name
                in product_model.name_search('4600000000500', limit=20)
            ],
        )

    def test_ai_search_products(self):
        results = self.env['product.product'].ai_search_products('кран ду50')
        self.assertIn(self.product.id, [item['id'] for item in results])
