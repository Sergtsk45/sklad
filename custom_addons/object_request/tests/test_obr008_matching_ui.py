"""
OBR-008: Тесты полей и UI сопоставления строк.
"""
from odoo.tests.common import TransactionCase
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestObr008MatchingUI(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['object.request.project'].create({
            'name': 'Тестовый объект',
            'code': 'TST-001',
        })
        self.foreman = self.env['res.users'].create({
            'name': 'Прораб Тест',
            'login': 'foreman_test_obr008',
            'email': 'foreman_obr008@test.com',
        })
        self.vendor = self.env['res.partner'].create({
            'name': 'Поставщик Тест',
            'supplier_rank': 1,
        })
        self.product = self.env['product.product'].create({
            'name': 'Товар Тест',
            'type': 'consu',
        })
        self.request = self.env['object.request'].create({
            'project_id': self.project.id,
            'foreman_user_id': self.foreman.id,
            'need_date': '2026-04-01',
        })
        self.line = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Тестовый материал',
            'qty_requested': 10.0,
            'matching_required': True,
            'manual_vendor_required': True,
        })

    def test_onchange_product_clears_matching_required(self):
        """Выбор product_id через onchange очищает matching_required."""
        self.assertTrue(self.line.matching_required)
        self.line.product_id = self.product
        # Симулируем onchange вручную (в тестах onchange не вызывается автоматически)
        self.line._onchange_product_id()
        self.assertFalse(
            self.line.matching_required,
            'matching_required должен сбрасываться при выборе товара',
        )

    def test_onchange_product_fills_uom(self):
        """onchange product_id заполняет uom_id из товара."""
        uom = self.env.ref('uom.product_uom_unit')
        self.product.uom_id = uom
        self.line.product_id = self.product
        self.line._onchange_product_id()
        self.assertEqual(
            self.line.uom_id, uom,
            'uom_id должен заполняться из товара',
        )

    def test_onchange_product_suggests_vendor(self):
        """onchange product_id предлагает поставщика из vendor info."""
        self.env['product.supplierinfo'].create({
            'product_tmpl_id': self.product.product_tmpl_id.id,
            'partner_id': self.vendor.id,
            'price': 100.0,
        })
        self.line.product_id = self.product
        self.line._onchange_product_id()
        self.assertEqual(
            self.line.preferred_vendor_id, self.vendor,
            'preferred_vendor_id должен автоматически заполняться из seller_ids',
        )

    def test_onchange_vendor_clears_manual_vendor_required(self):
        """Выбор поставщика очищает флаг manual_vendor_required."""
        self.assertTrue(self.line.manual_vendor_required)
        self.line.preferred_vendor_id = self.vendor
        self.line._onchange_preferred_vendor_id()
        self.assertFalse(
            self.line.manual_vendor_required,
            'manual_vendor_required должен сбрасываться при выборе поставщика',
        )

    def test_matching_required_false_when_already_false(self):
        """onchange не ломает строку если matching_required уже False."""
        self.line.matching_required = False
        self.line.product_id = self.product
        self.line._onchange_product_id()
        self.assertFalse(self.line.matching_required)

    def test_manual_vendor_required_false_when_already_false(self):
        """onchange не ломает строку если manual_vendor_required уже False."""
        self.line.manual_vendor_required = False
        self.line.preferred_vendor_id = self.vendor
        self.line._onchange_preferred_vendor_id()
        self.assertFalse(self.line.manual_vendor_required)

    def test_allowed_substitute_ids_many2many(self):
        """Можно привязать допустимые замены к строке."""
        substitute = self.env['product.product'].create({
            'name': 'Замена Товара',
            'type': 'consu',
        })
        self.line.allowed_substitute_ids = [(4, substitute.id)]
        self.assertIn(substitute, self.line.allowed_substitute_ids)
        self.assertTrue(self.line.has_substitutes)

    def test_line_state_requires_mapping_when_matching_required(self):
        """line_state = requires_mapping когда matching_required=True."""
        self.line.matching_required = True
        self.line._compute_line_state()
        self.assertEqual(self.line.line_state, 'requires_mapping')

    def test_line_state_ready_after_matching(self):
        """После выбора product_id и сброса matching_required — line_state = ready."""
        self.line.product_id = self.product
        self.line.matching_required = False
        self.line._compute_line_state()
        self.assertEqual(self.line.line_state, 'ready')

    def test_search_view_filter_problem_lines(self):
        """Поиск проблемных строк находит строки с matching_required или manual_vendor_required."""
        good_line = self.env['object.request.line'].create({
            'request_id': self.request.id,
            'name_raw': 'Хорошая строка',
            'qty_requested': 5.0,
            'product_id': self.product.id,
            'matching_required': False,
            'manual_vendor_required': False,
        })
        problem_lines = self.env['object.request.line'].search([
            '|',
            ('matching_required', '=', True),
            ('manual_vendor_required', '=', True),
            ('request_id', '=', self.request.id),
        ])
        self.assertIn(self.line, problem_lines)
        self.assertNotIn(good_line, problem_lines)
