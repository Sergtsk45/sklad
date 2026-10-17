"""Копия требования не наследует закупки, выдачи и обеспеченность оригинала."""
from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestRequestCopyResetsSupply(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env['res.partner'].create(
            {'name': 'Vendor COPY', 'supplier_rank': 1}
        )
        cls.product = cls.env['product.product'].create({
            'name': 'Задвижка COPY Ду80',
            'type': 'consu',
            'is_storable': True,
        })
        project = cls.env['object.request.project'].create(
            {'name': 'Объект COPY'}
        )
        cls.request = cls.env['object.request'].create({
            'project_id': project.id,
            'foreman_user_id': cls.env.uid,
            'need_date': fields.Date.today(),
            'approval_state': 'approved',
        })
        cls.po = cls.env['purchase.order'].create({
            'partner_id': cls.vendor.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_qty': 3.0,
                'price_unit': 100.0,
            })],
        })
        cls.line = cls.env['object.request.line'].create({
            'request_id': cls.request.id,
            'name_raw': 'Задвижка чугунная Ду80',
            'qty_requested': 3.0,
            'product_id': cls.product.id,
            'preferred_vendor_id': cls.vendor.id,
        })
        cls.line.write({
            'purchase_order_id': cls.po.id,
            'purchase_order_line_id': cls.po.order_line.id,
            'procurement_mode': 'buy',
            'qty_to_buy': 3.0,
            'qty_issued': 3.0,
            'qty_received_purchase': 3.0,
            'qty_reserved': 1.0,
            'issue_reserved': True,
            'manual_plan_override': True,
        })
        cls.request.purchase_order_ids = cls.po

    def test_original_is_fully_supplied(self):
        self.assertEqual(self.line.line_state, 'fully_supplied')

    def test_copy_drops_purchase_links_and_supply(self):
        line = self.request.copy().line_ids
        self.assertFalse(line.purchase_order_id)
        self.assertFalse(line.purchase_order_line_id)
        self.assertFalse(line.issue_picking_id)
        self.assertEqual(
            (line.qty_issued, line.qty_reserved, line.qty_received_purchase),
            (0.0, 0.0, 0.0),
        )
        self.assertFalse(line.issue_reserved)

    def test_copy_line_is_ready_not_supplied(self):
        line = self.request.copy().line_ids
        self.assertEqual(line.line_state, 'ready')
        self.assertEqual(line.qty_supplied, 0.0)

    def test_copy_resets_plan(self):
        line = self.request.copy().line_ids
        self.assertEqual(line.procurement_mode, 'manual')
        self.assertEqual((line.qty_to_buy, line.qty_to_issue), (0.0, 0.0))
        self.assertFalse(line.manual_plan_override)

    def test_copy_keeps_product_vendor_and_qty(self):
        line = self.request.copy().line_ids
        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.preferred_vendor_id, self.vendor)
        self.assertEqual(line.qty_requested, 3.0)
        self.assertEqual(line.name_raw, 'Задвижка чугунная Ду80')

    def test_copy_request_has_no_purchases_and_needs_approval(self):
        copy = self.request.copy()
        self.assertFalse(copy.purchase_order_ids)
        self.assertFalse(copy.issue_picking_ids)
        self.assertEqual(copy.approval_state, 'not_required')
        self.assertEqual(copy.state, 'draft')
