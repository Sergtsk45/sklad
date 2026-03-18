from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestOBR020Reservation(TransactionCase):
    """OBR-020: Резервирование товаров под требование."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.project = cls.env['object.request.project'].create({
            'name': 'Тест резервирования',
            'code': 'RES-001',
        })
        cls.user = cls.env.ref('base.user_admin')

        # Продукт и склад
        cls.product = cls.env['product.product'].create({
            'name': 'Тестовый товар резерв',
            'type': 'consu',
            'is_storable': True,
        })
        cls.warehouse = cls.env['stock.warehouse'].search(
            [('company_id', '=', cls.env.company.id)], limit=1,
        )
        cls.location = cls.warehouse.lot_stock_id

        # Добавим остаток на склад
        cls.env['stock.quant'].with_context(inventory_mode=True).create({
            'product_id': cls.product.id,
            'location_id': cls.location.id,
            'quantity': 50.0,
        })

    def _create_request_with_line(self, qty_to_issue=10.0):
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.user.id,
            'need_date': '2026-04-01',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Тестовая позиция',
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
            'qty_requested': qty_to_issue,
            'qty_to_issue': qty_to_issue,
        })
        request.write({'state': 'in_progress'})
        return request, line

    def test_reservation_created_on_picking(self):
        """При создании picking резервирование выполняется автоматически."""
        request, line = self._create_request_with_line(qty_to_issue=10.0)

        wizard = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.location.id,
            'destination_location_id': self.warehouse.lot_stock_id.id,
        })
        wizard.action_create_issue()

        line.invalidate_recordset()
        # При наличии стока (50 ед) должно зарезервироваться 10
        self.assertEqual(line.qty_reserved, 10.0)
        self.assertTrue(line.issue_reserved)

    def test_reservation_cleared_on_cancel(self):
        """При отмене документа резерв снимается: qty_reserved=0."""
        request, line = self._create_request_with_line(qty_to_issue=5.0)

        wizard = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.location.id,
            'destination_location_id': self.warehouse.lot_stock_id.id,
        })
        wizard.action_create_issue()
        line.invalidate_recordset()

        # Убеждаемся что зарезервировано
        picking = line.issue_picking_id
        self.assertTrue(picking)

        # Отменяем документ
        request.action_cancel()
        line.invalidate_recordset()
        picking.invalidate_recordset()

        self.assertEqual(line.qty_reserved, 0.0)
        self.assertFalse(line.issue_reserved)
        # Picking должен быть unreserved (не assigned)
        self.assertNotEqual(picking.state, 'assigned')

    def test_qty_total_reserved_computed(self):
        """qty_total_reserved на документе пересчитывается по строкам."""
        request, line = self._create_request_with_line(qty_to_issue=7.0)

        # Вручную устанавливаем qty_reserved
        line.write({'qty_reserved': 7.0})
        request.invalidate_recordset()

        self.assertEqual(request.qty_total_reserved, 7.0)

        # Добавим вторую строку с резервом
        line2 = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Вторая позиция',
            'product_id': self.product.id,
            'uom_id': self.product.uom_id.id,
            'qty_requested': 3.0,
            'qty_to_issue': 3.0,
            'qty_reserved': 3.0,
        })
        request.invalidate_recordset()
        self.assertEqual(request.qty_total_reserved, 10.0)

        # Убираем резерв со второй строки
        line2.write({'qty_reserved': 0.0})
        request.invalidate_recordset()
        self.assertEqual(request.qty_total_reserved, 7.0)

    def test_cancel_without_picking_does_not_fail(self):
        """Отмена документа без picking проходит без ошибок."""
        request, _line = self._create_request_with_line(qty_to_issue=5.0)
        # Отменяем без создания picking
        request.action_cancel()
        self.assertEqual(request.state, 'cancelled')

    def test_issue_reserved_false_when_no_stock(self):
        """Если стока нет — issue_reserved=False, qty_reserved=0."""
        # Продукт без остатка
        product_no_stock = self.env['product.product'].create({
            'name': 'Товар без остатка',
            'type': 'consu',
            'is_storable': True,
        })
        request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.user.id,
            'need_date': '2026-04-01',
        })
        line = self.env['object.request.line'].create({
            'request_id': request.id,
            'name_raw': 'Позиция без стока',
            'product_id': product_no_stock.id,
            'uom_id': product_no_stock.uom_id.id,
            'qty_requested': 5.0,
            'qty_to_issue': 5.0,
        })
        request.write({'state': 'in_progress'})

        wizard = self.env['object.request.issue.wizard'].with_context(
            default_request_id=request.id,
        ).create({
            'request_id': request.id,
            'line_ids': [(6, 0, [line.id])],
            'warehouse_id': self.warehouse.id,
            'picking_type_id': self.warehouse.int_type_id.id,
            'source_location_id': self.location.id,
            'destination_location_id': self.warehouse.lot_stock_id.id,
        })
        wizard.action_create_issue()
        line.invalidate_recordset()

        self.assertEqual(line.qty_reserved, 0.0)
        self.assertFalse(line.issue_reserved)
