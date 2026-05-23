from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindObjectRequestTool,
    FindPartnerTool,
    FindPickingTypeTool,
    FindProductByIdTool,
    FindWarehouseTool,
    ReadObjectRequestTool,
    SearchStockQuantsTool,
    SearchProductsTool,
)
from odoo.addons.ai_assistant.services.action_tools.registry import (
    default_registry,
)


@tagged('post_install', '-at_install')
class TestActionReadTools(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.pipe_category = cls.env['product.category'].create({
            'name': 'Трубы read tools',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Труба ВГП 50 read tool',
            'default_code': 'PIPE-READ-50',
            'is_storable': True,
            'list_price': 123.45,
            'categ_id': cls.pipe_category.id,
            'uom_id': cls.env.ref('uom.product_uom_meter').id,
        })
        cls.supplier = cls.env['res.partner'].create({
            'name': 'ООО Read Supplier',
            'vat': '1435000000',
            'supplier_rank': 1,
        })
        cls.customer = cls.env['res.partner'].create({
            'name': 'Read Customer',
            'vat': '1435000001',
            'supplier_rank': 0,
        })
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'ОбМ Read Tools',
            'code': 'ОбМ-R',
        })
        cls.env['stock.quant']._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 7.0
        )
        cls.project = cls.env['object.request.project'].create({
            'name': 'Read Tools Object',
        })
        cls.request = cls.env['object.request'].create({
            'project_id': cls.project.id,
            'foreman_user_id': cls.env.user.id,
            'need_date': '2026-06-01',
        })
        cls.line = cls.env['object.request.line'].create({
            'request_id': cls.request.id,
            'name_raw': 'Труба ВГП 50',
            'product_id': cls.product.id,
            'uom_id': cls.env.ref('uom.product_uom_meter').id,
            'qty_requested': 7.0,
            'qty_to_buy': 7.0,
        })

    def test_search_products_basic(self):
        result = SearchProductsTool().execute(
            self.env, {'query': 'труба вгп 50', 'limit': 10}
        )
        product_ids = [item['id'] for item in result['products']]
        self.assertIn(self.product.id, product_ids)
        product = next(
            item for item in result['products']
            if item['id'] == self.product.id
        )
        self.assertTrue(product['is_storable'])
        self.assertEqual(product['default_code'], 'PIPE-READ-50')

    def test_find_product_by_id(self):
        result = FindProductByIdTool().execute(
            self.env, {'product_id': self.product.id}
        )
        self.assertEqual(result['product']['id'], self.product.id)
        self.assertEqual(result['product']['is_storable'], True)

    def test_find_product_by_id_missing(self):
        result = FindProductByIdTool().execute(
            self.env, {'product_id': 999999999}
        )
        self.assertIsNone(result['product'])

    def test_find_partner_by_vat(self):
        result = FindPartnerTool().execute(
            self.env, {'query': '1435000000', 'is_supplier': True}
        )
        partner_ids = [item['id'] for item in result['partners']]
        self.assertIn(self.supplier.id, partner_ids)
        self.assertNotIn(self.customer.id, partner_ids)

    def test_find_partner_without_supplier_filter(self):
        result = FindPartnerTool().execute(
            self.env, {'query': '1435000001', 'is_supplier': False}
        )
        partner_ids = [item['id'] for item in result['partners']]
        self.assertIn(self.customer.id, partner_ids)

    def test_read_tools_registered(self):
        self.assertIsInstance(
            default_registry.get('search_products'), SearchProductsTool
        )
        self.assertIsInstance(
            default_registry.get('find_product_by_id'), FindProductByIdTool
        )
        self.assertIsInstance(
            default_registry.get('find_partner'), FindPartnerTool
        )
        self.assertIsInstance(
            default_registry.get('search_stock_quants'), SearchStockQuantsTool
        )

    def test_search_stock_quants_basic(self):
        result = SearchStockQuantsTool().execute(self.env, {
            'product_id': self.product.id,
            'warehouse_codes': ['ОбМ-R'],
            'only_positive': True,
        })
        self.assertTrue(result['quants'])
        self.assertEqual(result['quants'][0]['quantity'], 7.0)

    def test_find_warehouse_by_code(self):
        result = FindWarehouseTool().execute(
            self.env, {'code_pattern': 'ОбМ-R'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.warehouse.id, warehouse_ids)

    def test_find_picking_type(self):
        result = FindPickingTypeTool().execute(self.env, {
            'warehouse_id': self.warehouse.id,
            'code': 'incoming',
        })
        self.assertTrue(result['picking_types'])
        self.assertEqual(
            result['picking_types'][0]['warehouse_id'][0],
            self.warehouse.id
        )

    def test_find_object_request(self):
        result = FindObjectRequestTool().execute(self.env, {
            'query': self.request.name,
            'state': 'draft',
            'project_id': self.project.id,
        })
        request_ids = [item['id'] for item in result['requests']]
        self.assertIn(self.request.id, request_ids)

    def test_read_object_request(self):
        result = ReadObjectRequestTool().execute(
            self.env, {'request_id': self.request.id}
        )
        request_data = result['request']
        self.assertEqual(request_data['id'], self.request.id)
        self.assertEqual(request_data['lines'][0]['id'], self.line.id)
        self.assertIn('summary', request_data)
