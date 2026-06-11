# @file: test_invoice_context_helper.py
# @description: Тесты InvoiceContextHelper (AIA-057).
# @dependencies: invoice_context_helper, invoice_extraction_store
# @created: 2026-05-30

from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.invoice_context_helper import (
    InvoiceContextHelper,
)
from odoo.addons.ai_assistant.services.invoice_extraction_store import (
    InvoiceExtractionStore,
)


_MOCK_INVOICE = {
    'document_type': 'supplier_invoice',
    'invoice_number': 'НФ-504',
    'invoice_date': '2026-05-20',
    'supplier': {
        'name': 'ИП Татаринов Вадим Владимирович',
        'inn': '280110406377',
    },
    'items': [
        {
            'line_no': 1,
            'name': 'Труба ВГП 50 invoice helper',
            'unit': 'м',
            'qty': 10.0,
            'price': 100.0,
            'amount_w_vat': 1200.0,
            'article': '',
        },
        {
            'line_no': 2,
            'name': 'Уникальный товар без совпадения XYZ-999',
            'unit': 'шт',
            'qty': 1.0,
            'price': 50.0,
            'amount_w_vat': 60.0,
            'article': '',
        },
    ],
    'totals': {
        'total_wo_vat': 60191.67,
        'vat_total': 12437.14,
        'total_w_vat': 72096.22,
    },
}


@tagged('post_install', '-at_install')
class TestInvoiceContextHelper(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.supplier = cls.env['res.partner'].create({
            'name': 'ИП Татаринов Вадим Владимирович',
            'vat': '280110406377',
            'supplier_rank': 1,
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Труба ВГП 50 invoice helper',
            'is_storable': True,
            'purchase_ok': True,
        })

    def setUp(self):
        super().setUp()
        self.store = InvoiceExtractionStore()
        self.helper = InvoiceContextHelper(self.env, self.store)

    def test_fetch_context_matches_partner_and_product(self):
        token = self.store.put(self.env.uid, _MOCK_INVOICE)
        context = self.helper.fetch_context(self.env.uid, token)

        self.assertEqual(context['invoice_number'], 'НФ-504')
        self.assertEqual(context['partner']['status'], 'matched')
        self.assertEqual(context['partner']['partner_id'], self.supplier.id)
        self.assertEqual(len(context['items']), 2)

        matched = context['items'][0]['product']
        self.assertEqual(matched['status'], 'matched')
        self.assertEqual(matched['product_id'], self.product.id)
        self.assertFalse(matched['needs_create_product_draft'])

        missing = context['items'][1]['product']
        self.assertEqual(missing['status'], 'not_found')
        self.assertTrue(missing['needs_create_product_draft'])

    def test_fetch_context_marks_partner_draft_needed(self):
        invoice = dict(_MOCK_INVOICE)
        invoice['supplier'] = {
            'name': 'ООО Новый Контекст Поставщик',
            'inn': '7727123401',
            'kpp': '772701001',
            'address': '109012, г. Москва, ул. Контекстная, д. 1',
        }
        token = self.store.put(self.env.uid, invoice)

        context = self.helper.fetch_context(self.env.uid, token)

        partner = context['partner']
        self.assertEqual(partner['status'], 'not_found')
        self.assertTrue(partner['needs_create_partner_draft'])
        args = partner['partner_draft_args']
        self.assertEqual(args['name'], invoice['supplier']['name'])
        self.assertEqual(args['vat'], invoice['supplier']['inn'])
        self.assertTrue(args['is_company'])
        self.assertEqual(args['street'], invoice['supplier']['address'])
        self.assertEqual(args['comment'], 'КПП: 772701001')

    def test_fetch_context_marks_partner_inn_required(self):
        invoice = dict(_MOCK_INVOICE)
        invoice['supplier'] = {
            'name': 'ООО Без ИНН Context',
            'inn': '',
        }
        token = self.store.put(self.env.uid, invoice)

        context = self.helper.fetch_context(self.env.uid, token)

        partner = context['partner']
        self.assertEqual(partner['status'], 'not_found')
        self.assertFalse(partner['needs_create_partner_draft'])
        self.assertEqual(partner['partner_error'], 'inn_required')

    def test_build_context_message_contains_ids(self):
        token = self.store.put(self.env.uid, _MOCK_INVOICE)
        context = self.helper.fetch_context(self.env.uid, token)
        message = self.helper.build_context_message(context)

        self.assertIn('INVOICE_CONTEXT', message)
        self.assertIn('"partner_id": %d' % self.supplier.id, message)
        self.assertIn('"product_id": %d' % self.product.id, message)
        self.assertIn('needs_create_product_draft', message)
        self.assertIn('create_partner_draft', message)
        self.assertIn('find_warehouse', message)

    def test_fetch_context_returns_none_for_unknown_token(self):
        self.assertIsNone(
            self.helper.fetch_context(self.env.uid, 'unknown-token'),
        )

    def test_fetch_context_returns_none_without_token(self):
        self.assertIsNone(self.helper.fetch_context(self.env.uid, None))
