"""Поставщик по умолчанию в строке требования (этап 4)."""
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRequestDefaultVendor(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Partner = cls.env['res.partner']
        cls.first, cls.second, cls.other = (
            Partner.create({'name': name, 'supplier_rank': 1})
            for name in ('Vendor DV first', 'Vendor DV second',
                         'Vendor DV other')
        )
        cls.parent_categ = cls.env['product.category'].create(
            {'name': 'Электрика DV'}
        )
        categ = cls.env['product.category'].create(
            {'name': 'Шины DV', 'parent_id': cls.parent_categ.id}
        )
        cls.product = cls.env['product.product'].create({
            'name': 'Шина N DV 8×12',
            'type': 'consu',
            'categ_id': categ.id,
            'seller_ids': [
                (0, 0, {'partner_id': cls.first.id, 'sequence': 1,
                        'price': 100.0}),
                (0, 0, {'partner_id': cls.second.id, 'sequence': 2,
                        'price': 90.0}),
            ],
        })
        cls.company = cls.env.company

    def _default(self):
        return self.product._or_default_vendor(self.company)

    def test_without_settings_first_price_row(self):
        self.assertEqual(self._default(), self.first)

    def test_main_vendor_from_parent_category(self):
        self.parent_categ.or_main_vendor_id = self.second
        self.assertEqual(self._default(), self.second)

    def test_main_vendor_without_price_row_is_skipped(self):
        self.parent_categ.or_main_vendor_id = self.other
        self.assertEqual(self._default(), self.first)

    def test_last_purchase_vendor(self):
        order = self.env['purchase.order'].create({
            'partner_id': self.second.id,
            'order_line': [(0, 0, {
                'product_id': self.product.id,
                'product_qty': 1.0,
                'price_unit': 90.0,
            })],
        })
        order.button_confirm()
        self.assertEqual(self._default(), self.second)

    def _request_line(self, **vals):
        project = self.env['object.request.project'].create(
            {'name': 'Объект DV'}
        )
        request = self.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': self.env.uid,
            'need_date': fields.Date.today(),
        })
        return self.env['object.request.line'].create(dict(
            request_id=request.id, name_raw='шина нулевая DV 8×12',
            qty_requested=1.0, **vals,
        ))

    def test_accept_suggestion_sets_default_vendor(self):
        self.parent_categ.or_main_vendor_id = self.second
        line = self._request_line()
        line.ai_suggested_product_id = self.product
        line.action_accept_ai_candidate()
        self.assertEqual(line.preferred_vendor_id, self.second)

    def test_onchange_product_sets_default_vendor(self):
        self.parent_categ.or_main_vendor_id = self.second
        line = self._request_line()
        line.product_id = self.product
        line._onchange_product_id()
        self.assertEqual(line.preferred_vendor_id, self.second)
