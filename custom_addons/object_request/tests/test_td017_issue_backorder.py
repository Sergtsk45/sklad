"""
TD-017: частичное проведение выдачи — backorder остаётся в обеспечении строки.
"""
import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTD017IssueBackorder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["object.request.project"].create(
            {"name": "Объект TD-017 backorder"}
        )
        cls.foreman = cls.env["res.users"].create(
            {"name": "Прораб TD017 BO", "login": "foreman_td017_bo"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Фланец Ду80 TD017", "type": "consu", "is_storable": True}
        )

    def setUp(self):
        super().setUp()
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        self.line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Фланец Ду80",
                "qty_requested": 10.0,
                "product_id": self.product.id,
            }
        )
        warehouse = self.request._get_issue_warehouses()[:1]
        self.env["stock.quant"]._update_available_quantity(
            self.product, warehouse.lot_stock_id, 50.0
        )
        self.request.write({"state": "in_progress"})
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.picking = self.request.issue_picking_ids

    def _issue_part(self, qty, backorder=True):
        move = self.picking.move_ids
        move.quantity = qty
        move.picked = True
        self.picking.with_context(
            cancel_backorder=not backorder
        )._action_done()

    def _open_pickings(self):
        return self.request.issue_picking_ids.filtered(
            lambda picking: picking.state not in ("done", "cancel")
        )

    # --- Частичная выдача с backorder ---

    def test_backorder_keeps_fact_and_reserve(self):
        """Выдано 4 из 10: факт 4, резерв backorder 6, строка обеспечена."""
        self._issue_part(4.0)
        self.assertAlmostEqual(self.line.qty_issued, 4.0)
        self.assertAlmostEqual(self.line.qty_reserved, 6.0)
        self.assertEqual(self.line.line_state, "reserved")

    def test_backorder_becomes_current_issue(self):
        """Ссылка «Выдача» строки переходит на backorder."""
        self._issue_part(4.0)
        backorder = self._open_pickings()
        self.assertEqual(backorder.backorder_id, self.picking)
        self.assertEqual(self.line.issue_picking_id, backorder)

    def test_backorder_keeps_issue_plan(self):
        """«К выдаче» = непроведённый остаток."""
        self._issue_part(4.0)
        self.assertAlmostEqual(self.line.qty_to_issue, 6.0)

    def test_validate_backorder_fully_supplies(self):
        """Проведение backorder: факт 10, строка полностью обеспечена."""
        self._issue_part(4.0)
        backorder = self._open_pickings()
        backorder.with_context(skip_backorder=True).button_validate()
        self.assertAlmostEqual(self.line.qty_issued, 10.0)
        self.assertEqual(self.line.line_state, "fully_supplied")

    def test_repeat_auto_split_keeps_backorder(self):
        """Авто-разбивка не дублирует открытый backorder."""
        self._issue_part(4.0)
        self.request.action_auto_split()
        self.assertEqual(len(self._open_pickings()), 1)

    # --- Частичная выдача без backorder ---

    def test_no_backorder_leaves_remaining_plan(self):
        """Без backorder: факт 4, резерва нет, остаток 6 к выдаче."""
        self._issue_part(4.0, backorder=False)
        self.assertAlmostEqual(self.line.qty_reserved, 0.0)
        self.assertAlmostEqual(self.line.qty_to_issue, 6.0)
        self.assertEqual(self.line.line_state, "partially_issued")

    def test_no_backorder_auto_split_issues_remaining(self):
        """После отказа от backorder авто-разбивка резервирует остаток."""
        self._issue_part(4.0, backorder=False)
        self.request.action_auto_split()
        self.assertEqual(len(self._open_pickings()), 1)
        self.assertAlmostEqual(self._open_pickings().move_ids.quantity, 6.0)
        self.assertEqual(self.line.line_state, "reserved")

    def test_no_backorder_recompute_keeps_remaining_plan(self):
        """Пересчёт после повторной выдачи не занижает остаток плана."""
        self._issue_part(4.0, backorder=False)
        self.request.action_auto_split()
        self.line.recompute_supply_state_from_done_moves()
        self.assertAlmostEqual(self.line.qty_to_issue, 6.0)

    def test_no_backorder_then_second_issue_fully_supplies(self):
        """Повторная выдача остатка доводит строку до 10."""
        self._issue_part(4.0, backorder=False)
        self.request.action_auto_split()
        self._open_pickings().with_context(
            skip_backorder=True
        ).button_validate()
        self.assertAlmostEqual(self.line.qty_issued, 10.0)
        self.assertEqual(self.line.line_state, "fully_supplied")

    def test_issue_wizard_available_for_other_lines(self):
        """Мастер выдачи открывается, если у другой строки уже есть выдача."""
        self.request.write({"state": "draft"})
        other = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Фланец Ду80, ещё",
                "qty_requested": 2.0,
                "product_id": self.product.id,
            }
        )
        self.request.action_check_stock()
        other._apply_auto_issue_distribution()
        self.request.write({"state": "in_progress"})
        action = self.request.action_open_issue_wizard()
        self.assertEqual(
            action["res_model"], "object.request.issue.preview.wizard"
        )
