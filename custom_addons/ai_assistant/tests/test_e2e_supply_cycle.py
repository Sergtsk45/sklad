from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.action_tools.executor import (
    ToolExecutor,
    ToolRateLimiter,
)


@tagged('post_install', '-at_install')
class TestUT1132PipelineDraft(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['object.request.project'].create({
            'name': 'Б. Хмельницкого, 112',
        })
        cls.warehouse = cls._get_or_create_obm4_warehouse()
        cls.vendor = cls.env['res.partner'].create({
            'name': 'ООО ПроМеталл',
            'vat': '1435000360',
            'supplier_rank': 1,
        })
        cls.category = cls.env['product.category'].create({
            'name': 'AIA-049 трубы',
        })
        cls.uom_meter = cls.env.ref('uom.product_uom_meter')
        cls.products = cls._create_pipe_products()
        cls.request = cls._create_object_request()
        cls.supply_user = cls._create_user(
            'aia049_supply',
            [
                'ai_assistant.group_ai_assistant_supply',
                'object_request.group_supply_manager',
            ],
        )

    @classmethod
    def _get_or_create_obm4_warehouse(cls):
        warehouse = cls.env['stock.warehouse'].search(
            [('code', '=', 'ОбМ-4')],
            limit=1,
        )
        if warehouse:
            return warehouse
        return cls.env['stock.warehouse'].create({
            'name': 'Б. Хмельницкого, 112',
            'code': 'ОбМ-4',
        })

    @classmethod
    def _create_pipe_products(cls):
        names = [
            'Труба э/с 89×3,5 L12 AIA-049',
            'Труба э/с 76×3,5 L12 AIA-049',
            'Труба вгп 50×3,5 L6 AIA-049',
            'Труба вгп 40×3,5 L6 AIA-049',
            'Труба вгп 20×2,8 L6 AIA-049',
            'Труба вгп 15×2,8 L6 AIA-049',
        ]
        products = cls.env['product.product']
        for index, name in enumerate(names):
            products |= cls.env['product.product'].create({
                'name': name,
                'default_code': 'AIA049-%s' % index,
                'is_storable': True,
                'categ_id': cls.category.id,
                'uom_id': cls.uom_meter.id,
            })
        return products

    @classmethod
    def _create_object_request(cls):
        request_record = cls.env['object.request'].create({
            'name': 'OR/2026/05/0007',
            'project_id': cls.project.id,
            'foreman_user_id': cls.env.user.id,
            'need_date': '2026-06-12',
        })
        quantities = [18.0, 180.0, 78.0, 306.0, 180.0, 336.0]
        for product, qty in zip(cls.products, quantities):
            cls.env['object.request.line'].create({
                'request_id': request_record.id,
                'name_raw': product.display_name,
                'product_id': product.id,
                'uom_id': cls.uom_meter.id,
                'qty_requested': qty,
                'preferred_vendor_id': cls.vendor.id,
            })
        return request_record

    @classmethod
    def _create_user(cls, login, group_xmlids):
        groups = [cls.env.ref('base.group_user').id]
        groups += [cls.env.ref(xmlid).id for xmlid in group_xmlids]
        return cls.env['res.users'].create({
            'name': login,
            'login': login,
            'email': '%s@example.invalid' % login,
            'group_ids': [(6, 0, groups)],
        })

    def test_ut1132_pipeline_creates_purchase_order_draft(self):
        executor = ToolExecutor(
            self.env(user=self.supply_user),
            rate_limiter=ToolRateLimiter(),
        )

        warehouse_result = executor.execute(
            'find_warehouse',
            {'query': 'ОбМ-4'},
        )
        self.assertTrue(warehouse_result['success'])
        warehouse = self._find_result_by_id(
            warehouse_result['result']['warehouses'],
            self.warehouse.id,
        )
        self.assertTrue(warehouse)

        partner_result = executor.execute(
            'find_partner',
            {'query': 'ПроМеталл', 'is_supplier': True},
        )
        self.assertTrue(partner_result['success'])
        partner = self._find_result_by_id(
            partner_result['result']['partners'],
            self.vendor.id,
        )
        self.assertTrue(partner)

        product_result = executor.execute(
            'search_products',
            {'query': '89×3,5', 'limit': 10},
        )
        self.assertTrue(product_result['success'])
        product = self._find_result_by_id(
            product_result['result']['products'],
            self.products[0].id,
        )
        self.assertTrue(product)

        po_result = executor.execute(
            'create_purchase_order_draft',
            self._purchase_args(warehouse['in_type_id'][0], partner['id']),
        )

        self.assertTrue(po_result['success'])
        po = self.env['purchase.order'].browse(
            po_result['result']['po_id']
        )
        self.assertEqual(po.state, 'draft')
        self.assertEqual(po.picking_type_id.warehouse_id.code, 'ОбМ-4')
        self.assertEqual(po.origin, 'OR/2026/05/0007')
        self.assertEqual(po.partner_ref, 'УТ-1132')
        self.assertEqual(sum(po.order_line.mapped('product_qty')), 1098)
        body = '\n'.join(po.message_ids.mapped('body'))
        self.assertIn('AI Assistant', body)

    def _purchase_args(self, picking_type_id, partner_id):
        quantities = [18.0, 180.0, 78.0, 306.0, 180.0, 336.0]
        return {
            'partner_id': partner_id,
            'picking_type_id': picking_type_id,
            'origin': self.request.name,
            'partner_ref': 'УТ-1132',
            'date_planned': '2026-06-12 08:00:00',
            'lines': [
                {
                    'product_id': product.id,
                    'product_qty': quantities[index],
                    'product_uom': self.uom_meter.id,
                    'price_unit': 100.0 + index,
                    'name': product.display_name,
                }
                for index, product in enumerate(self.products)
            ],
        }

    def _find_result_by_id(self, rows, record_id):
        for row in rows:
            if row.get('id') == record_id:
                return row
        return None
