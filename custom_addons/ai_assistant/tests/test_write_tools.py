from odoo.exceptions import AccessError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase

from odoo.addons.ai_assistant.services.action_tools.registry import (
    default_registry,
)
from odoo.addons.ai_assistant.services.action_tools.write_tools import (
    CreateInternalPickingDraftTool,
    CreateObjectRequestDraftTool,
    CreateProductDraftTool,
    CreatePurchaseOrderDraftTool,
)


@tagged('post_install', '-at_install')
class TestActionWriteTools(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env['object.request.project'].create({
            'name': 'Write Tools Object',
        })
        cls.vendor = cls.env['res.partner'].create({
            'name': 'ООО ПроМеталл',
            'vat': '1435000360',
            'supplier_rank': 1,
        })
        cls.customer = cls.env['res.partner'].create({
            'name': 'Покупатель Write Tools',
            'supplier_rank': 0,
        })
        cls.pipe_category = cls.env['product.category'].create({
            'name': 'Трубы write tools',
        })
        cls.object_warehouse = cls.project.warehouse_id
        cls.default_warehouse = cls.env.ref('stock.warehouse0')
        cls.pipe_products = cls.env['product.product']
        for idx in range(6):
            cls.pipe_products |= cls.env['product.product'].create({
                'name': 'Труба ВГП 89x3.5 WT %s' % idx,
                'is_storable': True,
                'categ_id': cls.pipe_category.id,
                'uom_id': cls.env.ref('uom.product_uom_meter').id,
            })
        cls.consumable_product = cls.env['product.product'].create({
            'name': 'Услуга Write Tools',
            'is_storable': False,
        })
        cls.kg_pipe = cls.env['product.product'].create({
            'name': 'Труба в кг Write Tools',
            'is_storable': True,
            'categ_id': cls.pipe_category.id,
            'uom_id': cls.env.ref('uom.product_uom_kgm').id,
        })
        cls.supply_user = cls._create_user(
            'ai_write_supply',
            [
                'ai_assistant.group_ai_assistant_supply',
                'object_request.group_supply_manager',
            ],
        )
        cls.no_ai_user = cls._create_user(
            'object_write_without_ai',
            ['object_request.group_supply_manager'],
        )

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

    def test_create_or_draft_happy(self):
        tool = CreateObjectRequestDraftTool()
        args = self._draft_args()

        result = tool.execute(self.env(user=self.supply_user), args)

        request_record = self.env['object.request'].browse(
            result['request_id']
        )
        self.assertEqual(request_record.state, 'draft')
        self.assertEqual(request_record.project_id, self.project)
        self.assertEqual(request_record.foreman_user_id, self.supply_user)
        self.assertEqual(request_record.need_date.isoformat(), '2026-06-10')
        self.assertEqual(len(request_record.line_ids), 2)
        self.assertEqual(
            result['url'], '/odoo/object_request/%s' % request_record.id
        )

    def test_create_or_draft_rejects_without_supply_group(self):
        tool = CreateObjectRequestDraftTool()

        with self.assertRaises(AccessError):
            tool.execute(self.env(user=self.no_ai_user), self._draft_args())

    def test_create_or_draft_message_post_called(self):
        tool = CreateObjectRequestDraftTool()

        result = tool.execute(
            self.env(user=self.supply_user),
            self._draft_args(),
        )

        request_record = self.env['object.request'].browse(
            result['request_id']
        )
        body = '\n'.join(request_record.message_ids.mapped('body'))
        self.assertIn('AI-ассистентом', body)

    def test_create_or_draft_rejects_empty_lines(self):
        tool = CreateObjectRequestDraftTool()
        args = self._draft_args()
        args['lines'] = []

        with self.assertRaises(ValidationError):
            tool.execute(self.env(user=self.supply_user), args)

    def test_create_or_draft_rejects_non_positive_qty(self):
        tool = CreateObjectRequestDraftTool()
        args = self._draft_args()
        args['lines'][0]['qty_requested'] = 0

        with self.assertRaises(ValidationError):
            tool.execute(self.env(user=self.supply_user), args)

    def test_create_or_draft_registered(self):
        self.assertIsInstance(
            default_registry.get('create_object_request_draft'),
            CreateObjectRequestDraftTool,
        )

    def test_create_or_draft_idempotency_key_is_stable(self):
        tool = CreateObjectRequestDraftTool()
        args = self._draft_args()
        reversed_args = self._draft_args()
        reversed_args['lines'] = list(reversed(reversed_args['lines']))

        self.assertEqual(
            tool.idempotency_key(args),
            tool.idempotency_key(reversed_args),
        )

    def test_create_purchase_order_draft_happy_obm4(self):
        tool = CreatePurchaseOrderDraftTool()

        result = tool.execute(
            self.env(user=self.supply_user),
            self._purchase_args(),
        )

        po = self.env['purchase.order'].browse(result['po_id'])
        self.assertEqual(po.state, 'draft')
        self.assertEqual(po.partner_id, self.vendor)
        self.assertEqual(po.picking_type_id, self.object_warehouse.in_type_id)
        self.assertEqual(po.origin, 'OR/2026/05/0007')
        self.assertEqual(po.partner_ref, 'УТ-1132')
        self.assertEqual(len(po.order_line), 6)
        self.assertEqual(sum(po.order_line.mapped('product_qty')), 1098)
        self.assertEqual(result['warnings'], [])

    def test_create_purchase_order_accepts_non_object_picking_type(self):
        tool = CreatePurchaseOrderDraftTool()
        args = self._purchase_args()
        args['picking_type_id'] = self.default_warehouse.in_type_id.id

        result = tool.execute(self.env(user=self.supply_user), args)

        po = self.env['purchase.order'].browse(result['po_id'])
        self.assertEqual(po.picking_type_id, self.default_warehouse.in_type_id)

    def test_create_purchase_order_rejects_non_storable_product(self):
        tool = CreatePurchaseOrderDraftTool()
        args = self._purchase_args()
        args['lines'][0]['product_id'] = self.consumable_product.id

        with self.assertRaises(ValidationError):
            tool.execute(self.env(user=self.supply_user), args)

    def test_create_purchase_order_warns_for_pipe_uom_kg(self):
        tool = CreatePurchaseOrderDraftTool()
        args = self._purchase_args()
        args['lines'] = [{
            'product_id': self.kg_pipe.id,
            'product_qty': 100.0,
            'product_uom': self.env.ref('uom.product_uom_kgm').id,
            'price_unit': 10.0,
            'name': 'Труба в кг',
        }]

        result = tool.execute(self.env(user=self.supply_user), args)

        self.assertTrue(result['warnings'])
        self.assertIn('TD-002', result['warnings'][0])

    def test_create_purchase_order_registered(self):
        self.assertIsInstance(
            default_registry.get('create_purchase_order_draft'),
            CreatePurchaseOrderDraftTool,
        )

    def test_create_product_draft_happy(self):
        tool = CreateProductDraftTool()
        product_name = 'Тройник 76х3,5-45х3-20 ГОСТ 17376-2001'

        result = tool.execute(
            self.env(user=self.supply_user),
            {
                'name': product_name,
                'categ_id': self.pipe_category.id,
                'uom_id': self.env.ref('uom.product_uom_unit').id,
                'purchase_ok': True,
                'sale_ok': False,
            },
        )

        product = self.env['product.product'].browse(result['product_id'])
        self.assertTrue(product.is_storable)
        self.assertEqual(product.name, product_name)
        self.assertEqual(product.categ_id, self.pipe_category)
        self.assertTrue(product.purchase_ok)
        self.assertFalse(product.sale_ok)
        self.assertEqual(
            result['url'], '/odoo/product.product/%s' % product.id
        )
        body = '\n'.join(product.product_tmpl_id.message_ids.mapped('body'))
        self.assertIn('AI-ассистентом', body)

    def test_create_product_draft_with_list_price(self):
        tool = CreateProductDraftTool()
        result = tool.execute(
            self.env(user=self.supply_user),
            {
                'name': 'ЗРК тест цена',
                'list_price': 1500.0,
                'purchase_ok': True,
            },
        )
        product = self.env['product.product'].browse(result['product_id'])
        self.assertEqual(product.list_price, 1500.0)
        self.assertEqual(product.standard_price, 1500.0)

    def test_create_product_draft_uses_default_category_when_omitted(self):
        tool = CreateProductDraftTool()
        product_name = 'ЗРК 25ч945п-25-4,0-1,6-150-УХЛ4 default categ'

        result = tool.execute(
            self.env(user=self.supply_user),
            {
                'name': product_name,
                'purchase_ok': True,
            },
        )

        product = self.env['product.product'].browse(result['product_id'])
        default_categ = self.env.ref('product.product_category_goods')
        self.assertEqual(product.categ_id, default_categ)
        self.assertEqual(product.uom_id, self.env.ref('uom.product_uom_unit'))
        self.assertTrue(product.purchase_ok)

    def test_create_product_draft_rejects_without_supply_group(self):
        tool = CreateProductDraftTool()

        with self.assertRaises(AccessError):
            tool.execute(
                self.env(user=self.no_ai_user),
                {'name': 'Новый товар Write Tools'},
            )

    def test_create_product_draft_rejects_duplicate_name(self):
        tool = CreateProductDraftTool()
        args = {
            'name': self.pipe_products[0].name,
            'categ_id': self.pipe_category.id,
        }

        with self.assertRaises(ValidationError):
            tool.execute(self.env(user=self.supply_user), args)

    def test_create_product_draft_registered(self):
        self.assertIsInstance(
            default_registry.get('create_product_draft'),
            CreateProductDraftTool,
        )

    def test_create_product_draft_idempotency_key_is_stable(self):
        tool = CreateProductDraftTool()
        args = {
            'name': 'Тройник тест',
            'categ_id': self.pipe_category.id,
        }

        self.assertEqual(
            tool.idempotency_key(args),
            tool.idempotency_key(dict(args)),
        )

    def test_create_internal_picking_draft_happy(self):
        tool = CreateInternalPickingDraftTool()

        result = tool.execute(
            self.env(user=self.supply_user),
            self._internal_picking_args(),
        )

        picking = self.env['stock.picking'].browse(result['picking_id'])
        self.assertEqual(picking.state, 'draft')
        self.assertEqual(
            picking.picking_type_id, self.object_warehouse.int_type_id
        )
        self.assertEqual(
            picking.location_id, self.default_warehouse.lot_stock_id
        )
        self.assertEqual(
            picking.location_dest_id, self.object_warehouse.lot_stock_id
        )
        self.assertEqual(picking.origin, 'OR/2026/05/0007')
        self.assertEqual(len(picking.move_ids), 2)

    def test_create_internal_picking_rejects_non_object_dest(self):
        tool = CreateInternalPickingDraftTool()
        args = self._internal_picking_args()
        args['location_dest_id'] = self.default_warehouse.lot_stock_id.id

        with self.assertRaises(ValidationError):
            tool.execute(self.env(user=self.supply_user), args)

    def test_create_internal_picking_registered(self):
        self.assertIsInstance(
            default_registry.get('create_internal_picking_draft'),
            CreateInternalPickingDraftTool,
        )

    def _draft_args(self):
        return {
            'project_id': self.project.id,
            'need_date': '2026-06-10',
            'lines': [
                {
                    'name_raw': 'Труба ВГП 50',
                    'qty_requested': 12.5,
                    'preferred_vendor_id': self.vendor.id,
                },
                {
                    'name_raw': 'Отвод 50',
                    'qty_requested': 3.0,
                    'preferred_vendor_id': None,
                },
            ],
        }

    def _purchase_args(self):
        quantities = [180.0, 180.0, 180.0, 180.0, 180.0, 198.0]
        return {
            'partner_id': self.vendor.id,
            'picking_type_id': self.object_warehouse.in_type_id.id,
            'origin': 'OR/2026/05/0007',
            'partner_ref': 'УТ-1132',
            'date_planned': '2026-06-11 08:00:00',
            'lines': [
                {
                    'product_id': product.id,
                    'product_qty': quantities[index],
                    'product_uom': self.env.ref('uom.product_uom_meter').id,
                    'price_unit': 100.0 + index,
                    'name': product.display_name,
                }
                for index, product in enumerate(self.pipe_products)
            ],
        }

    def _internal_picking_args(self):
        products = self.pipe_products[:2]
        return {
            'picking_type_id': self.object_warehouse.int_type_id.id,
            'location_id': self.default_warehouse.lot_stock_id.id,
            'location_dest_id': self.object_warehouse.lot_stock_id.id,
            'origin': 'OR/2026/05/0007',
            'scheduled_date': '2026-06-12 08:00:00',
            'moves': [
                {
                    'product_id': product.id,
                    'product_uom_qty': 5.0,
                    'product_uom': self.env.ref('uom.product_uom_meter').id,
                    'name': product.display_name,
                }
                for product in products
            ],
        }
