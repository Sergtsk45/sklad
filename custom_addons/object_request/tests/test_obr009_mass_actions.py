"""
OBR-009: Тесты массовых действий и ускорения сопоставления.
"""
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError
import datetime


@tagged("post_install", "-at_install")
class TestObr009MassActions(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["object.request.project"].create(
            {
                "name": "Тестовый объект OBR-009",
            }
        )
        self.foreman = self.env["res.users"].create(
            {
                "name": "Прораб Тест OBR009",
                "login": "foreman_test_obr009",
                "email": "foreman_obr009@test.com",
            }
        )
        self.vendor = self.env["res.partner"].create(
            {
                "name": "Поставщик ООО Тест",
                "supplier_rank": 1,
            }
        )
        self.product = self.env["product.product"].create(
            {
                "name": "Цемент М500",
                "default_code": "CEM-500",
                "type": "consu",
            }
        )
        self.env["product.supplierinfo"].create(
            {
                "partner_id": self.vendor.id,
                "product_tmpl_id": self.product.product_tmpl_id.id,
                "product_code": "ART-001",
                "price": 100.0,
            }
        )
        self.request = self.env["object.request"].create(
            {
                "project_id": self.project.id,
                "foreman_user_id": self.foreman.id,
                "need_date": datetime.date.today(),
            }
        )
        # Несопоставленная строка
        self.line_unmatched = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 10.0,
                "matching_required": True,
                "manual_vendor_required": True,
            }
        )
        # Строка с поставщиком, но без товара
        self.line_no_vendor = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Краска белая",
                "qty_requested": 5.0,
                "manual_vendor_required": True,
            }
        )

    # ----- line_problem_count -----

    def test_line_problem_count_includes_vendor_required(self):
        """line_problem_count считает строки с manual_vendor_required тоже."""
        self.request._compute_line_counters()
        # line_unmatched: matching_required + manual_vendor_required
        # line_no_vendor: manual_vendor_required
        self.assertEqual(self.request.line_problem_count, 2)

    def test_line_problem_count_decreases_after_fix(self):
        """Счётчик уменьшается, когда проблемы устраняются."""
        self.line_no_vendor.write({"manual_vendor_required": False})
        self.request._compute_line_counters()
        self.assertEqual(self.request.line_problem_count, 1)

    def test_line_problem_count_zero_when_all_matched(self):
        """Счётчик 0, когда все строки сопоставлены."""
        self.line_unmatched.write(
            {
                "matching_required": False,
                "manual_vendor_required": False,
                "product_id": self.product.id,
            }
        )
        self.line_no_vendor.write({"manual_vendor_required": False})
        self.request._compute_line_counters()
        self.assertEqual(self.request.line_problem_count, 0)

    # ----- action_rematch_lines -----

    def test_rematch_finds_product_by_article(self):
        """Пересопоставление находит товар по артикулу поставщика."""
        self.request.action_rematch_lines()
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.product_id, self.product)

    def test_rematch_finds_vendor(self):
        """Пересопоставление находит поставщика по имени."""
        self.request.action_rematch_lines()
        self.assertEqual(self.line_unmatched.preferred_vendor_id, self.vendor)

    def test_rematch_returns_notification(self):
        """action_rematch_lines возвращает display_notification."""
        result = self.request.action_rematch_lines()
        self.assertEqual(result.get("type"), "ir.actions.client")
        self.assertEqual(result.get("tag"), "display_notification")

    def test_rematch_no_unmatched_lines(self):
        """Пересопоставление без проблемных строк даёт info уведомление."""
        self.line_unmatched.write(
            {
                "matching_required": False,
                "product_id": self.product.id,
            }
        )
        self.line_no_vendor.write(
            {
                "matching_required": False,
                "product_id": self.product.id,
                "manual_vendor_required": False,
            }
        )
        result = self.request.action_rematch_lines()
        self.assertEqual(result["params"]["type"], "info")

    def test_rematch_lines_does_not_touch_already_matched(self):
        """Обычное пересопоставление не трогает уже сопоставленные строки."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Ошибочный товар OBR009",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_lines()

        self.assertEqual(line.product_id, wrong_product)

    def test_rematch_all_lines_updates_auto_matched_line(self):
        """Пересопоставление всех строк пересматривает auto matched строки."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Ошибочный товар OBR009 all",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertEqual(line.product_id, self.product)
        self.assertEqual(line.matching_source, "rematch_auto")
        self.assertIn("old product:", line.matching_note)

    def test_rematch_all_lines_clears_false_auto_match(self):
        """All-lines очищает старый auto match, если товар не найден."""
        wrong_product = self.env["product.product"].create(
            {
                "name": "Переход 108-57 ст.",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Переход",
                "supplier_article": "80x50 ГОСТ 17378-2001",
                "qty_requested": 1.0,
                "product_id": wrong_product.id,
                "matching_required": False,
                "matching_note": "import auto match",
                "matching_source": "import_auto",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertFalse(line.product_id)
        self.assertTrue(line.matching_required)
        self.assertEqual(line.matching_source, "unknown")
        self.assertIn("old product:", line.matching_note)

    def test_rematch_all_lines_keeps_manual_match(self):
        """All-lines не перезаписывает строку, похожую на ручной выбор."""
        manual_product = self.env["product.product"].create(
            {
                "name": "Ручной товар OBR009",
                "type": "consu",
            }
        )
        line = self.env["object.request.line"].create(
            {
                "request_id": self.request.id,
                "name_raw": "Цемент М500",
                "supplier_article": "ART-001",
                "supplier_raw": "Поставщик ООО Тест",
                "qty_requested": 1.0,
                "product_id": manual_product.id,
                "matching_required": False,
                "matching_note": "выбрано снабженцем",
                "matching_source": "manual",
            }
        )

        self.request.action_rematch_all_lines()

        self.assertEqual(line.product_id, manual_product)

    # ----- Wizard массового назначения: Назначить поставщика -----

    def test_assign_vendor_wizard(self):
        """Wizard назначает поставщика выбранным строкам."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id, self.line_no_vendor.id],
                active_model="object.request.line",
            )
            .create(
                {
                    "assign_type": "vendor",
                    "vendor_id": self.vendor.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.preferred_vendor_id, self.vendor)
        self.assertEqual(self.line_no_vendor.preferred_vendor_id, self.vendor)
        self.assertFalse(self.line_unmatched.manual_vendor_required)
        self.assertFalse(self.line_no_vendor.manual_vendor_required)

    def test_assign_vendor_wizard_no_vendor_raises(self):
        """Wizard без выбранного поставщика — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create({"assign_type": "vendor"})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    def test_assign_vendor_wizard_no_lines_raises(self):
        """Wizard без active_ids — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[],
            )
            .create({"assign_type": "vendor", "vendor_id": self.vendor.id})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    # ----- Wizard массового назначения: Назначить товар -----

    def test_assign_product_wizard(self):
        """Wizard назначает товар и снимает флаг matching_required."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
                active_model="object.request.line",
            )
            .create(
                {
                    "assign_type": "product",
                    "product_id": self.product.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.product_id, self.product)
        self.assertFalse(self.line_unmatched.matching_required)
        self.assertEqual(self.line_unmatched.matching_source, "manual")

    def test_assign_product_wizard_sets_uom(self):
        """Wizard при назначении товара выставляет uom_id."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create(
                {
                    "assign_type": "product",
                    "product_id": self.product.id,
                }
            )
        )
        wizard.action_assign()
        self.assertEqual(self.line_unmatched.uom_id, self.product.uom_id)

    def test_assign_product_wizard_no_product_raises(self):
        """Wizard без выбранного товара — UserError."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id],
            )
            .create({"assign_type": "product"})
        )
        with self.assertRaises(UserError):
            wizard.action_assign()

    # ----- line_count в wizard -----

    def test_wizard_line_count(self):
        """Wizard корректно отображает количество выбранных строк."""
        wizard = (
            self.env["object.request.line.assign.wizard"]
            .with_context(
                active_ids=[self.line_unmatched.id, self.line_no_vendor.id],
            )
            .create({"assign_type": "vendor", "vendor_id": self.vendor.id})
        )
        self.assertEqual(wizard.line_count, 2)
