from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestWarehouseStockAction(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('code', '=', 'O002')],
            limit=1,
        )
        if not cls.warehouse:
            cls.warehouse = cls.env['stock.warehouse'].create({
                'name': 'Б. Хмельницкого, 112',
                'code': 'O002',
            })

    def test_action_sets_warehouse_context(self):
        action = self.env['stock.warehouse'].with_context(
            active_id=self.warehouse.id,
        ).action_ai_open_warehouse_stock()
        self.assertEqual(action['res_model'], 'product.product')
        self.assertEqual(
            action['context']['search_warehouse'],
            self.warehouse.id,
        )
        self.assertEqual(
            action['context']['search_default_real_stock_available'],
            1,
        )

    def test_action_without_available_filter(self):
        action = self.env['stock.warehouse'].with_context(
            active_ids=[self.warehouse.id, 0],
        ).action_ai_open_warehouse_stock()
        self.assertEqual(
            action['context']['search_warehouse'],
            self.warehouse.id,
        )
        self.assertNotIn(
            'search_default_real_stock_available',
            action['context'],
        )

    def test_action_missing_warehouse_raises(self):
        with self.assertRaises(UserError):
            self.env['stock.warehouse'].action_ai_open_warehouse_stock()

    def test_server_action_path_exists(self):
        action = self.env.ref('ai_assistant.action_ai_warehouse_stock')
        self.assertEqual(action.path, 'ai-warehouse-stock')
