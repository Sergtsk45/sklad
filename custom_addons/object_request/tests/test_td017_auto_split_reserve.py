"""
TD-017: авто-разбивка создаёт выдачи с резервом, резерв = «Обеспечено».
"""
import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestTD017AutoSplitReserve(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.project = cls.env["object.request.project"].create(
            {"name": "Объект TD-017"}
        )
        cls.foreman = cls.env["res.users"].create(
            {"name": "Прораб TD017", "login": "foreman_td017"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Фланец Ду40 TD017", "type": "consu", "is_storable": True}
        )

    def setUp(self):
        super().setUp()
        self.request = self._create_request(qty=10.0)
        self.line = self.request.line_ids
        self.warehouse = self.request._get_issue_warehouses()[:1]

    def _create_request(self, qty):
        request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        self.env["object.request.line"].create(
            {
                "request_id": request.id,
                "name_raw": "Фланец Ду40",
                "qty_requested": qty,
                "product_id": self.product.id,
            }
        )
        return request

    def _put_stock(self, qty):
        self.env["stock.quant"]._update_available_quantity(
            self.product, self.warehouse.lot_stock_id, qty
        )

    def _auto_split(self, request=None, state="in_progress"):
        request = request or self.request
        request.write({"state": state})
        request.action_check_stock()
        return request.action_auto_split()

    def _validate(self, picking):
        picking.with_context(skip_backorder=True).button_validate()

    # --- Авто-разбивка и резерв ---

    def test_auto_split_creates_issue_with_full_reserve(self):
        """Остатка хватает: выдача создана, резерв = план."""
        self._put_stock(50.0)
        self._auto_split()
        self.assertEqual(len(self.request.issue_picking_ids), 1)
        self.assertEqual(self.request.issue_picking_ids.state, "assigned")
        self.assertAlmostEqual(self.line.qty_reserved, 10.0)

    def test_reserved_line_counts_as_supplied(self):
        """Резерв входит в «Обеспечено», факт остаётся нулём."""
        self._put_stock(50.0)
        self._auto_split()
        self.assertAlmostEqual(self.line.qty_supplied, 10.0)
        self.assertAlmostEqual(self.line.qty_issued, 0.0)
        self.assertEqual(self.line.line_state, "reserved")

    def test_reserved_line_keeps_issue_plan(self):
        """«К выдаче» уменьшается только проведением, не резервом."""
        self._put_stock(50.0)
        self._auto_split()
        self.assertAlmostEqual(self.line.qty_to_issue, 10.0)
        self.assertAlmostEqual(self.line.qty_to_buy, 0.0)

    def test_reserved_line_counted_in_supplied_counter(self):
        """Счётчик обеспеченных строк считает резерв."""
        self._put_stock(50.0)
        self._auto_split()
        self.assertEqual(self.request.line_fully_supplied_count, 1)

    def test_no_stock_creates_no_issue(self):
        """Нет остатка — выдача не создаётся, всё в закупку."""
        result = self._auto_split()
        self.assertFalse(self.request.issue_picking_ids)
        self.assertAlmostEqual(self.line.qty_to_buy, 10.0)
        self.assertIn("Новых выдач нет", result["params"]["message"])

    def test_partial_stock_reserves_available_part(self):
        """Остатка 4 из 10: резерв 4, строка частично обеспечена."""
        self._put_stock(4.0)
        self._auto_split()
        self.assertAlmostEqual(self.line.qty_reserved, 4.0)
        self.assertAlmostEqual(self.line.qty_to_buy, 6.0)
        self.assertEqual(self.line.line_state, "partially_issued")

    def test_draft_auto_split_plans_without_issue(self):
        """В черновике только план: выдачи и резерва нет."""
        self._put_stock(50.0)
        result = self._auto_split(state="draft")
        self.assertFalse(self.request.issue_picking_ids)
        self.assertAlmostEqual(self.line.qty_to_issue, 10.0)
        self.assertIn("в работе", result["params"]["message"])

    def test_partial_reserve_warns(self):
        """План больше свободного остатка — предупреждение «X из Y»."""
        self._put_stock(3.0)
        self.request.write({"state": "in_progress"})
        self.request.action_check_stock()
        stock = self.line.stock_ids.filtered(
            lambda item: item.warehouse_id == self.warehouse
        )
        stock.with_context(auto_stock_distribution=True).write(
            {"qty_to_issue": 10.0}
        )
        pickings = self.request._create_issue_pickings_for_plan(stock)
        message, partial = self.request._auto_split_reserve_summary(
            stock, pickings
        )
        self.assertTrue(partial)
        self.assertIn("зарезервировано 3 из 10", message)

    # --- Проведение, снятие резерва, отмена ---

    def test_validate_issue_marks_fully_supplied(self):
        """Проведение выдачи: факт = запрошено, резерв не задваивается."""
        self._put_stock(50.0)
        self._auto_split()
        self._validate(self.request.issue_picking_ids)
        self.assertEqual(self.line.line_state, "fully_supplied")
        self.assertAlmostEqual(self.line.qty_reserved, 0.0)
        self.assertAlmostEqual(self.line.qty_supplied, 10.0)

    def test_unreserve_returns_line_to_ready(self):
        """Снятие резерва кладовщиком возвращает строку в «Готово»."""
        self._put_stock(50.0)
        self._auto_split()
        self.request.issue_picking_ids.do_unreserve()
        self.assertAlmostEqual(self.line.qty_supplied, 0.0)
        self.assertEqual(self.line.line_state, "ready")

    def test_reassign_restores_reserve(self):
        """Повторная проверка наличия на выдаче снова резервирует."""
        self._put_stock(50.0)
        self._auto_split()
        picking = self.request.issue_picking_ids
        picking.do_unreserve()
        picking.action_assign()
        self.assertEqual(self.line.line_state, "reserved")

    def test_cancel_issue_unlinks_and_returns_ready(self):
        """Отмена выдачи: строка в «Готово», распределение отвязано."""
        self._put_stock(50.0)
        self._auto_split()
        self.request.issue_picking_ids.action_cancel()
        self.assertEqual(self.line.line_state, "ready")
        self.assertFalse(self.line.stock_ids.mapped("move_id"))

    def test_auto_split_after_cancelled_issue_creates_new_one(self):
        """После отмены выдачи авто-разбивка создаёт новую."""
        self._put_stock(50.0)
        self._auto_split()
        self.request.issue_picking_ids.action_cancel()
        self.request.action_auto_split()
        open_pickings = self.request.issue_picking_ids.filtered(
            lambda picking: picking.state != "cancel"
        )
        self.assertEqual(len(open_pickings), 1)

    def test_repeat_auto_split_does_not_duplicate_issue(self):
        """Повторная авто-разбивка не трогает строку с открытой выдачей."""
        self._put_stock(50.0)
        self._auto_split()
        self.request.action_auto_split()
        self.assertEqual(len(self.request.issue_picking_ids), 1)
        self.assertAlmostEqual(self.line.qty_reserved, 10.0)

    def test_reset_split_cancels_open_issue(self):
        """Сброс разбивки отменяет выдачу и снимает резерв."""
        self._put_stock(50.0)
        self._auto_split()
        picking = self.request.issue_picking_ids
        self.line.action_reset_split()
        self.assertEqual(picking.state, "cancel")
        self.assertAlmostEqual(self.line.qty_supplied, 0.0)

    def test_request_cancel_cancels_open_issue(self):
        """Отмена требования отменяет непроведённые выдачи."""
        self._put_stock(50.0)
        self._auto_split()
        picking = self.request.issue_picking_ids
        self.request.action_cancel()
        self.assertEqual(picking.state, "cancel")

    def test_close_mentions_reserved_lines(self):
        """Закрытие предупреждает о строках, обеспеченных только резервом."""
        self._put_stock(50.0)
        self._auto_split()
        result = self.request.action_close()
        self.assertIn("в резерве", result["context"]["default_message"])

    # --- Другие заявки ---

    def test_second_request_does_not_see_reserved_stock(self):
        """Вторая заявка видит остаток за вычетом резерва первой."""
        self._put_stock(12.0)
        self._auto_split()
        other = self._create_request(qty=10.0)
        self._auto_split(request=other)
        self.assertAlmostEqual(other.line_ids.qty_reserved, 2.0)
        self.assertAlmostEqual(other.line_ids.qty_to_buy, 8.0)

    def test_issue_wizard_reserve_counts_as_supplied(self):
        """Выдача из мастера тоже засчитывает резерв."""
        self._put_stock(50.0)
        self._auto_split(state="draft")
        self.request.write({"state": "in_progress"})
        wizard = self.env["object.request.issue.preview.wizard"].with_context(
            default_request_id=self.request.id
        ).create({})
        wizard.action_create_issues()
        self.assertEqual(self.line.line_state, "reserved")
