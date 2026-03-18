"""
OBR-011: Тесты создания складского документа выдачи.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestObr011IssuePicking(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-011',
            'code': 'TST-011',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб OBR011',
            'login': 'foreman_test_obr011',
            'email': 'foreman_obr011@test.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Цемент М500 OBR011',
            'default_code': 'CEM-011',
            'type': 'consu',
        })
        self.uom = self.product.uom_id
        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        self.request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })
        # Line with qty_to_issue
        self.line = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Цемент',
            'qty_requested': 10.0,
            'qty_to_issue': 6.0,
            'product_id': self.product.id,
            'uom_id': self.uom.id,
        })
        self.request.write({'state': 'in_progress'})

    def _create_wizard(self):
        """Создать wizard с корректными данными."""
        customer_loc = self.env.ref('stock.stock_location_customers')
        return self.env['object.request.issue.wizard'].create({
            'request_id': self.request.id,
            'line_ids': [(6, 0, [self.line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })

    def test_wizard_default_get_fills_lines(self):
        """default_get заполняет строки из запроса с qty_to_issue > 0."""
        wiz = self.env['object.request.issue.wizard'].with_context(
            default_request_id=self.request.id
        ).create({})
        self.assertIn(self.line, wiz.line_ids)

    def test_wizard_no_lines_raises_user_error(self):
        """Если нет строк — UserError."""
        customer_loc = self.env.ref('stock.stock_location_customers')
        wiz = self.env['object.request.issue.wizard'].create({
            'request_id': self.request.id,
            'line_ids': [(5,)],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        with self.assertRaises(UserError):
            wiz.action_create_issue()

    def test_create_issue_creates_picking(self):
        """action_create_issue создаёт stock.picking."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        self.assertEqual(result['res_model'], 'stock.picking')
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertTrue(picking.exists())
        self.assertTrue(picking.is_object_request_issue)
        self.assertEqual(picking.origin, self.request.name)

    def test_picking_has_correct_moves(self):
        """Picking содержит move с правильным количеством."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertEqual(len(picking.move_ids), 1)
        move = picking.move_ids[0]
        self.assertEqual(move.product_id, self.product)
        self.assertEqual(move.product_uom_qty, 6.0)

    def test_picking_linked_to_request(self):
        """Picking привязан к документу требования."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertIn(picking, self.request.issue_picking_ids)

    def test_line_linked_to_picking(self):
        """Строка документа привязана к picking и move."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.line.invalidate_recordset()
        self.assertEqual(self.line.issue_picking_id, picking)
        self.assertTrue(self.line.issue_move_id)

    def test_request_issue_picking_count(self):
        """issue_picking_count увеличивается после создания выдачи."""
        wiz = self._create_wizard()
        wiz.action_create_issue()
        self.request.invalidate_recordset()
        self.assertEqual(self.request.issue_picking_count, 1)

    def test_multiple_lines_creates_multiple_moves(self):
        """Несколько строк → несколько moves в одном picking."""
        product2 = self.env['product.product'].create({
            'name': 'Арматура 12мм OBR011',
            'default_code': 'ARM-011',
            'type': 'consu',
        })
        line2 = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Арматура',
            'qty_requested': 20.0,
            'qty_to_issue': 15.0,
            'product_id': product2.id,
            'uom_id': product2.uom_id.id,
        })
        customer_loc = self.env.ref('stock.stock_location_customers')
        wiz = self.env['object.request.issue.wizard'].create({
            'request_id': self.request.id,
            'line_ids': [(6, 0, [self.line.id, line2.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.warehouse.lot_stock_id.id,
            'destination_location_id': customer_loc.id,
            'scheduled_date': datetime.datetime.now(),
        })
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertEqual(len(picking.move_ids), 2)

    def test_picking_project_linked(self):
        """Picking содержит ссылку на объект проекта."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertEqual(picking.object_request_project_id, self.project)

    def test_picking_back_link_to_request(self):
        """Обратная связь picking → request работает."""
        wiz = self._create_wizard()
        result = wiz.action_create_issue()
        picking = self.env['stock.picking'].browse(result['res_id'])
        self.assertIn(self.request, picking.object_request_ids)

    def test_action_open_issue_wizard_no_lines_raises(self):
        """action_open_issue_wizard без qty_to_issue → UserError."""
        request2 = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })
        self.env['object.request.line'].create({
            'request_id': request2.id,
            'name_raw': 'Цемент',
            'qty_requested': 5.0,
            'product_id': self.product.id,
        })
        request2.write({'state': 'in_progress'})
        with self.assertRaises(UserError):
            request2.action_open_issue_wizard()

    def test_action_open_issue_wizard_returns_wizard_action(self):
        """action_open_issue_wizard возвращает действие открытия wizard."""
        action = self.request.action_open_issue_wizard()
        self.assertEqual(action['res_model'], 'object.request.issue.wizard')
        self.assertEqual(action['target'], 'new')
