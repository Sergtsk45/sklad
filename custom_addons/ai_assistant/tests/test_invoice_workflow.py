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
            InvoiceWorkflow.ACTION_PO_START,
        )
        self.assertEqual(suggestions[0]['payload']['create_po'], True)

    def test_purchase_flow_no_stops_without_writes(self):
        token = self._put_token()
        self.workflow.record_product_created(self.env.uid, token, '1', 101)
        self.workflow.record_product_created(self.env.uid, token, '2', 102)

        payload = self.workflow.set_create_po_decision(
            self.env.uid, token, False,
        )

        self.assertEqual(payload['status'], InvoiceWorkflow.FLOW_DONE)
        flow = self.workflow.current_purchase_flow_state(
            self.env.uid, token,
        )
        self.assertFalse(flow['create_po'])
        self.assertFalse(flow['po_id'])

    def test_purchase_flow_yes_asks_warehouse(self):
        token = self._put_token()
        self.workflow.record_product_created(self.env.uid, token, '1', 101)
        self.workflow.record_product_created(self.env.uid, token, '2', 102)

        payload = self.workflow.set_create_po_decision(
            self.env.uid, token, True,
        )

        self.assertEqual(
            payload['status'],
            InvoiceWorkflow.FLOW_AWAITING_WAREHOUSE,
        )
        self.assertTrue(payload['meta']['awaiting_po_warehouse'])

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

    def test_execute_purchase_plan_creates_confirmed_po_and_attachment(self):
        product_1 = self.env['product.product'].create({
            'name': 'AIA execute product 1',
            'is_storable': True,
            'purchase_ok': True,
        })
        product_2 = self.env['product.product'].create({
            'name': 'AIA execute product 2',
            'is_storable': True,
            'purchase_ok': True,
        })
        token = self.store.put(
            self.env.uid,
            self.invoice_data,
            filename='invoice-aia.pdf',
            file_bytes=b'%PDF-test',
            mimetype='application/pdf',
        )
        self.workflow.record_product_created(
            self.env.uid, token, '1', product_1.id,
        )
        self.workflow.record_product_created(
            self.env.uid, token, '2', product_2.id,
        )
        self.workflow.set_create_po_decision(self.env.uid, token, True)
        self.workflow.select_warehouse(
            self.env.uid,
            token,
            payload={'warehouse_query': 'Ос.ск'},
        )
        self.workflow.set_attach_invoice_decision(self.env.uid, token, True)
        self.workflow.set_receive_picking_decision(self.env.uid, token, False)

        result = self.workflow.execute_purchase_plan(self.env.uid, token)
        flow = self.workflow.current_purchase_flow_state(self.env.uid, token)
        po = self.env['purchase.order'].browse(flow['po_id'])
        attachment = self.env['ir.attachment'].browse(flow['attachment_id'])

        self.assertEqual(result['status'], InvoiceWorkflow.FLOW_EXECUTED)
        self.assertEqual(po.state, 'purchase')
        self.assertEqual(po.partner_ref, '3315')
        self.assertTrue(attachment.exists())
        self.assertEqual(attachment.res_model, 'purchase.order')
        self.assertEqual(attachment.res_id, po.id)
        bill = self.env['account.move'].browse(flow['bill_id'])
        self.assertTrue(bill.exists())
        self.assertEqual(bill.move_type, 'in_invoice')
        self.assertEqual(bill.ref, '3315')
        self.assertEqual(str(bill.invoice_date), '2026-05-25')
        self.assertIn(bill, po.invoice_ids)
        bill_pdf = self.env['ir.attachment'].search([
            ('res_model', '=', 'account.move'),
            ('res_id', '=', bill.id),
            ('name', '=', 'invoice-aia.pdf'),
        ], limit=1)
        self.assertTrue(bill_pdf.exists())
        self.assertAlmostEqual(bill.amount_untaxed, po.amount_untaxed, places=2)
        self.assertAlmostEqual(bill.amount_total, po.amount_total, places=2)
        self.assertIn('Счёт поставщика создан', result['answer'])

        second = self.workflow.execute_purchase_plan(self.env.uid, token)
        self.assertEqual(second['status'], InvoiceWorkflow.FLOW_EXECUTED)
        self.assertEqual(
            self.env['purchase.order'].search_count([
                ('origin', '=', '3315/AIA'),
            ]),
            1,
        )
        self.assertEqual(len(po.invoice_ids), 1)

    def test_execute_purchase_plan_can_validate_receipt(self):
        product = self.env['product.product'].create({
            'name': 'AIA receive product',
            'is_storable': True,
            'purchase_ok': True,
        })
        invoice = dict(self.invoice_data)
        invoice['invoice_number'] = 'AIA-RCV-1'
        invoice['items'] = [{
            'line_no': 1,
            'name': product.name,
            'unit': 'шт',
            'qty': 3,
            'price': 10.0,
        }]
        token = self.store.put(self.env.uid, invoice)
        self.workflow.record_product_created(
            self.env.uid, token, '1', product.id,
        )
        self.workflow.set_create_po_decision(self.env.uid, token, True)
        self.workflow.select_warehouse(
            self.env.uid,
            token,
            payload={'warehouse_query': 'Ос.ск'},
        )
        self.workflow.set_attach_invoice_decision(self.env.uid, token, False)
        self.workflow.set_receive_picking_decision(self.env.uid, token, True)

        self.workflow.execute_purchase_plan(self.env.uid, token)
        flow = self.workflow.current_purchase_flow_state(self.env.uid, token)
        picking = self.env['stock.picking'].browse(flow['picking_id'])
        po = self.env['purchase.order'].browse(flow['po_id'])

        self.assertTrue(picking.exists())
        self.assertEqual(picking.state, 'done')
        self.assertFalse(flow.get('bill_id'))
        self.assertFalse(po.invoice_ids)

    def test_execute_purchase_plan_bill_uses_received_qty(self):
        product = self.env['product.product'].create({
            'name': 'AIA bill receive product',
            'is_storable': True,
            'purchase_ok': True,
            'purchase_method': 'receive',
        })
        invoice = dict(self.invoice_data)
        invoice['invoice_number'] = 'AIA-BILL-RCV'
        invoice['items'] = [{
            'line_no': 1,
            'name': product.name,
            'unit': 'шт',
            'qty': 3,
            'price': 10.0,
        }]
        token = self.store.put(
            self.env.uid,
            invoice,
            filename='invoice-rcv.pdf',
            file_bytes=b'%PDF-test',
            mimetype='application/pdf',
        )
        self.workflow.record_product_created(
            self.env.uid, token, '1', product.id,
        )
        self.workflow.set_create_po_decision(self.env.uid, token, True)
        self.workflow.select_warehouse(
            self.env.uid,
            token,
            payload={'warehouse_query': 'Ос.ск'},
        )
        self.workflow.set_attach_invoice_decision(self.env.uid, token, True)
        self.workflow.set_receive_picking_decision(self.env.uid, token, True)

        self.workflow.execute_purchase_plan(self.env.uid, token)
        flow = self.workflow.current_purchase_flow_state(self.env.uid, token)
        bill = self.env['account.move'].browse(flow['bill_id'])
        line = bill.invoice_line_ids.filtered('product_id')[:1]

        self.assertTrue(bill.exists())
        self.assertEqual(line.quantity, 3.0)
        self.assertEqual(line.price_unit, 10.0)

    def test_next_partner_draft_for_unknown_supplier(self):
        invoice = dict(self.invoice_data)
        invoice['supplier'] = {
            'name': 'ООО Workflow Новый Поставщик',
            'inn': '7727123402',
            'kpp': '772701002',
            'address': '109012, г. Москва, ул. Workflow, д. 2',
        }
        token = self.store.put(self.env.uid, invoice)

        draft = self.workflow.next_partner_draft(self.env.uid, token)

        self.assertEqual(draft['token'], token)
        self.assertEqual(draft['args']['name'], invoice['supplier']['name'])
        self.assertEqual(draft['args']['vat'], invoice['supplier']['inn'])
        self.assertEqual(draft['args']['comment'], 'КПП: 772701002')

    def test_prepare_po_draft_requires_partner_before_warehouse(self):
        invoice = dict(self.invoice_data)
        invoice['supplier'] = {
            'name': 'ООО Workflow Partner First',
            'inn': '7727123403',
        }
        token = self.store.put(self.env.uid, invoice)

        payload = self.workflow.prepare_po_draft(
            self.env.uid, token, 'Ос.ск',
        )

        self.assertEqual(payload['status'], 'partner_incomplete')
        self.assertEqual(
            payload['suggestions'][0]['action'],
            InvoiceWorkflow.ACTION_CREATE_PARTNER,
        )

    def test_record_partner_created_makes_partner_ready(self):
        invoice = dict(self.invoice_data)
        invoice['supplier'] = {
            'name': 'ООО Workflow Created Partner',
            'inn': '7727123404',
        }
        token = self.store.put(self.env.uid, invoice)
        partner = self.env['res.partner'].create({
            'name': invoice['supplier']['name'],
            'vat': invoice['supplier']['inn'],
            'supplier_rank': 1,
        })

        self.workflow.record_partner_created(self.env.uid, token, partner.id)

        self.assertTrue(self.workflow.partner_ready(self.env.uid, token))
        self.assertIsNone(
            self.workflow.next_partner_draft(self.env.uid, token)
        )
