"""Автопредложение товара при вводе строки требования (этап 3)."""
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRequestLineAutoSuggest(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env['product.product']
        cls.valve = Product.create(
            {'name': 'Задвижка СУГГЕСТ чугунная Ду80', 'type': 'consu'}
        )
        cls.bolt = Product.create(
            {'name': 'Болт СУГГЕСТ М16×70', 'type': 'consu'}
        )
        project = cls.env['object.request.project'].create(
            {'name': 'Объект СУГГЕСТ'}
        )
        cls.request = cls.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': cls.env.uid,
            'need_date': fields.Date.today(),
        })

    def _line(self, name, env=None, **vals):
        Line = (env or self.env)['object.request.line']
        return Line.create(dict(
            request_id=self.request.id, name_raw=name, qty_requested=1.0,
            **vals,
        ))

    def test_line_without_product_gets_suggestion(self):
        line = self._line('задвижка суггест чуг. Ду 80')
        self.assertEqual(line.ai_suggested_product_id, self.valve)
        self.assertFalse(line.product_id)
        self.assertEqual(line.matching_state, 'manual_review')
        self.assertTrue(line.matching_required)

    def test_typo_query_is_found_by_catalog_search(self):
        line = self._line('болд суггест м16х70')
        self.assertEqual(line.ai_suggested_product_id, self.bolt)

    def test_line_with_product_is_left_alone(self):
        line = self._line('что-то', product_id=self.bolt.id)
        self.assertFalse(line.ai_suggested_product_id)

    def test_import_context_skips_suggestion(self):
        Line = self.env['object.request.line'].with_context(
            object_request_skip_auto_suggest=True,
        )
        line = Line.create({
            'request_id': self.request.id,
            'name_raw': 'задвижка суггест Ду80',
            'qty_requested': 1.0,
        })
        self.assertFalse(line.ai_suggested_product_id)

    def test_name_change_updates_suggestion(self):
        line = self._line('задвижка суггест Ду80')
        line.name_raw = 'болт суггест М16х70'
        self.assertEqual(line.ai_suggested_product_id, self.bolt)

    def test_accept_applies_suggested_product(self):
        line = self._line('задвижка суггест Ду80')
        line.action_accept_ai_candidate()
        self.assertEqual(line.product_id, self.valve)
        self.assertFalse(line.matching_required)

    def test_foreman_without_stock_rights_gets_suggestion(self):
        foreman = self.env['res.users'].create({
            'name': 'Foreman СУГГЕСТ',
            'login': 'foreman_suggest',
            'group_ids': [
                (4, self.env.ref('base.group_user').id),
                (4, self.env.ref('object_request.group_foreman').id),
            ],
        })
        self.request.foreman_user_id = foreman
        line = self._line(
            'задвижка суггест Ду80', env=self.env(user=foreman),
        )
        self.assertEqual(line.ai_suggested_product_id, self.valve)
