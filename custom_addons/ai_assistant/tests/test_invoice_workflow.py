# @file: test_invoice_workflow.py
# @description: Пошаговый workflow счёта — товары и PO.
# @created: 2026-05-31

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.invoice_extraction_store import (
    InvoiceExtractionStore,
)
from odoo.addons.ai_assistant.services.invoice_workflow import (
    InvoiceWorkflow,
)


@tagged('post_install', '-at_install')
class TestInvoiceWorkflow(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.store = InvoiceExtractionStore()
        cls.workflow = InvoiceWorkflow(cls.env, cls.store)
        cls.supplier = cls.env['res.partner'].create({
            'name': 'АО Энерготехномаш',
            'vat': '0323085570',
            'supplier_rank': 1,
        })
        cls.env['stock.warehouse'].create({
            'name': 'Основной склад контейнер',
            'code': 'Ос.ск',
        })
        cls.invoice_data = {
            'invoice_number': '3315',
            'invoice_date': '2026-05-25',
            'supplier': {'name': 'АО Энерготехномаш', 'inn': '0323085570'},
            'items': [
                {
                    'line_no': 1,
                    'name': 'ЗРК 25ч945п-25-4,0',
                    'unit': 'шт',
                    'qty': 2,
                    'price': 1500.0,
                    'article': 'ZRK-1',
                },
                {
                    'line_no': 2,
                    'name': 'ЗРК 25ч945п-25-6,3',
                    'unit': 'шт',
                    'qty': 1,
                    'price': 1800.0,
                    'article': 'ZRK-2',
                },
            ],
            'totals': {'total_w_vat': 4800.0},
        }

    def _put_token(self):
        return self.store.put(self.env.uid, self.invoice_data)

    def test_build_product_draft_args_includes_price(self):
        line = self.invoice_data['items'][0]
        args = self.workflow.build_product_draft_args(line)
        self.assertEqual(args['name'], line['name'])
        self.assertEqual(args['list_price'], 1500.0)
        self.assertEqual(args['default_code'], 'ZRK-1')
        self.assertTrue(args['purchase_ok'])

    def test_next_product_and_suggestions(self):
        token = self._put_token()
        draft = self.workflow.next_product_draft(self.env.uid, token)
        self.assertEqual(draft['line_key'], '1')
        self.assertEqual(draft['args']['list_price'], 1500.0)

        self.workflow.record_product_created(
            self.env.uid, token, '1', 999,
        )
        suggestions = self.workflow.suggestions_after_product_created(
            self.env.uid, token,
        )
        self.assertEqual(len(suggestions), 1)
        self.assertEqual(
            suggestions[0]['action'],
            InvoiceWorkflow.ACTION_NEXT_PRODUCT,
        )

    def test_all_products_ready_suggests_po(self):
        token = self._put_token()
        self.workflow.record_product_created(self.env.uid, token, '1', 101)
        self.workflow.record_product_created(self.env.uid, token, '2', 102)
        suggestions = self.workflow.suggestions_after_product_created(
            self.env.uid, token,
        )
        self.assertEqual(
            suggestions[0]['action'],
            InvoiceWorkflow.ACTION_PREPARE_PO,
        )

    def test_prepare_po_draft_builds_lines(self):
        token = self._put_token()
        self.workflow.record_product_created(self.env.uid, token, '1', 101)
        self.workflow.record_product_created(self.env.uid, token, '2', 102)
        payload = self.workflow.prepare_po_draft(
            self.env.uid, token, 'Ос.ск',
        )
        self.assertEqual(payload['status'], 'pending')
        po_args = payload['po_args']
        self.assertEqual(po_args['partner_id'], self.supplier.id)
        self.assertEqual(po_args['partner_ref'], '3315')
        self.assertEqual(len(po_args['lines']), 2)
        self.assertEqual(po_args['lines'][0]['product_qty'], 2.0)
        self.assertEqual(po_args['lines'][0]['price_unit'], 1500.0)
