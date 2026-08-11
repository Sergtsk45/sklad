import time
from unittest.mock import MagicMock

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.purchase_order_actions import (
    PurchaseOrderActionsService,
)
from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    GetProductSupplierInfoTool,
)
from odoo.addons.ai_assistant.services.replenishment_intent import (
    keyword_replenishment_fallback,
)
from odoo.addons.ai_assistant.services.replenishment_session_store import (
    ReplenishmentSessionStore,
)
from odoo.addons.ai_assistant.services.replenishment_workflow import (
    ReplenishmentWorkflow,
)


@tagged('post_install', '-at_install')
class TestReplenishmentServices(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.vendor = cls.env['res.partner'].create({
            'name': 'Replenishment Test Vendor',
            'supplier_rank': 1,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Replenishment Test Product',
            'is_storable': True,
        })
        common = {
            'partner_id': cls.vendor.id,
            'product_tmpl_id': cls.product.product_tmpl_id.id,
            'product_uom_id': cls.product.uom_id.id,
            'currency_id': cls.env.company.currency_id.id,
        }
        cls.env['product.supplierinfo'].create({
            **common, 'min_qty': 0, 'price': 100, 'discount': 0,
        })
        cls.selected_seller = cls.env['product.supplierinfo'].create({
            **common, 'min_qty': 10, 'price': 80, 'discount': 10,
        })

    def test_keyword_fallback_is_conservative(self):
        result = keyword_replenishment_fallback(
            'сделай пополнение отвода Ду50 100 шт от Башняк'
        )
        self.assertTrue(result['intent'])
        self.assertEqual(result['product_query'], 'отвода Ду50')
        self.assertIsNone(result['quantity'])
        self.assertIsNone(keyword_replenishment_fallback('что ты умеешь'))

    def test_session_store_is_uid_scoped_and_expires(self):
        store = ReplenishmentSessionStore(ttl_seconds=0.01)
        token = store.put(10, {'product_query': 'Отвод'})
        self.assertIsNotNone(store.get_session(10, token))
        self.assertIsNone(store.get_session(11, token))
        time.sleep(0.02)
        self.assertIsNone(store.get_session(10, token))

    def test_workflow_click_ids_are_allowlisted(self):
        workflow = ReplenishmentWorkflow(self.env, MagicMock())
        session = {'last_options': [{'id': 12}]}
        self.assertTrue(workflow._payload_is_allowlisted(
            session, workflow.ACTION_SELECT_PRODUCT, {'product_id': 12}
        ))
        self.assertFalse(workflow._payload_is_allowlisted(
            session, workflow.ACTION_SELECT_PRODUCT, {'product_id': 13}
        ))

    def test_result_card_keeps_token_and_backend_actions(self):
        po = MagicMock()
        po.id = 42
        po.name = 'P00042'
        po.state = 'purchase'
        card = PurchaseOrderActionsService(self.env).card(po, 'token-42')
        self.assertEqual(card['record']['id'], 42)
        self.assertEqual(card['replenishmentToken'], 'token-42')
        disabled = {item['action']: item['disabled']
                    for item in card['actions']}
        self.assertTrue(disabled['send_rfq'])
        self.assertTrue(disabled['confirm'])
        self.assertFalse(disabled['print'])
        self.assertFalse(disabled['cancel'])

    def test_supplier_offer_uses_standard_tier_and_discount(self):
        result = GetProductSupplierInfoTool().execute(self.env, {
            'product_id': self.product.id,
            'quantity': 12,
            'uom_id': self.product.uom_id.id,
        })
        self.assertEqual(len(result['offers']), 1)
        offer = result['offers'][0]
        self.assertEqual(offer['supplierinfo_id'], self.selected_seller.id)
        self.assertEqual(offer['purchase_qty'], 12)
        self.assertEqual(offer['discount'], 10)
        self.assertEqual(offer['normalized_price_discounted'], 72)

    def _prepared_workflow(self):
        offer = GetProductSupplierInfoTool().execute(self.env, {
            'product_id': self.product.id,
            'quantity': 12,
            'uom_id': self.product.uom_id.id,
        })['offers'][0]
        warehouse = self.env['stock.warehouse'].search([], limit=1)
        self.assertTrue(warehouse and warehouse.in_type_id)
        store = ReplenishmentSessionStore()
        token = store.put(self.env.uid, {})
        store.get_session(self.env.uid, token).update({
            'state': ReplenishmentWorkflow.AWAITING_PLAN,
            'product_id': self.product.id,
            'qty': 12,
            'requested_uom_id': self.product.uom_id.id,
            'vendor': offer,
            'warehouse': {
                'id': warehouse.id,
                'name': warehouse.display_name,
                'picking_type_id': warehouse.in_type_id.id,
            },
        })
        return ReplenishmentWorkflow(self.env, store), store, token

    def test_execute_creates_one_po_and_ignores_forged_po_id(self):
        workflow, store, token = self._prepared_workflow()
        first = workflow.execute_plan(self.env.uid, token)
        second = workflow.execute_plan(self.env.uid, token)
        po_id = first['cards'][0]['record']['id']
        self.assertEqual(second['cards'][0]['record']['id'], po_id)
        po = self.env['purchase.order'].browse(po_id)
        self.assertEqual(po.partner_id, self.vendor)
        self.assertEqual(len(po.order_line), 1)
        self.assertEqual(po.order_line.product_qty, 12)
        self.assertEqual(po.order_line.price_unit, 80)
        self.assertEqual(po.order_line.discount, 10)
        self.assertEqual(
            po.order_line.selected_seller_id, self.selected_seller
        )

        forged = self.env['purchase.order'].create({
            'partner_id': self.vendor.id,
        })
        result = PurchaseOrderActionsService(self.env).dispatch_for_session(
            store, self.env.uid, token, 'cancel', advisory_po_id=forged.id
        )
        self.assertTrue(result['ok'])
        self.assertEqual(po.state, 'cancel')
        self.assertEqual(forged.state, 'draft')

    def test_execute_requires_reconfirmation_after_price_change(self):
        workflow, _store, token = self._prepared_workflow()
        before = self.env['purchase.order'].search_count([
            ('origin', '=', 'Пополнение (AI): %s' % self.product.display_name),
        ])
        self.selected_seller.price = 81
        result = workflow.execute_plan(self.env.uid, token)
        after = self.env['purchase.order'].search_count([
            ('origin', '=', 'Пополнение (AI): %s' % self.product.display_name),
        ])
        self.assertEqual(before, after)
        self.assertIn('условия поставщика изменились', result['answer'].lower())
        self.assertEqual(
            result['meta']['replenishment_state'],
            ReplenishmentWorkflow.AWAITING_PLAN,
        )
