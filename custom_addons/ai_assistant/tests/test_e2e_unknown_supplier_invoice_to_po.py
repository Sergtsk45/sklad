# @file: test_e2e_unknown_supplier_invoice_to_po.py
# @description: E2E: unknown supplier -> partner draft -> product -> PO.
# @created: 2026-06-12

from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.action_tools.executor import (
    ToolExecutor,
    ToolRateLimiter,
)
from odoo.addons.ai_assistant.services.invoice_context_helper import (
    InvoiceContextHelper,
)
from odoo.addons.ai_assistant.services.invoice_extraction_store import (
    InvoiceExtractionStore,
)
from odoo.addons.ai_assistant.services.invoice_workflow import (
    InvoiceWorkflow,
)


_UNKNOWN_SUPPLIER_VAT = '7727999101'

_UNKNOWN_SUPPLIER_INVOICE = {
    'document_type': 'supplier_invoice',
    'invoice_number': 'МК-CPP-012',
    'invoice_date': '2026-06-12',
    'supplier': {
        'name': 'ООО CPP Новый Поставщик',
        'inn': _UNKNOWN_SUPPLIER_VAT,
        'kpp': '772701001',
        'address': '109012, г. Москва, ул. CPP, д. 12',
        'bank': {
            'name': 'Банк не переносится',
            'bik': '044525225',
            'account': '40702810000000000001',
            'corr_account': '30101810400000000225',
        },
    },
    'buyer': {'name': 'ООО ТЕПЛОСЕРВИС-КОМПЛЕКТ'},
    'items': [{
        'line_no': 1,
        'name': 'CPP-012 Болт оцинкованный М12х60',
        'unit': 'шт',
        'qty': 25.0,
        'price': 42.5,
        'amount_wo_vat': 1062.5,
        'vat_rate': '20%',
        'vat_amount': 212.5,
        'amount_w_vat': 1275.0,
        'article': 'CPP-BOLT-12',
        'discount': '',
    }],
    'totals': {
        'total_wo_vat': 1062.5,
        'vat_total': 212.5,
        'total_w_vat': 1275.0,
    },
    'pages': 1,
    'warnings': [],
}


@tagged('post_install', '-at_install')
class TestUnknownSupplierInvoiceToPODraft(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.store = InvoiceExtractionStore()
        cls.workflow = InvoiceWorkflow(cls.env, cls.store)
        cls.helper = InvoiceContextHelper(cls.env, cls.store)
        cls.warehouse = cls._get_or_create_o002_warehouse()
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        cls.category = cls.env['product.category'].create({
            'name': 'CPP-012 E2E номенклатура',
        })
        cls.supply_user = cls._create_supply_user()
        cls.env['res.partner'].search([
            ('vat', '=', _UNKNOWN_SUPPLIER_VAT),
        ]).unlink()

    @classmethod
    def _get_or_create_o002_warehouse(cls):
        warehouse = cls.env['stock.warehouse'].search(
            [('code', '=', 'O002')], limit=1,
        )
        if warehouse:
            return warehouse
        return cls.env['stock.warehouse'].create({
            'name': 'Б. Хмельницкого, 112',
            'code': 'O002',
        })

    @classmethod
    def _create_supply_user(cls):
        groups = [
            cls.env.ref('base.group_user').id,
            cls.env.ref(
                'ai_assistant.group_ai_assistant_supply'
            ).id,
            cls.env.ref('product.group_product_manager').id,
        ]
        return cls.env['res.users'].create({
            'name': 'cpp012_supply',
            'login': 'cpp012_supply',
            'email': 'cpp012_supply@example.invalid',
            'group_ids': [(6, 0, groups)],
        })

    def _executor(self):
        return ToolExecutor(
            self.env(user=self.supply_user),
            rate_limiter=ToolRateLimiter(),
        )

    def test_unknown_supplier_invoice_to_partner_and_po_draft(self):
        uid = self.env.ref('base.user_admin').id
        token = self.store.put(uid, _UNKNOWN_SUPPLIER_INVOICE)
        context = self.helper.fetch_context(uid, token)

        partner_context = context['partner']
        self.assertEqual(partner_context['status'], 'not_found')
        self.assertTrue(partner_context['needs_create_partner_draft'])
        self.assertEqual(
            partner_context['partner_draft_args']['vat'],
            _UNKNOWN_SUPPLIER_VAT,
        )
        self.assertTrue(self.workflow.next_partner_draft(uid, token))

        executor = self._executor()
        partner_result = executor.execute(
            'create_partner_draft',
            partner_context['partner_draft_args'],
        )
        self.assertTrue(
            partner_result['success'],
            msg='create_partner_draft failed: %s' % partner_result,
        )
        partner = self.env['res.partner'].browse(
            partner_result['result']['partner_id']
        )
        self.assertTrue(partner.exists())
        self.assertEqual(partner.vat, _UNKNOWN_SUPPLIER_VAT)
        self.assertGreater(partner.supplier_rank, 0)
        self.assertEqual(partner.customer_rank, 0)
        self.assertIn('CPP', partner.street)
        self.assertIn('КПП: 772701001', partner.comment)
        self.assertFalse(partner.bank_ids)

        self.workflow.record_partner_created(uid, token, partner.id)
        self.assertTrue(self.workflow.partner_ready(uid, token))

        product_draft = self.workflow.next_product_draft(uid, token)
        self.assertTrue(product_draft)
        product_args = dict(product_draft['args'])
        product_args.update({
            'categ_id': self.category.id,
            'uom_id': self.uom_unit.id,
        })
        product_result = executor.execute(
            'create_product_draft',
            product_args,
        )
        self.assertTrue(
            product_result['success'],
            msg='create_product_draft failed: %s' % product_result,
        )
        product_id = product_result['result']['product_id']
        self.workflow.record_product_created(
            uid,
            token,
            product_draft['line_key'],
            product_id,
        )

        po_payload = self.workflow.prepare_po_draft(uid, token, 'O002')
        self.assertEqual(po_payload['status'], 'pending')
        self.assertEqual(po_payload['po_args']['partner_id'], partner.id)

        po_result = executor.execute(
            'create_purchase_order_draft',
            po_payload['po_args'],
        )
        self.assertTrue(
            po_result['success'],
            msg='create_purchase_order_draft failed: %s' % po_result,
        )
        po = self.env['purchase.order'].browse(po_result['result']['po_id'])
        self.assertEqual(po.state, 'draft')
        self.assertEqual(po.partner_id, partner)
        self.assertEqual(po.partner_ref, 'МК-CPP-012')
        self.assertEqual(len(po.order_line), 1)
        self.assertEqual(po.order_line.product_id.id, product_id)
