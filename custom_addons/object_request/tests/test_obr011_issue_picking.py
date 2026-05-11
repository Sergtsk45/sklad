"""
OBR-011: Тесты создания складского документа выдачи.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged("post_install", "-at_install")
class TestObr011IssuePicking(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR-011",
            }
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб OBR011",
                "login": "foreman_test_obr011",
                "email": "foreman_obr011@test.com",
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Цемент М500 OBR011",
                "default_code": "CEM-011",
                "type": "consu",
            }
        )
        self.uom = self.product.uom_id
        self.warehouse = self.env["stock.warehouse"].search([], limit=1)
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        # Line with qty_to_issue
        self.line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент",
                "qty_requested": 10.0,
                "product_id": self.product.id,
                "uom_id": self.uom.id,
            }
        )
        self._add_stock_distribution(self.line, 6.0)
        self.request.write({"state": "in_progress"})

    def _add_stock_distribution(self, line, qty, warehouse=None):
        warehouse = warehouse or self.warehouse
        return (
            self.env["object.request.line.stock"]
            .with_context(
                auto_stock_distribution=True,
            )
            .create(
                {
                    "line_id": line.id,
                    "warehouse_id": warehouse.id,
                    "qty_on_hand": qty,
                    "qty_to_issue": qty,
                }
            )
        )

    def _create_warehouse(self, suffix):
        return (
            self.env["stock.warehouse"]
            .sudo()
            .create(
                {
                    "name": f"Склад OBR011-{suffix}",
                    "code": f"11{suffix}",
                    "company_id": self.env.company.id,
                }
            )
        )

    def _create_wizard(self):
        """Создать wizard предпросмотра с корректными данными."""
        return (
            self.env["object.request.issue.preview.wizard"]
            .with_context(
                default_request_id=self.request.id,
            )
            .create({})
        )

    def _create_issue(self, wizard=None):
        wizard = wizard or self._create_wizard()
        result = wizard.action_create_issues()
        picking = self.env["stock.picking"].search(result["domain"])
        return result, picking

    def test_wizard_default_get_fills_lines(self):
        """default_get группирует распределение с qty_to_issue > 0."""
        wiz = (
            self.env["object.request.issue.preview.wizard"]
            .with_context(default_request_id=self.request.id)
            .create({})
        )
        self.assertEqual(len(wiz.group_ids), 1)
        self.assertIn(self.line.stock_ids, wiz.group_ids.stock_line_ids)

    def test_wizard_no_lines_raises_user_error(self):
        """Если нет строк — UserError."""
        wiz = self.env["object.request.issue.preview.wizard"].create(
            {
                "request_id": self.request.id,
                "group_ids": [(5,)],
            }
        )
        with self.assertRaises(UserError):
            wiz.action_create_issues()

    def test_create_issue_creates_picking(self):
        """action_create_issues создаёт stock.picking."""
        result, picking = self._create_issue()
        self.assertEqual(result["res_model"], "stock.picking")
        self.assertTrue(picking.exists())
        self.assertTrue(picking.is_object_request_issue)
        self.assertEqual(picking.origin, self.request.name)

    def test_picking_has_correct_moves(self):
        """Picking содержит move с правильным количеством."""
        _result, picking = self._create_issue()
        self.assertEqual(len(picking.move_ids), 1)
        move = picking.move_ids[0]
        self.assertEqual(move.product_id, self.product)
        self.assertEqual(move.product_uom_qty, 6.0)

    def test_picking_linked_to_request(self):
        """Picking привязан к документу требования."""
        _result, picking = self._create_issue()
        self.assertIn(picking, self.request.issue_picking_ids)

    def test_line_linked_to_picking(self):
        """Строка документа привязана к picking и move."""
        _result, picking = self._create_issue()
        self.line.invalidate_recordset()
        self.assertEqual(self.line.issue_picking_id, picking)
        self.assertTrue(self.line.issue_move_id)

    def test_request_issue_picking_count(self):
        """issue_picking_count увеличивается после создания выдачи."""
        self._create_issue()
        self.request.invalidate_recordset()
        self.assertEqual(self.request.issue_picking_count, 1)

    def test_multiple_lines_creates_multiple_moves(self):
        """Несколько строк → несколько moves в одном picking."""
        product2 = self.env["product.product"].create(
            {
                "name": "Арматура 12мм OBR011",
                "default_code": "ARM-011",
                "type": "consu",
            }
        )
        line2 = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Арматура",
                "qty_requested": 20.0,
                "product_id": product2.id,
                "uom_id": product2.uom_id.id,
            }
        )
        self._add_stock_distribution(line2, 15.0)
        _result, picking = self._create_issue()
        self.assertEqual(len(picking.move_ids), 2)

    def test_multiwarehouse_distribution_creates_picking_per_warehouse(self):
        """Одна строка, два склада → две выдачи."""
        warehouse2 = self._create_warehouse("B")
        self._add_stock_distribution(self.line, 4.0, warehouse=warehouse2)

        _result, pickings = self._create_issue()

        self.assertEqual(len(pickings), 2)
        self.assertEqual(
            set(pickings.mapped("picking_type_id").ids),
            {self.warehouse.int_type_id.id, warehouse2.int_type_id.id},
        )
        self.assertEqual(
            set(self.line.stock_ids.mapped("picking_id").ids),
            set(pickings.ids),
        )
        self.assertEqual(
            sum(pickings.mapped("move_ids.product_uom_qty")),
            10.0,
        )

    def test_issue_preview_excluded_group_is_not_created(self):
        """Исключённая группа склада не создаёт picking."""
        warehouse2 = self._create_warehouse("C")
        self._add_stock_distribution(self.line, 4.0, warehouse=warehouse2)
        wizard = self._create_wizard()
        wizard.group_ids.filtered(
            lambda group: group.warehouse_id == warehouse2
        ).write({"included": False})

        _result, pickings = self._create_issue(wizard)

        self.assertEqual(len(pickings), 1)
        self.assertEqual(pickings.picking_type_id, self.warehouse.int_type_id)
        excluded_pickings = self.line.stock_ids.filtered(
            lambda stock: stock.warehouse_id == warehouse2
        ).mapped("picking_id")
        self.assertNotIn(pickings, excluded_pickings)

    def test_issue_preview_excluded_group_keeps_warehouse_from_lines(self):
        """Склад группы выводится из распределений; снятие «Создать» не ломает склад."""
        warehouse2 = self._create_warehouse("D")
        self._add_stock_distribution(self.line, 4.0, warehouse=warehouse2)
        wizard = self._create_wizard()
        group = wizard.group_ids.filtered(lambda g: g.warehouse_id == warehouse2)
        self.assertEqual(len(group), 1)
        group.write({"included": False})
        group.invalidate_recordset()
        self.assertEqual(group.warehouse_id, warehouse2)

    def test_issue_preview_relinks_cleared_stock_lines_on_create(self):
        """Пустые stock_line_ids на группе (как у веб-клиента при правках) восстанавливаются перед выдачей."""
        warehouse2 = self._create_warehouse("E")
        self._add_stock_distribution(self.line, 4.0, warehouse=warehouse2)
        wizard = self._create_wizard()
        g2 = wizard.group_ids.filtered(lambda g: g.warehouse_id == warehouse2)
        g2.write({"stock_line_ids": [(5,)]})
        g2.invalidate_recordset()
        self.assertFalse(g2.stock_line_ids)

        _result, pickings = self._create_issue(wizard)

        self.assertEqual(len(pickings), 2)

    def test_picking_project_linked(self):
        """Picking содержит ссылку на объект проекта."""
        _result, picking = self._create_issue()
        self.assertEqual(picking.object_request_project_id, self.project)

    def test_picking_back_link_to_request(self):
        """Обратная связь picking → request работает."""
        _result, picking = self._create_issue()
        self.assertIn(self.request, picking.object_request_ids)

    def test_action_open_issue_wizard_no_lines_raises(self):
        """action_open_issue_wizard без qty_to_issue → UserError."""
        request2 = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        self.env["object.request.line"].create(
            {
                "request_id": request2.id,
                "name_raw": "Цемент",
                "qty_requested": 5.0,
                "product_id": self.product.id,
            }
        )
        request2.write({"state": "in_progress"})
        with self.assertRaises(UserError):
            request2.action_open_issue_wizard()

    def test_action_open_issue_wizard_returns_wizard_action(self):
        """action_open_issue_wizard возвращает действие открытия wizard."""
        action = self.request.action_open_issue_wizard()
        self.assertEqual(
            action["res_model"],
            "object.request.issue.preview.wizard",
        )
        self.assertEqual(action["target"], "new")
