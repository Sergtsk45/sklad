"""Объединённая закупка по нескольким требованиям (этап 4)."""
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestMergedPurchase(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        Partner = cls.env['res.partner']
        cls.alpha, cls.beta = (
            Partner.create({'name': name, 'supplier_rank': 1})
            for name in ('Vendor MP alpha', 'Vendor MP beta')
        )
        Product = cls.env['product.product']
        cls.p1, cls.p2, cls.p3 = (
            Product.create({'name': name, 'type': 'consu'})
            for name in ('Шина MP N', 'Автомат MP 6А', 'DIN-рейка MP')
        )
        cls.req_a = cls._request('Объект MP A', '2026-11-10', [
            (cls.p1, 2.0, cls.alpha), (cls.p2, 1.0, cls.beta),
        ])
        cls.req_b = cls._request('Объект MP B', '2026-11-05', [
            (cls.p1, 3.0, cls.alpha), (cls.p3, 1.0, cls.alpha),
        ])
        cls.picking_type = cls.env['stock.picking.type'].search(
            [('code', '=', 'incoming')], limit=1,
        )

    @classmethod
    def _request(cls, project_name, need_date, rows):
        project = cls.env['object.request.project'].create(
            {'name': project_name}
        )
        request = cls.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': cls.env.ref('base.user_admin').id,
            'need_date': need_date,
        })
        for product, qty, vendor in rows:
            cls.env['object.request.line'].create({
                'request_id': request.id,
                'name_raw': product.name,
                'product_id': product.id,
                'uom_id': product.uom_id.id,
                'qty_requested': qty,
                'qty_to_buy': qty,
                'preferred_vendor_id': vendor.id,
            })
        return request

    def _wizard(self, requests, **vals):
        action = requests.action_open_purchase_wizard()
        Wizard = self.env['object.request.purchase.wizard'].with_context(
            **action['context']
        )
        return Wizard.create(dict(
            picking_type_id=self.picking_type.id, **vals,
        ))

    def _orders(self, requests, **vals):
        action = self._wizard(requests, **vals).action_create_purchase()
        if action.get('res_id'):
            return self.env['purchase.order'].browse(action['res_id'])
        return self.env['purchase.order'].search(action['domain'])

    def test_wizard_collects_lines_of_all_requests(self):
        wizard = self._wizard(self.req_a | self.req_b)
        self.assertEqual(wizard.request_ids, self.req_a | self.req_b)
        self.assertEqual(len(wizard.line_ids), 4)

    def test_one_order_per_vendor_across_requests(self):
        orders = self._orders(self.req_a | self.req_b)
        alpha = orders.filtered(lambda o: o.partner_id == self.alpha)
        self.assertEqual(len(orders), 2)
        self.assertEqual(len(alpha.order_line), 3)

    def test_each_request_line_keeps_own_order_line(self):
        orders = self._orders(self.req_a | self.req_b)
        lines = (self.req_a | self.req_b).line_ids
        self.assertEqual(len(lines.purchase_order_line_id), 4)
        self.assertTrue(
            all(line.purchase_order_id in orders for line in lines)
        )

    def test_origin_and_line_names_reference_requests(self):
        orders = self._orders(self.req_a | self.req_b)
        alpha = orders.filtered(lambda o: o.partner_id == self.alpha)
        self.assertIn(self.req_a.name, alpha.origin)
        self.assertIn(self.req_b.name, alpha.origin)
        self.assertTrue(any(
            self.req_b.name in line.name for line in alpha.order_line
        ))
        self.assertFalse(alpha.object_request_project_id)

    def test_both_requests_see_shared_order(self):
        orders = self._orders(self.req_a | self.req_b)
        alpha = orders.filtered(lambda o: o.partner_id == self.alpha)
        self.assertIn(alpha, self.req_a.purchase_order_ids)
        self.assertIn(alpha, self.req_b.purchase_order_ids)

    def test_append_to_existing_vendor_draft(self):
        first = self._orders(self.req_a)
        alpha_draft = first.filtered(lambda o: o.partner_id == self.alpha)
        second = self._orders(self.req_b, append_to_drafts=True)
        self.assertEqual(second, alpha_draft)
        self.assertEqual(len(alpha_draft.order_line), 3)
        self.assertIn(self.req_b.name, alpha_draft.origin)

    def test_single_request_flow_unchanged(self):
        orders = self._orders(self.req_a)
        self.assertEqual(len(orders), 2)
        self.assertEqual(orders.mapped('origin'), [self.req_a.name] * 2)

    def test_object_receipt_mode_splits_by_object_warehouse(self):
        orders = self._orders(self.req_a | self.req_b, receipt_mode='object')
        alpha = orders.filtered(lambda o: o.partner_id == self.alpha)
        self.assertEqual(len(alpha), 2)
        self.assertEqual(
            set(alpha.picking_type_id.warehouse_id.ids),
            set((self.req_a | self.req_b).project_id.warehouse_id.ids),
        )

    def test_common_receipt_warns_about_other_objects(self):
        wizard = self._wizard(self.req_a | self.req_b)
        wizard.picking_type_id = (
            self.req_a.project_id.warehouse_id.in_type_id
        )
        self.assertIn(self.req_b.name, wizard.receipt_warning)
        self.assertNotIn(self.req_a.name, wizard.receipt_warning)

    def test_receipt_supplies_each_request_line(self):
        orders = self._orders(self.req_a | self.req_b, receipt_mode='object')
        for order in orders:
            order.button_confirm()
            for picking in order.picking_ids:
                for move in picking.move_ids:
                    move.quantity = move.product_uom_qty
                picking.button_validate()
        for line in (self.req_a | self.req_b).line_ids:
            with self.subTest(line=line.name_raw, request=line.request_id):
                self.assertEqual(
                    line.qty_received_purchase, line.qty_requested
                )
