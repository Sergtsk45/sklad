"""
OBR-019: Тесты автоматического расчёта наличия и авто-разбивки.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError


@tagged('post_install', '-at_install')
class TestObr019StockCheck(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-019',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб Тест OBR019',
            'login': 'foreman_test_obr019',
            'email': 'foreman_obr019@test.com',
        })
        # storable product (consu + is_storable=True в Odoo 19)
        self.product_a = self.env['product.product'].create({
            'name': 'Кирпич OBR019',
            'default_code': 'BRICK-019',
            'type': 'consu',
            'is_storable': True,
        })
        self.product_b = self.env['product.product'].create({
            'name': 'Цемент OBR019',
            'default_code': 'CEM-019',
            'type': 'consu',
            'is_storable': True,
        })
        self.warehouse = self.env['stock.warehouse'].search([], limit=1)
        self.stock_loc = self.warehouse.lot_stock_id
        self.request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })
        self.line_a = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Кирпич',
            'qty_requested': 100.0,
            'product_id': self.product_a.id,
        })
        self.line_b = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Цемент',
            'qty_requested': 50.0,
            'product_id': self.product_b.id,
        })

    def _add_stock(self, product, qty):
        """Добавить stock.quant для продукта на основной склад."""
        self.env['stock.quant']._update_available_quantity(
            product, self.stock_loc, qty,
        )

    def _create_warehouse(self, suffix):
        return self.env['stock.warehouse'].sudo().create({
            'name': f'Склад OBR019-{suffix}',
            'code': f'19{suffix}',
            'company_id': self.env.company.id,
        })

    def _put_stock(self, product, warehouse, qty):
        self.env['stock.quant']._update_available_quantity(
            product, warehouse.lot_stock_id, qty,
        )

    # ── action_check_stock ──────────────────────────────────────────────────

    def test_check_stock_fills_stock_check_date(self):
        """action_check_stock заполняет stock_check_date для строк с product_id."""  # noqa: E501
        self.request.action_check_stock()
        self.assertTrue(self.line_a.stock_check_date)
        self.assertTrue(self.line_b.stock_check_date)

    def test_check_stock_zero_when_no_stock(self):
        """При отсутствии остатка stock_qty_on_hand = 0."""
        self.request.action_check_stock()
        self.assertEqual(self.line_a.stock_qty_on_hand, 0.0)
        self.assertEqual(self.line_b.stock_qty_on_hand, 0.0)

    def test_check_stock_reads_actual_qty(self):
        """stock_qty_on_hand заполняется по реальному остатку со склада."""
        self._add_stock(self.product_a, 80.0)
        self._add_stock(self.product_b, 20.0)
        self.request.action_check_stock()
        self.assertEqual(self.line_a.stock_qty_on_hand, 80.0)
        self.assertEqual(self.line_b.stock_qty_on_hand, 20.0)

    def test_check_stock_skips_lines_without_product(self):
        """Строки без product_id не обрабатываются и не вызывают ошибку."""
        line_no_product = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Неизвестный материал',
            'qty_requested': 5.0,
        })
        self.request.action_check_stock()
        self.assertFalse(line_no_product.stock_check_date)

    def test_check_stock_raises_if_no_matched_lines(self):
        """UserError, если в документе нет строк с product_id."""
        request_empty = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })
        self.env['object.request.line'].create({
            'request_id': request_empty.id,
            'name_raw': 'Нет товара',
            'qty_requested': 1.0,
        })
        with self.assertRaises(UserError):
            request_empty.action_check_stock()

    def test_check_stock_returns_notification(self):
        """action_check_stock возвращает display_notification."""
        result = self.request.action_check_stock()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')

    # ── action_auto_split ───────────────────────────────────────────────────

    def test_auto_split_raises_if_not_checked(self):
        """UserError, если расчёт наличия ещё не выполнен."""
        with self.assertRaises(UserError):
            self.request.action_auto_split()

    def test_auto_split_full_stock_issues_all(self):
        """Если остатка достаточно — qty_to_issue = qty_requested, qty_to_buy = 0."""  # noqa: E501
        self._add_stock(self.product_a, 200.0)
        self._add_stock(self.product_b, 200.0)
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.assertAlmostEqual(self.line_a.qty_to_issue, 100.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)
        self.assertEqual(self.line_a.procurement_mode, 'issue')

    def test_auto_split_zero_stock_buys_all(self):
        """Если остатка нет — qty_to_issue = 0, qty_to_buy = qty_requested."""
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.assertAlmostEqual(self.line_a.qty_to_issue, 0.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 100.0)
        self.assertEqual(self.line_a.procurement_mode, 'buy')

    def test_auto_split_partial_stock_mixed(self):
        """Частичный остаток → qty_to_issue = остаток, qty_to_buy = дефицит."""
        self._add_stock(self.product_a, 60.0)
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.assertAlmostEqual(self.line_a.qty_to_issue, 60.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 40.0)
        self.assertEqual(self.line_a.procurement_mode, 'mixed')

    def test_auto_split_uses_two_warehouses_when_one_is_not_enough(self):
        """Если одного склада не хватает, план берётся с нескольких."""
        warehouse2 = self._create_warehouse('B')
        self._put_stock(self.product_a, self.warehouse, 60.0)
        self._put_stock(self.product_a, warehouse2, 50.0)

        self.request.action_check_stock()
        self.request.action_auto_split()

        planned = self.line_a.stock_ids.filtered(
            lambda stock: stock.qty_to_issue > 0
        )
        self.assertEqual(len(planned), 2)
        self.assertAlmostEqual(sum(planned.mapped('qty_to_issue')), 100.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)

    def test_auto_split_uses_remaining_qty_after_partial_issue(self):
        """Уже выданное количество уменьшает остаток к обеспечению."""
        self.line_a.write({'qty_issued': 20.0})
        self._add_stock(self.product_a, 200.0)

        self.request.action_check_stock()
        self.request.action_auto_split()

        self.assertAlmostEqual(self.line_a.qty_to_issue, 80.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)

    def test_auto_split_warns_before_overwriting_manual_plan(self):
        """Ручная правка распределения открывает wizard подтверждения."""
        self._add_stock(self.product_a, 60.0)
        self.request.action_check_stock()
        self.line_a.stock_ids[:1].write({'qty_to_issue': 10.0})

        result = self.request.action_auto_split()

        self.assertEqual(result['type'], 'ir.actions.act_window')
        self.assertEqual(
            result['res_model'],
            'object.request.auto.split.confirm.wizard',
        )

    def test_auto_split_skips_zero_project_warehouse_stock(self):
        """Склад объекта с нулём не получает план выдачи."""
        other_warehouse = self._create_warehouse('C')
        self._put_stock(self.product_a, other_warehouse, 100.0)

        self.request.action_check_stock()
        self.request.action_auto_split()

        project_stock = self.line_a.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.project.warehouse_id
        )
        self.assertAlmostEqual(project_stock.qty_to_issue, 0.0)

    def test_auto_split_prioritizes_project_warehouse_when_it_has_stock(self):
        """Положительный остаток на складе объекта используется первым."""
        other_warehouse = self._create_warehouse('D')
        self._put_stock(self.product_a, self.project.warehouse_id, 5.0)
        self._put_stock(self.product_a, other_warehouse, 100.0)

        self.request.action_check_stock()
        self.request.action_auto_split()

        project_stock = self.line_a.stock_ids.filtered(
            lambda stock: stock.warehouse_id == self.project.warehouse_id
        )
        self.assertAlmostEqual(project_stock.qty_to_issue, 5.0)
        self.assertAlmostEqual(self.line_a.qty_to_issue, 100.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)

    def test_auto_split_exact_stock_issues_all(self):
        """Остаток равен запрошенному — всё выдаётся, ничего не закупается."""
        self._add_stock(self.product_a, 100.0)
        self.request.action_check_stock()
        self.request.action_auto_split()
        self.assertAlmostEqual(self.line_a.qty_to_issue, 100.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)
        self.assertEqual(self.line_a.procurement_mode, 'issue')

    def test_auto_split_does_not_exceed_requested(self):
        """qty_to_issue + qty_to_buy не превышает qty_requested."""
        self._add_stock(self.product_a, 500.0)
        self._add_stock(self.product_b, 500.0)
        self.request.action_check_stock()
        self.request.action_auto_split()
        total_a = self.line_a.qty_to_issue + self.line_a.qty_to_buy
        total_b = self.line_b.qty_to_issue + self.line_b.qty_to_buy
        self.assertAlmostEqual(total_a, self.line_a.qty_requested)
        self.assertAlmostEqual(total_b, self.line_b.qty_requested)

    def test_auto_split_skips_cancelled_lines(self):
        """Отменённые строки не обрабатываются при авто-разбивке."""
        self._add_stock(self.product_b, 200.0)
        self.line_b.write({'is_cancelled': True})
        self.request.action_check_stock()
        self.request.action_auto_split()
        # line_b отменена — её qty не должны были измениться
        self.assertAlmostEqual(self.line_b.qty_to_issue, 0.0)
        self.assertAlmostEqual(self.line_b.qty_to_buy, 0.0)

    def test_auto_split_returns_notification(self):
        """action_auto_split возвращает display_notification."""
        self.request.action_check_stock()
        result = self.request.action_auto_split()
        self.assertEqual(result['type'], 'ir.actions.client')
        self.assertEqual(result['tag'], 'display_notification')

    def test_check_stock_multiple_calls_update_date(self):
        """Повторный вызов action_check_stock обновляет stock_check_date."""
        import time
        self.request.action_check_stock()
        date1 = self.line_a.stock_check_date
        time.sleep(0.01)
        self.request.action_check_stock()
        date2 = self.line_a.stock_check_date
        self.assertGreaterEqual(date2, date1)

    def test_line_action_buy_all_moves_remaining_qty_to_purchase(self):
        """Массовое действие «Закупить всё» обнуляет план выдачи."""
        self.request.action_check_stock()
        stock = self.line_a.stock_ids[:1]
        stock.write({'qty_to_issue': 10.0})

        self.line_a.action_buy_all()

        self.assertAlmostEqual(self.line_a.qty_to_issue, 0.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 100.0)
        self.assertEqual(self.line_a.procurement_mode, 'buy')
        self.assertTrue(self.line_a.manual_plan_override)

    def test_line_action_reset_split_clears_plan(self):
        """Массовое действие «Сбросить разбивку» очищает выдачу и закупку."""
        self.request.action_check_stock()
        self.line_a.write({'qty_to_issue': 4.0, 'qty_to_buy': 6.0})

        self.line_a.action_reset_split()

        self.assertAlmostEqual(self.line_a.qty_to_issue, 0.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 0.0)
        self.assertEqual(self.line_a.procurement_mode, 'manual')

    def test_line_action_issue_max_uses_available_stock(self):
        """«Выдать максимум» повторяет авто-разбивку строки."""
        self._add_stock(self.product_a, 60.0)
        self.request.action_check_stock()

        self.line_a.action_issue_max()

        self.assertAlmostEqual(self.line_a.qty_to_issue, 60.0)
        self.assertAlmostEqual(self.line_a.qty_to_buy, 40.0)
        self.assertEqual(self.line_a.procurement_mode, 'mixed')
