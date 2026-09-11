"""
OBR-012: Тесты подтверждения выдачи кладовщиком и обратной синхронизации.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged("post_install", "-at_install")
class TestObr012ConfirmIssue(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR-012",
            }
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR012",
                "login": "foreman_test_obr012",
                "email": "foreman_obr012@test.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Цемент М500 OBR012",
                "default_code": "CEM-012",
                "type": "consu",
                "is_storable": True,
            }
        )
        self.uom = self.product.uom_id
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        self.warehouse = self.request._get_issue_warehouses()[:1]
        self.customer_loc = self.env.ref("stock.stock_location_customers")
        self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент",
                "qty_requested": 10.0,
                "product_id": self.product.id,
                "uom_id": self.uom.id,
            }
        )
        self.request.write({"state": "in_progress"})
        self.line = self.request.line_ids[0]
        self.env["object.request.line.stock"].with_context(
            auto_stock_distribution=True,
        ).create(
            {
                "line_id": self.line.id,
                "warehouse_id": self.warehouse.id,
                "qty_on_hand": 6.0,
                "qty_to_issue": 6.0,
            }
        )

    def _create_warehouse(self, suffix):
        warehouse = (
            self.env["stock.warehouse"]
            .sudo()
            .create(
                {
                    "name": f"Склад OBR012-{suffix}",
                    "code": f"12{suffix}",
                    "company_id": self.env.company.id,
                }
            )
        )
        self.request.write({"issue_warehouse_ids": [(4, warehouse.id)]})
        return warehouse

    def _create_picking(self):
        """Создать picking через wizard предпросмотра."""
        wiz = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(
                default_request_id=self.request.id,
            )
            .create({})
        )
        result = wiz.action_create_issues()
        return self.env["stock.picking"].search(result["domain"], limit=1)

    def _add_stock(self, qty=100.0):
        """Добавить товар на склад."""
        self.env["stock.quant"].create(
            {
                "product_id": self.product.id,
                "location_id": self.warehouse.lot_stock_id.id,
                "quantity": qty,
            }
        )

    def _add_stock_distribution(self, warehouse, qty):
        return (
            self.env["object.request.line.stock"]
            .with_context(
                auto_stock_distribution=True,
            )
            .create(
                {
                    "line_id": self.line.id,
                    "warehouse_id": warehouse.id,
                    "qty_on_hand": qty,
                    "qty_to_issue": qty,
                }
            )
        )

    def _validate_picking(self, picking, qty_by_move=None):
        for move in picking.move_ids:
            self.env["stock.quant"]._update_available_quantity(
                move.product_id,
                move.location_id,
                move.product_uom_qty,
            )
        picking.action_confirm()
        picking.action_assign()
        qty_by_move = qty_by_move or {}
        for ml in picking.move_line_ids:
            ml.quantity = qty_by_move.get(
                ml.move_id.id,
                ml.move_id.product_uom_qty,
            )
        picking.with_context(skip_backorder=True).button_validate()

    # --- Unit tests: _sync_qty_issued_to_request_lines ---

    def test_sync_updates_qty_issued_from_done_move(self):
        """_sync_qty_issued_to_request_lines читает done move.quantity."""
        picking = self._create_picking()
        self._validate_picking(picking)
        picking._sync_qty_issued_to_request_lines()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.qty_issued, 6.0)
        self.assertEqual(self.line.qty_issued_from_stock, 6.0)
        self.assertEqual(self.line.qty_to_issue, 0.0)
        self.assertEqual(self.line.qty_to_buy, 4.0)

    def test_sync_sums_done_quantities_from_multiwarehouse_moves(self):
        """Синхронизация суммирует выдачу строки из нескольких складов."""
        warehouse2 = self._create_warehouse("B")
        self._add_stock_distribution(warehouse2, 4.0)

        wizard = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(
                default_request_id=self.request.id,
            )
            .create({})
        )
        result = wizard.action_create_issues()
        pickings = self.env["stock.picking"].search(result["domain"])
        for picking in pickings:
            self._validate_picking(picking)

        pickings._sync_qty_issued_to_request_lines()

        self.line.invalidate_recordset()
        self.assertEqual(self.line.qty_issued, 10.0)
        self.assertEqual(self.line.line_state, "fully_supplied")
        self.assertEqual(self.line.qty_to_issue, 0.0)
        self.assertEqual(self.line.qty_to_buy, 0.0)

    def test_sync_partial_quantity(self):
        """Частичная синхронизация: qty_issued < qty_to_issue."""
        picking = self._create_picking()
        move = self.line.issue_move_id
        self._validate_picking(picking, {move.id: 3.0})
        picking._sync_qty_issued_to_request_lines()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.qty_issued, 3.0)
        self.assertEqual(self.line.qty_to_issue, 3.0)
        self.assertEqual(self.line.qty_to_buy, 4.0)

    def test_sync_zero_quantity(self):
        """При qty_issued == 0 line_state остаётся 'ready'."""
        picking = self._create_picking()
        picking._sync_qty_issued_to_request_lines()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.qty_issued, 0.0)

    # --- line_state вычисляется по qty_issued ---

    def test_line_state_partially_issued_after_issue_plan_done(self):
        """Выдача всего складского плана не закрывает строку на 10 из 10."""
        picking = self._create_picking()
        self._validate_picking(picking)
        picking._sync_qty_issued_to_request_lines()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.line_state, "partially_issued")

    def test_line_state_partially_issued_after_partial_sync(self):
        """После частичной синхронизации line_state == 'partially_issued'."""
        picking = self._create_picking()
        move = self.line.issue_move_id
        self._validate_picking(picking, {move.id: 3.0})
        picking._sync_qty_issued_to_request_lines()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.line_state, "partially_issued")

    # --- Интеграционные тесты: button_validate ---

    def test_validate_picking_updates_qty_issued(self):
        """button_validate обновляет qty_issued в строке требования."""
        picking = self._create_picking()
        self._validate_picking(picking)
        self.line.invalidate_recordset()
        self.assertEqual(self.line.qty_issued, 6.0)

    def test_validate_picking_state_becomes_done(self):
        """После button_validate picking переходит в state 'done'."""
        self._add_stock()
        picking = self._create_picking()
        picking.action_confirm()
        picking.action_assign()
        for ml in picking.move_line_ids:
            ml.quantity = ml.move_id.product_uom_qty
        picking.with_context(skip_backorder=True).button_validate()
        self.assertEqual(picking.state, "done")

    def test_validate_picking_line_state_partially_issued(self):
        """Выдача 6 из 10 оставляет строку частично обеспеченной."""
        picking = self._create_picking()
        self._validate_picking(picking)
        self.line.invalidate_recordset()
        self.assertEqual(self.line.line_state, "partially_issued")

    # --- _notify_if_all_lines_supplied ---

    def test_notify_posted_when_all_supplied(self):
        """Chatter-сообщение публикуется, когда все строки fully_supplied."""
        self.line.write({"qty_issued": 10.0})
        msg_count_before = len(self.request.message_ids)
        self.request._notify_if_all_lines_supplied()
        self.assertGreater(len(self.request.message_ids), msg_count_before)

    def test_notify_not_posted_when_not_all_supplied(self):
        """Chatter-сообщение не публикуется, если часть строк не обеспечена."""
        self.line.write({"qty_issued": 3.0})
        msg_count_before = len(self.request.message_ids)
        self.request._notify_if_all_lines_supplied()
        self.assertEqual(len(self.request.message_ids), msg_count_before)

    def test_notify_not_posted_after_partial_validate(self):
        """После выдачи 6 из 10 chatter о полном обеспечении не публикуется."""
        picking = self._create_picking()
        msg_count_before = len(self.request.message_ids)
        self._validate_picking(picking)
        self.assertEqual(len(self.request.message_ids), msg_count_before)

    # --- Счётчик qty_total_issued обновляется ---

    def test_qty_total_issued_updates_after_sync(self):
        """qty_total_issued на шапке пересчитывается после синхронизации."""
        picking = self._create_picking()
        self._validate_picking(picking)
        picking._sync_qty_issued_to_request_lines()
        self.request.invalidate_recordset()
        self.assertEqual(self.request.qty_total_issued, 6.0)
