from odoo.tests.common import TransactionCase
from odoo.tests import tagged

from odoo.addons.ai_assistant.services.action_tools.read_tools import (
    FindObjectRequestTool,
    FindPartnerTool,
    FindPickingTypeTool,
    FindProductByIdTool,
    FindWarehouseTool,
    GetNavigationLinkTool,
    GetWarehouseStockLinkTool,
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
        cls.supplier.category_id = [(6, 0, [
            cls.env['res.partner.category'].create({
                'name': 'Read Supplier Tag',
            }).id,
        ])]
        cls.customer = cls.env['res.partner'].create({
            'name': 'Read Customer',
            'vat': '1435000001',
            'supplier_rank': 0,
            'customer_rank': 1,
            'city': 'Якутск',
        })
        cls.warehouse = cls.env['stock.warehouse'].create({
            'name': 'ОбМ Read Tools',
            'code': 'ОбМ-R',
        })
        cls.address_warehouse = cls._get_or_create_warehouse(
            'Б. Хмельницкого, 112',
            'O002',
        )
        cls.prefix_warehouse = cls._get_or_create_warehouse(
            'Ломоносова 164',
            'O001',
        )
        cls.env['stock.quant']._update_available_quantity(
            cls.product, cls.warehouse.lot_stock_id, 7.0
        )
        cls.env['stock.quant']._update_available_quantity(
            cls.product, cls.address_warehouse.lot_stock_id, 3.0
        )
        cls.env['stock.quant']._update_available_quantity(
            cls.product, cls.prefix_warehouse.lot_stock_id, 2.0
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

    @classmethod
    def _get_or_create_warehouse(cls, name, code):
        warehouse = cls.env['stock.warehouse'].search(
            [('code', '=', code)],
            limit=1,
        )
        if warehouse:
            warehouse.name = name
            return warehouse
        return cls.env['stock.warehouse'].create({
            'name': name,
            'code': code,
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
        partner = next(
            item for item in result['partners']
            if item['id'] == self.supplier.id
        )
        self.assertIn('customer_rank', partner)
        self.assertIn('category_id', partner)
        self.assertIn('city', partner)

    def test_find_partner_without_supplier_filter(self):
        result = FindPartnerTool().execute(
            self.env, {'query': '1435000001', 'is_supplier': False}
        )
        partner_ids = [item['id'] for item in result['partners']]
        self.assertIn(self.customer.id, partner_ids)

    def test_find_partner_role_customer(self):
        result = FindPartnerTool().execute(
            self.env, {'query': '1435000001', 'role': 'customer'}
        )
        partner_ids = [item['id'] for item in result['partners']]
        self.assertIn(self.customer.id, partner_ids)
        self.assertNotIn(self.supplier.id, partner_ids)

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
        self.assertIsInstance(
            default_registry.get('get_navigation_link'), GetNavigationLinkTool
        )
        self.assertIsInstance(
            default_registry.get('get_warehouse_stock_link'),
            GetWarehouseStockLinkTool,
        )

    def test_search_stock_quants_basic(self):
        result = SearchStockQuantsTool().execute(self.env, {
            'product_id': self.product.id,
            'warehouse_codes': ['ОбМ-R'],
            'only_positive': True,
        })
        self.assertTrue(result['quants'])
        self.assertEqual(result['quants'][0]['quantity'], 7.0)

    def test_search_stock_quants_uses_legacy_warehouse_alias(self):
        result = SearchStockQuantsTool().execute(self.env, {
            'product_id': self.product.id,
            'warehouse_codes': ['ОбМ-4'],
            'only_positive': True,
        })
        warehouse_ids = {
            quant['warehouse_id'][0]
            for quant in result['quants']
        }
        self.assertIn(self.address_warehouse.id, warehouse_ids)

    def test_find_warehouse_by_code(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'ОбМ-R'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.warehouse.id, warehouse_ids)

    def test_find_warehouse_by_legacy_code_pattern(self):
        result = FindWarehouseTool().execute(
            self.env, {'code_pattern': 'ОбМ-R'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.warehouse.id, warehouse_ids)

    def test_find_warehouse_by_name_fragment(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'Хмельницкого'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.address_warehouse.id, warehouse_ids)

    def test_find_warehouse_by_full_name(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'Б. Хмельницкого, 112'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.address_warehouse.id, warehouse_ids)

    def test_find_warehouse_no_match(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'Несуществующий склад read tools'}
        )
        self.assertEqual(result['warehouses'], [])

    def test_find_warehouse_obm_prefix_list(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'ОбМ-'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.address_warehouse.id, warehouse_ids)
        self.assertIn(self.prefix_warehouse.id, warehouse_ids)

    def test_find_warehouse_object_prefix_list(self):
        result = FindWarehouseTool().execute(
            self.env, {'query': 'O'}
        )
        warehouse_ids = [item['id'] for item in result['warehouses']]
        self.assertIn(self.address_warehouse.id, warehouse_ids)
        self.assertIn(self.prefix_warehouse.id, warehouse_ids)

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

    def test_get_navigation_link_known_topic(self):
        result = GetNavigationLinkTool().execute(
            self.env, {'topic': 'заказы поставщикам'}
        )
        self.assertEqual(result['label'], 'Заказы поставщикам')
        self.assertTrue(result['url'].startswith('/odoo/'))
        self.assertIn('menu_breadcrumb', result)

    def test_get_navigation_link_zakupku_alias(self):
        result = GetNavigationLinkTool().execute(
            self.env, {'topic': 'заказы на закупку'}
        )
        self.assertEqual(result['label'], 'Заказы поставщикам')
        self.assertTrue(result['url'].startswith('/odoo/'))

    def test_get_navigation_link_unknown_topic(self):
        result = GetNavigationLinkTool().execute(
            self.env, {'topic': 'несуществующий раздел xyz'}
        )
        self.assertIsNone(result['url'])
        self.assertEqual(result['reason'], 'unknown_topic')

    def test_get_navigation_link_no_group(self):
        user = self.env['res.users'].create({
            'name': 'AI Nav No Purchase',
            'login': 'ai_nav_no_purchase',
            'email': 'ai_nav_no_purchase@example.com',
            'group_ids': [(6, 0, [
                self.env.ref('base.group_user').id,
                self.env.ref('ai_assistant.group_ai_assistant_user').id,
            ])],
        })
        result = GetNavigationLinkTool().execute(
            self.env(user=user),
            {'topic': 'заказы поставщикам'},
        )
        self.assertIsNone(result['url'])
        self.assertEqual(result['reason'], 'forbidden')

    def test_get_navigation_link_with_context_defaults(self):
        result = GetNavigationLinkTool().execute(
            self.env, {'topic': 'заказы поставщикам'}
        )
        self.assertIn('search_default_my_purchases=1', result['url'])

    def test_get_navigation_link_aliases(self):
        tool = GetNavigationLinkTool()
        by_po = tool.execute(self.env, {'topic': 'po'})
        by_purchase = tool.execute(self.env, {'topic': 'закупки'})
        self.assertEqual(by_po['label'], 'Заказы поставщикам')
        self.assertEqual(
            by_purchase['label'],
            'Запросы коммерческих предложений',
        )

    def test_get_navigation_link_action_missing(self):
        tool = GetNavigationLinkTool()
        tool.catalog = ({
            'topic_keys': ('missing action test',),
            'label': 'Missing Action',
            'action_xml_id': 'ai_assistant.missing_action_for_test',
            'required_groups': ('base.group_user',),
            'menu_breadcrumb': 'Missing',
        },)
        result = tool.execute(self.env, {'topic': 'missing action test'})
        self.assertIsNone(result['url'])
        self.assertEqual(result['reason'], 'not_found')

    def test_get_warehouse_stock_link_by_id(self):
        result = GetWarehouseStockLinkTool().execute(
            self.env,
            {'warehouse_id': self.address_warehouse.id},
        )
        self.assertTrue(result['url'].startswith('/odoo/ai-warehouse-stock?'))
        self.assertIn(
            'active_id=%s' % self.address_warehouse.id,
            result['url'],
        )
        self.assertNotIn('search_warehouse', result['url'])
        self.assertIn('O002', result['label'])

    def test_get_warehouse_stock_link_by_query(self):
        result = GetWarehouseStockLinkTool().execute(
            self.env,
            {'query': 'Хмельницкого', 'only_available': False},
        )
        self.assertIn('ai-warehouse-stock', result['url'])
        self.assertIn('active_ids=', result['url'])

    def test_get_warehouse_stock_link_not_found(self):
        result = GetWarehouseStockLinkTool().execute(
            self.env,
            {'query': 'несуществующий склад xyz'},
        )
        self.assertIsNone(result['url'])
        self.assertEqual(result['reason'], 'warehouse_not_found')
