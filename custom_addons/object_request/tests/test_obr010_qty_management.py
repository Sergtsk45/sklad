"""
OBR-010: Тесты ручного управления количествами к выдаче.
"""
import datetime
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import ValidationError


@tagged('post_install', '-at_install')
class TestObr010QtyManagement(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект OBR-010',
            'code': 'TST-010',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб Тест OBR010',
            'login': 'foreman_test_obr010',
            'email': 'foreman_obr010@test.com',
        })
        self.product = self.env['product.product'].create({
            'name': 'Цемент М500 OBR010',
            'default_code': 'CEM-010',
            'type': 'consu',
        })
        self.request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': datetime.date.today(),
        })
        self.line = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Цемент М500',
            'qty_requested': 10.0,
            'product_id': self.product.id,
        })

    # --- Тесты onchange авто-заполнения qty_to_buy ---

    def test_onchange_qty_to_issue_fills_qty_to_buy(self):
        """Когда задаём qty_to_issue, qty_to_buy авто-заполняется как остаток."""
        self.line.qty_to_issue = 6.0
        self.line._onchange_qty_to_issue()
        self.assertEqual(self.line.qty_to_buy, 4.0)

    def test_onchange_qty_to_issue_full_fills_zero_to_buy(self):
        """Если qty_to_issue == qty_requested, qty_to_buy = 0."""
        self.line.qty_to_issue = 10.0
        self.line._onchange_qty_to_issue()
        self.assertEqual(self.line.qty_to_buy, 0.0)

    def test_onchange_qty_to_issue_zero_fills_full_to_buy(self):
        """Если qty_to_issue == 0, qty_to_buy = qty_requested."""
        self.line.qty_to_issue = 0.0
        self.line._onchange_qty_to_issue()
        self.assertEqual(self.line.qty_to_buy, 10.0)

    def test_onchange_qty_to_issue_partial(self):
        """Частичная выдача: qty_to_buy = qty_requested - qty_to_issue."""
        self.line.qty_to_issue = 3.0
        self.line._onchange_qty_to_issue()
        self.assertEqual(self.line.qty_to_buy, 7.0)

    # --- Тесты procurement_mode автообновления ---

    def test_procurement_mode_issue_only(self):
        """Только qty_to_issue > 0 → procurement_mode = 'issue'."""
        self.line.write({'qty_to_issue': 10.0, 'qty_to_buy': 0.0})
        self.line._onchange_qty_distribution()
        self.assertEqual(self.line.procurement_mode, 'issue')

    def test_procurement_mode_buy_only(self):
        """Только qty_to_buy > 0 → procurement_mode = 'buy'."""
        self.line.write({'qty_to_issue': 0.0, 'qty_to_buy': 10.0})
        self.line._onchange_qty_distribution()
        self.assertEqual(self.line.procurement_mode, 'buy')

    def test_procurement_mode_mixed(self):
        """qty_to_issue > 0 и qty_to_buy > 0 → procurement_mode = 'mixed'."""
        self.line.write({'qty_to_issue': 5.0, 'qty_to_buy': 5.0})
        self.line._onchange_qty_distribution()
        self.assertEqual(self.line.procurement_mode, 'mixed')

    def test_procurement_mode_manual_when_both_zero(self):
        """qty_to_issue == 0 и qty_to_buy == 0 → procurement_mode = 'manual'."""
        self.line.write({'qty_to_issue': 0.0, 'qty_to_buy': 0.0})
        self.line._onchange_qty_distribution()
        self.assertEqual(self.line.procurement_mode, 'manual')

    # --- Тесты constraints ---

    def test_constraint_sum_exceeds_requested(self):
        """qty_to_issue + qty_to_buy > qty_requested → ValidationError."""
        with self.assertRaises(ValidationError):
            self.line.write({'qty_to_issue': 7.0, 'qty_to_buy': 5.0})

    def test_constraint_sum_equals_requested_ok(self):
        """qty_to_issue + qty_to_buy == qty_requested — допустимо."""
        self.line.write({'qty_to_issue': 4.0, 'qty_to_buy': 6.0})
        self.assertEqual(self.line.qty_to_issue + self.line.qty_to_buy, 10.0)

    def test_constraint_qty_to_issue_negative(self):
        """qty_to_issue < 0 → IntegrityError (SQL CHECK)."""
        with self.assertRaises(Exception):
            self.line.write({'qty_to_issue': -1.0})
            self.env.flush_all()

    # --- Тесты агрегатных полей шапки ---

    def test_header_qty_totals_computed(self):
        """Сумма qty_total_to_issue/qty_total_to_buy/qty_total_issued пересчитывается."""
        self.line.write({'qty_to_issue': 3.0, 'qty_to_buy': 7.0})
        self.request.invalidate_recordset()
        self.assertEqual(self.request.qty_total_requested, 10.0)
        self.assertEqual(self.request.qty_total_to_issue, 3.0)
        self.assertEqual(self.request.qty_total_to_buy, 7.0)
        self.assertEqual(self.request.qty_total_issued, 0.0)

    def test_header_qty_totals_multiple_lines(self):
        """Агрегаты суммируют несколько строк."""
        self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Арматура 12мм',
            'qty_requested': 20.0,
            'product_id': self.product.id,
            'qty_to_issue': 10.0,
            'qty_to_buy': 10.0,
        })
        self.line.write({'qty_to_issue': 5.0, 'qty_to_buy': 5.0})
        self.request.invalidate_recordset()
        self.assertEqual(self.request.qty_total_requested, 30.0)
        self.assertEqual(self.request.qty_total_to_issue, 15.0)
        self.assertEqual(self.request.qty_total_to_buy, 15.0)
