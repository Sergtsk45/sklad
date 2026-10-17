"""Автоматический план «выдать / закупить» при переводе в работу (этап 5)."""
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRequestAutoPlan(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Product = cls.env['product.product']
        cls.in_stock, cls.no_stock, cls.manual = (
            Product.create({
                'name': name, 'type': 'consu', 'is_storable': True,
            })
            for name in ('Фланец AP Ду80', 'Задвижка AP Ду80',
                         'Отвод AP Ду80')
        )
        cls.project = cls.env['object.request.project'].create(
            {'name': 'Объект AP'}
        )
        location = cls.project.warehouse_id.lot_stock_id
        cls.env['stock.quant']._update_available_quantity(
            cls.in_stock, location, 5.0,
        )
        cls.env['stock.quant']._update_available_quantity(
            cls.manual, location, 5.0,
        )

    def _request(self, user=None):
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': (user or self.env.user).id,
            'need_date': fields.Date.today(),
            'line_ids': [
                (0, 0, {'name_raw': p.name, 'product_id': p.id,
                        'qty_requested': qty})
                for p, qty in ((self.in_stock, 8.0), (self.no_stock, 2.0),
                               (self.manual, 1.0))
            ],
        })
        manual_line = request.line_ids.filtered(
            lambda line: line.product_id == self.manual
        )
        manual_line.write({'qty_to_buy': 1.0, 'manual_plan_override': True})
        return request

    def _line(self, request, product):
        return request.line_ids.filtered(
            lambda line: line.product_id == product
        )

    def test_stock_split_into_issue_and_buy(self):
        request = self._request()
        request.action_in_progress()
        line = self._line(request, self.in_stock)
        self.assertEqual((line.qty_to_issue, line.qty_to_buy), (5.0, 3.0))
        self.assertEqual(line.procurement_mode, 'mixed')

    def test_missing_stock_goes_to_buy(self):
        request = self._request()
        request.action_in_progress()
        line = self._line(request, self.no_stock)
        self.assertEqual((line.qty_to_issue, line.qty_to_buy), (0.0, 2.0))
        self.assertEqual(line.procurement_mode, 'buy')

    def test_manual_plan_is_kept(self):
        request = self._request()
        request.action_in_progress()
        line = self._line(request, self.manual)
        self.assertEqual((line.qty_to_issue, line.qty_to_buy), (0.0, 1.0))

    def test_foreman_without_stock_rights_starts_request(self):
        foreman = self.env['res.users'].create({
            'name': 'Foreman AP',
            'login': 'foreman_ap',
            'group_ids': [
                (4, self.env.ref('base.group_user').id),
                (4, self.env.ref('object_request.group_foreman').id),
            ],
        })
        request = self._request(user=foreman)
        request.with_user(foreman).action_in_progress()
        self.assertEqual(request.state, 'in_progress')
        line = self._line(request, self.in_stock)
        self.assertEqual(line.qty_to_issue, 5.0)
