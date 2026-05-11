"""
OBR-025: Проверка наличия по всем активным складам компании.
"""
import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install')
class TestObr025MultiwarehouseCheck(TransactionCase):
    """Проверка multi-warehouse расчёта через object.request.line.stock."""

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-025',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб OBR025',
            'login': 'foreman_test_obr025',
            'email': 'foreman_obr025@test.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Цемент OBR025',
            'default_code': 'CEMENT-025',
            'type': 'consu',
            'is_storable': True,
        })
        warehouses = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True),
        ], limit=2)
        self.warehouse1 = warehouses[0]
        self.warehouse2 = warehouses[1] if len(warehouses) > 1 else self._create_warehouse2()
        self.request = self._create_request()
        self.line = self._add_line(self.request)

    def _create_warehouse2(self):
        return self.env['stock.warehouse'].sudo().create({
            'name': 'Склад OBR025-2',
            'code': 'O25B',
            'company_id': self.env.company.id,
        })

    def _create_request(self):
        return self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })

    def _add_line(self, request):
        return self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Цемент',
            'qty_requested': 10.0,
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
        })

    def _put_stock(self, warehouse, qty):
        self.env['stock.quant']._update_available_quantity(
            self.product, warehouse.lot_stock_id, qty,
        )

    def test_check_stock_creates_row_for_each_active_warehouse(self):
        self.request.action_check_stock()
        active_warehouses = self.env['stock.warehouse'].search([
            ('company_id', '=', self.env.company.id),
            ('active', '=', True),
        ])
        self.assertEqual(
            set(self.line.stock_ids.mapped('warehouse_id').ids),
            set(active_warehouses.ids),
        )

    def test_check_stock_sums_multiple_warehouses(self):
        self._put_stock(self.warehouse1, 5.0)
        self._put_stock(self.warehouse2, 3.0)

        self.request.action_check_stock()

        self.assertAlmostEqual(self.line.stock_qty_on_hand, 8.0)
        self.assertAlmostEqual(
            self.line.stock_ids.filtered(
                lambda stock: stock.warehouse_id == self.warehouse1
            ).qty_on_hand,
            5.0,
        )
        self.assertAlmostEqual(
            self.line.stock_ids.filtered(
                lambda stock: stock.warehouse_id == self.warehouse2
            ).qty_on_hand,
            3.0,
        )

    def test_check_stock_returns_warning_if_nothing_found(self):
        result = self.request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')
        self.assertEqual(result['params']['type'], 'warning')

    def test_check_stock_opens_wizard_if_found(self):
        self._put_stock(self.warehouse1, 10.0)
        result = self.request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(result['res_model'], 'object.request.stock.check.wizard')

    def test_wizard_action_confirm_returns_close(self):
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        result = wizard.action_confirm()
        self.assertEqual(result['type'], 'ir.actions.act_window_close')

    def test_wizard_action_recheck_returns_close(self):
        wizard = self.env['object.request.stock.check.wizard'].create({
            'request_id': self.request.id,
        })
        result = wizard.action_recheck()
        self.assertEqual(result['type'], 'ir.actions.act_window_close')
