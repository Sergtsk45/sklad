"""Regression tests for normalized product search."""

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.product_search_utils import (
    normalize_product_search_text,
    russian_morphology_search_tokens,
)


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
        self.assertEqual(
            normalize_product_search_text('Клапан РУ-16 Ду 80'),
            'клапан ру16 ду80',
        )
        self.assertEqual(
            normalize_product_search_text('Бобышка М20х1,5 L=40'),
            'бобышка м20x1.5 l=40',
        )

    def test_conservative_russian_morphology_tokens(self):
        self.assertEqual(
            russian_morphology_search_tokens('пену противопожарную'),
            ['пен', 'противопожарн'],
        )
        self.assertEqual(
            russian_morphology_search_tokens('кран Ду50'),
            ['кран', 'ду50'],
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
                template_model = self.env['product.template']
                template_ids = [
                    template_id
                    for template_id, _display_name
                    in template_model.name_search(query, limit=20)
                ]
                self.assertIn(self.product.product_tmpl_id.id, template_ids)

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
        self.assertTrue(all(item['match_type'] == 'exact' for item in results))

    def test_ai_search_products_morphology_fallback_is_marked(self):
        foam = self.env['product.product'].create({
            'name': 'Пена монтажная противопожарная',
            'type': 'consu',
        })
        results = self.env['product.product'].ai_search_products(
            'пену противопожарную'
        )
        match = next(item for item in results if item['id'] == foam.id)
        self.assertEqual(match['match_type'], 'morphology')

        exact_results = self.env['product.product'].ai_search_products(
            'пена противопожарная'
        )
        exact_match = next(
            item for item in exact_results if item['id'] == foam.id
        )
        self.assertEqual(exact_match['match_type'], 'exact')

    def test_ai_search_products_by_supplier_article(self):
        vendor = self.env['res.partner'].create({
            'name': 'Vendor Article Search',
            'supplier_rank': 1,
        })
        product = self.env['product.product'].create({
            'name': 'Каноническое имя не из прайса',
            'default_code': 'INT-ART-1',
            'type': 'consu',
        })
        self.env['product.supplierinfo'].create({
            'partner_id': vendor.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'product_code': '00-00036296',
            'min_qty': 1,
            'price': 100.0,
        })

        results = self.env['product.product'].ai_search_products(
            '00-00036296',
        )
        self.assertIn(product.id, [item['id'] for item in results])

    def test_product_search_technical_designations(self):
        bushing = self.env['product.product'].create({
            'name': 'Бобышка М20×1,5 L=40',
            'type': 'consu',
        })
        valve = self.env['product.product'].create({
            'name': 'Клапан фланцевый ДУ-80 РУ 16',
            'type': 'consu',
        })

        bushing_results = self.env['product.product'].ai_search_products(
            'М20х1,5',
        )
        valve_results = self.env['product.product'].ai_search_products(
            'Ду 80 Ру-16',
        )

        self.assertIn(bushing.id, [item['id'] for item in bushing_results])
        self.assertIn(valve.id, [item['id'] for item in valve_results])
