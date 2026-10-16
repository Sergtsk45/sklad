"""Regression tests for product search v2 through the ORM."""

from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from ..models.product_search_mixin import TOKENIZER_VERSION_PARAM
from ..models.product_search_utils import normalize_product_search_text


@tagged('post_install', '-at_install')
class TestCustomProductSearch(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env['product.product']
        cls.product = Product.create({
            'name': 'кран  шаровый  Ду50',
            'default_code': 'KS-DU50',
            'barcode': '4600000000500',
            'type': 'consu',
        })
        cls.bolt_70 = Product.create({
            'name': 'Болт М16×70 ГОСТ 7798-70 тестовый',
            'type': 'consu',
        })
        cls.bolt_75 = Product.create({
            'name': 'Болт М16×75 ГОСТ 7798-70 тестовый',
            'type': 'consu',
        })
        cls.washer = Product.create({
            'name': 'Шайба тестовая 160',
            'type': 'consu',
        })

    def _name_search_ids(
        self, query, model='product.product', limit=8, **kwargs,
    ):
        return [
            record_id
            for record_id, _display_name
            in self.env[model].name_search(query, limit=limit, **kwargs)
        ]

    def test_normalize_product_search_text(self):
        self.assertEqual(
            normalize_product_search_text('  Кран  шаровый  ДУ 50  '),
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
        self.assertEqual(
            normalize_product_search_text('Тройник 159*4.5'),
            'тройник 159x4.5',
        )

    def test_computed_search_fields(self):
        self.assertEqual(self.product.x_search_name, 'кран шаровый ду50')
        self.assertEqual(
            self.product.product_tmpl_id.x_search_name,
            'кран шаровый ду50',
        )
        self.assertIn('кран', self.product.x_search_tokens.split())
        self.assertIn('ks', self.product.x_search_tokens.split())
        self.assertIn(
            'кран', self.product.product_tmpl_id.x_search_tokens.split(),
        )

    def test_tokens_follow_rename(self):
        self.washer.name = 'Шайба переименованная 160'
        self.assertIn('переи', self.washer.x_search_tokens.split())
        self.assertIn(
            self.washer.id, self._name_search_ids('шайба переименованная'),
        )

    def test_product_name_search_normalized_queries(self):
        # No limit: a real catalog may hold many «Ду50» products.
        for query in ('кран шаровый Ду50', 'кран ду50', 'шаровый ду 50',
                      'ДУ50', 'кран шар. DN50'):
            with self.subTest(query=query):
                self.assertIn(
                    self.product.id, self._name_search_ids(query, limit=None),
                )
                self.assertIn(
                    self.product.product_tmpl_id.id,
                    self._name_search_ids(
                        query, 'product.template', limit=None,
                    ),
                )

    def test_name_search_ranks_full_match_first(self):
        result = self._name_search_ids('болт 16х70 тестовый')
        self.assertEqual(result[0], self.bolt_70.id)
        self.assertIn(self.bolt_75.id, result)

    def test_name_search_number_is_whole_token(self):
        self.assertNotIn(self.washer.id, self._name_search_ids('болт 16'))

    def test_name_search_ignores_unknown_words(self):
        self.assertEqual(
            self._name_search_ids('болт тестовый М16х70 (кор) zzqq')[0],
            self.bolt_70.id,
        )

    def test_name_search_respects_domain(self):
        result = self._name_search_ids(
            'болт 16х70 тестовый',
            domain=[('id', '!=', self.bolt_70.id)],
        )
        self.assertNotIn(self.bolt_70.id, result)
        self.assertIn(self.bolt_75.id, result)

    def test_name_search_negative_operator_uses_standard_search(self):
        result = self.env['product.product'].name_search(
            'тестовый', operator='not ilike', limit=None,
        )
        result_ids = [record_id for record_id, _name in result]
        self.assertNotIn(self.bolt_70.id, result_ids)
        self.assertIn(self.product.id, result_ids)

    def test_product_name_search_by_reference_and_barcode(self):
        self.assertEqual(self._name_search_ids('KS-DU50')[0], self.product.id)
        self.assertEqual(
            self._name_search_ids('4600000000500')[0], self.product.id,
        )

    def test_list_filter_is_strict(self):
        Product = self.env['product.product']
        found = Product.search([('x_smart_search', 'ilike', 'болт м16 гост')])
        self.assertIn(self.bolt_70, found)
        self.assertIn(self.bolt_75, found)
        self.assertNotIn(self.washer, found)
        self.assertNotIn(self.product, found)

    def test_template_list_filter(self):
        found = self.env['product.template'].search(
            [('x_smart_search', 'ilike', 'болт 16х75 тестовый')],
        )
        self.assertIn(self.bolt_75.product_tmpl_id, found)
        self.assertNotIn(self.bolt_70.product_tmpl_id, found)

    def test_search_view_product_field_uses_smart_search(self):
        for model in ('product.template', 'product.product'):
            with self.subTest(model=model):
                arch = self.env[model].get_view(view_type='search')['arch']
                self.assertIn('x_smart_search', arch)

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

    def test_ai_search_products_only_available(self):
        results = self.env['product.product'].ai_search_products(
            'болт 16х70 тестовый', only_available=True,
        )
        self.assertNotIn(self.bolt_70.id, [item['id'] for item in results])

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


@tagged('post_install', '-at_install')
class TestProductSearchSynonyms(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Synonym = cls.env['product.search.synonym']
        cls.product = cls.env['product.product'].create({
            'name': 'Хомут червячный тестовый',
            'type': 'consu',
        })

    def test_default_synonyms_are_seeded(self):
        self.assertTrue(self.Synonym.search([('term', '=', 'оцинк')]))

    def test_new_synonym_reindexes_products(self):
        self.Synonym.create({'term': 'Струбцина', 'canonical': 'хомут'})
        record = self.Synonym.search([('term', '=', 'струбцина')])
        self.assertEqual(record.canonical, 'хомут')
        result = [
            record_id for record_id, _name
            in self.env['product.product'].name_search(
                'струбцина червячная', limit=8,
            )
        ]
        self.assertEqual(result[0], self.product.id)

    def test_synonym_applies_to_product_names(self):
        self.Synonym.create({'term': 'червячный', 'canonical': 'винтовой'})
        self.assertIn('винто', self.product.x_search_tokens.split())

    def test_synonym_must_be_single_word(self):
        with self.assertRaises(ValidationError):
            self.Synonym.create({'term': 'два слова', 'canonical': 'слово'})

    def test_refresh_after_tokenizer_version_change(self):
        params = self.env['ir.config_parameter'].sudo()
        param = f'{TOKENIZER_VERSION_PARAM}.product_product'
        params.set_param(param, '0')
        self.env.cr.execute(
            "UPDATE product_product SET x_search_tokens = NULL WHERE id = %s",
            [self.product.id],
        )
        self.product.invalidate_recordset(['x_search_tokens'])
        self.env['product.product']._refresh_search_tokens_if_outdated()
        self.assertTrue(self.product.x_search_tokens)
        self.assertNotEqual(params.get_param(param), '0')
